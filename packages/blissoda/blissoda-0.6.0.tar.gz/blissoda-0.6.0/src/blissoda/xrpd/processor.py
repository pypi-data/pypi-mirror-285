"""User API for XRPD processing on the Bliss repl"""

import os
import json
import shutil
import logging
from typing import Optional, List, Dict, Tuple, Any

try:
    from bliss import current_session
except ImportError:
    current_session = None

from ewoksjob.client import submit, get_future

from ..persistent.parameters import WithPersistentParameters
from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import autocomplete_property
from ..resources import resource_filename
from ..utils import trigger
from ..utils import directories
from .plotter import Plotter

logger = logging.getLogger(__name__)


class XrpdProcessor(
    WithPersistentParameters,
    parameters=[
        ParameterInfo("_enabled"),
        ParameterInfo("workflow_with_saving", category="workflows"),
        ParameterInfo("workflow_without_saving", category="workflows"),
        ParameterInfo("worker", category="workflows"),
        ParameterInfo("trigger_at", category="workflows"),
        ParameterInfo("lima_names", category="data access"),
        ParameterInfo("data_from_memory", category="data access"),
        ParameterInfo("retry_timeout", category="data access"),
        ParameterInfo("retry_period", category="data access"),
        ParameterInfo("flush_period", category="data access"),
        ParameterInfo("lima_url_template", category="data access"),
        ParameterInfo("lima_url_template_args", category="data access"),
        ParameterInfo("save_scans_separately", category="data access"),
        ParameterInfo("number_of_scans", category="plotting"),
        ParameterInfo("trigger_from_bliss", category="plotting"),
        ParameterInfo("monitor_name", category="PyFai"),
        ParameterInfo("reference", category="PyFai"),
    ],
):
    """A class that holds parameters related to online workflow triggering.

    This class must be subclassed to implement:
    - the generation of the pyFAI config file: `get_config_file`
    - the generation of integration options: `get_integration_options`

    These are generally beamline-specific.
    """

    DEFAULT_WORKFLOW: Optional[str] = resource_filename(
        "xrpd", "integrate_scan_with_saving.json"
    )
    DEFAULT_WORKFLOW_NO_SAVE: Optional[str] = resource_filename(
        "xrpd", "integrate_scan_without_saving.json"
    )
    DEFAULT_LIMA_URL_TEMPLATE: Optional[str] = None

    def __init__(self, **defaults) -> None:
        if current_session is None:
            raise ImportError("bliss")
        defaults.setdefault("_enabled", False)
        defaults.setdefault("workflow_with_saving", self.DEFAULT_WORKFLOW)
        defaults.setdefault("workflow_without_saving", self.DEFAULT_WORKFLOW_NO_SAVE)
        defaults.setdefault("lima_names", list())
        defaults.setdefault("data_from_memory", True)
        defaults.setdefault("trigger_from_bliss", True)
        defaults.setdefault("retry_period", 1)
        defaults.setdefault("flush_period", 5)
        defaults.setdefault("number_of_scans", 4)
        defaults.setdefault("trigger_at", "PREPARED")
        defaults.setdefault("lima_url_template", self.DEFAULT_LIMA_URL_TEMPLATE)
        defaults.setdefault("save_scans_separately", False)
        super().__init__(**defaults)

        self._plotter = Plotter(number_of_scans=self.number_of_scans)
        self._plotter.replot()
        self._sync_scan_metadata()

    @property
    def plotter(self) -> Plotter:
        return self._plotter

    def clear_plots(self) -> None:
        return self.plotter.clear()

    def replot(self) -> None:
        return self.plotter.replot()

    def purge_plotting_tasks(self) -> int:
        return self.plotter.purge_tasks()

    def stop_plotting_tasks(self) -> int:
        return self.plotter.kill_tasks()

    @autocomplete_property
    def number_of_scans(self) -> Optional[int]:
        return self._get_parameter("number_of_scans")

    @number_of_scans.setter
    def number_of_scans(self, value: int):
        self.plotter.number_of_scans = value
        self._set_parameter("number_of_scans", self.plotter.number_of_scans)

    @autocomplete_property
    def trigger_at(self) -> Optional[int]:
        return self._get_parameter("trigger_at")

    @trigger_at.setter
    def trigger_at(self, value: int):
        self._set_parameter("trigger_at", value)
        if self._enabled:
            self.disable()
            self.enable()

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        ntasks = self.plotter.purge_tasks()
        categories["status"] = {"Enabled": self._enabled, "Plotting tasks": ntasks}
        return categories

    def enable(self, *detectors) -> None:
        self._enabled = True
        self.set_lima_names(*detectors)
        self._sync_scan_metadata()

    def disable(self) -> None:
        self._enabled = False
        self._sync_scan_metadata()

    def _sync_scan_metadata(self) -> None:
        if self._enabled:
            workflows_category = trigger.register_workflow_category(
                timing=self.trigger_at
            )
            workflows_category.set("processing", self.on_new_scan_metadata)
        else:
            trigger.unregister_workflow_category()

    def set_lima_names(self, *detectors) -> None:
        lima_names = set()
        for detector in detectors:
            lima_names.add(detector.name)
        if lima_names:
            self.lima_names = sorted(lima_names)

    def on_new_scan_metadata(self, scan) -> Optional[dict]:
        metadata, _ = self._on_new_scan(scan)
        return metadata

    def on_new_scan(self, scan) -> Optional[Any]:
        _, future = self._on_new_scan(scan)
        return future

    def _on_new_scan(self, scan) -> Tuple[Optional[dict], Optional[Any]]:
        """Executed at the start of every scan"""
        future = None
        metadata = None
        if not self.scan_requires_processing(scan):
            return metadata, future
        if not self.check_monitor(scan):
            print(
                f"Monitor '{self.monitor_name}' is not included in the scan. Remove it from the pyfai options."
            )
            return metadata, future

        workflow = self.get_workflow(scan)
        for lima_name in self.get_lima_names(scan):
            # Submit arguments
            kwargs = self.get_submit_arguments(scan, lima_name)
            if scan.scan_info.get("save"):
                kwargs["convert_destination"] = self.workflow_destination(
                    scan, lima_name
                )

            if self.trigger_from_bliss:
                # Trigger workflow from the current process.
                future = submit(args=(workflow,), kwargs=kwargs, queue=self.worker)
                filename = self.get_filename(scan)
                scan_nb = scan.scan_info.get("scan_nb")

                scan_name = os.path.splitext(os.path.basename(filename))[0]
                scan_name = f"{scan_name}: {scan_nb}.1 {scan.name}"

                if scan.scan_info.get("save"):
                    output_url = self.online_output_url(scan, lima_name)
                    output_url = f"{output_url}/{lima_name}_integrate/integrated"
                else:
                    output_url = None

                self.plotter.handle_workflow_result(
                    future,
                    lima_name,
                    scan_name,
                    output_url=output_url,
                    retry_timeout=self.retry_timeout,
                    retry_period=self.retry_period,
                )
                future = get_future(future.task_id)
            else:
                # Save metadata to Redis (is saved in the raw data file as well).
                # Workflows may be triggered by an external process as a result.
                kwargs["workflow"] = workflow
                metadata = dict()
                metadata[f"process_{lima_name}"] = {
                    "@NX_class": "NXprocess",
                    "program": "ewoks",
                    "configuration": {
                        "@NX_class": "NXnote",
                        "type": "application/json",
                        "data": json.dumps(kwargs),
                    },
                }

        return metadata, future

    def get_submit_arguments(self, scan, lima_name) -> dict:
        return {
            "inputs": self.get_inputs(scan, lima_name),
            "outputs": [{"all": False}],
        }

    def _get_workflow(self, scan) -> Optional[str]:
        """Get the workflow filename for the scan"""
        if scan.scan_info.get("save"):
            return self.workflow_with_saving
        else:
            return self.workflow_without_saving

    def _get_default_workflow(self, scan) -> Optional[str]:
        """Get the workflow filename for the scan"""
        if scan.scan_info.get("save"):
            return self.DEFAULT_WORKFLOW
        else:
            return self.DEFAULT_WORKFLOW_NO_SAVE

    def _set_workflow(self, scan, filename) -> None:
        """Set the workflow filename for the scan"""
        if scan.scan_info.get("save"):
            self.workflow_with_saving = filename
        else:
            self.workflow_without_saving = filename

    def get_filename(self, scan) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def get_workflow(self, scan) -> Optional[str]:
        """Get the workflow to execute for the scan and ensure it is located
        in the proposal directory for user reference and worker accessibility.
        """
        src_file = self._get_workflow(scan)
        if src_file is None:
            return
        if not os.path.isfile(src_file):
            src_file = self._get_default_workflow(scan)

        dataset_filename = self.get_filename(scan)
        workflow_directory = self._get_workflows_dir(dataset_filename)
        dst_file = os.path.join(workflow_directory, os.path.basename(src_file))
        if src_file != dst_file:
            self._set_workflow(scan, dst_file)

        if not os.path.exists(dst_file):
            os.makedirs(workflow_directory, exist_ok=True)
            shutil.copyfile(src_file, dst_file)

        return dst_file

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        return directories.get_workflows_dir(dataset_filename)

    def get_lima_names(self, scan) -> List[str]:
        channels = scan.scan_info.get("channels", dict())
        return sorted(
            (
                lima_name
                for lima_name in self.lima_names
                if f"{lima_name}:image" in channels
            )
        )

    def check_monitor(self, scan) -> bool:
        monitor_name = self.monitor_name
        if not monitor_name:
            return True
        channels = scan.scan_info.get("channels", dict())
        return any(monitor_name in name for name in channels)

    def scan_requires_processing(self, scan) -> bool:
        return bool(self.get_lima_names(scan)) and self._get_workflow(scan) is not None

    def scan_processed_directory(self, scan) -> str:
        filename = self.get_filename(scan)
        root = directories.get_processed_dir(filename)
        collection = os.path.basename(directories.get_collection_dir(filename))
        dataset = os.path.basename(directories.get_dataset_dir(filename))
        return os.path.join(root, collection, dataset)

    def workflow_destination(self, scan, lima_name) -> str:
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self.scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        lima_sep = len(self.lima_names) > 1
        if lima_sep:
            basename = f"{stem}_{lima_name}_{scan_nb:04d}.json"
        else:
            basename = f"{stem}_{scan_nb:04d}.json"
        return os.path.join(root, basename)

    def master_output_filename(self, scan) -> str:
        """Filename which can be used to inspect the results after the processing."""
        filename = self.get_filename(scan)
        root = self.scan_processed_directory(scan)
        basename = os.path.basename(filename)
        return os.path.join(root, basename)

    def external_output_filename(self, scan, lima_name: str) -> Optional[str]:
        """External filename in which the online processing saves the results.
        When `None` the online processing saves directly in the master file.
        """
        lima_sep = len(self.lima_names) > 1
        scan_sep = self.save_scans_separately
        if not lima_sep and not scan_sep:
            return  # save directly in the master file

        filename = self.get_filename(scan)
        root = self.scan_processed_directory(scan)
        basename = os.path.basename(filename)

        stem, ext = os.path.splitext(basename)
        stem_parts = [stem]
        if lima_sep:
            stem_parts.append(lima_name)
        if scan_sep:
            scan_nb = scan.scan_info.get("scan_nb")
            stem_parts.append(f"{scan_nb:04d}")
        basename = "_".join(stem_parts)

        return os.path.join(root, f"{basename}{ext}")

    def online_output_filename(self, scan, lima_name: str) -> Optional[str]:
        """Filename which can be used to inspect the results during and after the processing."""
        filename = self.external_output_filename(scan, lima_name)
        if not filename:
            return self.master_output_filename(scan)
        return filename

    def master_output_url(self, scan) -> str:
        """URL which can be used to inspect the results after the processing."""
        scan_nb = scan.scan_info.get("scan_nb")
        filename = self.master_output_filename(scan)
        return f"{filename}::/{scan_nb}.1"

    def external_output_url(self, scan, lima_name: str) -> Optional[str]:
        """External URL in which the online processing saves the results.
        When `None` the online processing saves directly in the master URL.
        """
        scan_nb = scan.scan_info.get("scan_nb")
        filename = self.external_output_filename(scan, lima_name)
        if filename:
            return f"{filename}::/{scan_nb}.1"

    def online_output_url(self, scan, lima_name: str) -> str:
        """URL which can be used to inspect the results during and after the processing."""
        scan_nb = scan.scan_info.get("scan_nb")
        filename = self.online_output_filename(scan, lima_name)
        return f"{filename}::/{scan_nb}.1"

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = self.get_config_inputs(lima_name)
        inputs += self.get_integrate_inputs(scan, lima_name, "IntegrateBlissScan")
        inputs += self.get_integrate_inputs(
            scan, lima_name, "IntegrateBlissScanWithoutSaving"
        )
        inputs += self.get_save_inputs(scan, lima_name, "SaveNexusIntegrated")
        inputs += self.get_integrate_list_inputs(scan, lima_name)
        inputs += self.get_integrate_1d_inputs(scan, lima_name)
        return inputs

    def get_integrate_inputs(
        self, scan, lima_name: str, task_identifier: str
    ) -> List[dict]:
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
                "name": "monitor_name",
                "value": self.monitor_name,
            },
            {
                "task_identifier": task_identifier,
                "name": "reference",
                "value": self.reference,
            },
            {
                "task_identifier": task_identifier,
                "name": "maximum_persistent_workers",
                "value": len(self.lima_names),
            },
            {
                "task_identifier": task_identifier,
                "name": "detector_name",
                "value": lima_name,
            },
        ]
        external_output_filename = self.external_output_filename(scan, lima_name)
        if external_output_filename:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "external_output_filename",
                    "value": self.external_output_filename(scan, lima_name),
                }
            )
        if self.data_from_memory:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "scan_memory_url",
                    "value": _get_scan_memory_url(scan),
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
        if self.lima_url_template:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "lima_url_template",
                    "value": self.lima_url_template,
                }
            )
        if self.lima_url_template_args:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "lima_url_template_args",
                    "value": dict(self.lima_url_template_args),
                }
            )
        return inputs

    def get_integrate_list_inputs(self, scan, lima_name: str) -> List[dict]:
        task_identifier = "Integrate1DList"
        scan_nb = scan.scan_info.get("scan_nb")
        inputs = [
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
                "name": "maximum_persistent_workers",
                "value": len(self.lima_names),
            },
            {
                "task_identifier": task_identifier,
                "name": "detector_name",
                "value": lima_name,
            },
        ]
        external_output_filename = self.external_output_filename(scan, lima_name)
        if external_output_filename:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "external_output_filename",
                    "value": self.external_output_filename(scan, lima_name),
                }
            )
        if self.data_from_memory:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "scan_memory_url",
                    "value": _get_scan_memory_url(scan),
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
        inputs += [
            {
                "task_identifier": task_identifier,
                "name": "monitors",
                "value": [self.monitor_name],
            },
            {
                "task_identifier": task_identifier,
                "name": "references",
                "value": [self.reference],
            },
            {
                "task_identifier": task_identifier,
                "name": "detector_name",
                "value": lima_name,
            },
        ]
        return inputs

    def get_integrate_1d_inputs(self, scan, lima_name: str) -> List[dict]:
        task_identifier = "Integrate1D"
        inputs = [
            {
                "task_identifier": task_identifier,
                "name": "maximum_persistent_workers",
                "value": len(self.lima_names),
            },
            {
                "task_identifier": task_identifier,
                "name": "detector_name",
                "value": lima_name,
            },
        ]
        if self.retry_timeout:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "retry_timeout",
                    "value": self.retry_timeout,
                }
            )
        inputs += [
            {
                "task_identifier": task_identifier,
                "name": "monitor",
                "value": self.monitor_name,
            },
            {
                "task_identifier": task_identifier,
                "name": "reference",
                "value": self.reference,
            },
        ]
        return inputs

    def get_save_inputs(self, scan, lima_name: str, task_identifier: str) -> List[dict]:
        inputs = [
            {
                "task_identifier": task_identifier,
                "name": "url",
                "value": self.master_output_url(scan),
            }
        ]
        external_url = self.external_output_url(scan, lima_name)
        if external_url:
            inputs += [
                {
                    "task_identifier": task_identifier,
                    "name": "external_url",
                    "value": external_url,
                }
            ]
        return inputs

    def get_config_inputs(self, lima_name: str) -> List[dict]:
        inputs = []
        filename = self.get_config_filename(lima_name)
        if filename:
            inputs.append(
                {
                    "task_identifier": "PyFaiConfig",
                    "name": "filename",
                    "value": filename,
                }
            )
        integration_options = self.get_integration_options(lima_name)
        if integration_options:
            try:
                integration_options = integration_options.to_dict()
            except AttributeError:
                pass
            inputs.append(
                {
                    "task_identifier": "PyFaiConfig",
                    "name": "integration_options",
                    "value": integration_options,
                }
            )
        return inputs

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        raise NotImplementedError

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        raise NotImplementedError


def _get_scan_memory_url(scan) -> str:
    try:
        return scan._scan_data.key
    except AttributeError:
        # bliss < 1.0.0
        return f"{scan.root_node.db_name}:{scan._node_name}"
