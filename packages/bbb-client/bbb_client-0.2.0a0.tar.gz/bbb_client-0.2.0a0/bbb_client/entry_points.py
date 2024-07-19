# bbb-client --- Client library and CLI to interact with the BBB API
# Copyright © 2021, 2023 Easter-Eggs <developpement@easter-eggs.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
from typing import Dict, Optional

from bbb_client.domain.meeting_management.model import Bbb, BbbException


def cli() -> None:
    from bbb_client.infrastructure.click.bbb import cli

    config = read_config_from_env()
    bbb = Bbb(config["url"], config["secret"])

    try:
        cli(obj={"bbb": bbb})
    except BbbException as exc:
        sys.stderr.write(str(exc))
        sys.exit(3)


def read_config_from_env() -> Dict[str, str]:
    return {
        "url": read_variable_from_env("BBB_API_URL"),
        "secret": read_variable_from_env("BBB_API_SECRET"),
    }


def read_variable_from_env(variable: str, default: Optional[str] = None) -> str:
    if variable not in os.environ:
        if default is not None:
            return default
        sys.stderr.write(f"Please set the ENV variable '{variable}'.")
        sys.exit(1)
    return os.environ[variable]
