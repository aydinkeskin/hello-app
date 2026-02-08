# CLAUDE.md — Hello App

## Project Overview

- **Name:** Hello App
- **Description:** A lightweight Python service that runs on a Mac Mini and listens for commands from an iPhone via ntfy.sh pub/sub. When the user sends a name string from their phone, the service receives it, processes it into a greeting ("Hello {name}!"), and pushes the result back to the phone as a notification. No inbound connections — all communication is outbound HTTPS only.
- **Stage:** MVP
- **Repository:** [TBD]

## Tech Stack

- **Language:** Python 3.12+
- **Framework:** None (standalone script)
- **Database:** None
- **Auth:** ntfy topic obscurity (long random topic names) + optional ntfy token auth
- **Hosting/Infra:** Mac Mini (local, always-on)
- **Key Libraries:**
  - `requests` — HTTP calls to ntfy.sh
  - `sseclient-py` — parsing Server-Sent Events stream from ntfy
  - `python-dotenv` — loading config from .env file
  - `logging` — structured logging to stdout

## Architecture

- **Pattern:** Event-driven pub/sub via ntfy.sh (no inbound connections)
- **Communication Flow:**

```
iPhone (ntfy app / iOS Shortcut)
  │
  │  POST https://ntfy.sh/{COMMANDS_TOPIC}
  │  Body: "World"
  ▼
ntfy.sh (cloud relay)
  │
  │  SSE stream (outbound HTTPS from Mac Mini)
  ▼
Mac Mini (Python service)
  │
  │  Processes: "Hello World!"
  │  POST https://ntfy.sh/{RESULTS_TOPIC}
  ▼
ntfy.sh (cloud relay)
  │
  │  Push notification
  ▼
iPhone (ntfy app shows notification)
```

- **Folder Structure:**
```
hello-app/
├── CLAUDE.md           # This file — project context
├── .env                # Topic names, config (gitignored)
├── .env.example        # Template for .env
├── .gitignore
├── requirements.txt    # Python dependencies
├── src/
│   ├── __init__.py
│   ├── main.py         # Entry point — starts the listener
│   ├── listener.py     # Subscribes to commands topic via SSE
│   ├── processor.py    # Business logic (greeting generation)
│   ├── notifier.py     # Publishes results to ntfy
│   └── config.py       # Loads and validates env vars
├── tests/
│   ├── __init__.py
│   ├── test_processor.py
│   ├── test_notifier.py
│   └── test_listener.py
└── scripts/
    ├── install-service.sh    # Install as launchd auto-start service
    └── uninstall-service.sh  # Remove launchd service
```

## User Types & Roles

| Role          | Description                              | Interaction Method                    |
|---------------|------------------------------------------|---------------------------------------|
| iPhone User   | Sends a name, receives a greeting back   | ntfy app or iOS Shortcut              |

## Core Features

### 1. Command Listener (SSE Subscriber)
- **Description:** Maintains a persistent outbound HTTPS connection to ntfy.sh, subscribing to the commands topic via Server-Sent Events. Receives messages in real time.
- **User-facing behavior:** Invisible — runs in background on Mac Mini.
- **Technical notes:**
  - Connect to `https://ntfy.sh/{COMMANDS_TOPIC}/sse`
  - Parse incoming SSE events, extract the message body
  - On connection drop: auto-reconnect with exponential backoff (1s, 2s, 4s, max 60s)
  - Log all received commands with timestamp
  - Ignore empty or malformed messages gracefully
- **Priority:** Must-have

### 2. Greeting Processor
- **Description:** Takes the received name string and produces a greeting.
- **User-facing behavior:** The user sends "World" and gets back "Hello World!"
- **Technical notes:**
  - Input: raw string from ntfy message body
  - Output: `f"Hello {name.strip()}!"`
  - Strip whitespace, handle empty strings (respond with "Hello stranger!")
  - Max input length: 200 characters (truncate with "..." if exceeded)
- **Priority:** Must-have

### 3. Result Notifier (ntfy Publisher)
- **Description:** Publishes the greeting result to the results ntfy topic so the iPhone receives a push notification.
- **User-facing behavior:** iPhone shows a notification with title "Hello App 👋" and the greeting as body text.
- **Technical notes:**
  - POST to `https://ntfy.sh/{RESULTS_TOPIC}`
  - Headers: `Title: Hello App 👋`, `Priority: default`
  - Body: the greeting string
  - Timeout: 10 seconds
  - On failure: log error, do not retry (fire and forget for MVP)
- **Priority:** Must-have

### 4. Graceful Shutdown
- **Description:** Handle SIGINT/SIGTERM cleanly so the service can be stopped with Ctrl+C or by launchd.
- **Technical notes:**
  - Catch signals, close SSE connection, log "Service stopped"
  - Exit code 0 on clean shutdown
- **Priority:** Must-have

### 5. Health Logging
- **Description:** Periodic log output so the user knows the service is alive.
- **Technical notes:**
  - Log "Listening on {COMMANDS_TOPIC}..." on startup
  - Log "Still listening... (uptime: Xh Ym)" every 5 minutes
  - Log every received command and sent notification
- **Priority:** Nice-to-have

### 6. macOS Auto-Start (launchd)
- **Description:** A launchd plist so the service starts automatically on boot and restarts on crash.
- **Technical notes:**
  - Generate `com.hello-app.plist` for `~/Library/LaunchAgents/`
  - Include stdout/stderr log paths
  - KeepAlive: true
  - Provide install/uninstall scripts
- **Priority:** Nice-to-have

## Environment Variables

| Variable         | Purpose                              | Example                                  |
|------------------|--------------------------------------|------------------------------------------|
| COMMANDS_TOPIC   | ntfy topic to subscribe for commands | `hello-cmd-a7f3b2e1-9c4d-4e8f-b6a1-x`   |
| RESULTS_TOPIC    | ntfy topic to publish results to     | `hello-res-d2c8e5f4-1a3b-4d7e-9f2c-x`   |
| NTFY_BASE_URL    | ntfy server URL (default: ntfy.sh)   | `https://ntfy.sh`                        |
| NTFY_TOKEN       | Optional auth token for ntfy         | `tk_abc123...` (leave empty if unused)   |
| LOG_LEVEL        | Logging verbosity                    | `INFO`                                   |

## Coding Conventions

- **Style:** Simple, functional Python. No classes unless they add clarity. Prefer small, pure functions.
- **Naming:** snake_case everywhere. Constants in UPPER_SNAKE_CASE.
- **Error Handling:** Try/except around all HTTP calls and SSE parsing. Log errors with full context. Never crash the main loop — catch, log, and continue.
- **Testing:** pytest. Test processor logic and notifier (mock HTTP calls). Test files mirror source structure in `tests/`.
- **Comments:** Minimal. Docstrings on each module and public function. No inline comments unless explaining something non-obvious.
- **Type Hints:** Use them on all function signatures.
- **Imports:** Standard library first, third-party second, local third. Separated by blank lines.

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit with your topic names

# Run
python -m src.main

# Test
pytest tests/ -v

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Install as launchd service (auto-start on boot)
./scripts/install-service.sh

# Uninstall launchd service
./scripts/uninstall-service.sh
```

## Third-Party Integrations

| Service   | Purpose                          | Setup Notes                                    |
|-----------|----------------------------------|------------------------------------------------|
| ntfy.sh   | Pub/sub messaging + push notifs  | Free tier. No account needed. Use long random topic names for privacy. Optional: create account for token auth at https://ntfy.sh/app |

## iPhone Setup Instructions

### Option A: ntfy App (simplest)
1. Install **ntfy** from the App Store
2. Subscribe to your `RESULTS_TOPIC` to receive notifications
3. To send a command: tap ✏️, publish to your `COMMANDS_TOPIC`, type a name, send

### Option B: iOS Shortcut (one-tap trigger)
1. Open **Shortcuts** app → New Shortcut
2. Add action: **Ask for Input** → type: Text, prompt: "Enter a name"
3. Add action: **Get Contents of URL**
   - URL: `https://ntfy.sh/{COMMANDS_TOPIC}`
   - Method: POST
   - Request Body: the input from step 2
4. Save shortcut as "Say Hello"
5. Add to Home Screen for one-tap access

## Constraints & Non-Goals

- No web UI — interaction is entirely via ntfy app or iOS Shortcuts
- No database — stateless, no message history
- No inbound connections to Mac Mini — all traffic is outbound HTTPS
- No multi-user support — single user, single device
- No message queue persistence — if the service is down, missed commands are lost
- No rate limiting for MVP — trust the single user
- Do not over-engineer — this is a simple proof-of-concept for the ntfy pub/sub pattern

## Known Issues / Tech Debt

- [ ] SSE reconnection not yet implemented (first build)
- [ ] No integration tests (only unit tests for MVP)
- [ ] No message deduplication if ntfy replays on reconnect

## Notes for Claude

- This is a simple starter project to validate the ntfy pub/sub architecture. Keep it minimal.
- Prefer small, focused commits with conventional commit messages (feat:, fix:, docs:, etc.)
- Always ask before adding new dependencies beyond what's listed.
- Do not introduce async/await unless there's a clear reason — keep it synchronous with `requests` for simplicity.
- Run `pytest` and `ruff check` before considering any task complete.
- When creating .env.example, use placeholder values that clearly indicate they need to be replaced.
- Generate fresh UUID-based topic names in setup instructions — never hardcode real topic names.
