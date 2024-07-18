import os
from typing import Generator, Optional
from contextlib import contextmanager

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None

from . import optimize_exposure
from ..streamline.scanner import StreamlineScanner
from ..persistent.parameters import ParameterInfo


class Id31StreamlineScanner(
    StreamlineScanner,
    parameters=[
        ParameterInfo("optimize_pixel_value", category="exposure/attenuator"),
        ParameterInfo("optimize_nb_frames", category="exposure/attenuator"),
        ParameterInfo("optimize_max_exposure_time", category="exposure/attenuator"),
        ParameterInfo("default_attenuator", category="exposure/attenuator"),
        ParameterInfo("attenuator_name", category="names"),
        ParameterInfo("newflat", category="Flat-field"),
        ParameterInfo("oldflat", category="Flat-field"),
        ParameterInfo("optimize_exposure_per", category="robust vs. speed"),
        ParameterInfo("rockit_distance", category="sample changer"),
    ],
):
    def __init__(self, **defaults):
        defaults.setdefault("detector_name", "p3")
        defaults.setdefault("attenuator_name", "atten")
        defaults.setdefault("sample_changer_name", "streamline_sc")
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "integrator_name": "sigma_clip_ng",
                "extra_options": {"max_iter": 3, "thres": 0},
                "error_model": "azimuthal",  # hybrid gives weird results
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        defaults.setdefault("optimize_pixel_value", 1e5)
        defaults.setdefault("optimize_nb_frames", 3)
        defaults.setdefault("optimize_max_exposure_time", 4)
        defaults.setdefault("optimize_exposure_per", "baguette")
        defaults.setdefault("rockit_distance", 0.07)
        super().__init__(**defaults)
        self._exposure_conditions = list()
        self._fixed_attenuator_position = None

    @property
    def optimize_exposure_per(self) -> Optional[str]:
        return self._get_parameter("optimize_exposure_per")

    @optimize_exposure_per.setter
    def optimize_exposure_per(self, value: Optional[str]):
        if value not in (None, "sample", "baguette"):
            raise ValueError("Allowed values are 'sample', 'baguette' or None")
        self._set_parameter("optimize_exposure_per", value)

    def _get_scan_metadata(self) -> dict:
        return dict()

    @contextmanager
    def run_context(self):
        setup_globals.shopen(
            check_pilatus=False
        )  # check_pilatus = False when the detector was just started
        with super().run_context():
            yield

    def load(self):
        super().load()
        if self.optimize_exposure_per == "baguette":
            self.determine_exposure_conditions()

    def measure_sample(
        self, count_time: float = 1, *args, has_qrcode: bool = True, **kwargs
    ):
        with rockit(self.sample_changer.translation, self.rockit_distance):
            with self._optimize_sample_exposure(
                count_time, has_qrcode=has_qrcode
            ) as expo_time:
                if has_qrcode:
                    expo_time_max = self.optimize_max_exposure_time
                else:
                    expo_time_max = count_time
                expo_time = min(expo_time, expo_time_max)
                return super().measure_sample(expo_time, *args, **kwargs)

    def determine_exposure_conditions(self):
        """Pre-define optimal conditions: ascan at fixed attenuator position"""
        detector = getattr(setup_globals, self.detector_name)
        if self.default_attenuator is None:
            attenuator = getattr(setup_globals, self.attenuator_name)
            self.default_attenuator = attenuator.bits
        else:
            setup_globals.att(self.default_attenuator)
        self._exposure_conditions = optimize_exposure.optimal_exposure_conditions(
            *self.sample_changer.ascan_arguments(),
            detector,
            tframe=0.2,
            desired_counts=self.optimize_pixel_value,
            nframes_measure=1,
            nframes_default=self.optimize_nb_frames,
            reduce_desired_deviation=True,
            expose_with_integral_frames=False,
        )

    def determine_exposure_conditions_individually(self):
        """Pre-define optimal conditions: ct on each sample with adapted attenuator
        if the default attenuator position gives too much or too little counts"""
        detector = getattr(setup_globals, self.detector_name)
        attenuator = getattr(setup_globals, self.attenuator_name)
        att_value = attenuator.bits
        exposure_conditions = list()
        try:
            for _ in self.sample_changer.iterate_samples_without_qr():
                exposure_conditions.append(self._optimize_exposure_condition(detector))
        finally:
            setup_globals.att(att_value)
        self._exposure_conditions = exposure_conditions

    @contextmanager
    def _optimize_sample_exposure(
        self, count_time: float, has_qrcode: bool = True
    ) -> Generator[float, None, None]:
        """Selecting the optimal measurement conditions and returning the corresponding
        exposure time for the current sample."""

        if not self.optimize_exposure_per:
            # Optimization is disabled
            yield count_time

        elif self.optimize_exposure_per == "baguette":
            # Select pre-defined optimization
            count_time = self._set_exposure_condition()
            yield count_time

        elif not has_qrcode:
            # No QR-code probably means no sample so do not waste time optimizing
            yield count_time

        else:
            # Optimize condition for this sample individually
            detector = getattr(setup_globals, self.detector_name)
            attenuator = getattr(setup_globals, self.attenuator_name)
            att_value = attenuator.bits
            try:
                condition = self._optimize_exposure_condition(detector)
                yield condition.expo_time
            finally:
                setup_globals.att(att_value)

    def _set_exposure_condition(self) -> float:
        if not self._exposure_conditions:
            self.determine_exposure_conditions()
        sample_index = self.sample_changer.current_sample_index
        condition = self._exposure_conditions[sample_index]
        print(f"Pre-defined optimal exposure conditions: {condition}")
        setup_globals.att(condition.att_position)
        return condition.expo_time

    def _optimize_exposure_condition(
        self, detector
    ) -> optimize_exposure.ExposureCondition:
        return optimize_exposure.optimize_exposure_condition(
            detector,
            tframe=0.2,
            default_att_position=self.default_attenuator,
            desired_counts=self.optimize_pixel_value,
            dynamic_range=1 << 20,
            min_counts_per_frame=0,  # take 100
            nframes_measure=1,
            nframes_default=self.optimize_nb_frames,
            reduce_desired_deviation=True,
            expose_with_integral_frames=False,
        )

    def init_workflow(
        self, with_autocalibration: bool = False, flatfield: bool = True
    ) -> None:
        wd = "/users/opid31/ewoks/resources/workflows"
        if flatfield:
            if with_autocalibration:
                self.workflow = os.path.join(wd, "streamline_with_calib_with_flat.json")
            else:
                self.workflow = os.path.join(
                    wd, "streamline_without_calib_with_flat.json"
                )
        else:
            if with_autocalibration:
                self.workflow = os.path.join(wd, "streamline_with_calib.json")
            else:
                self.workflow = os.path.join(wd, "streamline_without_calib.json")

        print(f"Active data processing workflow: {self.workflow}")

    def _job_arguments(self, scan_info, processed_metadata: dict):
        args, kwargs = super()._job_arguments(scan_info, processed_metadata)
        inputs = kwargs["inputs"]
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
        energy = getattr(setup_globals, self.energy_name).position
        inputs.append(
            {
                "task_identifier": "FlatFieldFromEnergy",
                "name": "energy",
                "value": energy,
            }
        )
        return args, kwargs


@contextmanager
def rockit(motor, distance):
    if distance:
        try:
            with setup_globals.rockit(motor, distance):
                print("ROCKING ON")
                yield
        finally:
            print("ROCKING OFF")
    else:
        print("ROCKING DISABLED")
        yield
