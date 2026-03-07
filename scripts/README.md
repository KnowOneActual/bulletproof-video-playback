# Bulletproof Video Playback - Scripts Directory

This directory contains **universal tools** that work across all platforms (macOS, Linux, WSL2).

---

## Universal Tools (Works Everywhere)

### `./analyze.sh <video_file>`
Inspect video codec, resolution, fps, bitrate, audio, and subtitle information.

**Install dependencies:**
```bash
# macOS
brew install ffmpeg jq

# Ubuntu/Debian
sudo apt install ffmpeg jq

# Fedora/RHEL
sudo dnf install ffmpeg jq
```

**Usage:**
```bash
./analyze.sh video.mov              # Human-readable output
./analyze.sh video.mov --json       # JSON output for parsing
```

---

### `./list-profiles.sh`
Display all available transcoding profiles and their details.

**Usage:**
```bash
./list-profiles.sh                  # Concise table
./list-profiles.sh --verbose        # Full details for each profile
```

**Output:** Shows 7 transcoding profiles optimized for:
- Live event playback (H.264)
- Streaming (H.265/HEVC)
- Archival (FFv1 lossless or ProRes)
- Web compatibility

---

### `./profiles.json`
Profile catalog shared across all tools. Contains:
- Codec settings (bitrate, preset, profile)
- Use case descriptions
- Speed estimates
- Quality ratings

Edit this file to customize profiles or add new ones.

---

## Platform-Specific Transcoding

### macOS Users
👉 **See the main [README.md](../README.md)** for Python version with:
- Full feature set
- macOS-native ProRes support

```bash
# Install with pip
pip install bulletproof-video-playback

# Or use from source
python3 -m bvp
```

---

### Linux Users
👉 **See [linux/QUICK_START.md](../linux/QUICK_START.md)** for Bash version with:
- Pure FFmpeg + Shell scripts (no Python)
- Works on machines you don't own
- 5 transcoding scripts:
  - `./scripts/transcode.sh` — Single-file transcoding
  - `./scripts/batch.sh` — Batch directory processing
  - `./scripts/analyze.sh` — Video analysis (also in root)
  - `./scripts/list-profiles.sh` — Profile browser (also in root)
  - `./scripts/config.sh` — Configuration management

```bash
# Quick setup
cd linux
bash install.sh

# Transcode a file
./scripts/transcode.sh video.mov --profile live-h264-linux
```

---

### Windows Users
Use **WSL2** with Linux Bash scripts, or **Python version** on Windows native.

---

## Quick Comparison

| Feature | macOS (Python) | Linux (Bash) |
|---------|----------------|---------------|
| **Installation** | `pip install` | `bash install.sh` |
| **Python required** | Yes | No |
| **ProRes support** | Native | Optional |
| **Single file transcode** | Yes | Yes |
| **Batch processing** | Yes | Yes |
| **Video analysis** | Yes | Yes |
| **Profile management** | Python API | JSON + Bash |

---

## Getting Started

### Just Want to Analyze a Video?
```bash
chmod +x analyze.sh list-profiles.sh
./analyze.sh your_video.mov
./list-profiles.sh
```

### macOS Transcoding
```bash
# See main README for Python version setup
cd ..
cat README.md
```

### Linux Transcoding
```bash
# See linux/ folder for Bash version
cd linux
cat QUICK_START.md
```

---

## File Structure

```
scripts/
├── README.md                    # This file
├── analyze.sh                   # Video inspection (universal)
├── list-profiles.sh             # Profile browser (universal)
├── profiles.json                # Profile catalog (shared)
└── linux/ → symlinks to:
    ├── analyze.sh               # (symlink to ../analyze.sh)
    ├── list-profiles.sh         # (symlink to ../list-profiles.sh)
    ├── profiles.json            # (symlink to ../profiles.json)
    ├── transcode.sh             # Single-file transcoding (Linux only)
    ├── batch.sh                 # Batch processing (Linux only)
    └── config.sh                # Config management (Linux only)
```

---

## Dependencies

**Always required:**
- `ffmpeg` - Video encoding
- `ffprobe` - Video analysis (bundled with ffmpeg)
- `jq` - JSON parsing
- `bash` - Shell scripting

**Installation:**
```bash
# macOS
brew install ffmpeg jq

# Ubuntu/Debian
sudo apt update && sudo apt install -y ffmpeg jq

# Fedora/RHEL
sudo dnf install -y ffmpeg jq
```

---

## FAQ

**Q: Why is there a `scripts/` folder in root AND in `linux/`?**  
A: Root contains universal tools (analyze, list-profiles). Linux folder contains full transcoding suite (transcode, batch, config).

**Q: Why are there symlinks in `linux/scripts/`?**  
A: To avoid duplicating universal tools and keep a single source of truth.

**Q: Can I use Linux Bash scripts on macOS?**  
A: Yes, if you install ffmpeg + jq. But Python version is recommended for macOS.

**Q: Can I use Python version on Linux?**  
A: Yes, but Bash version is recommended for machines where you can't install Python.

**Q: What if I'm on Windows?**  
A: Use WSL2 with Linux Bash scripts, or install Python for native Windows version.

---

## Next Steps

1. **Analyze your video:** `./analyze.sh my_video.mov`
2. **See available profiles:** `./list-profiles.sh`
3. **Choose your platform:**
   - macOS → [Main README](../README.md)
   - Linux → [linux/QUICK_START.md](../linux/QUICK_START.md)
   - Windows → Use WSL2 with Linux version

---

**Made in Chicago** 🎬 | MIT License
