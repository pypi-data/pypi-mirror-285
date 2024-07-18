"""Bliss-side client for Flint EXAFS plots"""

try:
    from bliss.flint.client.plots import BasePlot
except ImportError:
    BasePlot = object


class ExafsPlot(BasePlot):
    WIDGET = "blissoda.exafs.widgets.ExafsWidget"

    def clear(self):
        self.submit("clear")

    def remove_scan(self, legend):
        self.submit("remove_scan", legend)

    def update_scan(self, legend, data, color=None):
        self.submit("update_scan", legend, data, color=color)

    def get_scans(self):
        return self.submit("get_scans")
