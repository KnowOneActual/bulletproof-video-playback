# bulletproof-video-playback

[![Tests](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml/badge.svg)](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Professional video transcoding for live playback, streaming, and archival. Uses ffmpeg under the hood with seven prebuilt profiles optimized for different use cases.

## Choose Your Platform

### 🍎 **macOS / Python Version** (Recommended for interactive use)

- **TUI (Terminal UI)** with smart defaults
- **ProRes support** (native to macOS)
- **Real-time progress tracking**
- **Python API** for integration
- Requires: Python 3.9+

👉 See **Installation** section below

### 🐧 **Linux / Pure Bash Version** (No Python required)

- **Zero dependencies** beyond ffmpeg (no Python needed)
- **Works on machines you don't own** (restricted environments)
- **Cross-platform profiles** (H.264, H.265, FFv1, ProRes if available)
- **Simple JSON-based configuration**
- Requires: bash, ffmpeg, jq (lightweight)

👉 See [`linux/QUICK_START.md`](./linux/QUICK_START.md) for Linux setup

---

## Features

✅ **Real-Time Progress Tracking** - See live progress bar during transcoding (no more wondering if it's stuck!)  
✅ **7 Transcoding Profiles** - Prebuilt profiles for live playback (ProRes/H.264), streaming (H.265), and archival  
✅ **Three Interfaces** - CLI, TUI (interactive with smart defaults), and Python API  
✅ **Smart Output Naming** - Auto-correct file extensions based on profile, includes `__processed__` marker  
✅ **Safety Features** - Prevents accidental overwrite of input files, auto-cleans incomplete files on cancel  
✅ **Video Analysis** - Inspect video codec, resolution, fps, audio specs  
✅ **Professional Codecs** - ProRes Proxy/LT/HQ, H.264, H.265, FFv1  
✅ **Speed Presets** - `--preset fast|normal|slow` for quality vs encode time tradeoff  
✅ **Config Support** - Save default profiles and output folders  
✅ **CI/CD Ready** - GitHub Actions workflows for testing and releases  

---

## Installation

### Requirements
- Python 3.9+ (macOS/Python version)
- ffmpeg (`brew install ffmpeg` on macOS, `apt install ffmpeg` on Linux)
- ffprobe (usually included with ffmpeg)

### From PyPI

```bash
pip install bulletproof-video-playback
```

### From GitHub (Development)

```bash
git clone https://github.com/KnowOneActual/bulletproof-video-playback
cd bulletproof-video-playback
pip install -e ".[dev]"
```

### Linux (Pure Bash, No Python)

If you don't have Python or can't install it:

```bash
git clone https://github.com/KnowOneActual/bulletproof-video-playback
cd bulletproof-video-playback/linux
bash install.sh
```

See [`linux/QUICK_START.md`](./linux/QUICK_START.md) for full Linux instructions.

---

## Quick Start

### TUI (Interactive Mode - Recommended)

Best for beginners and one-off transcodes:

```bash
bulletproof tui
```

Will prompt you for:
1. Input video file
2. Transcoding profile (shows descriptions)
3. Output location (defaults to `input__processed__profile.mp4`)
4. Speed preset if needed (fast/normal/slow)
5. Shows real-time progress bar during transcode
6. Auto-cleans up if you press Ctrl+C

### CLI Usage

For scripting and automation:

```bash
# List available profiles
bulletproof transcode --list-profiles

# Transcode single file with profile
bulletproof transcode input.mov --profile live-qlab --output output.mov

# Transcode with speed preset (for live playback deadlines)
bulletproof transcode input.mov --profile live-qlab --preset fast

# Analyze video specs before transcoding
bulletproof analyze input.mov

# Batch process directory
bulletproof batch ./videos --profile standard-playback --output-dir ./output
```

### Config Management

```bash
# Set your default profile (saved to ~/.bulletproof/config.json)
bulletproof config set-default-profile live-qlab

# Set your default output folder
bulletproof config set-output-dir ~/Videos/processed

# View current config
bulletproof config show
```

### Linux Bash Version

If you installed the Linux version:

```bash
cd linux/scripts

# List profiles
./list-profiles.sh

# Analyze a video
./analyze.sh video.mov

# Transcode with a profile
./transcode.sh video.mov --profile live-h264-linux --preset fast

# Batch process
./batch.sh ./videos --profile standard-playback
```

### Python API

For integration into other projects:

```python
from bulletproof.core import TranscodeJob, list_profiles
from pathlib import Path

# Get a profile
profile = list_profiles()["live-qlab"]

# Create and execute a job
job = TranscodeJob(
    input_file=Path("input.mov"),
    output_file=Path("output.mov"),
    profile=profile,
    speed_preset="normal"  # fast, normal, or slow
)

if job.execute():
    print(f"Success! Output: {job.output_file}")
    print(f"Progress was: {job.progress}%")
else:
    print(f"Failed: {job.error_message}")
```

---

## Profiles

| Name | Codec | Extension | Quality | Use Case | Speed |
|------|-------|-----------|---------|----------|-------|
| **live-qlab** | ProRes Proxy | .mov | Good | QLab on Mac (recommended) | Medium |
| live-prores-lt | ProRes LT | .mov | High | Live playback (smaller) | Medium |
| live-h264 | H.264 | .mp4 | High | Cross-platform live | Slow |
| standard-playback | H.264 | .mp4 | Good | Miccia Player, VLC | Medium |
| stream-hd | H.265 | .mp4 | Good | 1080p streaming | Medium |
| stream-4k | H.265 | .mp4 | Good | 4K streaming | Medium |
| archival | ProRes HQ | .mov | Max | Long-term storage | Slow |

**Linux-specific profiles** (see `linux/QUICK_START.md`):
- `live-h264-linux` — H.264 for cross-platform playback
- `standard-playback` — General-purpose H.264
- `stream-hd` / `stream-4k` — H.265/HEVC streaming
- `archival-lossless` — FFv1 lossless for preservation
- `web-compat` — H.264 Baseline for maximum compatibility

---

## Speed Presets

Control encode time vs quality:

```bash
# For time-sensitive live playback (encode faster, slight quality loss)
bulletproof transcode input.mov --profile live-qlab --preset fast
# ~3 hours for 2-hour video

# Balanced (default)
bulletproof transcode input.mov --profile live-qlab --preset normal
# ~4-5 hours for 2-hour video

# Maximum quality (encode slower)
bulletproof transcode input.mov --profile live-qlab --preset slow
# ~6-8 hours for 2-hour video
```

## Output Naming

The TUI automatically generates helpful output filenames:

```
Input:   spider_reveal_v1.mov
Profile: live-qlab
Output:  spider_reveal_v1__processed__live-qlab.mov
```

The `__processed__` marker makes it easy to distinguish original vs transcoded files in your folder.

## Progress Tracking

During transcoding, you'll see a real-time progress bar:

```
Transcoding: SF90_Spider_Reveal(1).mov
Duration: 2.2 minutes

Progress: |████████████░░░░░░░░░░░░░░░░░░░░| 35.2% (42/120s)
```

**Pro Tip:** If no progress bar appears, the video might lack duration metadata. The transcode is still running! This is common with some MOV files.

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=bulletproof tests/

# Format code
black bulletproof tests
```

## Development

### Adding a New Profile

Edit `bulletproof/core/profile.py` and add to `BUILT_IN_PROFILES`:

```python
BUILT_IN_PROFILES["my-profile"] = TranscodeProfile(
    name="my-profile",
    codec="h265",
    preset="medium",
    quality=85,
    max_bitrate="10M",
    description="Description for TUI",
    extension="mp4"
)
```

### Adding a New Command

Create `bulletproof/cli/commands/my_command.py`:

```python
import click

@click.command()
@click.argument("input_file")
def my_command(input_file):
    """Description of my command."""
    # Implementation
    pass
```

Then register in `bulletproof/cli/main.py` and `bulletproof/cli/commands/__init__.py`.

## Releases

To release a new version:

```bash
# Tag a release
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will:
# 1. Run tests
# 2. Build package
# 3. Create GitHub release
# 4. Upload to PyPI (requires PYPI_API_TOKEN secret)
```

## Architecture

```
bulletproof/
├── core/              # Transcode logic
│   ├── profile.py     # Profile definitions & codec mapping
│   └── job.py         # Transcode execution with progress tracking
├── cli/               # Command-line interface
│   ├── main.py        # CLI entry point
│   └── commands/      # Subcommands (transcode, analyze, batch, config, tui)
├── config/            # Configuration management
│   └── manager.py     # Config file handling
├── tui/               # Terminal UI with smart defaults
└── utils/             # Utilities (validation, etc)

linux/                # Pure Bash implementation (no Python)
├── scripts/           # Bash scripts (transcode, batch, analyze, config, list-profiles)
├── profiles.json      # Profile catalog (shared with root scripts/)
└── install.sh         # Setup script

scripts/              # Universal tools (work on any OS with ffmpeg + jq)
├── analyze.sh         # Video analysis
├── list-profiles.sh   # Profile browser
└── profiles.json      # Profile catalog

tests/                # Test suite
.github/workflows/    # CI/CD (test.yml, release.yml)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ffmpeg not found" | Install ffmpeg: `brew install ffmpeg` or `apt install ffmpeg` |
| No progress bar | Video lacks duration metadata. Transcode is still running. Use Ctrl+C to cancel. |
| Transcode takes 20+ minutes | This is normal for large files or complex codecs. Progress bar shows speed. |
| Want to cancel? | Press Ctrl+C - incomplete file is auto-deleted |
| Import errors | Ensure venv is active and you ran `pip install -e ".[dev]"` |
| Linux issues | See [`linux/QUICK_START.md`](./linux/QUICK_START.md) for troubleshooting |

## License

MIT License - see LICENSE file

## Author

Beau Bremer ([@KnowOneActual](https://github.com/KnowOneActual))

## Philosophy

> "What does this system need?" → Use that codec

Instead of debating codecs, bulletproof asks the question:
- Are you QLab on macOS for live playback? → Use ProRes Proxy
- Are you streaming? → Use H.265
- Are you long-term storage? → Use ProRes HQ
- On Linux without Python? → Use H.264/H.265 with pure Bash

Each profile is a prepackaged answer to that question.

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass and code is formatted with `black`
5. Submit a pull request

---

**Latest Update:** December 2025 — Added Linux Bash port for systems without Python  
**Current Version:** 0.1.0+linux
