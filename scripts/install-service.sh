#!/bin/bash
# Install hello-app as a launchd service (auto-start on login)

set -euo pipefail

SERVICE_NAME="com.hello-app"
PLIST_PATH="$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$HOME/Library/Logs/hello-app"

mkdir -p "$LOG_DIR"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${SERVICE_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PROJECT_DIR}/venv/bin/python</string>
        <string>-m</string>
        <string>src.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${PROJECT_DIR}</string>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

launchctl load "$PLIST_PATH"

echo "Service installed and started."
echo "  Plist: $PLIST_PATH"
echo "  Logs:  $LOG_DIR/"
echo ""
echo "To check status: launchctl list | grep hello-app"
echo "To view logs:    tail -f $LOG_DIR/stdout.log"
