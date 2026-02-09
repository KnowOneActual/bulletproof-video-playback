# 📋 Quick Reference Card - v2.5.0

## 🎯 In 30 Seconds

**Your GitHub Repo:** https://github.com/KnowOneActual/bulletproof-video-playback

**What It Does:**
- Transcode videos for live playback (QLab/PlaybackPro) + streaming + archival
- **NEW v2.5.0:** Professional keyframe control for frame-accurate seeking
- **NEW:** Folder monitoring for automated batch processing
- 7 optimized profiles with smart keyframe intervals
- CLI + Folder Monitor + Python API
- ⚠️ **TUI DEPRECATED** (removal in v3.0.0)

---

## 🚀 Quick Setup (First Time)

```bash
# Set your defaults once
bulletproof config set-default-profile live-qlab
bulletproof config set-output-dir ~/Videos/processed
bulletproof config set-preset normal

# Verify
bulletproof config show
```

---

## 🎮 How to Use (Three Ways)

### 1. CLI (Fastest - Recommended)
```bash
# List all profiles
bulletproof transcode --list-profiles

# Transcode with defaults
bulletproof transcode input.mov

# Transcode with specific profile
bulletproof transcode input.mov --profile live-qlab --output output.mov

# With custom keyframe interval (NEW v2.5.0)
bulletproof transcode input.mov --profile live-qlab --keyframe-interval 3.0

# Fast encode for time-sensitive playback
bulletproof transcode input.mov --preset fast

# Analyze video before transcoding
bulletproof analyze input.mov

# Batch process folder
bulletproof batch ./videos --profile live-qlab --output-dir ./output
```

### 2. Folder Monitor (Automation)
```bash
# Generate config
bulletproof monitor generate-config --output monitor.yaml --watch /incoming

# Start watching
bulletproof monitor start --config monitor.yaml

# Check status
bulletproof monitor status --queue queue.json

# Clear queue
bulletproof monitor clear-queue --queue queue.json
```

### 3. ~~TUI (Interactive)~~ - DEPRECATED
```bash
bulletproof tui  # Shows deprecation warning
```

⚠️ **Migration:** Use `bulletproof transcode` CLI or `bulletproof monitor` instead.  
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
bulletproof config set-default-profile live-qlab

# Set default output folder
bulletproof config set-output-dir ~/Videos/processed

# Set speed preset (fast/normal/slow)
bulletproof config set-preset normal

# View current config
bulletproof config show

# Reset to factory defaults
bulletproof config reset
```

**Config location:** `~/.bulletproof/config.json`

---

## 🎬 The 7 Profiles

| Name | Codec | Quality | Keyframes | Use When | Speed |
|------|-------|---------|-----------|----------|-------|
| **live-qlab** | ProRes Proxy | Good | **5s** | QLab on Mac | Medium |
| live-prores-lt | ProRes LT | High | **5s** | Live playback | Medium |
| live-h264 | H.264 | High | **5s** | Cross-platform | Slow |
| standard-playback | H.264 | Good | **10s** | General use | Medium |
| stream-hd | H.265 | Good | **2s** | 1080p streaming | Medium |
| stream-4k | H.265 | Good | **2s** | 4K streaming | Medium |
| archival | ProRes HQ | Max | Source | Long-term storage | Slow |

### Keyframe Intervals (NEW v2.5.0)

**What are keyframes?**  
I-frames that enable instant video seeking. More keyframes = smoother scrubbing.

**Guidelines:**
- **Live playback (QLab):** 5-10 seconds
- **Video editing:** 1-3 seconds  
- **Streaming (HLS/DASH):** 2-4 seconds
- **Archive:** Preserve source

**Override any profile:**
```bash
bulletproof transcode input.mov --profile standard-playback --keyframe-interval 3.0
```

👉 **Full guide:** [docs/features/KEYFRAME_FEATURE.md](./docs/features/KEYFRAME_FEATURE.md)

---

## ⚡ Speed Presets

Control encode time vs quality:

```bash
# Fast (5-20% faster, slight quality loss)
bulletproof transcode input.mov --preset fast

# Normal (default, balanced)
bulletproof transcode input.mov --preset normal

# Slow (5-15% slower, maximum quality)
bulletproof transcode input.mov --preset slow
```

---

## 🔄 Folder Monitor Quick Reference

### Basic Setup
```bash
# 1. Generate config
bulletproof monitor generate-config -o monitor.yaml -w /incoming

# 2. Edit monitor.yaml
watch_directory: /incoming
output_directory: /output
poll_interval: 5

rules:
  - pattern: "*_live.mov"
    profile: live-qlab
    output_pattern: "{filename_no_ext}_qlab.mov"

# 3. Start monitoring
bulletproof monitor start --config monitor.yaml
```

### Monitor Commands
```bash
# Start watching folder
bulletproof monitor start --config monitor.yaml

# Check queue status
bulletproof monitor status --queue queue.json --verbose

# Clear queue (asks for confirmation)
bulletproof monitor clear-queue --queue queue.json

# Generate sample config
bulletproof monitor generate-config -o monitor.yaml -w /incoming
```

---

## 🎯 Real-World Workflows

### Workflow 1: Live Playback (QLab on macOS)
```bash
# First time setup
bulletproof config set-default-profile live-qlab
bulletproof config set-output-dir ~/Videos/QLab

# Then just:
bulletproof transcode video.mov
# → Saves to ~/Videos/QLab/video__processed__live-qlab.mov
# → 5-second keyframes for instant scrubbing
```

### Workflow 2: Automated Hot Folder
```bash
# Setup once
bulletproof monitor generate-config -o monitor.yaml -w /dropbox
# Edit monitor.yaml with your rules

# Run continuously
bulletproof monitor start --config monitor.yaml

# Drop videos in /dropbox → auto-transcode!
```

### Workflow 3: Frame-Accurate Editing
```bash
# 1-second keyframes for precise editing
bulletproof transcode input.mov --profile standard-playback --keyframe-interval 1.0
# → Perfect for Premiere, DaVinci Resolve, Final Cut
```

### Workflow 4: HLS/DASH Streaming
```bash
# 2-second keyframes for responsive web seeking
bulletproof transcode input.mov --profile stream-hd
# → Optimized for web players and adaptive streaming
```

### Workflow 5: Time-Sensitive Deadline
```bash
# Need fast encode for tonight's show?
bulletproof transcode video.mov --preset fast
# → ~30% faster encoding
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=bulletproof tests/ -v

# Linting
black bulletproof tests
isort bulletproof tests  
flake8 bulletproof tests
```

---

## 📁 Project Structure

```
bulletproof/
├── core/
│   ├── profile.py      # Profile definitions + keyframe support
│   ├── job.py          # Transcode execution
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
bulletproof config set-default-profile live-qlab
bulletproof config set-output-dir ~/Videos/processed

# Check version
bulletproof --version

# List profiles
bulletproof transcode --list-profiles

# Transcode (simple)
bulletproof transcode video.mov

# Transcode (with keyframes)
bulletproof transcode video.mov --profile live-qlab --keyframe-interval 5.0

# Analyze video
bulletproof analyze video.mov

# Start folder monitor
bulletproof monitor start --config monitor.yaml

# View config
bulletproof config show

# Testing
pytest -v

# Linting
black bulletproof tests
isort bulletproof tests
flake8 bulletproof tests
```

---

## ✨ What's New in v2.5.0

🎬 **Keyframe Interval Control** (NEW!)
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
- All linting checks passing (Black, isort, flake8)
- Multi-Python version support (3.9-3.12)
- 100-character line length standardization

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ffmpeg not found" | Install: `brew install ffmpeg` or `apt install ffmpeg` |
| Config not loading | Check: `cat ~/.bulletproof/config.json` |
| TUI not working | It's deprecated. Use `bulletproof transcode` instead |
| Tests failing | Run: `pytest -v` for details |
| Want to reset config | Run: `bulletproof config reset` |
| Import errors | Ensure venv: `source .venv/bin/activate` |
| Scrubbing still slow? | Use `--keyframe-interval 2.0` for more keyframes |
| Monitor not detecting | Check permissions and `poll_interval` in config |

---

## 🚀 Next Steps

1. ✅ **v2.5.0 Complete** - Keyframe control + TUI deprecation
2. 🔴 **v3.0.0** - Remove TUI completely
3. 🟢 **Phase 3.1** - Web Dashboard with real-time monitoring
4. 🔵 **Future** - GPU acceleration, concurrent processing, Docker

---

## 💡 Philosophy

> "What does this system need?" → Use that codec + keyframe strategy

Instead of debating:
- QLab on Mac? → ProRes Proxy + 5s keyframes
- Video editing? → H.264 + 1s keyframes
- Streaming? → H.265 + 2s keyframes (HLS/DASH)
- Archive? → ProRes HQ + preserve source
- Automation? → Folder Monitor

Each profile is a prepackaged answer.

---

## 📤 Share It

```bash
# Tag a release
git tag v2.5.0
git push origin v2.5.0

# Share the repo
# https://github.com/KnowOneActual/bulletproof-video-playback
```

---

**Status:** ✅ v2.5.0 Production Ready | All Tests Passing | Keyframe Control | TUI Deprecated
