"""Workflow execution and Flint EXAFS plotting during a scan"""

import time
import os
import logging
import gevent
from collections import OrderedDict
from typing import List, Optional, Tuple, Dict

from silx.io.h5py_utils import top_level_names

try:
    from bliss.common.plot import get_flint
    from bliss.flint.client.proxy import FlintClient
except ImportError:
    get_flint = None
    FlintClient = None

from ewoksjob.client import submit
from ewoksjob.client import get_future

from ..persistent.parameters import WithPersistentParameters
from .plots import ExafsPlot
from ..persistent.parameters import ParameterInfo


logger = logging.getLogger(__name__)


class ExafsPlotter(
    WithPersistentParameters,
    parameters=[
        ParameterInfo("refresh_period"),
        ParameterInfo("max_scans"),
        ParameterInfo("enabled"),
        ParameterInfo("workflow"),
        ParameterInfo("_counters"),
        ParameterInfo("_scan_type"),
        ParameterInfo("_color_index"),
    ],
):
    """Run a scan, execute a workflow every x seconds during the scan
    and plot the results in Flint. A fixed number of n scans stay plotted.
    """

    def __init__(self, **defaults) -> None:
        defaults.setdefault("refresh_period", 2)  # seconds
        defaults.setdefault("max_scans", 3)
        defaults.setdefault("enabled", True)
        defaults.setdefault("_counters", dict())
        defaults.setdefault("_color_index", 0)
        super().__init__(**defaults)

        # Fixed parameters
        self._plot_id = "EXAFS"
        self._plot_names = {
            "flatten_mu": "mu",
            "chi_weighted_k": "chi",
            "ft_mag": "ft",
            "noise_savgol": "noise",
        }

        # Runtime data
        self._scans = OrderedDict()  # scan_id -> scan_info
        self._plot: Optional[ExafsPlot] = None
        self._client = None

    @property
    def counters(self) -> dict:
        return self._counters.get(self.scan_type, dict())

    @property
    def scan_type(self):
        return self._scan_type

    @scan_type.setter
    def scan_type(self, value):
        if value not in self._counters:
            raise ValueError(f"Valid scan types are: {list(self._counters)}")
        self._scan_type = value

    @property
    def mu_name(self) -> Optional[str]:
        return self.counters.get("mu_name")

    @mu_name.setter
    def mu_name(self, value):
        self.counters["mu_name"] = value

    @property
    def energy_name(self) -> Optional[str]:
        return self.counters.get("energy_name")

    @energy_name.setter
    def energy_name(self, value):
        self.counters["energy_name"] = value

    @property
    def energy_unit(self) -> Optional[str]:
        return self.counters.get("energy_unit")

    @energy_unit.setter
    def energy_unit(self, value):
        self.counters["energy_unit"] = value

    def _scan_type_from_scan(self, scan) -> Optional[str]:
        raise NotImplementedError

    def run(self, scan, filename=None, **kw):
        if not self.enabled:
            scan.run()
            return

        self.scan_type = self._scan_type_from_scan(scan)

        if not self.scan_type:
            scan.run()
            return

        if filename is None:
            try:
                filename = scan.writer.get_filename()
            except AttributeError:
                # bliss < 1.0.0
                filename = scan.writer.filename
        if os.path.exists(filename):
            scans = top_level_names(filename, include_only=None)
            scannr = max(int(float(s)) for s in scans) + 1
        else:
            scannr = 1
        scan_legend = f"{scannr}.1"
        scan_url = f"silx://{filename}::/{scannr}.1"
        scan_id = scan_url
        scan_name = os.path.split(os.path.dirname(filename))[-1]
        scan_name = f"{scan_name}:{scannr}.1"
        scan_color = self._COLOR_PALETTE[min(self._color_index, self._n_colors - 1)]
        self._color_index = (self._color_index + 1) % self._n_colors
        args = scan_id, scan_name, scan_legend, scan_color, scan_url

        update_loop = gevent.spawn(self._plotting_loop, *args)

        try:
            scan.run(**kw)
        finally:
            try:
                try:
                    if not update_loop:
                        update_loop.get()
                    update_loop.kill()
                    gevent.spawn(self._last_submit_and_plot, scan_id)
                finally:
                    self._removed_failed_processing()
                    self._purge_plots()
            except Exception:
                logger.warning("Post-scan update failed", exc_info=True)

    def _last_submit_and_plot(self, *args, **kw):
        gevent.sleep(1)
        self._submit_and_plot(*args, **kw)

    def clear(self):
        """Remove all scan curves in all plots"""
        self._get_plot().clear()

    def refresh(self):
        """Refresh all plots with the current processed data"""
        for scan_id in self._scans:
            self._update_scan_plot(scan_id)

    def reprocess(self):
        """Reprocess all scans and update all curves"""
        for scan_id in self._scans:
            self._submit_and_plot(scan_id)

    def dump(self) -> List[Tuple[str, dict]]:
        skip = "future", "result", "previous_result"
        return [
            (scan_id, {k: v for k, v in info.items() if k not in skip})
            for scan_id, info in self._scans.items()
        ]

    def load(self, data: List[Tuple[str, dict]]) -> None:
        for scan_id, scan_info in data:
            self._init_scan_cache(scan_id, **scan_info)
        self.refresh()

    def _submit_and_plot(self, scan_id: str):
        self._submit_workfow(scan_id)
        self._update_scan_plot(scan_id)

    def _plotting_loop(
        self,
        scan_id: str,
        scan_name: str,
        scan_legend: str,
        scan_color: tuple,
        scan_url: str,
    ):
        self._init_scan_cache(
            scan_id,
            scan_name=scan_name,
            scan_legend=scan_legend,
            scan_color=scan_color,
            scan_url=scan_url,
        )
        t0 = time.time()
        while True:
            t1 = time.time()
            sleep_time = max(t0 + self.refresh_period - t1, 0)
            gevent.sleep(sleep_time)
            t0 = t1
            try:
                self._submit_and_plot(scan_id)
            except Exception as e:
                logger.error(f"EXAFS workflow or plot failed ({e})")

    def _init_scan_cache(self, scan_id: str, **kw):
        scan_info = self._scans.get(scan_id)
        if scan_info is not None:
            return
        scan_info = {
            "job_id": None,
            "future": None,
            "result": None,
            "previous_result": None,
            "scan_legend": None,
            "scan_url": None,
            "scan_name": None,
            "scan_color": None,
        }
        scan_info.update(kw)
        self._scans[scan_id] = scan_info
        return scan_info

    def _purge_plots(self, max_scans=None):
        if max_scans is None:
            max_scans = self.max_scans
        npop = max(len(self._scans) - max_scans, 0)
        for _ in range(npop):
            _, scan_info = self._scans.popitem(last=False)
            self._remove_scan_plot(scan_info["scan_legend"])

    def remove_scan(self, scan_legend: str):
        scans = OrderedDict()
        for scan_id, scan_info in self._scans.items():
            if scan_info["scan_legend"] == scan_legend:
                self._remove_scan_plot(scan_legend)
            else:
                scans[scan_id] = scan_info
        self._scans = scans

    def _removed_failed_processing(self):
        scans = OrderedDict()
        for scan_id, scan_info in self._scans.items():
            if scan_info["previous_result"]:
                scans[scan_id] = scan_info
            else:
                self._remove_scan_plot(scan_info["scan_legend"])
        self._scans = scans

    def _remove_scan_plot(self, legend: str):
        self._get_plot().remove_scan(legend)

    def _update_scan_plot(self, scan_id: str):
        """Update all scan curves in all plots"""
        if self._plot_exists():
            # Update the existing plot for the requested scan
            self._update_scan(scan_id)
        else:
            # Create a fresh plot with all scan curves
            for _scan_id in self._scans:
                self._update_scan(_scan_id)

    def _update_scan(self, scan_id: str):
        """Update the scan curve in all plots"""
        result, scan_info = self._get_data(scan_id)
        if result is None:
            return
        data = {self._plot_names[k]: v for k, v in result.items()}
        self._get_plot().update_scan(
            scan_info["scan_legend"], data, color=scan_info["scan_color"]
        )

    def _get_plot(self) -> ExafsPlot:
        """Launches Flint and creates the plot when either is missing"""
        if not self._plot_exists():
            self._plot = self._get_flint().get_plot(
                ExafsPlot, unique_name=self._plot_id
            )
        return self._plot

    def _plot_exists(self) -> bool:
        if self._plot is None:
            return False
        return self._get_flint().is_plot_exists(self._plot_id)

    def _get_flint(self) -> FlintClient:
        """Launches Flint when missing"""
        if not self._flint_exists():
            self._client = get_flint()
        return self._client

    def _flint_exists(self):
        if self._client is None:
            return False
        try:
            if self._client.is_available():
                return True
        except FileNotFoundError:
            pass
        return False

    def _get_data(self, scan_id: str) -> Optional[Tuple[dict, dict]]:
        """Get data and curve legend for a scan when available.
        Blocks when the workflow for the scan is still running"""
        scan_info = self._scans.get(scan_id)
        if scan_info is None:
            return scan_info["previous_result"], scan_info
        result = scan_info.get("result")
        if result is not None:
            return result, scan_info
        future = scan_info.get("future")
        if future is None:
            job_id = scan_info.get("job_id")
            if job_id is None:
                return scan_info["previous_result"], scan_info
            future = scan_info["future"] = get_future(job_id)
        try:
            result = future.get()
        except Exception:
            return scan_info["previous_result"], scan_info
        result = result["plot_data"]

        scan_info["previous_result"] = result
        scan_info["result"] = result
        return result, scan_info

    def _submit_workfow(self, scan_id: str) -> None:
        """Submit the data processing for a scan"""
        scan_info = self._scans.get(scan_id)
        if not scan_info or not scan_info["scan_url"]:
            return
        inputs = list()
        input_information = {
            "channel_url": f"{scan_info['scan_url']}/measurement/{self.energy_name}",
            "spectra_url": f"{scan_info['scan_url']}/measurement/{self.mu_name}",
            "energy_unit": self.energy_unit,
        }
        inputs.append(
            {
                "label": "xas input",
                "name": "input_information",
                "value": input_information,
            }
        )
        inputs.append(
            {
                "label": "plotdata",
                "name": "plot_names",
                "value": list(self._plot_names),
            }
        )
        future = submit(args=(self.workflow,), kwargs={"inputs": inputs})
        scan_info["future"] = future
        scan_info["job_id"] = future.task_id
        scan_info["result"] = None

    def _info_categories(self) -> Dict[str, dict]:
        return {"parameters": self._param_info(), "processing": self._process_info()}

    def _process_info(self) -> str:
        return {
            scan_info[
                "scan_name"
            ]: f"Job {scan_info['job_id']}, Processed = {bool(scan_info['previous_result'])}"
            for scan_info in self._scans.values()
        }

    def _param_info(self) -> dict:
        return {
            "enabled": self.enabled,
            "scan_type": self.scan_type,
            "workflow": self.workflow,
            "mu": self.mu_name,
            "energy": self.energy_name,
            "energy_unit": self.energy_unit,
            "refresh_period": self.refresh_period,
            "max_scans": self.max_scans,
        }

    @property
    def _n_colors(self):
        return min(len(self._COLOR_PALETTE), self.max_scans + 1)

    _COLOR_PALETTE = [
        (87, 81, 212),
        (235, 171, 33),
        (176, 69, 0),
        (0, 197, 248),
        (207, 97, 230),
        (0, 166, 107),
        (184, 0, 87),
        (0, 138, 248),
        (0, 110, 0),
        (0, 186, 171),
        (255, 145, 133),
        (133, 133, 0),
    ]
