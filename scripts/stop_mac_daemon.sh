#!/usr/bin/env bash
PLIST_PATH="$HOME/Library/LaunchAgents/com.wardash.worker.plist"

if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm -f "$PLIST_PATH"
    echo "✅ War Dash background daemon stopped and removed from macOS launchd."
else
    echo "Daemon plist not found at $PLIST_PATH (already stopped)."
fi
