"""API for XRPD plotting use by the processing"""

import time
import logging
import functools
from typing import Optional, Union, Tuple

import numpy

try:
    import gevent
except ImportError:
    gevent = None
try:
    from bliss import current_session
except ImportError:
    current_session = None

from silx.io import h5py_utils
from silx.utils.retry import RetryError

from ..flint import WithFlintAccess
from .plots import XrpdCurvePlot
from .plots import XrpdImagePlot
from .data import get_redis_store
from .data import add_plot
from .data import add_data
from .data import remove_plots


def _background_task(method):
    @functools.wraps(method)
    def wrapper(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as e:
            logging.error("XRPD plotter task failed (%s)", e, exc_info=True)
            raise

    return wrapper


class Plotter(WithFlintAccess):
    def __init__(self, number_of_scans: int = 0) -> None:
        if current_session is None:
            raise ModuleNotFoundError("No module named 'bliss'")
        super().__init__()
        self._tasks = list()
        self._redis_store = get_redis_store(
            f"blissoda:{current_session.name}:{self.__class__.__name__}"
        )
        self.number_of_scans = number_of_scans

    @property
    def number_of_scans(self):
        """Maximum number of scans to be plotted"""
        return self._plot_scans

    @number_of_scans.setter
    def number_of_scans(self, value):
        self._plot_scans = max(value, 0)
        self._remove_old_plots()

    def handle_workflow_result(
        self,
        future,
        lima_name: str,
        scan_name: str,
        output_url: Optional[str] = None,
        retry_timeout: int = 60,
        retry_period: int = 1,
    ):
        """Handle workflow results in a background task"""
        if output_url:
            func = self._handle_workflow_result_from_file
        else:
            func = self._handle_workflow_result_from_memory
        self._spawn(
            func,
            future,
            scan_name,
            lima_name,
            output_url=output_url,
            retry_timeout=retry_timeout,
            retry_period=retry_period,
        )

    def purge_tasks(self) -> int:
        """Remove references to tasks that have finished."""
        self._tasks = [t for t in self._tasks if t]
        return len(self._tasks)

    def kill_tasks(self) -> int:
        """Kill all tasks."""
        gevent.killall(self._tasks)
        return self.purge_tasks()

    def replot(self, **retry_options) -> None:
        """Re-draw all plots."""
        for plot_key, plot_info in self._redis_store.items():
            self._spawn(self._update_plot, plot_key, plot_info, retry_options)

    def clear(self):
        """Clear all plots."""
        self._remove_plots(0)

    def _spawn(self, *args, **kw):
        task = gevent.spawn(*args, **kw)
        self._tasks.append(task)
        self.purge_tasks()

    @_background_task
    def _handle_workflow_result_from_memory(
        self,
        future,
        scan_name: str,
        lima_name: str,
        retry_timout: int = 600,
        **retry_options,
    ) -> None:
        result = future.get(retry_timout)
        if result["radial_units"] is None:
            return

        points = result["intensity"]
        xvalues = result["radial"]
        xname, xunits = result["radial_units"].split("_")
        xlabel = f"{xname} ({xunits})"

        plot_key, plot_info = self._add_plot(
            scan_name, lima_name, xlabel, xvalues, points.ndim
        )
        self._add_data(plot_key, plot_info, numpy.atleast_2d(points), retry_options)

    @_background_task
    def _handle_workflow_result_from_file(
        self,
        future,
        scan_name: str,
        lima_name: str,
        output_url: str,
        **retry_options,
    ) -> None:
        plot_key, plot_info = self._add_plot_from_file(
            scan_name, lima_name, output_url, **retry_options
        )
        retry_period = retry_options.get("retry_period")
        while not future.ready():
            self._update_plot(plot_key, plot_info, retry_options)
            if retry_period:
                time.sleep(retry_period)
        self._update_plot(plot_key, plot_info, retry_options)

    @h5py_utils.retry()
    def _add_plot_from_file(
        self, scan_name: str, lima_name: str, output_url: str
    ) -> Tuple[str, str]:
        filename, nxdata_name = output_url.split("::")
        with h5py_utils.File(filename, mode="r") as f:
            try:
                nxdata = f[nxdata_name]
                xname = nxdata.attrs["axes"][-1]
                dset = nxdata[xname]
                xunits = dset.attrs["units"]
            except KeyError as e:
                raise RetryError(str(e))
            xlabel = f"{xname} ({xunits})"
            xvalues = dset[()]
            signal = nxdata[nxdata.attrs["signal"]]
            hdf5_url = f"{filename}::{signal.name}"
            plot_key, plot_info = self._add_plot(
                scan_name,
                lima_name,
                xlabel,
                xvalues,
                signal.ndim,
                hdf5_url=hdf5_url,
            )
            return plot_key, plot_info

    def _add_plot(
        self,
        scan_name: str,
        lima_name: str,
        xlabel: str,
        xvalues: numpy.ndarray,
        signal_ndim: int,
        hdf5_url: Optional[str] = None,
    ) -> Tuple[str, dict]:
        plot_key, plot_info = add_plot(
            self._redis_store,
            scan_name,
            lima_name,
            signal_ndim,
            xlabel,
            xvalues,
            hdf5_url=hdf5_url,
        )
        self._remove_old_plots()
        return plot_key, plot_info

    def _add_data(
        self, plot_key: str, plot_info: dict, points: numpy.ndarray, retry_options: dict
    ) -> str:
        add_data(plot_key, plot_info, points)
        self._update_plot(plot_key, plot_info, retry_options)

    def _update_plot(self, plot_key: str, plot_info: dict, retry_options: dict) -> None:
        if _is_not_ct(plot_info):
            imageplot = self._get_plot(plot_info["lima_name"])
            imageplot.update_plot(self._redis_store.name, plot_key, retry_options)
        curveplot = self._get_plot()
        curveplot.update_plot(self._redis_store.name, plot_key, retry_options)

    def _remove_plot(self, plot_key: str, plot_info: dict) -> None:
        if _is_not_ct(plot_info):
            imageplot = self._get_plot(plot_info["lima_name"])
            imageplot.remove_plot(self._redis_store.name, plot_key)
        curveplot = self._get_plot()
        curveplot.remove_plot(self._redis_store.name, plot_key)

    def _remove_plots(self, max_len: int):
        remove_plots(self._redis_store, max_len, self._remove_plot)

    def _remove_old_plots(self):
        self._remove_plots(self._plot_scans)

    def _get_plot(
        self, lima_name: Optional[str] = None
    ) -> Union[XrpdCurvePlot, XrpdImagePlot]:
        if lima_name:
            return super()._get_plot(f"Integrated {lima_name}", XrpdImagePlot)
        return super()._get_plot("Integrated (Last)", XrpdCurvePlot)


def _is_not_ct(plot_info: dict) -> bool:
    try:
        return plot_info["signal_ndim"] > 1
    except KeyError:
        # Plot produced by an old version of blissoda
        return not plot_info["ct"]
