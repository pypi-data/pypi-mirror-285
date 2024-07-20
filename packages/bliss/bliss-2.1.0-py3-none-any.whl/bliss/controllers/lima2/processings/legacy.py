# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging

from bliss.common.protocols import counter_namespace
from bliss.common.utils import typecheck
import bliss.common.plot as plot_module  # for edit_rois

from bliss.controllers.lima2.counter import FrameCounter, RoiStatCounters
from bliss.controllers.lima2.controller import RoiStatController
from bliss.controllers.lima2.settings import Settings, setting_property
from bliss.controllers.lima2.tabulate import tabulate

from bliss.controllers.lima2.processings.common import Saving

_logger = logging.getLogger("bliss.ctrl.lima2.processing")


class Processing(Settings):
    """Classic processing user interface"""

    def __init__(self, device, Processing):
        self._device = device
        self._params = Processing.params_default
        self._rois = []
        super().__init__(device._config, path=["classic"])

        # Define static counters
        self._frame_cnt = FrameCounter("frame", device._frame_cc, "procs.saving")
        self._input_frame_cnt = FrameCounter("input_frame", device._frame_cc, None)

        self._roi_counters_cc = RoiStatController(
            device, master_controller=device._frame_cc
        )

        self.saving = Saving(
            device._config, ["classic", "saving"], self._params["saving"]
        )

    @property
    def nb_fifo_frames(self):
        return self._params["fifo"]["nb_fifo_frames"]

    @nb_fifo_frames.setter
    def nb_fifo_frames(self, value: int):
        self._params["fifo"]["nb_fifo_frames"] = value

    @setting_property(default=False)
    def use_mask(self):
        return self._params["mask"]["enabled"]

    @use_mask.setter
    @typecheck
    def use_mask(self, value: bool):
        self._params["mask"]["enabled"] = value

    @setting_property
    def mask(self):
        return self._params["mask"]["path"]

    @mask.setter
    @typecheck
    def mask(self, value: str):
        self._params["mask"]["path"] = value

    @setting_property(default=False)
    def use_flatfield(self):
        return self._params["flatfield"]["enabled"]

    @use_flatfield.setter
    @typecheck
    def use_flatfield(self, value: bool):
        self._params["flatfield"]["enabled"] = value

    @setting_property(default=False)
    def use_background(self):
        return self._params["background"]["enabled"]

    @use_background.setter
    @typecheck
    def use_background(self, value: bool):
        self._params["background"]["enabled"] = value

    @setting_property(default=False)
    def use_roi_stats(self):
        return self._params["statistics"]["enabled"]

    @use_roi_stats.setter
    @typecheck
    def use_roi_stats(self, value: bool):
        self._params["statistics"]["enabled"] = value

    @setting_property
    def rois(self) -> list:
        return self._rois

    @rois.setter
    @typecheck
    def rois(self, values: list):
        self._rois = values

        self._params["statistics"]["rect_rois"] = [
            {
                "topleft": {"x": roi.x, "y": roi.y},
                "dimensions": {"x": roi.width, "y": roi.height},
            }
            for roi in values
        ]

    @setting_property(default=False)
    def enable_saving(self):
        return self._params["saving"]["enabled"]

    @enable_saving.setter
    @typecheck
    def enable_saving(self, value: bool):
        self._params["saving"]["enabled"] = value

    def __info__(self):
        def format(title, params):
            return f"{title}:\n" + tabulate(params) + "\n\n"

        return (
            format("Mask", self._params["mask"])
            + format("Flatfield", self._params["flatfield"])
            + format("Background", self._params["background"])
            + format("ROI Statistics", self._params["statistics"])
            + format("Saving", self._params["saving"])
        )

    def _get_roi_counters(self):
        res = []
        if not self.use_roi_stats:
            return res

        self._roi_counters_cc._rois = self.rois
        for i, roi in enumerate(self.rois):
            res.extend(RoiStatCounters(roi, self._roi_counters_cc))

        return res

    def edit_rois(self):
        """
        Edit this detector ROI counters with Flint.

        When called without arguments, it will use the image from specified detector
        from the last scan/ct as a reference. If `acq_time` is specified,
        it will do a `ct()` with the given count time to acquire a new image.

        .. code-block:: python

            # Flint will be open if it is not yet the case
            pilatus1.edit_rois(0.1)

            # Flint must already be open
            ct(0.1, pilatus1)
            pilatus1.edit_rois()
        """
        # Check that Flint is already there
        flint = plot_module.get_flint()

        # def update_image_in_plot():
        #     """Create a single frame from detector data if available
        #     else use a placeholder.
        #     """
        #     try:
        #         image_data = image_utils.image_from_server(self._proxy, -1)
        #         data = image_data.array
        #     except Exception:
        #         # Else create a checker board place holder
        #         y, x = np.mgrid[0 : self.image.height, 0 : self.image.width]
        #         data = ((y // 16 + x // 16) % 2).astype(np.uint8) + 2
        #         data[0, 0] = 0
        #         data[-1, -1] = 5

        #     channel_name = f"{self.name}:frame"
        #     flint.set_static_image(channel_name, data)

        # That it contains an image displayed for this detector
        plot_proxy = flint.get_live_plot(image_detector=self._device.name)
        ranges = plot_proxy.get_data_range()
        if ranges[0] is None:
            # update_image_in_plot()
            pass
        plot_proxy.focus()

        # roi_counters = self.roi_counters
        # roi_profiles = self.roi_profiles

        # Retrieve all the ROIs
        # selections.extend(roi_counters.get_rois())
        # selections.extend(roi_profiles.get_rois())

        print(f"Waiting for ROI edition to finish on {self._device.name}...")
        self.rois = plot_proxy.select_shapes(
            self.rois,
            kinds=[
                "lima-rectangle",
                "lima-arc",
                "lima-vertical-profile",
                "lima-horizontal-profile",
            ],
        )

        # roi_counters.clear()
        # roi_profiles.clear()
        # for roi in selections:
        #     if isinstance(roi, RoiProfile):
        #         roi_profiles[roi.name] = roi
        #     else:
        #         roi_counters[roi.name] = roi

        roi_string = ", ".join(sorted([s.__repr__() for s in self.rois]))
        print(f"Applied ROIS {roi_string} to {self._device.name}")

    @property
    def counters(self):
        return [self._input_frame_cnt, self._frame_cnt, *self._get_roi_counters()]

    @property
    def counter_groups(self):
        return {
            # "images": counter_namespace([self._frame_cnt]),
            "images": counter_namespace([self._input_frame_cnt, self._frame_cnt]),
            "rois": counter_namespace(self._get_roi_counters()),
        }


# class Controller(CounterController):
#     """Classic processing user interface"""

#     def __init__(self, name):
#         self.frame_counter = (FrameCounter("frame", self._device),)

#     @property
#     def counters(self):
#         # TODO
#         return [
#             FrameCounter("frame", self._device),
#             # *RoiStatCounters("roi1", self._device),
#         ]


# class RoiCountersCC(IntegratingCounterController):
#     pass
