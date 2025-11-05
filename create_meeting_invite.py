from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore


SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
SCRIPT_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"
TIMEZONE_ID = "Asia/Kolkata"
TIMEZONE = ZoneInfo(TIMEZONE_ID)
DEFAULT_HOST_EMAIL = "arjuntheprogrammer@gmail.com"
DEFAULT_MEETING_TITLE = "Meeting"
DEFAULT_DURATION_MINUTES = 60
MEETING_TIME_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Google Calendar meeting invite with minimal inputs."
    )
    parser.add_argument(
        "--meeting-title",
        default=DEFAULT_MEETING_TITLE,
        help="Title for the calendar event (default: Meeting).",
    )
    parser.add_argument(
        "--meeting-time",
        required=True,
        help=(
            "Meeting start time in IST (Asia/Kolkata). "
            "Use 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DDTHH:MM'."
        ),
    )
    parser.add_argument(
        "--other-email",
        required=True,
        help="Email address of the other attendee.",
    )
    parser.add_argument(
        "--host-email",
        default=DEFAULT_HOST_EMAIL,
        help=f"Your email address (default: {DEFAULT_HOST_EMAIL}).",
    )
    parser.add_argument(
        "--meeting-notes",
        default="",
        help="Optional notes/links to include in the invite body.",
    )
    parser.add_argument(
        "--duration-minutes",
        type=int,
        default=DEFAULT_DURATION_MINUTES,
        help=f"Meeting length in minutes (default: {DEFAULT_DURATION_MINUTES}).",
    )
    return parser.parse_args()


def parse_meeting_time(meeting_time: str) -> dt.datetime:
    """Convert the provided meeting time string to a timezone-aware datetime."""
    for fmt in MEETING_TIME_FORMATS:
        try:
            naive_dt = dt.datetime.strptime(meeting_time, fmt)
            return naive_dt.replace(tzinfo=TIMEZONE)
        except ValueError:
            continue
    raise ValueError(
        f"Meeting time '{meeting_time}' did not match accepted formats: "
        + ", ".join(MEETING_TIME_FORMATS)
    )


def get_credentials() -> Credentials:
    """Load cached user credentials or complete the OAuth flow."""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"Missing credentials file at {CREDENTIALS_FILE}. "
            "Download OAuth client credentials from Google Cloud Console "
            "and save them as 'credentials.json'."
        )

    creds: Optional[Credentials] = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with TOKEN_FILE.open("w") as token_file:
            token_file.write(creds.to_json())

    return creds


def build_event(
    meeting_title: str,
    meeting_start: dt.datetime,
    duration_minutes: int,
    host_email: str,
    other_email: str,
    meeting_notes: str,
) -> dict:
    """Create the payload for the calendar event."""
    if duration_minutes <= 0:
        raise ValueError("Duration must be a positive number of minutes.")

    meeting_end = meeting_start + dt.timedelta(minutes=duration_minutes)

    attendees = [{"email": host_email}]
    if other_email != host_email:
        attendees.append({"email": other_email})

    return {
        "summary": meeting_title,
        "description": meeting_notes,
        "start": {"dateTime": meeting_start.isoformat(), "timeZone": TIMEZONE_ID},
        "end": {"dateTime": meeting_end.isoformat(), "timeZone": TIMEZONE_ID},
        "attendees": attendees,
        "reminders": {"useDefault": True},
    }


def create_calendar_event(args: argparse.Namespace) -> dict:
    """Authenticate, build the event payload, and insert it into Google Calendar."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    meeting_start = parse_meeting_time(args.meeting_time)
    event_body = build_event(
        meeting_title=args.meeting_title,
        meeting_start=meeting_start,
        duration_minutes=args.duration_minutes,
        host_email=args.host_email,
        other_email=args.other_email,
        meeting_notes=args.meeting_notes,
    )

    return (
        service.events()
        .insert(calendarId="primary", body=event_body, sendUpdates="all")
        .execute()
    )


def main():
    args = parse_args()
    created_event = create_calendar_event(args)

    print("Event created.")
    print(f"Summary: {created_event.get('summary')}")
    start_time = created_event['start']['dateTime']
    end_time = created_event['end']['dateTime']
    print(f"When: {start_time} -> {end_time}")
    print(f"Guest count: {len(created_event.get('attendees', []))}")
    if link := created_event.get("htmlLink"):
        print(f"View at: {link}")


if __name__ == "__main__":
    main()
