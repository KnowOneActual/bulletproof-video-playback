#!/bin/bash

# install.sh - Setup bulletproof-linux transcoding tools
# This script checks dependencies, makes scripts executable, and creates config directory

set -euo pipefail

echo "Bulletproof Video Playback - Linux Installation"
echo "="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [[ ! -f "profiles.json" ]]; then
    echo -e "${RED}Error: profiles.json not found.${NC}"
    echo "Run this script from the linux/ directory of the bulletproof-video-playback repository."
    exit 1
fi

if [[ ! -d "scripts" ]]; then
    echo -e "${RED}Error: scripts/ directory not found.${NC}"
    echo "Run this script from the linux/ directory of the bulletproof-video-playback repository."
    exit 1
fi

echo "Checking prerequisites..."
echo ""

# Check for required commands
MISSING_DEPS=()

if ! command -v bash &> /dev/null; then
    MISSING_DEPS+=("bash")
else
    echo -e "${GREEN}✓${NC} bash found"
fi

if ! command -v ffmpeg &> /dev/null; then
    MISSING_DEPS+=("ffmpeg")
else
    echo -e "${GREEN}✓${NC} ffmpeg found ($(ffmpeg -version | head -1 | cut -d' ' -f1-3))"
fi

if ! command -v ffprobe &> /dev/null; then
    MISSING_DEPS+=("ffprobe")
else
    echo -e "${GREEN}✓${NC} ffprobe found"
fi

if ! command -v jq &> /dev/null; then
    MISSING_DEPS+=("jq")
else
    echo -e "${GREEN}✓${NC} jq found ($(jq --version))"
fi

echo ""

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo -e "${RED}Missing dependencies:${NC}"
    printf '  - %s\n' "${MISSING_DEPS[@]}"
    echo ""
    echo "Install missing packages:"
    
    if command -v apt &> /dev/null; then
        echo -e "  ${YELLOW}Debian/Ubuntu:${NC}"
        echo "    sudo apt update && sudo apt install -y ffmpeg jq"
    elif command -v dnf &> /dev/null; then
        echo -e "  ${YELLOW}Fedora/RHEL/CentOS:${NC}"
        echo "    sudo dnf install -y ffmpeg jq"
    elif command -v apk &> /dev/null; then
        echo -e "  ${YELLOW}Alpine:${NC}"
        echo "    apk add --no-cache ffmpeg jq"
    fi
    
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
else
    echo -e "${GREEN}All prerequisites found!${NC}"
    echo ""
fi

# Make scripts executable
echo "Making scripts executable..."
for script in scripts/*.sh; do
    chmod +x "$script"
    echo "  + $(basename "$script")"
done
echo ""

# Create symlinks for universal tools in linux/scripts/
echo "Setting up universal tool symlinks..."
ROOT_DIR="$(cd .. && pwd)"
UNIVERSAL_TOOLS=("analyze.sh" "list-profiles.sh")

for tool in "${UNIVERSAL_TOOLS[@]}"; do
    TARGET_FILE="scripts/${tool}"
    SOURCE_FILE="${ROOT_DIR}/scripts/${tool}"
    
    if [[ -f "$SOURCE_FILE" ]]; then
        # Remove existing file or symlink if it exists
        if [[ -e "$TARGET_FILE" ]]; then
            rm -f "$TARGET_FILE"
        fi
        # Create relative symlink to root scripts/
        ln -s "$SOURCE_FILE" "$TARGET_FILE"
        echo "  + Symlinked $tool from ../scripts/"
    else
        echo -e "  ${YELLOW}⚠${NC} Source not found: $SOURCE_FILE"
    fi
done

# Symlink profiles.json from root scripts/
SOURCE_PROFILES="${ROOT_DIR}/scripts/profiles.json"
TARGET_PROFILES="profiles.json"
if [[ -f "$SOURCE_PROFILES" ]]; then
    if [[ -e "$TARGET_PROFILES" ]]; then
        rm -f "$TARGET_PROFILES"
    fi
    ln -s "$SOURCE_PROFILES" "$TARGET_PROFILES"
    echo "  + Symlinked profiles.json from ../scripts/"
else
    echo -e "  ${YELLOW}⚠${NC} Source not found: $SOURCE_PROFILES"
fi
echo ""

# Create config directory
CONFIG_DIR="${HOME}/.bulletproof-linux"
echo "Setting up configuration..."
if [[ ! -d "$CONFIG_DIR" ]]; then
    mkdir -p "$CONFIG_DIR"
    echo "  + Created $CONFIG_DIR"
else
    echo "  + Config directory already exists at $CONFIG_DIR"
fi

# Copy profiles.json to config directory (symlink is better for updates)
if [[ ! -f "${CONFIG_DIR}/profiles.json" ]]; then
    ln -s "$(pwd)/profiles.json" "${CONFIG_DIR}/profiles.json"
    echo "  + Symlinked profiles.json to $CONFIG_DIR"
else
    echo "  + profiles.json already exists in $CONFIG_DIR"
fi

echo ""

# Offer to add scripts to PATH
echo "Installation options:"
echo ""
echo "Option 1: Add scripts to ~/.local/bin (add to PATH)"
echo "  chmod +x ~/.local/bin/transcode.sh"
echo "  ln -s $(pwd)/scripts/*.sh ~/.local/bin/"
echo ""
echo "Option 2: Use scripts from current directory"
echo "  cd $(pwd)/scripts"
echo "  ./transcode.sh --help"
echo ""
echo "Option 3: Add to PATH in ~/.bashrc"
echo "  echo 'export PATH=\"$(pwd)/scripts:\$PATH\"' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""

echo "Next steps:"
echo ""
echo "1. View available profiles:"
echo "   ./scripts/list-profiles.sh"
echo ""
echo "2. Analyze a video file:"
echo "   ./scripts/analyze.sh /path/to/video.mov"
echo ""
echo "3. Transcode a single file:"
echo "   ./scripts/transcode.sh /path/to/video.mov --profile live-h264-linux"
echo ""
echo "4. Read full documentation:"
echo "   cat README.md"
echo ""

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Configuration saved to: $CONFIG_DIR"
echo "Config file: ${CONFIG_DIR}/config.json"
echo ""
echo "Note: Universal tools (analyze.sh, list-profiles.sh) are symlinked from ../scripts/"
echo "      This allows cross-platform access and single-source maintenance."
echo ""
