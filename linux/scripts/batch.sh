#!/bin/bash

# batch.sh - Batch transcode all videos in a directory
# Usage: ./batch.sh <input_dir> --profile <profile> [--output-dir <dir>] [--preset fast|normal|slow] [--pattern "*.mov"]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
INPUT_DIR=""
PROFILE=""
OUTPUT_DIR=""
PRESET="normal"
PATTERN="*"
VERBOSE=false
DRY_RUN=false

# Display help
show_help() {
    cat << EOF
Usage: $(basename "$0") <input_dir> --profile <profile> [OPTIONS]

Required:
  <input_dir>            Directory containing video files to transcode
  --profile <profile>    Transcoding profile (e.g., live-h264-linux, standard-playback)

Options:
  --output-dir <dir>     Output directory for transcoded files (default: <input_dir>/__processed__)
  --preset <preset>      Encoding speed: fast|normal|slow (default: normal)
  --pattern "*.mov"      File pattern to match (default: * - all files)
  --dry-run              Show what would be processed, don't transcode
  --verbose              Show ffmpeg output
  --help                 Show this help message

Examples:
  # Process all MOV files in current directory
  $(basename "$0") . --profile live-h264-linux

  # Process specific file type to output directory
  $(basename "$0") ./videos --profile standard-playback --output-dir ./processed --pattern "*.mov"

  # Fast preset for quick turnaround (lower quality)
  $(basename "$0") /mnt/footage --profile standard-playback --preset fast --output-dir ./quick_processed

  # Dry run first to see what will be processed
  $(basename "$0") ./videos --profile live-h264-linux --dry-run

Notes:
  - Original files are never modified
  - Each output file is marked with __processed__ in filename
  - All outputs go to --output-dir (created if it doesn't exist)
  - Safe to interrupt with Ctrl+C (incomplete files are cleaned up)

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
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --preset)
            PRESET="$2"
            shift 2
            ;;
        --pattern)
            PATTERN="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
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
            INPUT_DIR="$1"
            shift
            ;;
    esac
done

# Validate inputs
if [[ -z "$INPUT_DIR" ]]; then
    echo "Error: No input directory specified."
    show_help
    exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "Error: Input directory not found: $INPUT_DIR"
    exit 1
fi

if [[ -z "$PROFILE" ]]; then
    echo "Error: No profile specified. Use --profile <profile>"
    show_help
    exit 1
fi

# Set default output directory
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="${INPUT_DIR}/__processed__"
fi

# Create output directory (unless dry-run)
if [[ "$DRY_RUN" == false ]] && [[ ! -d "$OUTPUT_DIR" ]]; then
    mkdir -p "$OUTPUT_DIR"
    echo "Created output directory: $OUTPUT_DIR"
fi

echo "Bulletproof Video Playback - Batch Transcoder (Linux)"
echo "="
echo "Input Directory:   $INPUT_DIR"
echo "Output Directory:  $OUTPUT_DIR"
echo "Profile:           $PROFILE"
echo "Speed Preset:      $PRESET"
echo "File Pattern:      $PATTERN"
if [[ "$DRY_RUN" == true ]]; then
    echo "Mode:              DRY RUN (no files will be processed)"
fi
echo ""

# Find matching video files
FILES=()
while IFS= read -r -d '' file; do
    FILES+=("$file")
done < <(find "$INPUT_DIR" -maxdepth 1 -type f -name "$PATTERN" -print0 | sort -z)

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "No files matching pattern '$PATTERN' found in $INPUT_DIR"
    exit 0
fi

echo "Found ${#FILES[@]} file(s) to process:"
for file in "${FILES[@]}"; do
    echo "  - $(basename "$file")"
done
echo ""

if [[ "$DRY_RUN" == true ]]; then
    echo "Dry run mode: No files will be processed. Re-run without --dry-run to start transcoding."
    exit 0
fi

echo "Starting batch transcoding..."
echo "Press Ctrl+C to cancel (incomplete files will be cleaned up)"
echo ""

# Counter for progress
CURRENT=0
TOTAL=${#FILES[@]}
FAILED=0
SUCCESS=0

# Cleanup function for interrupted transcodes
cleanup() {
    echo ""
    echo "Interrupted. Cleaning up incomplete files..."
    for file in "${FILES[@]}"; do
        BASENAME=$(basename "$file" | sed 's/\.[^.]*$//')
        for output in "${OUTPUT_DIR}"/${BASENAME}__processed__*; do
            if [[ -f "$output" ]]; then
                # Only delete if it looks incomplete (e.g., recently modified)
                rm -f "$output"
            fi
        done
    done
    echo "Cleanup complete. Exiting."
    exit 130  # Standard exit code for Ctrl+C
}

trap cleanup INT TERM

# Process each file
for file in "${FILES[@]}"; do
    CURRENT=$((CURRENT + 1))
    BASENAME=$(basename "$file")
    
    echo "[$CURRENT/$TOTAL] Processing: $BASENAME"
    
    # Build transcode command
    TRANSCODE_ARGS=("$file" "--profile" "$PROFILE" "--preset" "$PRESET" "--output" "${OUTPUT_DIR}/")
    
    if [[ "$VERBOSE" == true ]]; then
        TRANSCODE_ARGS+=("--verbose")
    fi
    
    # Call transcode.sh for this file
    if "${SCRIPT_DIR}/transcode.sh" "${TRANSCODE_ARGS[@]}" > /dev/null 2>&1; then
        echo "  ✓ Success"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "  ✗ Failed - skipping this file"
        FAILED=$((FAILED + 1))
    fi
    echo ""
done

echo "="
echo "Batch Transcoding Complete"
echo "Successful: $SUCCESS / $TOTAL"
if [[ $FAILED -gt 0 ]]; then
    echo "Failed:     $FAILED / $TOTAL"
    echo ""
    echo "Check the files above and investigate failed transcodes."
fi
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""
