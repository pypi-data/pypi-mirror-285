# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging
import numbers

from bliss.common.protocols import counter_namespace
from bliss.common.utils import typecheck

from bliss.controllers.lima2.counter import FrameCounter
from bliss.controllers.lima2.controller import DetectorController, RoiStatController
from bliss.controllers.lima2.settings import Settings, setting_property
from bliss.controllers.lima2.tabulate import tabulate

from bliss.controllers.lima2.processings.common import Saving

_logger = logging.getLogger("bliss.ctrl.lima2.processing")


class JungFrau(Settings):
    def __init__(self, config, path, params):
        self._params = params
        super().__init__(config, path=path)

    @setting_property
    def gain_path(self):
        return self._params["gain_path"]

    @gain_path.setter
    @typecheck
    def gain_path(self, value: str):
        self._params["gain_path"] = value

    @setting_property
    def pedestal_path(self):
        return self._params["gain_path"]

    @pedestal_path.setter
    @typecheck
    def pedestal_path(self, value: str):
        self._params["pedestal_path"] = value

    @setting_property(default=6.0)
    def photon_energy(self):
        return self._params["photon_energy"]

    @photon_energy.setter
    @typecheck
    def photon_energy(self, value: numbers.Real):
        self._params["photon_energy"] = value


class Processing(Settings):
    """Classic processing user interface"""

    def __init__(self, device, Processing):
        self._device = device
        self._params = Processing.params_default
        self._rois = []
        super().__init__(device._config, path=["smx"])

        # Define static counters
        self._frame_cc = DetectorController(device)
        self._frame_cnt = FrameCounter("frame", self._frame_cc, "procs.saving_dense")
        self._sparse_frame_cnt = FrameCounter(
            "sparse_frame", self._frame_cc, "procs.saving_sparse"
        )

        self._roi_counters_cc = RoiStatController(
            device, master_controller=self._frame_cc
        )

        self.saving_dense = Saving(
            device._config, ["smx", "saving_dense"], self._params["saving_dense"]
        )
        self.saving_sparse = Saving(
            device._config, ["smx", "saving_sparse"], self._params["saving_sparse"]
        )
        self.saving_accumulation_corrected = Saving(
            device._config,
            ["smx", "saving_accumulation_corrected"],
            self._params["saving_accumulation_corrected"],
        )
        self.saving_sparse = Saving(
            device._config,
            ["smx", "saving_accumulation_peak"],
            self._params["saving_accumulation_peak"],
        )
        self.jungfrau = JungFrau(
            device._config,
            ["smx", "jungfrau"],
            self._params["jfrau"],
        )

    @setting_property(default=100)
    def nb_frames_buffer(self):
        return self._params["buffers"]["nb_frames_buffer"]

    @nb_frames_buffer.setter
    @typecheck
    def nb_frames_buffer(self, value: int):
        self._params["buffers"]["nb_frames_buffer"] = value

    @setting_property(default=0)
    def nb_peak_counters_buffer(self):
        return self._params["buffers"]["nb_peak_counters_buffer"]

    @nb_peak_counters_buffer.setter
    @typecheck
    def nb_peak_counters_buffer(self, value: int):
        self._params["buffers"]["nb_peak_counters_buffer"] = value

    def __info__(self):
        def format(title, params):
            return f"{title}:\n" + tabulate(params) + "\n\n"

        return format("Saving", self._params["saving_dense"])

    @property
    def counters(self):
        return [
            self._frame_cnt,
            self._sparse_frame_cnt,
            *self._get_roi_counters(),
        ]

    @property
    def counter_groups(self):
        return {
            "images": counter_namespace(
                [self._raw_frame_cnt, self._frame_cnt, self._sparse_frame_cnt]
            ),
            "rois": counter_namespace(self._get_roi_counters()),
        }
