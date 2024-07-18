from typing import Optional

try:
    from bliss import setup_globals
    from bliss.physics import units
except ImportError:
    units = None
    setup_globals = None

from ..exafs.plotter import ExafsPlotter
from ..resources import resource_filename


class DemoExafsPlotter(ExafsPlotter):
    def __init__(self, **defaults) -> None:
        defaults.setdefault("workflow", resource_filename("exafs", "exafs.ows"))
        defaults.setdefault("_scan_type", "any")
        counters = defaults.setdefault("_counters", dict())
        energy_unit = setup_globals.energy.unit or "eV"
        counters.setdefault(
            "any",
            {
                "mu_name": "mu",
                "energy_name": "energy",
                "energy_unit": energy_unit,
            },
        )
        super().__init__(**defaults)

    def _scan_type_from_scan(self, scan) -> Optional[str]:
        return "any"

    def run(self, expo=0.003):
        e0 = 8800  # eV
        e1 = 9600  # eV
        step_size = 0.5  # eV
        intervals = int((e1 - e0) / step_size) - 1

        from_unit = "eV"
        to_unit = self.counters["energy_unit"]

        if units:
            e0 = (e0 * units.ur(from_unit)).to(to_unit).magnitude
            e1 = (e1 * units.ur(from_unit)).to(to_unit).magnitude
        else:
            assert (
                from_unit == to_unit
            ), f"counters energy unit is '{to_unit}' instead of 'eV'"

        scan = setup_globals.ascan(
            setup_globals.energy, e0, e1, intervals, expo, setup_globals.mu, run=False
        )
        super().run(scan)


if setup_globals is None:
    exafs_plotter = None
else:
    exafs_plotter = DemoExafsPlotter()
    exafs_plotter.refresh_period = 0.5
