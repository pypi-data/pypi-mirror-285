from typing import Optional

from ..exafs.plotter import ExafsPlotter


class Bm23ExafsPlotter(ExafsPlotter):
    def __init__(self, **defaults) -> None:
        defaults.setdefault("workflow", "/users/opd23/ewoks/online.ows")
        defaults.setdefault("_scan_type", "trigscan")
        counters = defaults.setdefault("_counters", dict())
        counters.setdefault(
            "cont",
            {
                "mu_name": "mu_trans",
                "energy_name": "energy_cenc",
                "energy_unit": "keV",
            },
        )
        counters.setdefault(
            "step",
            {
                "mu_name": "mu_trans",
                "energy_name": "eneenc",
                "energy_unit": "keV",
            },
        )
        counters.setdefault(
            "trigscan",
            {
                "mu_name": "mu_trans",
                "energy_name": "energy_enc",
                "energy_unit": "keV",
            },
        )
        super().__init__(**defaults)

    def _scan_type_from_scan(self, scan) -> Optional[str]:
        if "exafs_step" in getattr(scan, "name", None):
            return "step"
        elif "exafs_cont" in getattr(scan, "name", None):
            return "cont"
        elif "trigscan" in getattr(scan, "_scan_name", None):
            return "trigscan"
