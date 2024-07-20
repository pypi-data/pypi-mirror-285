# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from bliss.common.utils import typecheck

from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.settings import Settings, setting_property


class Saving(Settings):
    def __init__(self, config, path, params):
        self._params = params
        super().__init__(config, path)

    @setting_property(default=False)
    def enabled(self):
        return self._params["enabled"]

    @enabled.setter
    @typecheck
    def enabled(self, value: bool):
        self._params["enabled"] = value

    @setting_property(default="bshuf_lz4")
    def compression(self):
        return self._params["compression"]

    @compression.setter
    @typecheck
    def compression(self, value: str):
        self._params["compression"] = value

    @setting_property(default=50)
    def nb_frames_per_file(self):
        return self._params["nb_frames_per_file"]

    @nb_frames_per_file.setter
    @typecheck
    def nb_frames_per_file(self, value: int):
        self._params["nb_frames_per_file"] = value

    @setting_property(default="abort")
    def file_exists_policy(self):
        return self._params["file_exists_policy"]

    @file_exists_policy.setter
    @typecheck
    def file_exists_policy(self, value: str):
        self._params["file_exists_policy"] = value

    def __info__(self):
        return tabulate(self._params)
