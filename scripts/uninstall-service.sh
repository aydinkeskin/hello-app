#!/bin/bash
# Uninstall hello-app launchd service

set -euo pipefail

SERVICE_NAME="com.hello-app"
PLIST_PATH="$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist"

if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm "$PLIST_PATH"
    echo "Service uninstalled."
    echo "  Removed: $PLIST_PATH"
else
    echo "Service not installed (plist not found at $PLIST_PATH)."
fi
