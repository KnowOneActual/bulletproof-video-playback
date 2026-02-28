# bulletproof-video-playback

[![Tests](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml/badge.svg)](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.5.0-green.svg)](https://github.com/KnowOneActual/bulletproof-video-playback/releases)

Video transcoding for live playback, streaming, and archival. Uses ffmpeg under the hood with nine prebuilt profiles optimized for different use cases.

**NEW v2.5.0:** **Professional Keyframe Control** - Customize GOP (Group of Pictures) intervals for frame-accurate seeking in QLab, video editors, and streaming workflows.

**NEW:** **MKV Profiles for Linux** - H.265 MKV profiles optimized for Linux live event workflows with mpv and Linux Show Player. ProRes 422 replacement with 10-bit color depth support.

**NEW:** **Folder Monitoring** - Automatically transcode videos based on filename patterns. Drop videos into a folder, and they'll auto-process. Perfect for live events, streaming, broadcast, and batch workflows.

**COMING SOON:** **Web Dashboard** - Phase 3.1 in progress! Real-time monitoring via REST API + WebSocket. See [ROADMAP.md](./docs/ROADMAP.md) for details.

## 🚀 What You Get

### Three Ways to Use

1. **CLI (Command Line)** - Fast, scriptable, automation-ready ⚡
2. **Folder Monitor** - Watch directories, auto-transcode with rules 🔄
3. **REST API** (NEW!) - Remote monitoring and control via web dashboard 🌐

> **Note:** This project has shifted focus away from the Terminal UI (TUI) to concentrate on more practical automation tools (Folder Monitor) and modern web-based interfaces (Web Dashboard). The legacy TUI code remains in the codebase but is no longer actively developed.

### Platforms

- **macOS** (Python) - Native ProRes support, recommended for ProRes workflows
- **Linux** (Pure Bash + Python) - H.265 MKV profiles for live events, zero Python dependencies available
- **Windows/WSL** - CLI and Monitor work everywhere Python runs

---

## 🎯 Perfect for AV Techs

### Professional Keyframe Control (NEW in v2.5.0)

All profiles support customizable **keyframe intervals** for professional GOP management:
- **Frame-accurate seeking** - Jump to exact frames in QLab, Premiere, DaVinci
- **Streaming optimization** - 2-second GOP for HLS/DASH responsive seeking
- **Live event prep** - 5-second GOP for quick scrubbing during show setup
- **Broadcast compliance** - Match network requirements for frame-accurate edits

**Examples:**
```bash
# QLab live playback (5-second keyframes)
bvp transcode input.mov --profile live-qlab

# Linux live events with mpv (5-second keyframes)
bvp transcode input.mov --profile live-linux-hevc-mkv

# Streaming (2-second keyframes for web players)
bvp transcode input.mov --profile stream-hd

# Custom keyframe interval (every 3 seconds)
bvp transcode input.mov --profile standard-playback --keyframe-interval 3.0
```

👉 **Full guide:** [docs/features/KEYFRAME_FEATURE.md](./docs/features/KEYFRAME_FEATURE.md)

---

## Quick Start: Folder Monitor

Watch a folder for videos and automatically transcode them:

```bash
# Generate config
bvp monitor generate-config --output monitor.yaml --watch /incoming

# Start monitoring
bvp monitor start --config monitor.yaml

# Drop videos in /incoming
# They auto-transcode to /output based on your rules!
```

**Use cases:**
- 📺 Live broadcasting prep
- 🎬 Streaming services
- 📦 Archive preparation
- 🎞️ Post-production dailies
- 📢 Content distribution
- ✅ Quality control
- 🔄 Batch processing

---

## Choose Your Platform

### 🍎 **macOS / Python Version** (Recommended)

- **CLI** - Fast, scriptable command-line interface
- **ProRes support** (native to macOS)
- **Keyframe control** (NEW v2.5.0)
- **Real-time progress tracking**
- **Python API** for integration
- **Folder Monitor** with async processing
- **REST API** for remote monitoring (NEW!)
- Requires: Python 3.9+

👉 See **Installation** section below

### 🐧 **Linux / Python + MKV Profiles**

- **H.265 MKV profiles** optimized for mpv and Linux Show Player
- **ProRes 422 replacement** with 10-bit color depth (visually lossless)
- **GPU hardware acceleration** support (VA-API/VDPAU/NVDEC)
- **MKV container** for better seeking reliability in live cue systems
- **5-second keyframes** for instant scrubbing in live event playback
- Requires: Python 3.9+, ffmpeg

### 🐧 **Linux / Pure Bash Version** (No Python required)

- **Zero dependencies** beyond ffmpeg (no Python needed)
- **Works on machines you don't own** (restricted environments)
- **Cross-platform profiles** (H.264, H.265, FFv1, ProRes if available)
- **Simple JSON-based configuration**
- Requires: bash, ffmpeg, jq (lightweight)

👉 See [`linux/QUICK_START.md`](./linux/QUICK_START.md) for Linux setup

---

## Features

✅ **REST API for Remote Monitoring** - WebSocket + FastAPI (NEW Phase 3.1!)  
✅ **MKV Profiles for Linux** - H.265 MKV for live events (NEW!)  
✅ **Keyframe Interval Control** - Professional GOP management (NEW v2.5.0!)  
✅ **Folder Monitoring** - Watch directories, auto-transcode based on patterns  
✅ **Crash Recovery** - Queue persists to JSON, survives restarts  
✅ **Real-Time Progress Tracking** - See live progress bar during transcoding  
✅ **9 Transcoding Profiles** - Prebuilt profiles for live playback, streaming, and archival  
✅ **CLI + Folder Monitor** - Command-line and automation interfaces  
✅ **Smart Output Naming** - Auto-correct extensions, includes processing marker  
✅ **Safety Features** - Prevents overwrites, auto-cleans incomplete files  
✅ **Video Analysis** - Inspect codec, resolution, fps, audio specs  
✅ **Professional Codecs** - ProRes Proxy/LT/HQ, H.264, H.265 (8/10-bit), FFv1  
✅ **Speed Presets** - `--preset fast|normal|slow` for quality/time tradeoff  
✅ **Config Support** - Save defaults, YAML/JSON configuration  
✅ **CI/CD Ready** - GitHub Actions workflows included  

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

### CLI (Recommended)

Fast and scriptable:

```bash
# List available profiles
bvp transcode --list-profiles

# Transcode with a profile
bvp transcode input.mov --profile live-qlab --output output.mov

# Linux live events with MKV
bvp transcode input.mov --profile live-linux-hevc-mkv --output output.mkv

# With custom keyframe interval (NEW v2.5.0)
bvp transcode input.mov --profile live-qlab --keyframe-interval 3.0

# With speed preset (for time-sensitive deadlines)
bvp transcode input.mov --profile live-qlab --preset fast

# Analyze video before transcoding
bvp analyze input.mov

# Batch process directory
bvp batch ./videos --profile standard-playback --output-dir ./output
```

### Folder Monitor (Automated Processing)

Watch a folder and transcode automatically:

```bash
# Generate a sample config
bvp monitor generate-config --output monitor.yaml --watch /incoming

# Edit monitor.yaml (or use as-is)
# Start monitoring
bvp monitor start --config monitor.yaml

# Drop videos in /incoming folder
# They auto-transcode based on your rules!

# Check status anytime
bvp monitor status --queue queue.json
```

**Example config for Linux live events:**
```yaml
watch_directory: /incoming
output_directory: /output
poll_interval: 5
delete_input: true

rules:
  - pattern: "*_prores.mov"
    profile: live-linux-hevc-mkv
    output_pattern: "{filename_no_ext}_live.mkv"
    priority: 100
```

### REST API (NEW - Phase 3.1)

Monitor and control transcoding via REST API:

```bash
# Install API dependencies
pip install fastapi uvicorn[standard] websockets pydantic

# Start API server with monitoring
python examples/dashboard_example.py --config monitor.yaml

# API is now available at http://localhost:8080
# Interactive docs at http://localhost:8080/docs

# Test endpoints
curl http://localhost:8080/api/v1/health | jq
curl http://localhost:8080/api/v1/status | jq
curl http://localhost:8080/api/v1/queue | jq
```

**Available endpoints:**
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Monitor status
- `GET /api/v1/queue` - Queue status and jobs
- `GET /api/v1/history` - Processing history
- `GET /api/v1/rules` - Active rules
- `GET /api/v1/jobs/{id}` - Job details
- `WS /api/v1/stream` - Real-time WebSocket updates
- `GET /docs` - Interactive API documentation

👉 **Full API guide:** [docs/API_QUICKSTART.md](./docs/API_QUICKSTART.md)

### Config Management

```bash
# Set your default profile (saved to ~/.bulletproof/config.json)
bvp config set-default-profile live-qlab

# Set your default output folder
bvp config set-output-dir ~/Videos/processed

# View current config
bvp config show
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
from bulletproof.core import TranscodeJob, TranscodeProfile
from pathlib import Path

# Create a profile with custom keyframe interval
profile = TranscodeProfile(
    name="custom-live",
    codec="h264",
    preset="medium",
    keyframe_interval=3.0,  # NEW: Keyframes every 3 seconds
    force_keyframes=True,   # NEW: Strict keyframe placement
    quality=85,
    description="Custom live profile"
)

# Create and execute a job
job = TranscodeJob(
    input_file=Path("input.mov"),
    output_file=Path("output.mp4"),
    profile=profile,
    speed_preset="normal"
)

if job.execute():
    print(f"Success! Output: {job.output_file}")
else:
    print(f"Failed: {job.error_message}")
```

---

## Profiles

| Name | Codec | Extension | Quality | Keyframe Interval | Use Case | Speed |
|------|-------|-----------|---------|-------------------|----------|-------|
| **live-qlab** | ProRes Proxy | .mov | Good | **5s** | QLab on Mac (instant scrubbing) | Medium |
| live-prores-lt | ProRes LT | .mov | High | **5s** | Live playback (smaller, easy scrubbing) | Medium |
| live-h264 | H.264 | .mp4 | High | **5s** | Cross-platform live (easy scrubbing) | Slow |
| **live-linux-hevc-mkv** | H.265 | .mkv | High (CRF 20) | **5s** | Linux live events (mpv, Linux Show Player) | Medium |
| standard-playback | H.264 | .mp4 | Good | **10s** | General playback | Medium |
| stream-hd | H.265 | .mp4 | Good | **2s** | 1080p streaming (responsive seeking) | Medium |
| stream-4k | H.265 | .mp4 | Good | **2s** | 4K streaming (responsive seeking) | Medium |
| archival | ProRes HQ | .mov | Max | Source | Long-term storage (preserve original) | Slow |
| **archival-linux-mkv** | H.265 10-bit | .mkv | Near-lossless (CRF 18) | Source | Linux archival (ProRes 422 replacement) | Slow |

### Linux MKV Profiles (NEW)

**live-linux-hevc-mkv** - Optimized for Linux live event playback:
- H.265 codec with CRF 20 quality (visually transparent)
- MKV container for better seeking reliability
- 5-second keyframes for instant scrubbing in cue systems
- AAC audio at 192k for compatibility
- Perfect for mpv, VLC, and Linux Show Player integration

**archival-linux-mkv** - ProRes 422 replacement for Linux:
- H.265 10-bit (yuv422p10le) matching ProRes color depth
- CRF 18 for visually lossless quality
- Uncompressed PCM audio (24-bit)
- ~60-80% smaller files than ProRes 422 HQ
- Preserves source keyframes for maximum fidelity

**Usage example:**
```bash
# Convert ProRes to Linux-friendly MKV for live playback
bvp transcode prores_input.mov --profile live-linux-hevc-mkv

# High-quality archival alternative to ProRes
bvp transcode prores_input.mov --profile archival-linux-mkv

# Test playback with GPU acceleration (Linux)
mpv --hwdec=auto output.mkv
```

### Keyframe Intervals Explained (NEW v2.5.0)

**What are keyframes?**
Keyframes (I-frames) are reference points in video that enable instant seeking. More frequent keyframes = smoother scrubbing but larger file sizes.

**Built-in intervals:**
- **5 seconds** (live profiles) - Perfect for QLab and live event playback. Jump anywhere instantly.
- **2 seconds** (streaming) - Responsive seeking for web players and HLS/DASH streaming.
- **10 seconds** (general) - Balanced between file size and scrubbing convenience.
- **Source** (archival) - Preserves original keyframe structure for maximum quality.

**Custom intervals:**
```bash
# Override any profile's keyframe interval
bvp transcode input.mov --profile standard-playback --keyframe-interval 3.0
```

**Guidelines:**
- **Live playback (QLab, events):** 5-10 seconds
- **Editing/post-production:** 1-3 seconds
- **Streaming/HLS/DASH:** 2-4 seconds
- **Archive/preservation:** None (preserve source)

👉 **Full technical guide:** [docs/features/KEYFRAME_FEATURE.md](./docs/features/KEYFRAME_FEATURE.md)

---

## Speed Presets

Control encode time vs quality:

```bash
# For time-sensitive live playback (encode faster, slight quality loss)
bvp transcode input.mov --profile live-qlab --preset fast

# Balanced (default)
bvp transcode input.mov --profile live-qlab --preset normal

# Maximum quality (encode slower)
bvp transcode input.mov --profile live-qlab --preset slow
```

## Output Naming

Automatic helpful output filenames:

```
Input:   spider_reveal_v1.mov
Profile: live-linux-hevc-mkv
Output:  spider_reveal_v1__processed__live-linux-hevc-mkv.mkv
```

The `__processed__` marker makes it easy to distinguish original vs transcoded files.

## Progress Tracking

Real-time progress bar with keyframe info:

```
Transcoding: SF90_Spider_Reveal(1).mov
Duration: 2.2 minutes
Speed Preset: normal
Keyframe Interval: 5.0s (easy scrubbing enabled)

Progress: |████████████░░░░░░░░░░░░░░░░░░| 35.2% (42/120s)
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=bvp tests/

# Linting and formatting
ruff check .
ruff format .
```

## Development & Tooling

### Modern Python Tooling (Ruff)

Switched the entire linting and formatting stack to **[Ruff](https://github.com/astral-sh/ruff)**. 
- **Speed:** 10-100x faster than previous tools (Black, isort, flake8).
- **Efficiency:** Unified configuration in `pyproject.toml`.
- **Consistency:** All-in-one tool for linting, formatting, and import sorting.

**Ruff Commands:**
```bash
# Check all files
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Format all files
ruff format .
```

### Adding a New Profile

Edit `bulletproof/core/profile.py` and add to `BUILT_IN_PROFILES`:

```python
BUILT_IN_PROFILES["my-profile"] = TranscodeProfile(
    name="my-profile",
    codec="h265",
    preset="medium",
    quality=20,  # CRF value for H.265
    max_bitrate=None,  # Use CRF mode
    description="Description for CLI",
    extension="mkv",
    keyframe_interval=5.0,  # Keyframes every 5 seconds (NEW v2.5.0)
    force_keyframes=True    # Strict intervals (NEW v2.5.0)
)
```

## Architecture

```
bulletproof/
├── api/               # REST API (NEW Phase 3.1!)
│   ├── models.py      # Pydantic response models
│   ├── routes.py      # REST + WebSocket endpoints
│   └── server.py      # FastAPI app
├── core/              # Transcode logic
│   ├── profile.py     # Profile definitions & codec mapping
│   ├── monitor.py     # Folder watching and file detection
│   ├── rules.py       # Pattern matching rules
│   ├── queue.py       # Job queue with persistence
│   └── job.py         # Transcode execution with keyframe control
├── services/          # High-level services
│   └── monitor_service.py  # Orchestration for folder monitoring
├── cli/               # Command-line interface
│   ├── main.py        # CLI entry point
│   └── commands/      # Subcommands (transcode, monitor, analyze, batch, config)
├── config/            # Configuration management
│   └── loader.py      # Config file handling
└── utils/             # Utilities (validation, etc)

docs/
├── features/          # Feature documentation
│   └── KEYFRAME_FEATURE.md
├── API_QUICKSTART.md # REST API guide (NEW!)
├── ROADMAP.md         # Project roadmap
└── phase-3.1/        # Web Dashboard planning

examples/
└── dashboard_example.py  # API server example (NEW!)

linux/                # Pure Bash implementation (no Python)
scripts/              # Universal tools (work on any OS)
tests/                # Test suite (33 tests passing)
.github/workflows/    # CI/CD
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ffmpeg not found" | Install ffmpeg: `brew install ffmpeg` or `apt install ffmpeg` |
| No progress bar | Video lacks duration metadata. Transcode is still running. |
| Transcode takes long | Normal for large files. Check the progress bar for speed estimate. |
| Want to cancel? | Press Ctrl+C - incomplete file is auto-deleted |
| Import errors | Ensure venv is active and you ran `pip install -e ".[dev]"` |
| Linux issues | See [`linux/QUICK_START.md`](./linux/QUICK_START.md) |
| Monitor not detecting | Enable DEBUG logging. See monitor docs. |
| Scrubbing still slow? | Use `--keyframe-interval 2.0` for more frequent keyframes |
| MKV playback issues on Linux? | Enable GPU acceleration: `mpv --hwdec=auto video.mkv` |
| 10-bit encoding not working? | Update ffmpeg: some older versions lack 10-bit H.265 support |
| API not starting? | Install dependencies: `pip install fastapi uvicorn[standard] websockets pydantic` |

## Documentation

- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and release notes
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Common commands quick reference
- **[docs/API_QUICKSTART.md](./docs/API_QUICKSTART.md)** - REST API guide (NEW!)
- **[docs/features/KEYFRAME_FEATURE.md](./docs/features/KEYFRAME_FEATURE.md)** - Keyframe control guide
- **[docs/ROADMAP.md](./docs/ROADMAP.md)** - Project roadmap and future plans
- **[docs/SCRIPTS_STRUCTURE.md](./docs/SCRIPTS_STRUCTURE.md)** - Architecture overview
- **[linux/QUICK_START.md](./linux/QUICK_START.md)** - Linux Bash version guide

## License

MIT License - see LICENSE file

## Author

Beau Bremer ([@KnowOneActual](https://github.com/KnowOneActual))

## Philosophy

> "What does this system need?" → Use that codec + keyframe strategy

Instead of debating codecs, Bulletproof asks the question:
- Live playback on Mac? → ProRes/H.264 with 5s keyframes
- Live playback on Linux? → H.265 MKV with 5s keyframes (NEW!)
- Streaming? → H.265 with 2s keyframes for HLS/DASH
- Long-term storage? → ProRes HQ, preserve source keyframes
- Linux archival? → H.265 10-bit MKV, visually lossless (NEW!)
- Linux without Python? → H.264/H.265 with pure Bash
- Automation? → Folder Monitor with pattern rules
- Frame-accurate editing? → Custom keyframe intervals (NEW!)
- Remote monitoring? → REST API + WebSocket (NEW Phase 3.1!)

Each profile and tool is a prepackaged answer to that question.

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass: `pytest -v`
5. Format code: `ruff format .`
6. Run linting: `ruff check .`
7. Submit a pull request

---

**Latest Update:** February 27, 2026  
**Current Version:** 2.5.0 (API in development)
