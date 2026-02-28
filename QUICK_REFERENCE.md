# 📋 Quick Reference Card - v2.6.0

## 🎯 In 30 Seconds

**Your GitHub Repo:** https://github.com/KnowOneActual/bulletproof-video-playback

**What It Does (Who It’s For):**
- For AV and theater teams who need reliable, fast-scrubbing playback on macOS and Linux.
- Transcode videos for live playback (QLab/Linux Show Player) + streaming + archival
- **NEW v2.6.0:** MKV profiles for Linux live events (GPU accelerated)
- **NEW v2.5.0:** Professional keyframe control for frame-accurate seeking
- **NEW:** Folder monitoring for automated batch processing
- 9 optimized profiles with smart keyframe intervals
- CLI + Folder Monitor + Python API
- ⚠️ **TUI DEPRECATED** (removal in v3.0.0)

---

## 🚀 Quick Setup (First Time)

```bash
# Set your defaults once
bvp config set-default-profile live-qlab  # macOS
# Or for Linux:
bvp config set-default-profile live-linux-hevc-mkv

bvp config set-output-dir ~/Videos/processed
bvp config set-preset normal

# Verify
bvp config show
```

---

## 🎮 How to Use (Three Ways)

### 1. CLI (Fastest - Recommended)
```bash
# List all profiles
bvp transcode --list-profiles

# Transcode with defaults
bvp transcode input.mov

# Transcode with specific profile
bvp transcode input.mov --profile live-qlab --output output.mov

# Linux live events with MKV (NEW v2.6.0)
bvp transcode input.mov --profile live-linux-hevc-mkv --output output.mkv

# With custom keyframe interval (NEW v2.5.0)
bvp transcode input.mov --profile live-qlab --keyframe-interval 3.0

# Fast encode for time-sensitive playback
bvp transcode input.mov --preset fast

# Analyze video before transcoding
bvp analyze input.mov

# Batch process folder
bvp batch ./videos --profile live-qlab --output-dir ./output
```

### 2. Folder Monitor (Automation)
```bash
# Generate config
bvp monitor generate-config --output monitor.yaml --watch /incoming

# Start watching
bvp monitor start --config monitor.yaml

# Check status
bvp monitor status --queue queue.json

# Clear queue
bvp monitor clear-queue --queue queue.json
```

### 3. ~~TUI (Interactive)~~ - DEPRECATED
```bash
bvp tui  # Shows deprecation warning
```

⚠️ **Migration:** Use `bvp transcode` CLI or `bvp monitor` instead.  
👉 **Full guide:** [docs/TUI_DEPRECATION.md](./docs/TUI_DEPRECATION.md)

### Python API (Scripting)
```python
from bulletproof.core import TranscodeJob, TranscodeProfile
from pathlib import Path

# Create profile with custom keyframes (NEW v2.5.0)
profile = TranscodeProfile(
    name="custom",
    codec="h264",
    preset="medium",
    keyframe_interval=3.0,  # Keyframes every 3 seconds
    force_keyframes=True,   # Strict keyframe placement
    quality=85
)

job = TranscodeJob(
    Path("input.mov"),
    Path("output.mp4"),
    profile,
    speed_preset="normal"
)

if job.execute():
    print(f"Success: {job.output_file}")
```

---

## ⚙️ Configuration Commands

```bash
# Set default profile (saves clicking every time)
bvp config set-default-profile live-qlab

# Set default output folder
bvp config set-output-dir ~/Videos/processed

# Set speed preset (fast/normal/slow)
bvp config set-preset normal

# View current config
bvp config show

# Reset to factory defaults
bvp config reset
```

**Config location:** `~/.bulletproof/config.json`

---

## 🎬 The 9 Profiles

| Name | Codec | Quality | Keyframes | Use When | Speed |
|------|-------|---------|-----------|----------|-------|
| **live-qlab** | ProRes Proxy | Good | **5s** | QLab on Mac | Medium |
| live-prores-lt | ProRes LT | High | **5s** | Live playback | Medium |
| live-h264 | H.264 | High | **5s** | Cross-platform | Slow |
| **live-linux-hevc-mkv** | H.265 | High (CRF 20) | **5s** | Linux live events | Medium |
| standard-playback | H.264 | Good | **10s** | General use | Medium |
| stream-hd | H.265 | Good | **2s** | 1080p streaming | Medium |
| stream-4k | H.265 | Good | **2s** | 4K streaming | Medium |
| archival | ProRes HQ | Max | Source | macOS long-term storage | Slow |
| **archival-linux-mkv** | H.265 10-bit | Near-lossless (CRF 18) | Source | Linux archival (ProRes replacement) | Slow |

### Keyframe Intervals (NEW v2.5.0)

**What are keyframes?**  
I-frames that enable instant video seeking. More keyframes = smoother scrubbing.

**Guidelines:**
- **Live playback (QLab/Linux Show Player):** 5-10 seconds
- **Video editing:** 1-3 seconds  
- **Streaming (HLS/DASH):** 2-4 seconds
- **Archive:** Preserve source

**Override any profile:**
```bash
bvp transcode input.mov --profile standard-playback --keyframe-interval 3.0
```

👉 **Full guide:** [docs/features/KEYFRAME_FEATURE.md](./docs/features/KEYFRAME_FEATURE.md)

### MKV Profiles for Linux (NEW v2.6.0)

**live-linux-hevc-mkv** - Linux live playback:
- H.265 with CRF 20 (visually transparent quality)
- MKV container for better seeking than MP4
- 5-second keyframes for instant scrubbing
- Perfect for mpv, VLC, Linux Show Player
- GPU acceleration support (VA-API/VDPAU/NVDEC)

**archival-linux-mkv** - ProRes 422 replacement:
- H.265 10-bit (yuv422p10le) matching ProRes color depth
- CRF 18 for visually lossless quality
- ~60-80% smaller files than ProRes 422 HQ
- Uncompressed PCM audio (24-bit)
- Cross-platform compatible

---

## ⚡ Speed Presets

Control encode time vs quality:

```bash
# Fast (5-20% faster, slight quality loss)
bvp transcode input.mov --preset fast

# Normal (default, balanced)
bvp transcode input.mov --preset normal

# Slow (5-15% slower, maximum quality)
bvp transcode input.mov --preset slow
```

---

## 🔄 Folder Monitor Quick Reference

### Basic Setup
```bash
# 1. Generate config
bvp monitor generate-config -o monitor.yaml -w /incoming

# 2. Edit monitor.yaml
watch_directory: /incoming
output_directory: /output
poll_interval: 5

rules:
  - pattern: "*_live.mov"
    profile: live-qlab
    output_pattern: "{filename_no_ext}_qlab.mov"
  - pattern: "*_prores.mov"  # NEW: Convert ProRes to Linux MKV
    profile: live-linux-hevc-mkv
    output_pattern: "{filename_no_ext}_live.mkv"

# 3. Start monitoring
bvp monitor start --config monitor.yaml
```

### Monitor Commands
```bash
# Start watching folder
bvp monitor start --config monitor.yaml

# Check queue status
bvp monitor status --queue queue.json --verbose

# Clear queue (asks for confirmation)
bvp monitor clear-queue --queue queue.json

# Generate sample config
bvp monitor generate-config -o monitor.yaml -w /incoming
```

---

## 🎯 Core AV & Theater Workflows

These workflows target common AV/theater scenarios: QLab rigs, Linux Show Player/mpv, archival on show machines, and hot-folder ingest.

### Workflow 1: Live Playback (QLab on macOS)
```bash
# First time setup
bvp config set-default-profile live-qlab
bvp config set-output-dir ~/Videos/QLab

# Then just:
bvp transcode video.mov
# → Saves to ~/Videos/QLab/video__processed__live-qlab.mov
# → 5-second keyframes for instant scrubbing
```

### Workflow 2: Linux Live Events (NEW v2.6.0)
```bash
# Setup for Linux Show Player
bvp config set-default-profile live-linux-hevc-mkv
bvp config set-output-dir ~/Videos/LiveEvents

# Convert ProRes to Linux MKV
bvp transcode prores_input.mov
# → H.265 MKV with GPU acceleration support
# → 5-second keyframes for cue system scrubbing

# Test with GPU acceleration
mpv --hwdec=auto output.mkv
```

### Workflow 3: ProRes Replacement on Linux (NEW v2.6.0)
```bash
# High-quality archival on Linux
bvp transcode prores_422.mov --profile archival-linux-mkv
# → 10-bit H.265 MKV
# → Visually lossless (CRF 18)
# → 60-80% smaller than ProRes
# → Cross-platform compatible
```

### Workflow 4: Automated Hot Folder
```bash
# Setup once
bvp monitor generate-config -o monitor.yaml -w /dropbox
# Edit monitor.yaml with your rules

# Run continuously
bvp monitor start --config monitor.yaml

# Drop videos in /dropbox → auto-transcode!
```

### Workflow 5: Frame-Accurate Editing
```bash
# 1-second keyframes for precise editing
bvp transcode input.mov --profile standard-playback --keyframe-interval 1.0
# → Perfect for Premiere, DaVinci Resolve, Final Cut
```

### Workflow 6: HLS/DASH Streaming
```bash
# 2-second keyframes for responsive web seeking
bvp transcode input.mov --profile stream-hd
# → Optimized for web players and adaptive streaming
```

### Workflow 7: Time-Sensitive Deadline
```bash
# Need fast encode for tonight's show?
bvp transcode video.mov --preset fast
# → ~30% faster encoding
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=bvp tests/ -v

# Linting
ruff check .
ruff format .
```

---

## 📁 Project Structure

```
bulletproof/
├── core/
│   ├── profile.py      # Profile definitions + keyframe support + MKV profiles
│   ├── job.py          # Transcode execution + CRF mode support
│   ├── monitor.py      # Folder watching
│   ├── queue.py        # Job queue
│   └── rules.py        # Pattern matching
├── services/
│   └── monitor_service.py  # Monitoring orchestration
├── config/
│   └── loader.py       # Config management
├── cli/
│   ├── main.py         # CLI entry point
│   └── commands/
│       ├── transcode.py    # Transcode with keyframe support
│       ├── analyze.py      # Video analysis
│       ├── batch.py        # Batch processing
│       ├── monitor.py      # Folder monitoring
│       └── config.py       # Config management
├── tui/                # DEPRECATED (removal in v3.0.0)
└── utils/

docs/
├── features/           # Feature documentation
├── testing/            # Testing guides
├── phase-3.1/          # Web Dashboard planning
└── TUI_DEPRECATION.md  # TUI migration guide
```

---

## 🔧 Common Commands

```bash
# Installation (one time)
pip install bulletproof-video-playback
# Or from source:
pip install -e ".[dev]"

# Set defaults (one time)
bvp config set-default-profile live-qlab  # macOS
bvp config set-default-profile live-linux-hevc-mkv  # Linux
bvp config set-output-dir ~/Videos/processed

# Check version
bvp --version

# List profiles
bvp transcode --list-profiles

# Transcode (simple)
bvp transcode video.mov

# Transcode (with keyframes)
bvp transcode video.mov --profile live-qlab --keyframe-interval 5.0

# Linux MKV (NEW v2.6.0)
bvp transcode prores.mov --profile live-linux-hevc-mkv

# Analyze video
bvp analyze video.mov

# Start folder monitor
bvp monitor start --config monitor.yaml

# View config
bvp config show

# Testing
pytest -v

# Linting
ruff check .
ruff format .
```

---

## ✨ What's New in v2.6.0

🐧 **MKV Profiles for Linux** (NEW!)
- `live-linux-hevc-mkv` - H.265 MKV for Linux live events
- `archival-linux-mkv` - 10-bit H.265 for Linux archival (ProRes replacement)
- CRF mode support for quality-based encoding
- GPU acceleration compatible (VA-API/VDPAU/NVDEC)
- 60-80% smaller files than ProRes with same quality

🎬 **Keyframe Interval Control** (v2.5.0)
- Professional GOP management for frame-accurate seeking
- Customizable keyframe intervals per profile
- Force keyframes flag for strict interval placement
- CLI flag: `--keyframe-interval 3.0`

🔄 **Folder Monitor** (v2.4.0)
- Automated batch processing
- Pattern-based rules engine
- Queue persistence and crash recovery
- Real-time status monitoring

🚧 **TUI Deprecated**
- Shows warning on startup
- Will be removed in v3.0.0
- Migrate to CLI or wait for Web Dashboard

✅ **CI/CD Improvements**
- All linting checks passing (ruff)
- Multi-Python version support (3.9-3.12)
- 100-character line length standardization

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ffmpeg not found" | Install: `brew install ffmpeg` or `apt install ffmpeg` |
| Config not loading | Check: `cat ~/.bulletproof/config.json` |
| TUI not working | It's deprecated. Use `bvp transcode` instead |
| Tests failing | Run: `pytest -v` for details |
| Want to reset config | Run: `bvp config reset` |
| Import errors | Ensure venv: `source .venv/bin/activate` |
| Scrubbing still slow? | Use `--keyframe-interval 2.0` for more keyframes |
| Monitor not detecting | Check permissions and `poll_interval` in config |
| MKV playback issues? | Enable GPU: `mpv --hwdec=auto video.mkv` |
| 10-bit not working? | Update ffmpeg (older versions lack 10-bit H.265) |

---

## 💡 Philosophy

> "What does this system need?" → Use that codec + keyframe strategy

The north star: **no show embarrassments.** Every profile and feature is a prepackaged answer to a specific AV workflow, not a generic "video conversion" option.

Instead of debating:
- QLab on Mac? → ProRes Proxy + 5s keyframes
- Linux live events? → H.265 MKV + 5s keyframes (NEW!)
- Video editing? → H.264 + 1s keyframes
- Streaming? → H.265 + 2s keyframes (HLS/DASH)
- Archive (macOS)? → ProRes HQ + preserve source
- Archive (Linux)? → H.265 10-bit MKV + preserve source (NEW!)
- Automation? → Folder Monitor

Each profile is a prepackaged answer.

---

## 📤 Share It

```bash
# Tag a release
git tag v2.6.0
git push origin v2.6.0

# Share the repo
# https://github.com/KnowOneActual/bulletproof-video-playback
```

---

**Status:** ✅ v2.6.0 Production Ready | 9 Profiles | MKV for Linux | All Tests Passing | GPU Accelerated
