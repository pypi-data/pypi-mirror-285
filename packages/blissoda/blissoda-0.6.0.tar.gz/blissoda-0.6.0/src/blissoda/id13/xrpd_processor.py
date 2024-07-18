from typing import Optional, List

from ..xrpd.processor import XrpdProcessor
from ..persistent.parameters import ParameterInfo
from ..resources import resource_filename
from ..utils.pyfai import read_config


class Id13XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
    ],
):
    DEFAULT_WORKFLOW: Optional[str] = resource_filename(
        "id13", "integrate_scan_with_saving.json"
    )
    DEFAULT_LIMA_URL_TEMPLATE: Optional[str] = (
        "{dirname}/scan{scan_number_as_str}/{images_prefix}{{file_index}}.h5::/entry_0000/measurement/data"
    )

    def __init__(self, **defaults) -> None:
        defaults.setdefault("save_scans_separately", True)
        super().__init__(**defaults)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        if self.pyfai_config:
            integration_options = read_config(filename=self.pyfai_config)
        else:
            integration_options = dict()
        if self.integration_options:
            integration_options.update(self.integration_options.to_dict())
        return integration_options

    def get_integrate_inputs(
        self, scan, lima_name: str, task_identifier: str
    ) -> List[dict]:
        eval_dict = {"img_acq_device": lima_name, "scan_number": scan.scan_number}
        images_prefix = scan.scan_saving.eval_template(
            scan.scan_saving.images_prefix, eval_dict=eval_dict
        )
        original_template_args = self.lima_url_template_args.to_dict()
        self.lima_url_template_args["images_prefix"] = images_prefix
        self.lima_url_template_args["scan_number_as_str"] = scan.scan_number
        try:
            return super().get_integrate_inputs(scan, lima_name, task_identifier)
        finally:
            self.lima_url_template_args = original_template_args
