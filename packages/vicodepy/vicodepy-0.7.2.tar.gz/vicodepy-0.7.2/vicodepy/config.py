# ViCodePy - A video coder for psychological experiments
#
# Copyright (C) 2024 Esteban Milleret
# Copyright (C) 2024 Rafael Laboissière
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import appdirs
from yaml import load, Loader, safe_dump
from pathlib import Path

CONFIG_FILENAME = "config.yml"
APP_NAME = "vicodepy"


class Config(dict):
    def __init__(self, config_file=CONFIG_FILENAME):
        self.filename = config_file
        self._load()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def _get_config_paths(self):
        return [
            Path(__file__).parent.joinpath("config", CONFIG_FILENAME),
            Path(appdirs.site_data_dir(APP_NAME)).joinpath(CONFIG_FILENAME),
            Path(appdirs.site_config_dir(APP_NAME)).joinpath(CONFIG_FILENAME),
            Path(appdirs.user_config_dir(APP_NAME)).joinpath(CONFIG_FILENAME),
            self.filename,
        ]

    def _load(self):
        for path in self._get_config_paths():
            config = self._load_file(path)
            if self._load_file(path):
                for k, v in config.items():
                    self.__setitem__(k, v)

    def _load_file(self, path):
        if os.path.isfile(path):
            with open(path, "r") as fid:
                return load(fid, Loader=Loader)
        else:
            return None

    def save(self):
        with open(self.filename, "w") as fid:
            safe_dump(dict(self), fid)
        pass
