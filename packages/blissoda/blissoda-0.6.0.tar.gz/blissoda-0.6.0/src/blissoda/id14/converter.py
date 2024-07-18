"""User API for HDF5 conversion on the Bliss repl"""

import os
from typing import List, Dict

from ewoksjob.client import submit

try:
    from bliss import current_session
except ImportError:
    current_session = None

from ..utils import trigger
from ..utils import directories
from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import WithPersistentParameters


class Id14Hdf5ToSpecConverter(
    WithPersistentParameters,
    parameters=[
        ParameterInfo("_enabled"),
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("retry_timeout", category="data access"),
        ParameterInfo("worker", category="workflows"),
    ],
):
    def __init__(self, **defaults) -> None:
        if current_session is None:
            raise ImportError("bliss")
        defaults.setdefault("_enabled", False)
        defaults.setdefault("worker", "celery")
        defaults.setdefault(
            "workflow", "/data/id14/inhouse/ewoks/resources/workflows/convert.json"
        )
        super().__init__(**defaults)
        self._sync_scan_metadata()

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        categories["status"] = {"Enabled": self._enabled}
        return categories

    def enable(self, *detectors) -> None:
        self._enabled = True
        self._sync_scan_metadata()

    def disable(self) -> None:
        self._enabled = False
        self._sync_scan_metadata()

    def _sync_scan_metadata(self) -> None:
        if self._enabled:
            workflows_category = trigger.register_workflow_category()
            workflows_category.set("processing", self.on_new_scan_metadata)
        else:
            trigger.unregister_workflow_category()

    def on_new_scan_metadata(self, scan) -> None:
        if not self.scan_requires_processing(scan):
            return
        kwargs = self.get_submit_arguments(scan)
        _ = submit(args=(self.workflow,), kwargs=kwargs, queue=self.worker)

    def scan_requires_processing(self, scan) -> bool:
        # TODO: select scan that needs processing
        return True

    def get_submit_arguments(self, scan) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_inputs(self, scan) -> List[dict]:
        task_identifier = "Hdf5ToSpec"

        filename = self.get_filename(scan)
        output_filename = self.workflow_destination(scan)
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
                "value": output_filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "scan_numbers",
                "value": [scan_nb],
            },
        ]

        # Scan metadata published in id14.McaAcq.McaAcq.save
        calibration = scan.scan_info.get("instrument", dict()).get("calibration")
        if calibration:
            mca_calibration = calibration["a"], calibration["b"], 0
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "mca_calibration",
                    "value": mca_calibration,
                }
            )

        return inputs

    def get_filename(self, scan) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def workflow_destination(self, scan) -> str:
        filename = self.get_filename(scan)
        root = directories.get_processed_dir(filename)
        stem = os.path.splitext(os.path.basename(filename))[0]
        basename = f"{stem}.mca"
        return os.path.join(root, basename)

    def enable_slurm(self):
        self.worker = "slurm"

    def disable_slurm(self):
        self.worker = "celery"
