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

import logging
import sys

import click

from bbb_client.domain.meeting_management.model import (
    Bbb,
    BbbException,
    Features,
    MeetingDoesNotExist,
)
from bbb_client.interfaces import from_terminal as controllers
from bbb_client.interfaces import to_terminal as presenters
from bbb_client.use_cases import search_meetings

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    level=logging.WARNING,
)


def stdout(text: str) -> None:
    click.echo(text)


def stderr(text: str) -> None:
    click.echo(text, err=True)


@click.group()
@click.option("--verbose", "-v", count=True)
@click.pass_context
def cli(ctx: click.Context, verbose: int) -> None:
    if not ctx.obj:
        ctx.obj = {}

    if verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.group()
@click.pass_context
def meetings(ctx: click.Context) -> None:
    pass


@meetings.command(name="list")
@click.pass_context
def list_all(ctx: click.Context) -> None:
    """List all meetings."""

    bbb: Bbb = ctx.obj["bbb"]

    presenter = presenters.ListMeetings(stdout, stderr)
    interactor = search_meetings.Interactor(bbb, presenter)
    controller = controllers.ListMeetings()
    controller.call(interactor)
    ctx.exit(presenter.exit_code())


@meetings.command()
@click.argument("filters", nargs=-1, required=True)
@click.pass_context
def search(ctx: click.Context, filters: list[str]) -> None:
    """Only return meetings matching some criteria.

    Filters are a name/value paire, for instance `voiceBridge=12345`.
    """

    bbb: Bbb = ctx.obj["bbb"]

    separator = "="
    presenter = presenters.SearchMeetings(stdout, stderr, separator)
    interactor = search_meetings.Interactor(bbb, presenter)
    controller = controllers.SearchMeetings(filters, separator)
    controller.call(interactor)
    ctx.exit(presenter.exit_code())


@meetings.command()
@click.argument("id")
@click.argument("name", required=False, default="")
@click.option("--moderator-password", "-M", default="")
@click.option("--attendee-password", "-A", default="")
@click.option("--max-participants", "-P", default=0)
@click.option(
    "--list-features",
    "-L",
    default=False,
    is_flag=True,
    help="List available features.",
)
@click.option(
    "--enabled-features",
    "-E",
    default="",
    help="Comma separated list of features to enable. Use `ALL` for all.",
)
@click.option(
    "--disabled-features",
    "-D",
    default="",
    help="Comma separated list of features to disable. Use `ALL` for all.",
)
@click.pass_context
def create(
    ctx: click.Context,
    id: str,
    name: str,
    moderator_password: str,
    attendee_password: str,
    max_participants: int,
    list_features: bool,
    enabled_features: str,
    disabled_features: str,
) -> None:
    """Create a new meeting.

    No extra-features are enabled by default."""

    if list_features:
        print("Available features:")
        for f in sorted([f for f in Features], key=lambda f: f.value):
            print(f"  - {f.value}")
        sys.exit(0)

    if not name:
        name = id

    bbb: Bbb = ctx.obj["bbb"]
    try:
        bbb.create_meeting(
            id,
            name=name,
            moderator_password=moderator_password,
            attendee_password=attendee_password,
            max_participants=max_participants,
            features=compute_feature_list(enabled_features, disabled_features),
        )
        click.echo("[OK] Meeting successfully created.")
    except Exception as exc:
        click.echo(f"[ER] {exc}")


def compute_feature_list(enabled: str, disabled: str) -> list[Features]:
    if enabled and disabled:
        raise Exception("You cannot enable AND disable at the same time!")
    if "ALL" in enabled:
        return [f for f in Features]
    if "ALL" in disabled or (not enabled and not disabled):
        return []
    if enabled:
        return [f for f in Features if f.value in enabled.split(",")]
    return [f for f in Features if f.value not in disabled.split(",")]


@meetings.command()
@click.argument("meeting")
@click.argument("user")
@click.argument("password", default="")
@click.option("--moderator", "-m", is_flag=True, default=False)
@click.pass_context
def join(
    ctx: click.Context, meeting: str, user: str, password: str, moderator: bool
) -> None:
    """Create an URL to be used to join an existing meeting."""

    bbb: Bbb = ctx.obj["bbb"]
    try:
        url = bbb.generate_join_url(meeting, user, password, moderator=moderator)
        click.echo(url)
    except BbbException as exc:
        click.echo(f"[ER] {exc}")


@meetings.command()
@click.argument("id")
@click.pass_context
def show(ctx: click.Context, id: str) -> None:
    """Show information for a given meeting."""

    bbb: Bbb = ctx.obj["bbb"]
    try:
        info = bbb.get_meeting_info(id)
        click.echo(f'Name: "{info.meetingName}"')
        click.echo(f"ID: {info.meetingID}")
        participants = ", ".join(info.participants)
        click.echo(f"Participants: {info.participantCount} ({participants})")
        click.echo(f"Audio-conf. PIN: {info.voiceBridge}")
    except MeetingDoesNotExist:
        click.echo(f"[ER] Meeting '{id}' does not exist!")


@meetings.command()
@click.argument("id")
@click.pass_context
def end(ctx: click.Context, id: str) -> None:
    """End a given meeting."""

    bbb: Bbb = ctx.obj["bbb"]

    try:
        status = bbb.end_meeting(id)
    except MeetingDoesNotExist:
        click.echo(f"[ER] Meeting '{id}' does not exist!")
        return

    if status:
        click.echo("[OK] Meeting successfully ended.")
    else:
        click.echo("[ER] Meeting could not be ended!")


@meetings.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Display statistics about all meetings."""

    bbb: Bbb = ctx.obj["bbb"]
    meetings = bbb.get_meetings()

    if meetings:
        for m in meetings:
            click.echo(f'{m.participantCount} participant(s) in "{m.meetingID}"')
    else:
        click.echo("There are no meetings at the moment.")
