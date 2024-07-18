from typing import List, Dict, Any, Optional

try:
    from bliss import current_session
    import bliss.setup_globals as bliss_globals
except ImportError:
    scan_meta = None
    current_session = None
    user_print = print

import os
from ewoksjob.client import submit
from ..utils import directories

from ..persistent.parameters import (
    WithPersistentParameters,
    ParameterInfo,
)

_DEFAULT_USER_PARS: Dict[str, Any] = {
    "flip_ud": False,
    "flip_lr": True,
    "wavelength": 0.1,
    "beam": [1000, 1100],
    "polarization": 0.99,
    "kappa": 0,
    "alpha": 50,
    "theta": 0,
    "phi": 0,
    "omega": "",
    "rotation": 180,
    "dummy": -1,
    "offset": 1,
    "dry_run": False,
    "calc_mask": False,
}

_DEFAULT_SCAN_PARS: Dict[str, Any] = {
    "images": "",
    "output": "",
    "distance": 100,
}


class Id11Eiger2Crysalis(
    WithPersistentParameters,
    parameters=[
        ParameterInfo("worker", category="workflows"),
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo(
            "lima_name",
            category="Eiger2Crysalis",
            doc="Lima name of the camera: (i.e. eiger)",
        ),
        ParameterInfo(
            "scan_parameters",
            category="Eiger2Crysalis",
            doc="Derived from scan and motors",
        ),
        ParameterInfo(
            "user_parameters", category="Eiger2Crysalis", doc="Specify explicitly"
        ),
        ParameterInfo(
            "x_motor",
            category="Eiger2Crysalis",
            doc="Motor name to define distance value",
        ),
        ParameterInfo(
            "frameset_copy",
            category="Eiger2Crysalis",
            doc="frame.set path that will be copied automatically inside the output folder",
        ),
    ],
):
    def __init__(self, **defaults: Any) -> None:
        if current_session is None:
            raise ImportError("bliss")
        defaults.setdefault("workflow", "")
        defaults.setdefault("user_parameters", _DEFAULT_USER_PARS)
        defaults.setdefault("scan_parameters", _DEFAULT_SCAN_PARS)
        defaults.setdefault("frameset_copy", "")
        defaults.setdefault("x_motor", "")
        super().__init__(**defaults)

    def _info_categories(self) -> Dict[str, dict]:
        self.update_scan_parameters()
        return super()._info_categories()

    def update_scan_parameters(self, scan: Any = None) -> None:
        scan_parameters = dict()
        if scan:
            scan_parameters["images"] = self.get_lima_filenames(scan)
            scan_parameters["output"] = self.get_output_path(scan)
        scan_parameters["distance"] = self.get_distance()
        self.scan_parameters.update(scan_parameters)
        return scan_parameters

    def get_filename(self, scan) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def get_distance(self) -> str:
        x_motor = getattr(bliss_globals, f"{self.x_motor}")
        return x_motor.position

    def get_output_path(self, scan: Any) -> str:
        scan_nb = scan.scan_info["scan_nb"]
        dataset_processed_dir = get_dataset_processed_dir(self.get_filename(scan))
        scan_processed_dir = os.path.join(dataset_processed_dir, f"scan{scan_nb:04d}")
        output = os.path.join(scan_processed_dir, "frame_1_{index}.esperanto")
        return output

    def get_lima_filenames(self, scan: Any) -> List[str]:
        scan_number = scan.scan_number
        lima_files = [
            f"{scan.scan_saving.images_path.format(scan_number=scan_number,img_acq_device=self.lima_name)}0000.h5"
        ]
        return lima_files

    def get_inputs(self, scan) -> List[Dict[str, Any]]:
        parameters = self.user_parameters.to_dict()
        parameters.update(self.update_scan_parameters(scan))

        inputs = []
        for key, value in parameters.items():
            inputs.append(
                {
                    "task_identifier": "Eiger2Crysalis",
                    "name": key,
                    "value": value,
                }
            )
        inputs += [
            {
                "task_identifier": "Eiger2Crysalis",
                "name": "custom_frame_set_path",
                "value": self.frameset_copy,
            },
        ]
        return inputs

    def get_submit_arguments(self, scan) -> Dict[str, Any]:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": "False"}],
        }

    def run_conversion(self, scan: Optional[Any]) -> None:
        """Executes on given scan"""
        kwargs = self.get_submit_arguments(scan)
        submit(args=(self.workflow,), kwargs=kwargs, queue=self.worker)


def get_dataset_processed_dir(
    dataset_filename: str,
) -> str:  # Temporary, waiting for !173 to be merged
    root = directories.get_processed_dir(dataset_filename)
    collection = os.path.basename(directories.get_collection_dir(dataset_filename))
    dataset = os.path.basename(directories.get_dataset_dir(dataset_filename))
    return os.path.join(root, collection, dataset)
