#!/bin/bash

# list-profiles.sh - Display available transcoding profiles from profiles.json
# Usage: ./list-profiles.sh [--verbose]
# Works on: macOS, Linux, WSL2

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILES_FILE="${SCRIPT_DIR}/profiles.json"

if [[ ! -f "$PROFILES_FILE" ]]; then
    echo "Error: profiles.json not found at $PROFILES_FILE"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo ""
    echo "Install jq:"
    echo "  macOS:  brew install jq"
    echo "  Ubuntu: sudo apt install jq"
    echo "  Fedora: sudo dnf install jq"
    exit 1
fi

VERBOSE=false
if [[ "${1:-}" == "--verbose" ]] || [[ "${1:-}" == "-v" ]]; then
    VERBOSE=true
fi

echo "Available Transcoding Profiles"
echo "==============================="
echo ""

if [[ "$VERBOSE" == true ]]; then
    # Verbose output with full details
    jq -r '.profiles | to_entries[] | 
        "Profile: \(.value.name)\n" +
        "  Codec: \(.value.codec) (\(.value.codec_profile))\n" +
        "  Bitrate: \(.value.bitrate)\n" +
        "  Extension: \(.value.extension)\n" +
        "  Quality: \(.value.quality)/100\n" +
        "  Description: \(.value.description)\n" +
        "  Use Case: \(.value.use_case)\n" +
        "  Speed Estimate: \(.value.speed_estimate)\n" +
        "  Notes: \(.value.notes)\n"' "$PROFILES_FILE"
else
    # Concise table output - simple, no column command
    printf "%-28s %-12s %-8s %s\n" "Name" "Codec" "Ext" "Description"
    printf "%-28s %-12s %-8s %s\n" "----" "-----" "---" "-----------"
    jq -r '.profiles | to_entries[] | 
        "\(.value.name)|||\(.value.codec)|||\(.value.extension)|||\(.value.description[0:35])"' "$PROFILES_FILE" | \
    while IFS='|||' read -r name codec ext desc; do
        printf "%-28s %-12s %-8s %s\n" "$name" "$codec" "$ext" "$desc"
    done
fi

echo ""
echo "Speed Presets: fast | normal (default) | slow"
echo ""
echo "For Linux transcoding: see linux/QUICK_START.md"
echo "For macOS transcoding: see main README.md"
echo ""
