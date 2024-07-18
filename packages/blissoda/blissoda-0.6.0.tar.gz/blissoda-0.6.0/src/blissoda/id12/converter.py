"""User API for HDF5 conversion on the Bliss repl"""

import os
import re
from typing import List, Dict

from ewoksjob.client import submit

try:
    from bliss import current_session
except ImportError:
    current_session = None

from ..utils import trigger
from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import WithPersistentParameters
from ..resources import resource_filename


class Id12Hdf5ToAsciiConverter(
    WithPersistentParameters,
    parameters=[
        ParameterInfo("_enabled"),
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("external_proposal_outdir", category="parameters"),
        ParameterInfo("inhouse_proposal_outdir", category="parameters"),
        ParameterInfo("test_proposal_outdir", category="parameters"),
        ParameterInfo("retry_timeout", category="data access"),
    ],
):
    def __init__(self, **defaults) -> None:
        if current_session is None:
            raise ImportError("bliss")
        defaults.setdefault("_enabled", False)
        root_dir = "/data/id12/inhouse"
        defaults.setdefault(
            "external_proposal_outdir", os.path.join(root_dir, "EXTERNAL")
        )
        defaults.setdefault(
            "inhouse_proposal_outdir", os.path.join(root_dir, "INHOUSE2")
        )
        defaults.setdefault("test_proposal_outdir", os.path.join(root_dir, "NOBACKUP"))
        defaults.setdefault("workflow", resource_filename("id12", "convert.json"))
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
            workflows_category = trigger.register_workflow_category(timing="END")
            workflows_category.set("processing", self.on_new_scan_metadata)
        else:
            trigger.unregister_workflow_category()

    def on_new_scan_metadata(self, scan) -> None:
        if not self.scan_requires_processing(scan):
            return
        kwargs = self.get_submit_arguments(scan)
        _ = submit(args=(self.workflow,), kwargs=kwargs)

    def scan_requires_processing(self, scan) -> bool:
        return scan.scan_info["filename"] and scan.scan_info["save"]

    def get_submit_arguments(self, scan) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_inputs(self, scan) -> List[dict]:
        task_identifier = "Hdf5ToAscii"

        filename = scan.scan_info["filename"]
        output_filename = self.output_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")

        return [
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

    def output_filename(self, scan) -> str:
        proposal = current_session.scan_saving.proposal.name

        # Proposal directory is upper case and "-" between letters and digits
        matches = re.findall(r"[A-Za-z]+|\d+", proposal.upper())
        proposal_dir = "-".join(matches)

        # Handle special cases
        proposal_dir = proposal_dir.replace("IH", "IH-")
        proposal_dir = re.sub(r"ID-(\d{2})(.+)", r"ID\1-\2", proposal_dir)

        # Select directory for the ASCII files
        if current_session.scan_saving.proposal_type == "inhouse":
            dirname = self.inhouse_proposal_outdir
        elif current_session.scan_saving.proposal_type == "tmp":
            dirname = self.test_proposal_outdir
        elif proposal_dir.startswith("IH") or proposal_dir.startswith("BLC"):
            dirname = self.inhouse_proposal_outdir
        else:
            dirname = self.external_proposal_outdir

        filename = scan.scan_info["filename"]
        collection_dataset = os.path.splitext(os.path.basename(filename))[0]
        return os.path.join(dirname, proposal_dir, collection_dataset + ".dat")
