#!/bin/bash

# config.sh - Manage bvp-linux configuration (default profile, output directory)
# Usage: ./config.sh [show|set-profile <profile>|set-output-dir <dir>|reset]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.bvp-linux"
CONFIG_FILE="${CONFIG_DIR}/config.json"
PROFILES_FILE="${SCRIPT_DIR}/../profiles.json"

# Create config directory and default config if not exists
initialize_config() {
    if [[ ! -d "$CONFIG_DIR" ]]; then
        mkdir -p "$CONFIG_DIR"
    fi
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cat > "$CONFIG_FILE" << 'EOF'
{
  "default_profile": "standard-playback",
  "default_output_dir": "",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "notes": "Configuration for bvp-linux video transcoding tools"
}
EOF
        echo "Initialized config: $CONFIG_FILE"
    fi
}

# Show current configuration
show_config() {
    initialize_config
    
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required. Install with: apt install jq (Debian/Ubuntu)"
        exit 1
    fi
    
    echo "Bulletproof Linux Configuration"
    echo "="
    echo "Config File: $CONFIG_FILE"
    echo ""
    
    echo "Current Settings:"
    jq -r '
        "  Default Profile:     \(.default_profile)" +
        "\n  Default Output Dir:  \(.default_output_dir | if . == \"\" then \"(none - outputs to input dir)\" else . end)" +
        "\n  Last Modified:       \(.created_at)"' "$CONFIG_FILE"
    
    echo ""
    echo "Available Profiles (from profiles.json):"
    if [[ -f "$PROFILES_FILE" ]]; then
        jq -r '.profiles | keys[]' "$PROFILES_FILE" | sed 's/^/  - /'
    else
        echo "  (profiles.json not found)"
    fi
    
    echo ""
    echo "Usage:"
    echo "  $(basename "$0") set-profile <profile>      # Set default profile"
    echo "  $(basename "$0") set-output-dir <dir>      # Set default output directory"
    echo "  $(basename "$0") reset                     # Reset to defaults"
}

# Set default profile
set_profile() {
    local profile="$1"
    
    initialize_config
    
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required."
        exit 1
    fi
    
    # Validate profile exists
    if [[ -f "$PROFILES_FILE" ]]; then
        if ! jq -e ".profiles[\"$profile\"]" "$PROFILES_FILE" > /dev/null 2>&1; then
            echo "Error: Profile '$profile' not found in profiles.json"
            echo ""
            echo "Available profiles:"
            jq -r '.profiles | keys[]' "$PROFILES_FILE" | sed 's/^/  - /'
            exit 1
        fi
    fi
    
    # Update config
    jq ".default_profile = \"$profile\"" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
    mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    
    echo "✓ Default profile set to: $profile"
    echo ""
    echo "Next time you run transcode.sh, you can omit --profile:"
    echo "  transcode.sh video.mov  # Will use $profile"
}

# Set default output directory
set_output_dir() {
    local output_dir="$1"
    
    # Expand ~ to home directory
    output_dir="${output_dir/\~/$HOME}"
    
    # Resolve to absolute path
    output_dir="$(cd "$output_dir" 2>/dev/null && pwd)" || {
        echo "Error: Output directory does not exist or is not accessible: $1"
        exit 1
    }
    
    initialize_config
    
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required."
        exit 1
    fi
    
    # Update config
    jq ".default_output_dir = \"$output_dir\"" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
    mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    
    echo "✓ Default output directory set to: $output_dir"
    echo ""
    echo "Next time you run transcode.sh, output will go to:"
    echo "  $output_dir/video__processed__profile.mp4"
}

# Reset configuration to defaults
reset_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        rm -f "$CONFIG_FILE"
        echo "Configuration reset. Removed: $CONFIG_FILE"
    fi
    
    initialize_config
    echo "Configuration re-initialized to defaults."
}

# Display help
show_help() {
    cat << EOF
Usage: $(basename "$0") [COMMAND]

Commands:
  show                           Display current configuration and available profiles
  set-profile <profile>          Set default transcoding profile
  set-output-dir <directory>     Set default output directory for transcoded files
  reset                          Reset configuration to defaults
  help                           Show this help message

Examples:
  $(basename "$0") show
  $(basename "$0") set-profile live-h264-linux
  $(basename "$0") set-output-dir ~/Videos/processed
  $(basename "$0") reset

Configuration File:
  $CONFIG_FILE

EOF
}

# Main
case "${1:-show}" in
    show)
        show_config
        ;;
    set-profile)
        if [[ -z "${2:-}" ]]; then
            echo "Error: Profile name required."
            echo "Usage: $(basename "$0") set-profile <profile>"
            exit 1
        fi
        set_profile "$2"
        ;;
    set-output-dir)
        if [[ -z "${2:-}" ]]; then
            echo "Error: Output directory required."
            echo "Usage: $(basename "$0") set-output-dir <directory>"
            exit 1
        fi
        set_output_dir "$2"
        ;;
    reset)
        reset_config
        ;;
    help)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        show_help
        exit 1
        ;;
esac
