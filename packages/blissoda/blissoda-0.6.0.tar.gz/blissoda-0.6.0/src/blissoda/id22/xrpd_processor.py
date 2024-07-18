"""Automatic pyfai integration for every scan with saving and plotting"""

import os
from typing import List, Optional

from ..xrpd.processor import XrpdProcessor
from ..resources import resource_filename
from ..persistent.parameters import ParameterInfo


class Id22XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
    ],
):
    DEFAULT_WORKFLOW = resource_filename("id22", "Sum_then_integrate_with_saving.json")
    DEFAULT_WORKFLOW_NO_SAVE = None

    def __init__(self, **defaults) -> None:
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        defaults.setdefault("trigger_at", "END")
        super().__init__(**defaults)

        # Disable data from memory for now
        # The data structure is indeed different when getting it from file or from memory
        self._set_parameter("data_from_memory", False)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        integration_options = self.integration_options
        if integration_options:
            return integration_options.to_dict()
        return None

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        inputs += self.get_sum_inputs(scan, lima_name)
        inputs += self.get_save_ascii_inputs(scan, lima_name)
        return inputs

    def get_sum_inputs(self, scan, lima_name: str):
        task_identifier = "SumBlissScanImages"

        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")

        inputs = [
            {
                "task_identifier": task_identifier,
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "output_filename",
                "value": self.master_output_filename(scan),
            },
            {
                "task_identifier": task_identifier,
                "name": "scan",
                "value": scan_nb,
            },
            {
                "task_identifier": task_identifier,
                "name": "detector_name",
                "value": lima_name,
            },
        ]

        tscan_info = scan.scan_info.get("tscan_info")
        if tscan_info:
            background_step = tscan_info.get("background_step")
            if background_step is not None:
                inputs.append(
                    {
                        "task_identifier": task_identifier,
                        "name": "background_step",
                        "value": background_step,
                    }
                )

        if self.data_from_memory:
            scan_memory_url = f"{scan.root_node.db_name}:{scan._node_name}"
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "scan_memory_url",
                    "value": scan_memory_url,
                }
            )
        if self.retry_timeout:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "retry_timeout",
                    "value": self.retry_timeout,
                }
            )
        if self.flush_period:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "flush_period",
                    "value": self.flush_period,
                }
            )

        inputs.append(
            {
                "task_identifier": task_identifier,
                "name": "monitor_name",
                "value": self.monitor_name,
            },
        )

        return inputs

    def get_save_ascii_inputs(self, scan, lima_name):
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self.scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        basename = f"{stem}_{scan_nb}_{lima_name}_integrated.dat"

        return [
            {
                "task_identifier": "SaveAsciiPattern1D",
                "name": "filename",
                "value": os.path.join(root, basename),
            },
        ]

    def get_save_inputs(self, scan, lima_name, task_identifier):
        inputs = super().get_save_inputs(scan, lima_name, task_identifier)
        inputs += [
            {
                "task_identifier": task_identifier,
                "name": "nxprocess_name",
                "value": f"{lima_name}_integrate",
            }
        ]

        return inputs
