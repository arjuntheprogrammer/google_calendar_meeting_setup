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
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
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
