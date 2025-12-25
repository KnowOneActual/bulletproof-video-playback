#!/bin/bash

# transcode.sh - Transcode single video file with chosen profile and speed preset
# Usage: ./transcode.sh <input_file> --profile <profile> [--output <output_file>] [--preset fast|normal|slow]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILES_FILE="${SCRIPT_DIR}/../profiles.json"

# Default values
INPUT_FILE=""
PROFILE=""
OUTPUT_FILE=""
PRESET="normal"
VERBOSE=false
OVERWRITE=false

# Display help
show_help() {
    cat << EOF
Usage: $(basename "$0") <input_file> --profile <profile> [OPTIONS]

Required:
  <input_file>           Input video file to transcode
  --profile <profile>    Transcoding profile (e.g., live-h264-linux, standard-playback)

Options:
  --output <file>        Output filename (default: input__processed__profile.ext)
  --preset <preset>      Encoding speed: fast|normal|slow (default: normal)
  --overwrite            Overwrite output file if it exists (default: refuse)
  --verbose              Show ffmpeg output and command details
  --help                 Show this help message

Examples:
  # List available profiles
  $(dirname "$0")/list-profiles.sh

  # Transcode with live-h264-linux profile, fast preset
  $(basename "$0") video.mov --profile live-h264-linux --preset fast

  # Transcode to specific output file
  $(basename "$0") video.mov --profile standard-playback --output output.mp4

  # Analyze before transcoding
  $(dirname "$0")/analyze.sh video.mov

Speed Presets:
  fast    - Faster encoding (3-4 hrs for 2hr video), slightly lower quality
  normal  - Balanced (4-6 hrs for 2hr video), default
  slow    - Slower encoding (6-10 hrs for 2hr video), better quality

Note: If output file is not specified, it will be named as:
  <basename>__processed__<profile>.<extension>

Example: spider_reveal.mov + live-h264-linux = spider_reveal__processed__live-h264-linux.mp4

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --preset)
            PRESET="$2"
            shift 2
            ;;
        --overwrite)
            OVERWRITE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            echo "Error: Unknown option $1"
            show_help
            exit 1
            ;;
        *)
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

# Validate inputs
if [[ -z "$INPUT_FILE" ]]; then
    echo "Error: No input file specified."
    show_help
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

if [[ -z "$PROFILE" ]]; then
    echo "Error: No profile specified. Use --profile <profile>"
    show_help
    exit 1
fi

if [[ ! -f "$PROFILES_FILE" ]]; then
    echo "Error: profiles.json not found at $PROFILES_FILE"
    exit 1
fi

# Check dependencies
for cmd in ffmpeg ffprobe jq; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is required but not installed."
        exit 1
    fi
done

# Load profile from JSON
if ! PROFILE_DATA=$(jq -r ".profiles[\"$PROFILE\"]" "$PROFILES_FILE" 2>/dev/null); then
    echo "Error: Could not read profiles.json"
    exit 1
fi

if [[ "$PROFILE_DATA" == "null" ]]; then
    echo "Error: Profile '$PROFILE' not found in profiles.json"
    echo "Available profiles:"
    jq -r '.profiles | keys[]' "$PROFILES_FILE"
    exit 1
fi

# Extract profile values
CODEC=$(echo "$PROFILE_DATA" | jq -r '.codec')
CODEC_PROFILE=$(echo "$PROFILE_DATA" | jq -r '.codec_profile')
BITRATE=$(echo "$PROFILE_DATA" | jq -r '.bitrate')
EXTENSION=$(echo "$PROFILE_DATA" | jq -r '.extension')
FFMPEG_PRESET=$(echo "$PROFILE_DATA" | jq -r '.preset')

# Override preset from CLI if provided
if [[ "$PRESET" != "normal" ]]; then
    case "$PRESET" in
        fast)
            FFMPEG_PRESET="veryfast"
            ;;
        normal)
            FFMPEG_PRESET="medium"
            ;;
        slow)
            FFMPEG_PRESET="slow"
            ;;
        *)
            echo "Error: Invalid preset '$PRESET'. Use fast|normal|slow"
            exit 1
            ;;
    esac
fi

# Generate output filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
    BASENAME=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')
    OUTPUT_FILE="${BASENAME}__processed__${PROFILE}.${EXTENSION}"
fi

# Safety check: refuse to overwrite unless --overwrite is set
if [[ -f "$OUTPUT_FILE" ]] && [[ "$OVERWRITE" == false ]]; then
    echo "Error: Output file already exists: $OUTPUT_FILE"
    echo "Use --overwrite to replace it, or specify a different --output filename."
    exit 1
fi

# Safety check: prevent overwriting input file
if [[ "$(realpath "$OUTPUT_FILE")" == "$(realpath "$INPUT_FILE")" ]]; then
    echo "Error: Output file must be different from input file."
    exit 1
fi

# Display transcode information
echo "Bulletproof Video Playback - Linux Transcoder"
echo "="
echo "Profile:       $PROFILE"
echo "Input:         $INPUT_FILE"
echo "Output:        $OUTPUT_FILE"
echo "Codec:         $CODEC (profile: $CODEC_PROFILE)"
echo "Bitrate:       $BITRATE"
echo "Speed Preset:  $PRESET (ffmpeg: $FFMPEG_PRESET)"
echo ""
echo "Processing..."
echo ""

# Build ffmpeg command based on codec
case "$CODEC" in
    h264)
        FFMPEG_ARGS=(
            "-c:v" "libx264"
            "-preset" "$FFMPEG_PRESET"
            "-profile:v" "$CODEC_PROFILE"
            "-b:v" "$BITRATE"
            "-c:a" "aac"
            "-b:a" "192k"
        )
        ;;
    hevc)
        FFMPEG_ARGS=(
            "-c:v" "libx265"
            "-preset" "$FFMPEG_PRESET"
            "-profile:v" "$CODEC_PROFILE"
            "-b:v" "$BITRATE"
            "-c:a" "aac"
            "-b:a" "192k"
        )
        ;;
    ffv1)
        FFMPEG_ARGS=(
            "-c:v" "ffv1"
            "-level" "3"
            "-c:a" "flac"
        )
        ;;
    prores)
        FFMPEG_ARGS=(
            "-c:v" "prores_hq"
            "-profile:v" "$CODEC_PROFILE"
            "-c:a" "pcm_s16le"
        )
        ;;
    *)
        echo "Error: Codec '$CODEC' not yet implemented. Edit transcode.sh to add support."
        exit 1
        ;;
esac

# Run ffmpeg with optional verbose output
if [[ "$VERBOSE" == true ]]; then
    echo "Running: ffmpeg -i \"$INPUT_FILE\" ${FFMPEG_ARGS[@]} \"$OUTPUT_FILE\""
    echo ""
    ffmpeg -i "$INPUT_FILE" "${FFMPEG_ARGS[@]}" "$OUTPUT_FILE"
else
    # Suppress ffmpeg output, show only progress
    ffmpeg -i "$INPUT_FILE" "${FFMPEG_ARGS[@]}" -progress pipe:1 "$OUTPUT_FILE" 2>&1 | \
        grep -E "^(frame|time|bitrate|speed)=" || true
fi

# Check if transcode was successful
if [[ -f "$OUTPUT_FILE" ]]; then
    OUTPUT_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo "✓ Transcode complete!"
    echo "  Output: $OUTPUT_FILE ($OUTPUT_SIZE)"
    echo ""
    echo "Next steps:"
    echo "  1. Test playback on your target device"
    echo "  2. Keep original file for archival"
    echo "  3. Delete if satisfied (output marked with __processed__ for easy identification)"
else
    echo "✗ Transcode failed. No output file created."
    exit 1
fi
