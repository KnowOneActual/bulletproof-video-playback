# 📋 Quick Reference Card

## 🎯 In 30 Seconds

**Your GitHub Repo:** https://github.com/KnowOneActual/bulletproof-video-playback

**What It Does:**
- Transcode videos for theater (QLab/PlaybackPro) + streaming + archival
- Professional Python project with CLI + TUI
- 7 profiles for different use cases
- Real-time progress tracking during transcoding
- Tests + GitHub Actions CI/CD included

---

## 🎬 The 7 Profiles (Updated)

| # | Name | Codec | Extension | Quality | Use When |
|---|------|-------|-----------|---------|----------|
| 1 | **live-qlab** | ProRes Proxy | .mov | Good | QLab on Mac (QLab recommended) |
| 2 | live-prores-lt | ProRes LT | .mov | High | QLab on Mac (higher quality) |
| 3 | live-h264 | H.264 | .mp4 | High | Cross-platform theater |
| 4 | standard-playback | H.264 | .mp4 | Good | Miccia, VLC, web preview |
| 5 | stream-hd | H.265 | .mp4 | Good | 1080p streaming |
| 6 | stream-4k | H.265 | .mp4 | Good | 4K streaming |
| 7 | archival | ProRes HQ | .mov | Max | Long-term storage |

---

## ⚡ Key Features

### ✅ Smart Output Naming
```
Input:  video.mov
Profile: stream-4k
Output: video__stream-4k.mp4  ← Auto-correct extension!
```

### ✅ Real-Time Progress Tracking
```
Transcoding: SF90_Spider_Reveal(1).mov
Duration: 2.2 minutes

Progress: |████████████░░░░░░░░░░░░░░░░░░░░░░░░| 35.2% (42/120s)
```

### ✅ Safety Features
- Prevents overwriting input files
- Warns if output file already exists
- Handles special characters in filenames
- Ctrl+C to cancel (auto-cleans up incomplete files)

### ✅ Same-Folder Defaults
- Output files go to same folder as input by default
- Easy to find transcoded files
- Perfect for batch workflow

---

## 🎮 How to Use (Three Ways)

### CLI (Fastest)
```bash
# List profiles
buletproof transcode --list-profiles

# Transcode single file
buletproof transcode input.mov --profile live-qlab --output output.mov

# Analyze video
buletproof analyze input.mov
```

### TUI (Interactive + Progress)
```bash
buletproof tui
# Shows progress bar during transcode
# Ctrl+C to cancel safely
```

### Python API (Scripting)
```python
from bulletproof.core import TranscodeJob, list_profiles

profile = list_profiles()["live-qlab"]
job = TranscodeJob(Path("in.mov"), Path("out.mov"), profile)
job.execute()  # Shows progress automatically
```

---

## 📊 Transcode Times (Approximate)

Depending on video size and your Mac's specs:

| Duration | Profile | Time |
|----------|---------|------|
| 1 min | live-qlab | 2-4 min |
| 1 min | stream-4k | 5-10 min |
| 1 min | standard-playback | 3-6 min |

**Pro Tip:** If you see no progress for 20+ seconds, wait! Encoding is working, just slow. You'll see the progress bar update.

---

## 🆘 Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| No progress bar shown | Video file might not have duration metadata. It's still working! |
| `ffmpeg not found` | Install: `brew install ffmpeg` |
| `pytest: command not found` | Install dev deps: `pip install -e ".[dev]"` |
| Want to cancel? | Press Ctrl+C - incomplete output file is auto-deleted |
| Still stuck after 20+ min? | Press Ctrl+C and try with a simpler profile like `standard-playback` |

---

## 🎬 The Only Commands You Need

```bash
# Installation (one time)
pip install -e ".[dev]"

# Testing (before pushing)
pytest -v

# Formatting (before committing)
black bulletproof tests

# Using it with progress
buletproof tui

# Extending it
# (edit files, test, commit, push)

# Releasing it
git tag v0.2.0 && git push origin v0.2.0
```

---

## 💡 What's Different Now

**Before:** "Is it stuck? Should I Ctrl+C?"

**After:** 
```
Progress: |████████████░░░░░░░░░░░░░░░░░░░░░░░░| 35.2%
```
✅ You see exactly where you are in the process!

---

## 🚀 Next Steps

1. Pull latest changes
2. Test TUI with progress: `bulletproof tui`
3. Notice the progress bar during transcode
4. Try Ctrl+C - file cleans up automatically
5. Try different profiles with smart naming

🎯 **You now have a professional, user-friendly video transcode tool!**
