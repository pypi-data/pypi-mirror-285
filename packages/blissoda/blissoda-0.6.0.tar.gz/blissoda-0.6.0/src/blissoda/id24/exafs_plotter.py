from typing import Optional

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None

from ..exafs.plotter import ExafsPlotter


class Id24ExafsPlotter(ExafsPlotter):
    def __init__(self, **defaults) -> None:
        defaults.setdefault("workflow", "/users/opid24/ewoks/online.ows")
        defaults.setdefault("_scan_type", "escan")
        counters = defaults.setdefault("_counters", dict())
        counters.setdefault(
            "escan",
            {
                "mu_name": "mu_trans",
                "energy_name": "energy_enc",
                "energy_unit": "keV",
            },
        )
        super().__init__(**defaults)

    def _scan_type_from_scan(self, scan) -> Optional[str]:
        return "escan"

    def run(self, scan, **kw):
        super().run(scan, filename=setup_globals.SCAN_SAVING.filename, **kw)
