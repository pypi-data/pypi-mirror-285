# bbb-client --- Client library and CLI to interact with the BBB API
# Copyright © 2021, 2024 Easter-eggs
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

from typing import Callable, List

from bbb_client.domain.meeting_management.model import MeetingInfo
from bbb_client.use_cases import search_meetings


class SearchMeetings(search_meetings.Presenter):
    def __init__(
        self,
        stdout: Callable[[str], None],
        stderr: Callable[[str], None],
        separator: str,
    ) -> None:
        assert len(separator) == 1

        self.__stdout = stdout
        self.__stderr = stderr
        self.__separator = separator
        self.__exit_code = -1

    def unknown_filter(self, name: str, choices: List[str]) -> None:
        self.__stderr(f'[WA] unknown filter "{name}"! (choices: {", ".join(choices)})')

    def missing_filter_value(self, name: str) -> None:
        self.__stderr(
            f'[WA] Skipping filter "{name}" for it has no value! (separator: "{self.__separator}")'
        )

    def meeting_info(self, info: MeetingInfo) -> None:
        self.__stdout(f'"{info.meetingName}" (meeting ID: {info.meetingID})')
        self.__exit_code = 0

    def exit_code(self) -> int:
        if self.__exit_code == -1:
            self.__stderr("There are no meetings matching your criteria.")
            self.__exit_code = 2
        return self.__exit_code


class ListMeetings(search_meetings.Presenter):
    def __init__(
        self, stdout: Callable[[str], None], stderr: Callable[[str], None]
    ) -> None:
        self.__stdout = stdout
        self.__stderr = stderr
        self.__exit_code = -1

    def unknown_filter(self, name: str, choices: List[str]) -> None:
        assert False

    def missing_filter_value(self, name: str) -> None:
        assert False

    def meeting_info(self, info: MeetingInfo) -> None:
        self.__stdout(f'"{info.meetingName}" (meeting ID: {info.meetingID})')
        self.__exit_code = 0

    def exit_code(self) -> int:
        if self.__exit_code == -1:
            self.__stderr("There are no running meetings.")
            self.__exit_code = 0
        return self.__exit_code
