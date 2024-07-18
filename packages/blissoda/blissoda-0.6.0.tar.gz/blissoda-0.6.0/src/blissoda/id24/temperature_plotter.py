import os
import logging
from glob import glob
from typing import Optional, List, Dict

import gevent
import shutil
from ewoksjob.client import submit

try:
    from bliss import current_session
except ImportError:
    current_session = None

from ..utils import trigger
from ..utils import directories
from ..flint import WithFlintAccess
from ..resources import resource_filename
from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import WithPersistentParameters
from .plots import TemperaturePlot

logger = logging.getLogger(__name__)


class Id24TemperaturePlotter(
    WithPersistentParameters,
    parameters=[
        ParameterInfo("_enabled"),
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("workflow_with_fit", category="workflows"),
        ParameterInfo("energy_name", category="XAS"),
        ParameterInfo("mu_name", category="XAS"),
        ParameterInfo("extend_plotrange_left", category="plot", doc="(nm)"),
        ParameterInfo("extend_plotrange_right", category="plot", doc="(nm)"),
        ParameterInfo("two_color_difference", category="plot", doc="(nm)"),
        ParameterInfo("dpi", category="plot"),
        ParameterInfo("refit", category="fit"),
        ParameterInfo("wavelength_min", category="fit", doc="(nm)"),
        ParameterInfo("wavelength_max", category="fit", doc="(nm)"),
    ],
):
    DEFAULT_WORKFLOW = resource_filename("id24", "id24_planck_plot.json")
    DEFAULT_WORKFLOW_WITH_FIT = resource_filename("id24", "id24_planck_fitplot.json")

    def __init__(self, **defaults) -> None:
        defaults.setdefault("_enabled", False)
        defaults.setdefault("workflow", self.DEFAULT_WORKFLOW)
        defaults.setdefault("workflow_with_fit", self.DEFAULT_WORKFLOW_WITH_FIT)

        defaults.setdefault("energy_name", "energy_enc")
        defaults.setdefault("mu_name", "mu_trans")

        defaults.setdefault("extend_plotrange_left", -15)
        defaults.setdefault("extend_plotrange_right", 50)
        defaults.setdefault("two_color_difference", 42)
        defaults.setdefault("dpi", 150)

        defaults.setdefault("refit", False)
        defaults.setdefault("wavelength_min", None)
        defaults.setdefault("wavelength_max", None)

        super().__init__(**defaults)
        self.plotter = Plotter()
        self._sync_scan_metadata()

    def enable(self) -> None:
        self._enabled = True
        self._sync_scan_metadata()

    def disable(self) -> None:
        self._enabled = False
        self._sync_scan_metadata()

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        ntasks = self.plotter.purge_tasks()
        categories["status"] = {
            "Enabled": self._enabled,
            "Fitting": self.refit,
            "Plotting tasks": ntasks,
        }
        return categories

    def _sync_scan_metadata(self) -> None:
        if self._enabled:
            workflows_category = trigger.register_workflow_category(timing="END")
            workflows_category.set("temperature", self.trigger_workflow_for_scan)
        else:
            trigger.unregister_workflow_category()

    def trigger_workflow_for_scan(self, scan) -> Optional[dict]:
        if not self._scan_requires_workflow(scan):
            return
        filename = scan.scan_info["filename"]
        scan_number = scan.scan_info["scan_nb"]
        self.trigger_workflow(scan_number, filename=filename)

    def trigger_workflow(
        self, scan_number: int, filename: Optional[str] = None
    ) -> None:
        if filename:
            if not os.path.isabs(filename):
                basename = os.path.basename(filename)
                raw_data = directories.get_raw_dir(current_session.scan_saving.filename)
                filenames = glob(os.path.join(raw_data, "*", "*", basename))
                if not filenames:
                    raise FileNotFoundError(filename)
                filename = filenames[0]
        else:
            filename = current_session.scan_saving.filename
        workflow = self._get_workflow(filename)

        future = submit(
            args=(workflow,),
            kwargs={
                "inputs": self._get_workflow_inputs(filename, scan_number),
                "outputs": [{"all": False}],
            },
        )
        self.plotter.handle_workflow_result(future)

    def _scan_requires_workflow(self, scan) -> bool:
        if not self._has_temperature(scan):
            return False
        if not scan.scan_info.get("save"):
            return False
        if not scan.scan_info.get("filename"):
            return False
        if not scan.scan_info.get("scan_nb"):
            return False
        return True

    def _has_temperature(self, scan) -> bool:
        channels = scan.scan_info.get("channels", dict())
        return "laser_heating_down:T_planck" in channels

    def _get_workflow(self, filename) -> Optional[str]:
        """Get the workflow to execute for the scan and ensure it is located
        in the proposal directory for user reference and worker accessibility.
        """
        if self.refit:
            src_file = self.workflow_with_fit
        else:
            src_file = self.workflow
        if src_file is None:
            return
        if not os.path.isfile(src_file):
            if self.refit:
                src_file = self.DEFAULT_WORKFLOW_WITH_FIT
            else:
                src_file = self.DEFAULT_WORKFLOW

        workflow_directory = directories.get_workflows_dir(filename)
        dst_file = os.path.join(workflow_directory, os.path.basename(src_file))
        if src_file != dst_file:
            if self.refit:
                self.workflow_with_fit = dst_file
            else:
                self.workflow = dst_file

        if not os.path.exists(dst_file):
            os.makedirs(workflow_directory, exist_ok=True)
            shutil.copyfile(src_file, dst_file)

        return dst_file

    def _get_workflow_inputs(self, filename: str, scan_number: int) -> List[dict]:
        inputs = self._get_read_inputs(filename, scan_number)
        inputs += self._get_plot_inputs(filename)
        inputs += self._get_fit_inputs()
        return inputs

    def _get_read_inputs(self, filename: str, scan_number: int) -> List[dict]:
        task_identifier = "XasTemperatureRead"
        return [
            {
                "task_identifier": task_identifier,
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "scan_number",
                "value": scan_number,
            },
            {
                "task_identifier": task_identifier,
                "name": "retry_timeout",
                "value": 60,
            },
            {
                "task_identifier": task_identifier,
                "name": "energy_name",
                "value": self.energy_name,
            },
            {
                "task_identifier": task_identifier,
                "name": "mu_name",
                "value": self.mu_name,
            },
        ]

    def _get_plot_inputs(self, filename: str) -> List[dict]:
        task_identifier = "XasTemperaturePlot"
        output_directory = directories.get_processed_subdir(filename, "temperature")
        return [
            {
                "task_identifier": task_identifier,
                "name": "output_directory",
                "value": output_directory,
            },
            {
                "task_identifier": task_identifier,
                "name": "extend_plotrange_left",
                "value": self.extend_plotrange_left,
            },
            {
                "task_identifier": task_identifier,
                "name": "extend_plotrange_right",
                "value": self.extend_plotrange_right,
            },
            {
                "task_identifier": task_identifier,
                "name": "two_color_difference",
                "value": self.two_color_difference,
            },
            {
                "task_identifier": task_identifier,
                "name": "dpi",
                "value": self.dpi,
            },
        ]

    def _get_fit_inputs(self) -> List[dict]:
        if not self.refit:
            return []
        task_identifier = "PlanckRadianceFit"
        return [
            {
                "task_identifier": task_identifier,
                "name": "wavelength_min",
                "value": self.wavelength_min,
            },
            {
                "task_identifier": task_identifier,
                "name": "wavelength_max",
                "value": self.wavelength_max,
            },
        ]


class Plotter(WithFlintAccess):
    def __init__(self) -> None:
        super().__init__()
        self._tasks = list()

    def purge_tasks(self) -> int:
        """Remove references to tasks that have finished."""
        self._tasks = [t for t in self._tasks if t]
        return len(self._tasks)

    def kill_tasks(self) -> int:
        """Kill all tasks."""
        gevent.killall(self._tasks)
        return self.purge_tasks()

    def handle_workflow_result(self, *args, **kwargs) -> None:
        """Handle workflow results in a background task"""
        self._spawn(self._handle_workflow_result, *args, **kwargs)

    def _handle_workflow_result(self, future, timeout: int = 60):
        try:
            results = future.get(timeout=timeout)
            if not results:
                return
            filenames = results["filenames"]
            directory = os.path.dirname(filenames[0])

            plot = self._get_plot()
            plot.select_directory(directory)
        except Exception as e:
            logger.exception(e)

    def _spawn(self, *args, **kw):
        task = gevent.spawn(*args, **kw)
        self._tasks.append(task)
        self.purge_tasks()

    def _get_plot(self) -> TemperaturePlot:
        return super()._get_plot("Temperature", TemperaturePlot)
