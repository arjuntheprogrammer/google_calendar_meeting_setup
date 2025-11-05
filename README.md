# Google Calendar Meeting Setup

Automation script for creating Google Calendar meeting invites with minimal input. The script authenticates via OAuth, then creates an event on your primary calendar using the Google Calendar API.

## Prerequisites
- Python 3.11 (or use the provided Conda instructions).
- Google Cloud project with the Calendar API enabled.
- OAuth client credentials (`credentials.json`) downloaded to this folder.

### Recommended Conda Environment
```bash
conda create -n meeting_setup python=3.11
conda activate meeting_setup
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib mcp
```

## Obtain `credentials.json`
1. Visit the [Google Cloud Console](https://console.cloud.google.com/) and sign in.
2. Create/select a project.
3. Enable **Google Calendar API** under **APIs & Services → Library**.
4. Configure the OAuth consent screen (External is fine for testing) and add the Google accounts that will run this script as test users.
5. Navigate to **APIs & Services → Credentials** and create an **OAuth client ID** of type **Desktop app**.
6. Download the client configuration JSON, rename it to `credentials.json`, and place it beside `create_meeting_invite.py`.
7. (First run only) When the script opens a browser window, approve access—`token.json` will be saved for subsequent runs.

## Usage
```bash
python create_meeting_invite.py \
  --meeting-time "2025-11-09 17:00" \
  --other-email "karan.adhi@gmail.com" \
  --meeting-title "Karan <> Arjun | Intro call" \
  --meeting-notes "https://example.com/agenda"
```

- `--meeting-time` is required (IST timezone, format `YYYY-MM-DD HH:MM` or `YYYY-MM-DDTHH:MM`).
- `--other-email` is required.
- Optional flags:
  - `--meeting-title` (default: `Meeting`)
  - `--host-email` (default: `arjuntheprogrammer@gmail.com`)
  - `--meeting-notes` (default: empty)
  - `--duration-minutes` (default: 60)

The script prints the event details, including a link to view it in Google Calendar.

## MCP Server
This project also exposes a Model Context Protocol (MCP) server so MCP-capable assistants can call the meeting tool directly.

```bash
conda activate meeting_setup
python mcp_server.py
```

The server currently runs over stdio transport. When connected, call the `create_meeting_invite` tool with the same argument names used by the CLI flags (e.g. `meeting_time`, `other_email`, `meeting_title`, `meeting_notes`, `duration_minutes`, `host_email`). The tool responds with key event details (`summary`, `start`, `end`, `htmlLink`, etc.).

### Configure Codex to Use This MCP Server
1. Ensure the MCP environment is active (step above) and Codex CLI is installed.
2. Register the server once with Codex:
   ```bash
   codex mcp add calendar_meeting /Users/arjungupta/anaconda3/envs/meeting_setup/bin/python /Users/arjungupta/Development/extra/google_calendar_meeting_setup/mcp_server.py
   ```
3. Verify the registration:
   ```bash
   codex mcp list
   ```
   You should see `calendar_meeting` with transport `stdio` and the Python command.
4. Launch Codex normally (`codex`, `codex exec`, etc.). When Codex needs MCP tools it will start this server automatically.
5. Inside Codex, invoke the `create_meeting_invite` tool by supplying the same arguments as the CLI flags, for example:
   ```
   create_meeting_invite meeting_time="2025-11-16 16:00" other_email="partner@example.com" meeting_title="Strategy Sync"
   ```

Remove or reconfigure the server any time with `codex mcp remove calendar_meeting`.
