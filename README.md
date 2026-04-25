# WhatsApp Business Collector

Read-only WhatsApp Business Web collector for macOS. It turns an already logged-in Chrome WhatsApp Business Web session into structured JSON exports for dashboards, automations, and local reporting.

This project is deliberately not a bot and not a sender. It never types into WhatsApp, never targets the composer, never clicks send, and never creates outbound messages.

## Features

- Installable Python package with a `wa-business-collector` CLI.
- Active Chrome session collection through AppleScript JavaScript from Apple Events.
- Optional dedicated Chrome profile collection through Chrome DevTools Protocol for exact no-focus targeting.
- Label inventory and visible chat-list extraction.
- Labeled thread membership from WhatsApp Web IndexedDB.
- Bounded recent-message windows with a hard cap of 15 messages per chat.
- Stable export contract at `output/whatsapp-dashboard-export.json` by default.
- Atomic JSON writes with automatic backups before replacing an existing export.
- Runtime guardrails against send/composer JavaScript paths.

## Requirements

- macOS
- Python 3.11+
- Google Chrome
- WhatsApp Business Web already logged in at `https://web.whatsapp.com/`
- For active-session AppleScript mode: Chrome menu `View -> Developer -> Allow JavaScript from Apple Events`
- For dedicated-profile DevTools mode: Node.js 18+ available as `node`

## Install

From a local checkout:

```bash
python3 -m pip install .
```

For editable development:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pip install pytest build
```

After install, the command is available as:

```bash
wa-business-collector --help
```

## Quick start

Open WhatsApp Business Web in Chrome, verify you are logged in, then run:

```bash
wa-business-collector labels
wa-business-collector chat-list
```

Write the dashboard export:

```bash
wa-business-collector dashboard-export \
  --account-label "WhatsApp Business" \
  --max-messages 15 \
  --output output/whatsapp-dashboard-export.json
```

The export command preserves the previous output first:

```text
output/backup/whatsapp-dashboard-export.YYYYMMDD-HHMMSS.json
```

## Dedicated Chrome profile mode

Dedicated mode launches a separate Chrome profile with a remote-debugging port and a marker tab, then evaluates the WhatsApp tab through DevTools without bringing it to the front.

```bash
wa-business-collector ensure-tv-window \
  --profile-dir ~/.wa-business-collector/chrome-profile \
  --display-name TV \
  --placement-mode edge-hidden \
  --debug-port 19220
```

Then collect through that DevTools-backed target:

```bash
WA_CHROME_DEBUG_PORT=19220 \
WA_CHROME_MARKER_TITLE="Hermes WhatsApp Collector" \
WA_CHROME_MARKER_URL_SUBSTRING="hermes-whatsapp-collector" \
wa-business-collector dashboard-export \
  --account-label "WhatsApp Business" \
  --max-messages 15 \
  --output output/whatsapp-dashboard-export.json
```

When finished:

```bash
wa-business-collector quit-profile --profile-dir ~/.wa-business-collector/chrome-profile
```

## Scheduled export wrapper

A generic shell wrapper is included at `scripts/hourly_tv_export.sh`. It is safe to adapt for cron or launchd and is controlled through environment variables:

```bash
WA_COLLECTOR_PROJECT_DIR=/path/to/wa-business-collector \
WA_COLLECTOR_PROFILE_DIR=$HOME/.wa-business-collector/chrome-profile \
WA_COLLECTOR_OUTPUT=/path/to/output/whatsapp-dashboard-export.json \
WA_COLLECTOR_DISPLAY_NAME=TV \
WA_ACCOUNT_LABEL="WhatsApp Business" \
scripts/hourly_tv_export.sh
```

The wrapper tries dedicated-profile collection first, then active-session fallback, then preserves the existing non-empty export rather than overwriting it with an empty failure.

## Export shape

The dashboard export contains:

- `source`
- `exportedAt`
- `account`
- `allowLabels`
- `excludeLabels`
- `maxRecentMessages`
- `threads[]`
- per-thread `recentMessages`
- per-thread `messages` as a compatibility alias of `recentMessages`

Example thread fields:

```json
{
  "threadKey": "123456789@c.us",
  "chatTitle": "Example Contact",
  "chatType": "direct",
  "labelsRaw": ["Follow Up"],
  "labelsNormalized": ["follow-up"],
  "unread": true,
  "requiresResponse": true,
  "lastMessageAt": "2026-04-19T00:00:00+00:00",
  "recentMessages": [
    {
      "messageId": "false_123456789@c.us_ABCDEF",
      "timestamp": "2026-04-19T00:00:00+00:00",
      "direction": "inbound",
      "sender": "Example Contact",
      "text": "Hello",
      "textAvailable": true,
      "messageType": "chat",
      "subtype": null
    }
  ],
  "messages": []
}
```

## Safety model

Allowed operations:

- read page metadata
- read visible labels/chat list text
- read IndexedDB stores from the WhatsApp Web page context
- open a chat only for read-only true-ID message recovery in DevTools mode
- move/place the dedicated Chrome window without activating it

Forbidden operations:

- typing into the composer
- sending messages
- creating new chats for messaging
- interacting with attachments, calls, or voice recording
- fabricating message IDs from DOM position or visible text

The collector exports only messages with true underlying WhatsApp message IDs when available. It is better to emit fewer records than to publish unstable synthetic IDs.

## Development

Run tests:

```bash
python -m pytest
```

Build a distributable package:

```bash
python -m build
```

Install the built wheel locally:

```bash
python -m pip install dist/wa_business_collector-*.whl
```

## Publishing checklist

Before pushing to a public GitHub repo:

1. Confirm `.gitignore` is present.
2. Do not commit `.chrome-profiles/`, `output/`, `storage/`, `.venv/`, or live operational notes.
3. Run `python -m pytest`.
4. Run `python -m build`.
5. Review `git status --short` before the first commit.

## License

MIT
