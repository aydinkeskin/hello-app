# Hello App

A lightweight Python service that runs on a Mac Mini and listens for commands from an iPhone via [ntfy.sh](https://ntfy.sh) pub/sub. Send a name from your phone, get a greeting back as a push notification. No inbound connections — all communication is outbound HTTPS only.

## How It Works

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

## Requirements

- Python 3.12+
- A [ntfy.sh](https://ntfy.sh) account (optional — free tier works without one)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit with your topic names
```

### Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `COMMANDS_TOPIC` | ntfy topic to subscribe for commands | `hello-cmd-a7f3b2e1-9c4d-4e8f-b6a1-x` |
| `RESULTS_TOPIC` | ntfy topic to publish results to | `hello-res-d2c8e5f4-1a3b-4d7e-9f2c-x` |
| `NTFY_BASE_URL` | ntfy server URL (default: `https://ntfy.sh`) | `https://ntfy.sh` |
| `NTFY_TOKEN` | Optional auth token for ntfy | `tk_abc123...` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

## Usage

```bash
python -m src.main
```

The service connects to ntfy.sh via SSE, parses incoming JSON events, extracts the message field, and pushes back greeting notifications. It automatically reconnects with exponential backoff if the connection drops. Stop it with `Ctrl+C`.

### macOS Auto-Start (launchd)

```bash
# Install as a service that starts on login and restarts on crash
./scripts/install-service.sh

# Remove the service
./scripts/uninstall-service.sh
```

## iPhone Setup

### Option A: ntfy App (simplest)

1. Install **ntfy** from the App Store
2. Subscribe to your `RESULTS_TOPIC` to receive notifications
3. To send a command: tap the compose button, publish to your `COMMANDS_TOPIC`, type a name, send

### Option B: iOS Shortcut (one-tap trigger)

1. Open **Shortcuts** app > New Shortcut
2. Add action: **Ask for Input** > type: Text, prompt: "Enter a name"
3. Add action: **Get Contents of URL**
   - URL: `https://ntfy.sh/{COMMANDS_TOPIC}`
   - Method: POST
   - Request Body: the input from step 2
4. Save shortcut as "Say Hello"
5. Add to Home Screen for one-tap access

## Development

```bash
# Run tests
pytest tests/ -v

# Lint and format
ruff check src/ tests/
ruff format src/ tests/
```

## Project Structure

```
hello-app/
├── src/
│   ├── main.py         # Entry point — starts the listener
│   ├── listener.py     # Subscribes to commands topic via SSE, parses JSON events
│   ├── processor.py    # Business logic (greeting generation)
│   ├── notifier.py     # Publishes results to ntfy
│   └── config.py       # Loads and validates env vars
├── tests/
│   ├── test_processor.py
│   ├── test_notifier.py
│   └── test_listener.py
├── scripts/
│   ├── install-service.sh
│   └── uninstall-service.sh
├── .env.example
├── requirements.txt
├── README.md
└── CLAUDE.md
```

## License

MIT
