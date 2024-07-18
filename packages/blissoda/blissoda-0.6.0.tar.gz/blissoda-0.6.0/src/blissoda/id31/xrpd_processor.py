"""Automatic pyfai integration for every scan with saving and plotting"""

import os
from typing import Optional, List
from ..xrpd.processor import XrpdProcessor
from ..persistent.parameters import ParameterInfo

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


class Id31XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("newflat", category="Flat-field"),
        ParameterInfo("oldflat", category="Flat-field"),
    ],
):
    def __init__(self, **defaults) -> None:
        if setup_globals is None:
            raise ImportError("requires a bliss session")
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        super().__init__(**defaults)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        integration_options = self.integration_options
        if integration_options:
            return integration_options.to_dict()
        return None

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        inputs.append(
            {
                "task_identifier": "FlatFieldFromEnergy",
                "name": "newflat",
                "value": self.newflat,
            }
        )
        inputs.append(
            {
                "task_identifier": "FlatFieldFromEnergy",
                "name": "oldflat",
                "value": self.oldflat,
            }
        )
        inputs.append(
            {
                "task_identifier": "FlatFieldFromEnergy",
                "name": "energy",
                "value": setup_globals.energy.position,
            }
        )
        return inputs

    def get_submit_arguments(self, scan, lima_name) -> dict:
        kwargs = super().get_submit_arguments(scan, lima_name)
        return kwargs
        # TODO: Redis events don't show up
        handler = {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [
                {
                    "name": "url",
                    "value": "redis://bibhelm:25001/4",
                },
                {"name": "ttl", "value": 86400},
            ],
        }
        kwargs["execinfo"] = {"handlers": [handler]}
        return kwargs

    def enabled_flatfield(self, enable: bool) -> None:
        wd = "/users/opid31/ewoks/resources/workflows"
        if enable:
            self.workflow_with_saving = os.path.join(
                wd, "integrate_with_saving_with_flat.json"
            )
            self.workflow_without_saving = os.path.join(
                wd, "integrate_without_saving_with_flat.json"
            )
        else:
            self.workflow_with_saving = os.path.join(wd, "integrate_with_saving.json")
            self.workflow_without_saving = os.path.join(
                wd, "integrate_without_saving.json"
            )

    def ensure_workflow_accessible(self, scan) -> None:
        pass
