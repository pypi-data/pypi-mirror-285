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

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlencode

import requests
import untangle

LOGGER = logging.getLogger(__file__)


class BbbException(Exception):
    pass


class MeetingDoesNotExist(BbbException):
    def __init__(self) -> None:
        super().__init__("Meeting does not exist!")


class MeetingAlreadyExists(BbbException):
    def __init__(self) -> None:
        super().__init__("Meeting already exists!")


class ChecksumError(BbbException):
    def __init__(self) -> None:
        super().__init__("Checksum error! Please verify your shared secret.")


class BadResponseFromServer(BbbException):
    def __init__(self, url: str, response: requests.Response):
        super().__init__(
            f"Bad response from BBB API: {response.status_code}. "
            f"Please check URL: <{url}>."
        )
        self.url = url
        self.response = response


class AccessForbidden(BbbException):
    def __init__(self, url: str):
        super().__init__("Access forbidden! Make sure your secret is correct.")
        self.url = url


class UnixTimestamp(int):
    pass


class Features(Enum):
    CAPTIONS = "captions"  # Closed Caption
    CHAT = "chat"
    SNAPSHOT_SLIDES = "snapshotOfCurrentSlide"
    EXTERNAL_VIDEO = "externalVideos"  # Share an external video
    BREAKOUT_ROOMS = "breakoutRooms"
    BREAKOUT_ROOMS_IMPORT_PRESENTATION = (
        "importPresentationWithAnnotationsFromBreakoutRooms"
    )
    BREAKOUT_ROOMS_IMPORT_SHARED_NOTES = "importSharedNotesFromBreakoutRooms"
    LAYOUTS = "layouts"  # Allow only default layout
    LEARNING_DASHBOARD = "learningDashboard"
    LEARNING_DASHBOARD_DOWNLOAD = "learningDashboardDownloadSessionData"
    POLLS = "polls"
    SCREENSHARE = "screenshare"
    SHARED_NOTES = "sharedNotes"
    VIRTUAL_BACKGROUND = "virtualBackgrounds"
    VIRTUAL_BACKGROUND_CUSTOM = "customVirtualBackgrounds"  # Virtual Backgrounds Upload
    LIVE_TRANSCRIPTION = "liveTranscription"
    PRESENTATION = "presentation"
    PRESENTATION_DOWNLOAD = "downloadPresentationWithAnnotations"
    CAMERA_AS_CONTENT = "cameraAsContent"  # Enables/Disables camera as a content
    TIMER = "timer"


@dataclass(frozen=True)
class MeetingInfo:
    """
    See <https://docs.bigbluebutton.org/dev/api.html#getmeetinginfo>
    """

    meetingName: str
    meetingID: str
    createTime: UnixTimestamp
    startTime: UnixTimestamp
    endTime: UnixTimestamp
    attendeePW: str
    moderatorPW: str
    duration: int
    participantCount: int
    participants: list[str]
    maxUsers: int
    voiceBridge: str


@dataclass()
class MeetingFilters:
    voiceBridge: Optional[str] = ""


class Bbb:
    """Class defining methods to interact with a BBB API.

    See: <https://docs.bigbluebutton.org/development/api>.
    """

    def __init__(self, url: str, secret: str) -> None:
        self.__url = url
        self.__secret = secret

    def get_meetings(
        self, filters: Optional[MeetingFilters] = None
    ) -> list[MeetingInfo]:
        element = self.__xml_to_element(self.__get_xml(self.__build_url("getMeetings")))

        if not hasattr(element.response.meetings, "meeting"):
            return []

        return self.__filter(
            [
                self.__element_to_meeting_info(e)
                for e in element.response.meetings.meeting
            ],
            filters,
        )

    def __build_url(self, action: str, query: str = "") -> str:
        checksum = self.__compute_checksum(action, query, self.__secret)
        return f"{self.__url}/{action}?{query}&checksum={checksum}"

    def __get_xml(self, url: str) -> str:
        LOGGER.info(f"GET {url}")
        response = requests.get(url)
        LOGGER.debug("response = \n" + response.text)
        if self.__is_success(response) and self.__is_xml(response):
            return response.text
        self.__handle_bad_response(url, response)
        return ""

    def __is_success(self, response: requests.Response) -> bool:
        return 200 <= response.status_code < 300

    def __is_xml(self, response: requests.Response) -> bool:
        return response.headers.get("content-type", "").startswith("text/xml")

    def __handle_bad_response(self, url: str, response: requests.Response) -> None:
        if response.status_code == 401:
            raise AccessForbidden(url)
        raise BadResponseFromServer(url, response)

    def __compute_checksum(self, action: str, query: str, secret: str) -> str:
        return hashlib.sha1(str.encode(f"{action}{query}{secret}")).hexdigest()

    def __xml_to_element(self, xml: str) -> Any:
        element = untangle.parse(xml)

        # Warnings (come first because a warning is a success)
        if (
            hasattr(element.response, "messageKey")
            and element.response.messageKey.cdata == "duplicateWarning"
        ):
            raise MeetingAlreadyExists()

        # Success
        if element.response.returncode.cdata == "SUCCESS":
            return element

        # Errors
        if element.response.messageKey.cdata == "notFound":
            raise MeetingDoesNotExist()
        if element.response.messageKey.cdata == "checksumError":
            raise ChecksumError()
        raise Exception(xml)

    def __element_to_meeting_info(self, element: Any) -> MeetingInfo:
        try:
            participants = [a.fullName.cdata for a in element.attendees.attendee]
        except AttributeError:
            participants = []

        return MeetingInfo(
            meetingName=element.meetingName.cdata,
            meetingID=element.meetingID.cdata,
            createTime=element.createTime.cdata,
            startTime=element.startTime.cdata,
            endTime=element.endTime.cdata,
            attendeePW=element.attendeePW.cdata,
            moderatorPW=element.moderatorPW.cdata,
            duration=element.duration.cdata,
            participantCount=element.participantCount.cdata,
            participants=participants,
            maxUsers=element.maxUsers.cdata,
            voiceBridge=element.voiceBridge.cdata,
        )

    def __filter(
        self, meetings: list[MeetingInfo], filters: Optional[MeetingFilters]
    ) -> list[MeetingInfo]:
        if not filters:
            return meetings

        results = meetings
        if filters.voiceBridge:
            results = [m for m in results if filters.voiceBridge == m.voiceBridge]

        return results

    def create_meeting(
        self,
        meeting_id: str,
        name: str = "",
        moderator_password: str = "",
        attendee_password: str = "",
        max_participants: int = 0,
        logout_url: str = "",
        features: Optional[list[Features]] = None,
    ) -> bool:
        query = {"meetingID": meeting_id}
        if name:
            query["name"] = name
        if moderator_password:
            query["moderatorPW"] = moderator_password
        if attendee_password:
            query["attendeePW"] = attendee_password
        if max_participants:
            query["maxParticipants"] = str(max_participants)
        if logout_url:
            query["logoutURL"] = logout_url

        disabled_features = [f.value for f in Features if f not in (features or [])]
        query["disabledFeatures"] = ",".join(disabled_features)

        try:
            self.__xml_to_element(
                self.__get_xml(self.__build_url("create", urlencode(query)))
            )
            return True
        except Exception as exc:
            LOGGER.debug(exc)
            return False

    def generate_join_url(
        self,
        meeting_id: str,
        username: str,
        password: str = "",
        moderator: bool = False,
        error_url: str = "",
    ) -> str:
        if not password:
            info = self.get_meeting_info(meeting_id)
            if moderator:
                password = info.moderatorPW
            else:
                password = info.attendeePW

        if not password:
            raise BbbException(
                "Meeting does not yet exist, "
                "you MUST provide a password to include in the URL."
            )

        query = {"fullName": username, "meetingID": meeting_id, "password": password}
        if error_url:
            query["errorRedirectUrl"] = error_url
        return self.__build_url("join", urlencode(query))

    def get_meeting_info(self, meeting_id: str) -> MeetingInfo:
        query = {"meetingID": meeting_id}
        xml = self.__get_xml(self.__build_url("getMeetingInfo", urlencode(query)))
        element = self.__xml_to_element(xml)
        return self.__element_to_meeting_info(element.response)

    def end_meeting(self, meeting_id: str) -> bool:
        info = self.get_meeting_info(meeting_id)
        query = {"meetingID": meeting_id, "password": info.moderatorPW}
        xml = self.__get_xml(self.__build_url("end", urlencode(query)))
        try:
            return bool(self.__xml_to_element(xml))
        except Exception as exc:
            LOGGER.debug(exc)
            return False
