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

from typing import List

from bbb_client.use_cases import search_meetings


class SearchMeetings:
    def __init__(self, filters: List[str], separator: str) -> None:
        assert len(separator) == 1

        self.__request = search_meetings.Request()

        for f in filters:
            if separator not in f:
                self.__request.filters[f] = ""
            else:
                name, value = f.split(separator, 1)
                self.__request.filters[name] = value

    def call(self, interactor: search_meetings.Interactor) -> None:
        interactor.execute(self.__request)


class ListMeetings:
    def call(self, interactor: search_meetings.Interactor) -> None:
        interactor.execute(search_meetings.Request())
