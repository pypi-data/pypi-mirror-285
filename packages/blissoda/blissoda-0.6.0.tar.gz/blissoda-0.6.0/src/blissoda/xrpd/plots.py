"""Bliss-side for Flint XRPD plots"""

try:
    from bliss.flint.client.plots import BasePlot
except ImportError:
    BasePlot = object


class XrpdCurvePlot(BasePlot):
    WIDGET = "blissoda.xrpd.widgets.XrpdCurveWidget"

    def remove_plot(self, redis_store: str, plot_key: str) -> None:
        self.submit("remove_plot", redis_store, plot_key)

    def update_plot(self, redis_store: str, plot_key: str, hdf5_options: dict) -> None:
        self.submit("update_plot", redis_store, plot_key, hdf5_options)


class XrpdImagePlot(BasePlot):
    WIDGET = "blissoda.xrpd.widgets.XrpdImageWidget"

    def remove_plot(self, redis_store: str, plot_key: str) -> None:
        self.submit("remove_plot", redis_store, plot_key)

    def update_plot(self, redis_store: str, plot_key: str, hdf5_options: dict) -> None:
        self.submit("update_plot", redis_store, plot_key, hdf5_options)
