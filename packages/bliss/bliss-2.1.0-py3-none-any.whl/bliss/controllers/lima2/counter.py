# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import enum
import numpy as np

from bliss.common.counter import Counter, IntegratingCounter


class FrameCounter(Counter):
    def __init__(self, name, controller, saving_spec, file_only=False):
        self._max_width = 0
        self._max_height = 0
        self._saving_spec = saving_spec
        self._file_only = file_only

        super().__init__(name, controller)

    def __info__(self):
        return "width:    Unknown\n" "height:   Unknown\n" "bpp:      Unknown\n"

    @property
    def shape(self):
        # Required by scan_info["channels"][xxx].dim
        return (0, 0, 0)

    @property
    def saving_spec(self):
        """The path to the saving parameters"""
        return self._saving_spec

    @property
    def file_only(self):
        """True if the file is accessible only on file"""
        return self._file_only


class RoiStat(enum.Enum):
    Sum = "sum"
    Avg = "avg"
    Std = "std"
    Min = "min"
    Max = "max"


class RoiStatCounter(IntegratingCounter):
    """A Counter object used for the statistics counters associated to one Roi"""

    def __init__(self, roi, stat, controller, **kwargs):
        self.roi = roi
        self.stat = stat
        name = f"{roi.name}_{stat.name.lower()}"
        super().__init__(name, controller, dtype=np.float32, **kwargs)

    def scan_metadata(self) -> dict:
        metadata = super().scan_metadata()
        metadata.update({self.roi.name: self.roi.to_dict()})
        return metadata


class RoiStatCounters:
    """An iterable container (associated to one roi.name) that yield the RoiStatCounters"""

    def __init__(self, roi, controller, **kwargs):
        # self._sum = RoiStatCounter(name, RoiStat.Sum, controller, **kwargs)
        self._avg = RoiStatCounter(roi, RoiStat.Avg, controller, **kwargs)
        self._std = RoiStatCounter(roi, RoiStat.Std, controller, **kwargs)
        self._min = RoiStatCounter(roi, RoiStat.Min, controller, **kwargs)
        self._max = RoiStatCounter(roi, RoiStat.Max, controller, **kwargs)

    # @property
    # def sum(self):
    #     return self._sum

    @property
    def avg(self):
        return self._avg

    @property
    def std(self):
        return self._std

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    def __iter__(self):
        # yield self.sum
        yield self.avg
        yield self.std
        yield self.min
        yield self.max
