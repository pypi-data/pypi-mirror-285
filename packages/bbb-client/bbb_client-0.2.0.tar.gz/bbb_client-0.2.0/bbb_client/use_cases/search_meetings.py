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

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from bbb_client.domain.meeting_management.model import Bbb, MeetingFilters, MeetingInfo


@dataclass
class Request:
    filters: dict[str, str] = field(default_factory=dict)


class Presenter(metaclass=ABCMeta):
    @abstractmethod
    def unknown_filter(self, name: str, choices: list[str]) -> None:
        pass

    @abstractmethod
    def missing_filter_value(self, name: str) -> None:
        pass

    @abstractmethod
    def meeting_info(self, info: MeetingInfo) -> None:
        pass


class Interactor:
    def __init__(self, bbb: Bbb, presenter: Presenter) -> None:
        self.__bbb = bbb
        self.__presenter = presenter

    def execute(self, request: Request) -> None:
        filters = MeetingFilters()
        known_filters = [a for a in dir(filters) if not a.startswith("_")]

        for name, value in request.filters.items():
            if not hasattr(filters, name):
                self.__presenter.unknown_filter(name, known_filters)
                continue
            if not value:
                self.__presenter.missing_filter_value(name)
                continue
            setattr(filters, name, value)

        for m in self.__bbb.get_meetings(filters):
            self.__presenter.meeting_info(m)
