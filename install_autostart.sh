#!/bin/bash
# BIODISC Auto-Start Installation Script
# Configures BIODISC to start automatically on system boot/login

set -e

BIODISC_DIR="/Users/gjw255/astrodata/SWARM/BIODISC"
PLIST_FILE="com.biodisc.autonomous.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🧬 BIODISC Auto-Start Installation"
echo "======================================"

# Check if running from BIODISC directory
if [ "$(pwd)" != "$BIODISC_DIR" ]; then
    echo "❌ Please run this script from the BIODISC directory:"
    echo "   cd $BIODISC_DIR"
    echo "   ./install_autostart.sh"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
echo "📁 Setting up LaunchAgents directory..."
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist file to LaunchAgents
echo "📋 Installing launch agent..."
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Update plist with current user and paths
echo "🔧 Configuring launch agent..."
sed -i '' "s|/Users/gjw255/astrodata/SWARM/BIODISC|$BIODISC_DIR|g" "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Get current Python path
PYTHON_PATH=$(which python3)
echo "🐍 Using Python: $PYTHON_PATH"
sed -i '' "s|/Library/Frameworks/Python.framework/Versions/3.14/bin/python3|$PYTHON_PATH|g" "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Unload existing agent if running
echo "🔄 Unloading any existing BIODISC agent..."
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null || true

# Load the new agent
echo "✅ Loading BIODISC auto-start agent..."
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Start the service
echo "🚀 Starting BIODISC autonomous discovery..."
launchctl start com.biodisc.autonomous

echo ""
echo "✅ BIODISC Auto-Start Installation Complete!"
echo "=============================================="
echo ""
echo "📊 Status Commands:"
echo "   launchctl list | grep biodisc                    # Check if loaded"
echo "   launchctl start com.biodisc.autonomous           # Start manually"
echo "   launchctl stop com.biodisc.autonomous            # Stop manually"
echo "   tail -f biodisc_autonomous.log                   # Monitor activity"
echo ""
echo "🗑️  To uninstall:"
echo "   launchctl unload $LAUNCH_AGENTS_DIR/$PLIST_FILE"
echo "   rm $LAUNCH_AGENTS_DIR/$PLIST_FILE"
echo ""
echo "🧬 BIODISC will now start automatically on system login!"
