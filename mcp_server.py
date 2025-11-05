from __future__ import annotations

from typing import Optional

from mcp.server import FastMCP

from create_meeting_invite import (
    DEFAULT_DURATION_MINUTES,
    DEFAULT_HOST_EMAIL,
    DEFAULT_MEETING_TITLE,
    create_meeting_invite,
)


server = FastMCP(
    name="google-calendar-meeting",
    instructions=(
        "Use the `create_meeting_invite` tool to schedule meetings on the "
        "primary Google Calendar associated with the configured OAuth credentials."
    ),
)


@server.tool(
    name="create_meeting_invite",
    description=(
        "Create a Google Calendar meeting invite in Asia/Kolkata time. "
        "Requires meeting_time (YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM) "
        "and other_email."
    ),
)
def tool_create_meeting_invite(
    meeting_time: str,
    other_email: str,
    meeting_title: str = DEFAULT_MEETING_TITLE,
    host_email: str = DEFAULT_HOST_EMAIL,
    meeting_notes: str | None = None,
    duration_minutes: int = DEFAULT_DURATION_MINUTES,
) -> dict[str, Optional[str]]:
    event = create_meeting_invite(
        meeting_time=meeting_time,
        other_email=other_email,
        meeting_title=meeting_title,
        host_email=host_email,
        meeting_notes=meeting_notes or "",
        duration_minutes=duration_minutes,
    )

    return {
        "summary": event.get("summary"),
        "status": event.get("status"),
        "start": event.get("start", {}).get("dateTime"),
        "end": event.get("end", {}).get("dateTime"),
        "hangoutLink": event.get("hangoutLink"),
        "htmlLink": event.get("htmlLink"),
        "eventId": event.get("id"),
    }


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

