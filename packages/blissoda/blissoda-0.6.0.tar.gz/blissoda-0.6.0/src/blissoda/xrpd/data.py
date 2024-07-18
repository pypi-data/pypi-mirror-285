from typing import Tuple, List, Optional, Callable

import numpy
from silx.io import h5py_utils
from silx.utils.retry import RetryError
from silx.utils.retry import RetryTimeoutError

from ..persistent.ordereddict import PersistentOrderedDict
from ..persistent.ndarray import PersistentNdArray


def get_redis_store(redis_key: str) -> PersistentOrderedDict:
    return PersistentOrderedDict(redis_key)


def add_plot(
    redis_store: PersistentOrderedDict,
    scan_name: str,
    lima_name: str,
    signal_ndim: int,
    xlabel: str,
    xvalues: numpy.ndarray,
    hdf5_url: Optional[str] = None,
) -> Tuple[str, dict]:
    """Add a new curve plot."""
    plot_key = f"{scan_name}:{lima_name}"
    data_key = f"{redis_store.name}:{plot_key}"
    if hdf5_url is None:
        hdf5_url = ""
    plot_info = {
        "scan_name": scan_name,
        "lima_name": lima_name,
        "xlabel": xlabel,
        "signal_ndim": signal_ndim,
        "data_key": data_key,
        "hdf5_url": hdf5_url,
    }
    redis_store[plot_key] = plot_info
    PersistentNdArray(data_key).append(xvalues)
    return plot_key, plot_info


def remove_plots(
    redis_store: PersistentOrderedDict,
    max_len: int,
    remove_from_flint: Callable,
) -> List[Tuple[str, dict]]:
    """Remove plots when there are more than `max_len`."""
    all_plots = list(redis_store.items())
    if max_len > 0:
        remove = list()
        keep_scans = set()
        for plot_key, plot_info in all_plots[::-1]:
            scan_name = plot_info["scan_name"]
            if len(keep_scans) == max_len and scan_name not in keep_scans:
                remove.append((plot_key, plot_info))
            else:
                keep_scans.add(scan_name)
    else:
        remove = all_plots
    if remove:
        for plot_key, plot_info in remove:
            remove_from_flint(plot_key, plot_info)
            PersistentNdArray(plot_info["data_key"]).remove()
            redis_store.remove(plot_key)
    return remove


def add_data(plot_key: str, plot_info: dict, points: numpy.ndarray) -> str:
    """Append data to an existing plot."""
    PersistentNdArray(plot_info["data_key"]).extend(points)
    return plot_key


def get_curve_data(
    redis_store: PersistentOrderedDict, plot_key: str, **retry_options
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray], dict]:
    """Get the data from the results of the last processed point of the scan."""
    plot_info = redis_store[plot_key]
    data = PersistentNdArray(plot_info["data_key"])
    try:
        x = data[0]
    except IndexError:
        return None, None, plot_info

    if plot_info["hdf5_url"]:
        try:
            if plot_info["signal_ndim"] == 1:
                idx = tuple()
            else:
                idx = -1
        except KeyError:
            # Plot produced by an old version of blissoda
            if plot_info["ct"]:
                idx = tuple()
            else:
                idx = -1
        try:
            y = _get_data_from_file(plot_info["hdf5_url"], idx=idx, **retry_options)
        except RetryTimeoutError:
            y = None
        return x, y, plot_info
    else:
        try:
            y = data[-1]
        except IndexError:
            return None, None, plot_info

        if y.ndim == 2:
            return x, y[-1], plot_info
        return x, y, plot_info


def append_image_data(
    redis_store: PersistentOrderedDict,
    plot_key: str,
    current_data: Optional[numpy.ndarray] = None,
    **retry_options,
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray], dict]:
    """Add new data (if any) to the current data (if any)"""
    plot_info = redis_store[plot_key]
    data = PersistentNdArray(plot_info["data_key"])
    try:
        x = data[0]
    except IndexError:
        return None, None, plot_info

    if plot_info["hdf5_url"]:
        if current_data is None:
            idx = tuple()
        else:
            idx = slice(len(current_data), None)
        try:
            y = _get_data_from_file(plot_info["hdf5_url"], idx=idx, **retry_options)
        except RetryTimeoutError:
            y = None
        else:
            if current_data is not None:
                y = numpy.vstack([current_data, y])
    else:
        y = data[1:]

    return x, y, plot_info


@h5py_utils.retry()
def _get_data_from_file(hdf5_url: str, idx=tuple()):
    filename, dsetname = hdf5_url.split("::")
    with h5py_utils.File(filename) as root:
        try:
            return root[dsetname][idx]
        except KeyError as e:
            raise RetryError(str(e))
