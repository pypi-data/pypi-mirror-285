"""Flint-side for Flint XRPD plots"""

from silx.gui.plot import Plot1D
from silx.gui.plot import Plot2D

try:
    from blissdata import settings
except ImportError:
    try:
        from bliss.config import settings
    except ImportError:
        settings = None

from .data import get_redis_store
from .data import get_curve_data
from .data import append_image_data
from ..flint import capture_errors


import logging

logger = logging.getLogger(__name__)


class _WithRedisData:
    def __init__(self) -> None:
        super().__init__()
        self._redis_store = None

    def _get_redis_store(self, redis_store: str) -> settings.OrderedHashObjSetting:
        if self._redis_store is None:
            self._redis_store = get_redis_store(redis_store)
        return self._redis_store

    def _get_legend(self, plot_info: dict) -> str:
        return f"{plot_info['scan_name']} ({plot_info['lima_name']})"


class XrpdCurveWidget(Plot1D, _WithRedisData):
    @capture_errors
    def remove_plot(self, redis_store: str, plot_key: str) -> None:
        plot_info = self._get_redis_store(redis_store)[plot_key]
        legend = self._get_legend(plot_info)
        logger.debug(f"remove {legend}")
        self.remove(legend=legend)

    @capture_errors
    def update_plot(self, redis_store: str, plot_key: str, retry_options: dict) -> None:
        x, y, plot_info = get_curve_data(
            self._get_redis_store(redis_store), plot_key, **retry_options
        )
        if y is None:
            return
        legend = self._get_legend(plot_info)
        logger.debug("XRPD curve plot %s", legend)
        self.addCurve(
            x, y, legend=legend, xlabel=plot_info["xlabel"], ylabel="Intensity"
        )


class XrpdImageWidget(Plot2D, _WithRedisData):
    @capture_errors
    def remove_plot(self, redis_store: str, plot_key: str) -> None:
        self.clear()

    @capture_errors
    def update_plot(self, redis_store: str, plot_key: str, retry_options: dict) -> None:
        img = self.getImage(legend=plot_key)
        if img is None:
            current_data = None
        else:
            current_data = img.getData(copy=False)
        x, y, plot_info = append_image_data(
            self._get_redis_store(redis_store), plot_key, current_data, **retry_options
        )
        if y is None:
            return
        origin = x[0], 0
        scale = x[1] - x[0], 1
        self.clear()
        title = self._get_legend(plot_info)
        self.setGraphTitle(title)
        logger.debug("XRPD image plot %s: %s points", title, len(y))
        self.addImage(
            y,
            legend=title,
            xlabel=plot_info["xlabel"],
            ylabel="Scan points",
            origin=origin,
            scale=scale,
        )
