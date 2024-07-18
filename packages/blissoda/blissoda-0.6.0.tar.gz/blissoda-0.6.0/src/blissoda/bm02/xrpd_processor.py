"""Automatic pyfai integration for every scan with saving and plotting"""

from typing import Optional
from ..xrpd.processor import XrpdProcessor
from ..persistent.parameters import ParameterInfo


class Bm02XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("config_filename", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
    ],
):
    def __init__(self, **defaults) -> None:
        defaults.setdefault("config_filename", {"WOS": "", "D5": ""})
        defaults.setdefault(
            "integration_options",
            {
                "WOS": {
                    "method": "no_csr_cython",
                    "nbpt_rad": 4096,
                    "unit": "q_nm^-1",
                },
                "D5": {
                    "method": "no_csr_cython",
                    "nbpt_rad": 4096,
                    "unit": "q_nm^-1",
                },
            },
        )
        super().__init__(**defaults)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        try:
            return self.config_filename[lima_name]
        except KeyError:
            raise RuntimeError(
                f"Missing pyfai configuration file (poni or json) for '{lima_name}'"
            ) from None

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        try:
            return self.integration_options[lima_name]
        except KeyError:
            raise RuntimeError(
                f"Missing pyfai integration options for '{lima_name}'"
            ) from None
