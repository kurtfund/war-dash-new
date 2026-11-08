#!/usr/bin/env bash
set -e

# ========================================================
# Setup macOS launchd background daemon for War Dash
# Runs 100% locally on your Mac for FREE (zero cloud cost)
# ========================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.wardash.worker.plist"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$DIR/logs"

echo "Creating launchd service plist at $PLIST_PATH..."

cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wardash.worker</string>
    <key>WorkingDirectory</key>
    <string>$DIR</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$DIR/scripts/run_local.sh</string>
        <string>--once</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$DIR/logs/worker.log</string>
    <key>StandardErrorPath</key>
    <string>$DIR/logs/worker_err.log</string>
</dict>
</plist>
EOF

# Unload previous instance if running
launchctl unload "$PLIST_PATH" 2>/dev/null || true

# Load and start daemon
launchctl load "$PLIST_PATH"

echo "✅ War Dash background daemon installed and loaded successfully!"
echo "   - Interval: Every 30 minutes"
echo "   - Logs: $DIR/logs/worker.log"
echo "   - To stop anytime, run: ./scripts/stop_mac_daemon.sh"
