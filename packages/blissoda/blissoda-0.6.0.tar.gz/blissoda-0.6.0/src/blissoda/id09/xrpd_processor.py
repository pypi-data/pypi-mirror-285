"""Automatic pyfai integration for every scan with saving and plotting"""

import os
from typing import Optional, List
from ..xrpd.processor import XrpdProcessor
from ..persistent.parameters import ParameterInfo


try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


class Id09XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("thickness", category="Corrections"),
    ],
):
    def __init__(self, **defaults) -> None:
        if setup_globals is None:
            raise ImportError("requires a bliss session")
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "nbpt_rad": 1024,
                "unit": "q_A^-1",
                "rot1": 0,
                "rot2": 0,
                "rot3": 0,
                "binning": 2,
            },
        )
        defaults.setdefault("thickness", 1)
        super().__init__(**defaults)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> dict:
        integration_options = self.integration_options

        if integration_options:
            integration_options = integration_options.to_dict()
        else:
            integration_options = dict()

        integration_options.setdefault("energy", setup_globals.get_xray_energy())
        integration_options.setdefault("binning", 2)

        has_rotation = (
            integration_options.get("rot1")
            or integration_options.get("rot2")
            or integration_options.get("rot3")
        )

        center = integration_options.pop("center", None)
        if center is not None:
            if has_rotation:
                print(
                    "WARNING: 'center' will be disregarded because rotations are not all zero."
                )
            else:
                poni1, poni2 = setup_globals.get_poni(center)
                integration_options["poni1"] = poni1
                integration_options["poni2"] = poni2

        return integration_options

    def master_output_filename(self, scan) -> str:
        filename = super().master_output_filename(scan)
        filename, ext = os.path.splitext(filename)
        return f"{filename}_oda{ext}"

    def external_output_filename(self, scan, lima_name: str) -> Optional[str]:
        filename = super().external_output_filename(scan, lima_name)
        if filename:
            filename, ext = os.path.splitext(filename)
            return f"{filename}_oda{ext}"

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        inputs.append(
            {
                "task_identifier": "SensorCorrection",
                "name": "sensor_thickness",
                "value": self.thickness,
            },
        )
        return inputs

    def get_submit_arguments(self, scan, lima_name) -> dict:
        kwargs = super().get_submit_arguments(scan, lima_name)
        kwargs["outputs"] = [{"task_identifier": "IntegrateBlissScanWithoutSaving"}]
        kwargs["merge_outputs"] = True
        return kwargs
