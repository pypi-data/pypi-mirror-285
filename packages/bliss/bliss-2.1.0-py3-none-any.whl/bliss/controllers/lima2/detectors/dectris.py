# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numbers

from bliss.common.utils import typecheck
from bliss.common.counter import SamplingCounter
from bliss.common.protocols import counter_namespace

from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.counter import FrameCounter
from bliss.controllers.lima2.controller import (
    DetectorController,
    DetectorStatusController,
)
from bliss.controllers.lima2.settings import Settings, setting_property


class Detector:
    """Dectris Eiger2 detector user interface"""

    def __init__(self, device):
        self._det_cc = DetectorStatusController(device)
        self._frame_cc = DetectorController(device)

        self._temperature_cnt = SamplingCounter(
            "temperature", self._det_cc, unit="degC"
        )
        self._humidity_cnt = SamplingCounter("humidity", self._det_cc, unit="%")
        self._raw_frame_cnt = FrameCounter(
            "raw_frame", device._frame_cc, ("recvs", ["saving"]), file_only=True
        )

        class Acquisition(Settings):
            """
            {
                'thresholds': [{
                    'energy': 4020.5,
                    'enabled': True
                }, {
                    'energy': 4020.5,
                    'enabled': True
                }],
                'trigger_start_delay': 0.0,
                'roi': 'full',
                'nb_pipeline_threads': 1
            }
            """

            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["det"]
                super().__init__(device._config, path=["dectris", "acquisition"])

            @setting_property(default=True)
            def threshold1_enabled(self):
                return self._params["thresholds"][0]["enabled"]

            @threshold1_enabled.setter
            @typecheck
            def threshold1_enabled(self, value: bool):
                self._params["thresholds"][0]["enabled"] = value

            @setting_property(default=4020.5)
            def threshold1_energy(self):
                return self._params["thresholds"][0]["energy"]

            @threshold1_energy.setter
            @typecheck
            def threshold1_energy(self, value: numbers.Real):
                self._params["thresholds"][0]["energy"] = value

            @setting_property(default=True)
            def threshold2_enabled(self):
                return self._params["thresholds"][1]["enabled"]

            @threshold2_enabled.setter
            @typecheck
            def threshold2_enabled(self, value: bool):
                self._params["thresholds"][1]["enabled"] = value

            @setting_property(default=4020.5)
            def threshold2_energy(self):
                return self._params["thresholds"][1]["energy"]

            @threshold2_energy.setter
            @typecheck
            def threshold2_energy(self, value: numbers.Real):
                self._params["thresholds"][1]["energy"] = value

            @setting_property(default="full")
            def roi(self):
                return self._params["roi"]

            @roi.setter
            @typecheck
            def roi(self, value: str):
                self._params["roi"] = value

            @setting_property(default=1)
            def nb_pipeline_threads(self):
                return self._params["nb_pipeline_threads"]

            @nb_pipeline_threads.setter
            @typecheck
            def nb_pipeline_threads(self, value: numbers.Integral):
                self._params["nb_pipeline_threads"] = value

            def __info__(self):
                return "Acquisition:\n" + tabulate(self._params) + "\n\n"

        class Experiment(Settings):
            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["exp"]
                super().__init__(device._config, path=["dectris", "experiment"])

            @setting_property(default=8041)
            def photon_energy(self):
                return self._params["photon_energy"]

            @photon_energy.setter
            @typecheck
            def photon_energy(self, value: numbers.Real):
                self._params["photon_energy"] = value

            def __info__(self):
                return "Experiment:\n" + tabulate(self._params) + "\n\n"

        class Saving(Settings):
            """ "
            {
                'enabled': False,
                'filename': {
                    'base_path': '/tmp',
                    'filename_format': '{filename_prefix}_{rank}_{file_number:05d}{filename_suffix}',
                    'filename_prefix': 'lima2',
                    'filename_suffix': '.h5'
                }
            }
            """

            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["saving"]
                super().__init__(device._config, path=["dectris", "saving"])

            @setting_property(default=False)
            def enabled(self):
                return self._params["enabled"]

            @enabled.setter
            @typecheck
            def enabled(self, value: bool):
                self._params["enabled"] = value

            @property
            def filename_prefix(self):
                return self._params["filename_prefix"]

            @filename_prefix.setter
            @typecheck
            def filename_prefix(self, value: str):
                self._params["filename_prefix"] = value

            @setting_property
            def nb_frames_per_file(self):
                return self._params["nb_frames_per_file"]

            @nb_frames_per_file.setter
            @typecheck
            def nb_frames_per_file(self, value: int):
                self._params["nb_frames_per_file"] = value

            def __info__(self):
                return "Saving:\n" + tabulate(self._params) + "\n\n"

        self.acquisition = Acquisition(device)
        self.experiment = Experiment(device)
        self.saving = Saving(device)

    def __info__(self):
        return (
            self.acquisition.__info__()
            + self.experiment.__info__()
            + self.saving.__info__()
        )

    @property
    def counters(self):
        return [
            self._temperature_cnt,
            self._humidity_cnt,
            self._raw_frame_cnt,
        ]

    @property
    def counter_groups(self):
        res = {}
        res["health"] = counter_namespace([self._temperature_cnt, self._humidity_cnt])
        res["images"] = counter_namespace([self._raw_frame_cnt])
        return res
