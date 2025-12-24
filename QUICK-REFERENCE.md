# 📋 Quick Reference Card

## 🎯 In 30 Seconds

**Your GitHub Repo:** https://github.com/KnowOneActual/bulletproof-video-playback

**What It Does:**
- Transcode videos for live playback + streaming + archival
- Professional Python project with CLI + TUI
- 7 profiles for different use cases
- Tests + GitHub Actions CI/CD included

---

## 🎮 How to Use (Three Ways)

### CLI (Fastest)
```bash
# List profiles
bulletproof transcode --list-profiles

# Transcode single file
bulletproof transcode input.mov --profile live-qlab --output output.mov

# Analyze video
bulletproof analyze input.mov
```

### TUI (Interactive)
```bash
bulletproof tui
# Navigate with arrows, select options, watch it encode
```

### Python API (Scripting)
```python
from bulletproof.core import TranscodeJob
from bulletproof.core.profile import get_profile

profile = get_profile("live-qlab")
job = TranscodeJob(Path("in.mov"), Path("out.mov"), profile)
job.execute()
```

---

## 🎬 The 7 Profiles

| # | Name | Codec | Size | Quality | Use When |
|---|------|-------|------|---------|----------|
| 1 | live-qlab | ProRes HQ | Huge | Max | QLab on Mac (live playback) |
| 2 | live-prores-lt | ProRes LT | Large | High | Live playback (space-conscious) |
| 3 | live-h264 | H.264 | Medium | High | Cross-platform live playback |
| 4 | standard-playback | H.264 | Small | Good | Miccia, VLC, web preview |
| 5 | stream-hd | H.265 | Tiny | Good | 1080p streaming |
| 6 | stream-4k | H.265 | Tiny | Good | 4K streaming |
| 7 | archival | ProRes HQ | Huge | Max | Long-term storage |

---

## 🛠️ What You Need

**Before Starting:**
- [ ] Python 3.9+ (`python --version`)
- [ ] ffmpeg (`ffmpeg -version`)
- [ ] Git (`git --version`)
- [ ] A text editor

---

## 💡 Key Insight

The project follows your philosophy:

> "What does this system need?" → Use that codec

```python
# Instead of debating codecs, we ask the system:

"Do you need live playback on Mac?"
→ Use ProRes HQ (live-qlab)

"Do you need cross-platform live playback?"
→ Use H.264 (live-h264)

"Do you need streaming?"
→ Use H.265 (stream-hd or stream-4k)

"Do you need long-term storage?"
→ Use ProRes HQ (archival)
```

Each profile is a prepackaged answer to that question.

---

## 🎬 The Only Commands You Need

```bash
# Installation (one time)
pip install -e ".[dev]"

# Testing (before pushing)
pytest -v

# Formatting (before committing)
black bulletproof tests

# Using it
bulletproof transcode input.mov --profile live-qlab

# Extending it
# (edit files, test, commit, push)

# Releasing it
git tag v0.2.0 && git push origin v0.2.0
```
