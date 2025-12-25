#!/bin/bash

# analyze.sh - Inspect video codec, resolution, fps, and audio specs
# Usage: ./analyze.sh <input_file> [--json]
# Works on: macOS (with ffmpeg), Linux, WSL2

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $(basename "$0") <input_file> [--json]"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") video.mov                    # Human-readable output"
    echo "  $(basename "$0") video.mov --json            # JSON output for parsing"
    exit 1
fi

INPUT_FILE="$1"
JSON_OUTPUT=false
if [[ "${2:-}" == "--json" ]]; then
    JSON_OUTPUT=true
fi

# Check if file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: File not found: $INPUT_FILE"
    exit 1
fi

# Check if ffprobe is available
if ! command -v ffprobe &> /dev/null; then
    echo "Error: ffprobe is required but not installed."
    echo ""
    echo "Install ffmpeg:"
    echo "  macOS:  brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo "  Fedora: sudo dnf install ffmpeg"
    exit 1
fi

if [[ "$JSON_OUTPUT" == true ]]; then
    # JSON output for parsing by other scripts
    ffprobe -v error -show_format -show_streams -print_json "$INPUT_FILE"
else
    # Human-readable output
    echo "Video Analysis: $(basename "$INPUT_FILE")"
    echo "="
    echo ""
    
    # General file info
    echo "File Information:"
    ffprobe -v error -show_format -print_json "$INPUT_FILE" | jq -r '
        "  Size: \(.format.size | tonumber / 1024 / 1024 | floor) MB" +
        "\n  Duration: \(.format.duration | tonumber | floor) seconds" +
        "\n  Bitrate: \(.format.bit_rate | tonumber / 1000 | floor) kbps" +
        "\n  Container: \(.format.format_name)"'
    echo ""
    
    # Video stream info
    echo "Video Stream:"
    ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,codec_profile,width,height,r_frame_rate,pix_fmt,bit_rate -print_json "$INPUT_FILE" | jq -r '
        .streams[0] | 
        "  Codec: \(.codec_name) (profile: \(.codec_profile))" +
        "\n  Resolution: \(.width)x\(.height)" +
        "\n  Frame Rate: \(.r_frame_rate)" +
        "\n  Pixel Format: \(.pix_fmt)" +
        "\n  Bitrate: \(.bit_rate | tonumber / 1000000 | ".\*" | split(".")[0]) Mbps"'
    echo ""
    
    # Audio stream info
    echo "Audio Stream(s):"
    ffprobe -v error -select_streams a -show_entries stream=index,codec_name,channels,sample_rate,bit_rate,language -print_json "$INPUT_FILE" | jq -r '
        if .streams | length == 0 then
            "  No audio stream found"
        else
            .streams[] | 
            "  Stream \(.index): \(.codec_name) | \(.channels)ch @ \(.sample_rate // "N/A")Hz | \(.bit_rate | tonumber / 1000 | ".\*" | split(".")[0]) kbps" +
            (if .language then " (\(.language))" else "" end)
        end'
    echo ""
    
    # Subtitle info
    echo "Subtitle Stream(s):"
    ffprobe -v error -select_streams s -show_entries stream=index,codec_name,language -print_json "$INPUT_FILE" | jq -r '
        if .streams | length == 0 then
            "  No subtitle stream found"
        else
            .streams[] | 
            "  Stream \(.index): \(.codec_name)" +
            (if .language then " (\(.language))" else "" end)
        end'
    echo ""
    echo "TIP: Use this data to choose an appropriate transcoding profile."
fi
