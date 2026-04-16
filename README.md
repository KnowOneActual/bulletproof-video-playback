# bulletproof-video-playback

[![Tests](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml/badge.svg)](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.2.1-green.svg)](https://github.com/KnowOneActual/bulletproof-video-playback/releases)

> [!NOTE]
> > [!NOTE]
> BVP is still in active design and development. I’m using this project as a great opportunity to learn and improve my workflow, so things might change quickly and sometimes even break. I'm currently refactoring based on the feedback I've received. If you're trying it out, please be patient with some rough edges and occasional instability for now. Feel free to reach out with any issues or comments (good or bad ;)). Primary mandate is "no show-day embarrassments." Please check [ROADMAP.md](./docs/ROADMAP.md) for current phase details.

Video transcoding for live playback, streaming, and archival. Uses ffmpeg under the hood with curated profiles optimized for professional AV workflows.

**NEW v3.2.1:** **CI/CD Pipeline Stabilization** - Fixed security workflow, formatting issues, test dependencies, and version consistency across the codebase.

**NEW v3.2.0:** **QLab & AV Performance Integration** - Explicit support for QLab's official performance advice, including uncompressed 48kHz audio and exact resolution matching to bypass system overhead.

**NEW Phase 3.1:** **Web Dashboard UI** - Built-in web interface for real‑time monitoring, job controls, and live WebSocket updates.

**Professional Keyframe Control** - Customize GOP intervals for frame-accurate seeking in QLab, video editors, and streaming workflows.

**MKV Profiles for Linux** - H.265 MKV profiles optimized for Linux live event workflows (mpv, Linux Show Player) with 10-bit color support.

**Folder Monitoring** - Automated hot-folder transcoding with pattern-based rules and crash-safe persistence.

## 🚀 What You Get

### Three Ways to Use

1. **CLI (Command Line)** - Fast, scriptable, automation-ready ⚡
2. **Folder Monitor** - Watch directories, auto-transcode with pattern rules 🔄
3. **Web Dashboard & API** - Real‑time monitoring, job controls, and remote management via browser 🌐

### Platforms

- **macOS** (Python) - Native ProRes support, recommended for QLab and theater workflows.
- **Linux** (Pure Bash + Python) - H.265 MKV profiles for live events; zero-dependency Bash mode available for restricted environments.
- **Windows/WSL** - Full support for CLI and Folder Monitor.

---

## 🎯 Perfect for AV Techs

### Professional Keyframe Control

All profiles support customizable **keyframe intervals** for professional GOP management:
- **Frame-accurate seeking** - Jump to exact frames in QLab, Premiere, DaVinci.
- **Streaming optimization** - 2-second GOP for responsive HLS/DASH seeking.
- **Live event prep** - 5-second GOP for quick scrubbing during show setup.
- **Broadcast compliance** - Match specific network delivery requirements.

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

- **CLI** - Fast, scriptable command-line interface.
- **ProRes support** - Native to macOS.
- **Keyframe control** - Professional GOP management.
- **Real-time progress tracking**.
- **Python API** for custom integration.
- **Folder Monitor** with async processing.
- **Web API** for remote monitoring.
- Requires: Python 3.10+

👉 See **Installation** section below

### 🐧 **Linux / Python + MKV Profiles**

- **H.265 MKV profiles** optimized for mpv and Linux Show Player
- **ProRes 422 replacement** with 10-bit color depth (visually lossless)
- **GPU hardware acceleration** support (VA-API/VDPAU/NVDEC)
- **MKV container** for better seeking reliability in live cue systems
- **5-second keyframes** for instant scrubbing in live event playback
- Requires: Python 3.10+, ffmpeg

### 🐧 **Linux / Pure Bash Version** (No Python required)

- **Zero dependencies** beyond ffmpeg (no Python needed)
- **Works on machines you don't own** (restricted environments)
- **Cross-platform profiles** (H.264, H.265, FFv1, ProRes if available)
- **Simple JSON-based configuration**
- Requires: bash, ffmpeg, jq (lightweight)

👉 See [`linux/QUICK_START.md`](./linux/QUICK_START.md) for Linux setup

---

## 🛡️ Security & Reliability

This project is built for **live event production**, where "no show-day embarrassments" is the primary mandate. Security and reliability are core parts of the development process.

### Automated Security Pipeline
Every commit and pull request is automatically audited via a multi-layered security CI/CD pipeline:
- **Secret Scanning ([Gitleaks](https://github.com/gitleaks/gitleaks))**: Automatically detects and prevents credentials, tokens, or private keys from being committed.
- **Static Analysis (SAST - [Bandit](https://github.com/PyCQA/bandit))**: Scans the Python codebase for insecure patterns, such as shell injections or insecure network bindings.
- **Dependency Auditing (SCA - [pip-audit](https://github.com/pypa/pip-audit))**: Checks all third-party packages against the PyPI vulnerability database (CVEs).

### Secure by Default
- **Local Binding**: The Dashboard API server defaults to `127.0.0.1` (localhost) to prevent unintentional network exposure.
- **Configurable Access**: Use `--api-host` and `--api-port` to explicitly control where the service is accessible.
- **Safe Cleanup**: Incomplete or interrupted transcodes are automatically cleaned up to prevent disk clutter or corrupted media playback.
- **Persistence**: The transcode queue is persisted to disk, allowing the service to recover gracefully from crashes or power failures.

👉 **Security History:** [docs/SECURITY_LOG.md](./docs/SECURITY_LOG.md)

---

## ✅ Quality Assurance

We maintain a high standard of code quality to ensure stability in production environments.

### Testing
The project includes a comprehensive suite of **57+ automated tests** covering configuration, rule matching, job queuing, profile validation, and API endpoints.
```bash
# Run the test suite
pytest -v

# Check test coverage
pytest --cov=bulletproof tests/
```

### Type Safety & Linting
We use modern Python tooling to enforce strict coding standards:
- **[Ruff](https://github.com/astral-sh/ruff)**: All-in-one fast linter and formatter (100-character line length).
- **[Mypy](http://mypy-lang.org/)**: Static type checking to catch bugs before they reach production.

---

## 🛠️ Development Workflow

To contribute or run local audits, install the development environment:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run a full local audit (Lint + Format + Type Check + Security + Tests)
ruff check .
ruff format .
mypy .
bandit -r bulletproof/ -ll
pip-audit
pytest -v
```

---

## Features

✅ **QLab Performance Integration** - Uncompressed PCM audio & exact resolution matching (NEW v3.2.0!)  
✅ **Web Dashboard UI** - Built‑in browser interface with real‑time monitoring, job controls, and live WebSocket updates (Phase 3.1!)  
✅ **Async Transcode Core** - Non-blocking execution with real-time progress parsing  
✅ **Folder Monitoring** - Automated hot-folder transcoding with pattern rules  
✅ **Professional Keyframe Control** - Customizable GOP intervals for frame-accurate seeking  
✅ **MKV Profiles for Linux** - Optimized for mpv and Linux Show Player (10-bit H.265)  
✅ **Automated Security Pipeline** - CI/CD audits with Bandit, Gitleaks, and pip-audit  
✅ **Crash Recovery** - Persistent job queue survives service restarts  
✅ **Smart Output Naming** - Automatic extension correction and processing markers  
✅ **CLI & Batch Tools** - Powerful command-line interface for manual and batch jobs  
✅ **Video Analysis** - Deep inspection of codec, resolution, and audio specs  
✅ **Professional Codecs** - ProRes Proxy/LT/HQ, H.264, H.265, and FFv1  
✅ **Speed Presets** - Control quality vs. time with `--preset` flags  

---

## Installation

### Requirements
- Python 3.10+ (macOS/Python version)
- ffmpeg (`brew install ffmpeg` on macOS, `apt install ffmpeg` on Linux)
- ffprobe (usually included with ffmpeg)

### 🚀 Recommended: Install with pipx (Global Tool)

`pipx` is the best way to install BVP. It creates an isolated environment for the tool while making the `bvp` command available globally, preventing dependency conflicts with other Python apps.

```bash
# Install pipx if you don't have it
brew install pipx  # macOS
# or: python3 -m pip install --user pipx

# Install BVP directly from GitHub
pipx install git+https://github.com/KnowOneActual/bulletproof-video-playback.git

# Optional: Install with API dashboard support
pipx install "bulletproof-video-playback[api] @ git+https://github.com/KnowOneActual/bulletproof-video-playback.git"
```

### From GitHub (Development / Local)

If you want to contribute or run BVP locally:

```bash
git clone https://github.com/KnowOneActual/bulletproof-video-playback
cd bulletproof-video-playback
pip install -e ".[dev,api]"
```

### From PyPI (Coming Soon)

BVP will soon be available directly on PyPI:

```bash
# Not yet active - use pipx or GitHub for now
# pip install bulletproof-video-playback
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

### REST API & Dashboard (Phase 3.1)

Monitor and control transcoding remotely via an event-driven API with built-in web dashboard:

```bash
# Install API dependencies
pip install "bulletproof-video-playback[api]"

# Start API server with monitoring and web dashboard
python examples/dashboard_example.py --config monitor.yaml

# Or start dashboard without monitor (standalone API)
python -m bulletproof.api.server --host 127.0.0.1 --port 8000
```

**Web Dashboard UI** (NEW!):
- **Real-time Monitoring**: Live job queue, progress bars, and status updates.
- **Interactive Controls**: Cancel, retry, and view job details directly in the browser.
- **Responsive Design**: Works on desktop, tablet, and mobile.
- **WebSocket Live Updates**: Instant notifications for job state changes.

**Key API Features:**
- **Real-time Events**: WebSocket (`/stream`) pushes instant notifications for file detection, job starts, and errors.
- **Smooth Progress**: Frame-by-frame progress updates (throttled for network efficiency).
- **Remote Control**: Pause, resume, cancel, or retry jobs via REST endpoints.
- **Interactive Docs**: Full OpenAPI/Swagger documentation at `/docs`.

👉 **Full API guide:** [docs/API_QUICKSTART.md](./docs/API_QUICKSTART.md)  
👉 **Dashboard guide:** [docs/DASHBOARD_GUIDE.md](./docs/DASHBOARD_GUIDE.md)

### Config Management

```bash
# Set your default profile (saved to ~/.bvp/config.json)
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
| **audio-qlab** | PCM (WAV) | .wav | Lossless | N/A | QLab audio-only cues (replaces MP3/AAC) | Fast |
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

### QLab Performance Optimization (NEW)

Bulletproof explicitly integrates **QLab's official performance advice** to help you squeeze out every 0.01% of processing power for critical shows:

1. **Avoid MP3 and MP4/AAC:** Compressed audio takes extra CPU overhead to decode on the fly. BVP's `live-qlab` profile automatically uses uncompressed 24-bit PCM (`pcm_s24le`) in a `.mov` container.
2. **Dedicated Audio Cues:** Need to convert MP3/AAC files to QLab-friendly WAV? Use the new `audio-qlab` profile to instantly transcode them to 48kHz 24-bit WAV.
   ```bash
   bvp transcode audio.mp3 --profile audio-qlab
   ```
3. **Match Output Sample Rate & Resolution:** Core Audio resamples audio on the fly, and video cues scale dynamically. To remove this overhead, you can now explicitly tell BVP to match your exact display resolution and hardware sample rate:
   ```bash
   # Match your 1080p projector and 48kHz audio interface perfectly
   bvp transcode video.mp4 --profile live-qlab --resolution 1920:1080 --audio-sample-rate 48000
   ```

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

bulletproof/
├── api/               # Event-driven REST API & WebSocket server
│   ├── models.py      # Pydantic response models
│   ├── routes.py      # Broadcast-ready endpoints
│   └── server.py      # FastAPI application & lifespan management
├── core/              # Async Transcode Core
│   ├── profile.py     # Profile definitions & QLab performance specs
│   ├── monitor.py     # Folder watching & stability tracking
│   ├── rules.py       # Pattern matching engine
│   ├── queue.py       # Job queue with JSON persistence
│   └── job.py         # Async transcode execution (non-blocking)
├── services/          # Orchestration layer
│   └── monitor_service.py  # Event-emitting monitor service
├── cli/               # Command-line interface
...
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
- **[docs/DASHBOARD_GUIDE.md](./docs/DASHBOARD_GUIDE.md)** - Web dashboard quick start (NEW!)
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
- **QLab on Mac?** → ProRes with 5s keyframes & 48kHz PCM audio.
- **Live events on Linux?** → H.265 MKV with 5s keyframes.
- **Responsive Streaming?** → H.265 with 2s keyframes for HLS/DASH.
- **Long-term storage?** → ProRes HQ or 10-bit H.265 MKV.
- **Automation?** → Folder Monitor with pattern rules.
- **Remote Monitoring?** → Event-driven REST API + WebSockets.

Each profile and tool is a prepackaged answer to a real-world AV requirement.

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

**Latest Update:** April 15, 2026  
**Current Version:** 3.2.2 (Web Dashboard UI)
