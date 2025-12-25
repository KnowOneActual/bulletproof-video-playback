# Bulletproof Video Playback (Linux) - Quick Start

**TL;DR for impatient folks:**

## 1-Minute Setup

```bash
# Install dependencies (Debian/Ubuntu)
sudo apt update && sudo apt install -y ffmpeg jq

# Or Fedora/RHEL
sudo dnf install -y ffmpeg jq

# Clone and setup
git clone https://github.com/KnowOneActual/bulletproof-video-playback.git
cd bulletproof-video-playback/linux
bash install.sh
```

## 1-Line Examples

### See available profiles
```bash
./scripts/list-profiles.sh
```

### Analyze a video
```bash
./scripts/analyze.sh video.mov
```

### Transcode for live event playback (QLab replacement)
```bash
./scripts/transcode.sh video.mov --profile live-h264-linux
```

### Transcode for streaming (1080p)
```bash
./scripts/transcode.sh video.mov --profile stream-hd
```

### Transcode for archival (lossless)
```bash
./scripts/transcode.sh video.mov --profile archival-lossless --preset slow
```

### Batch process a directory
```bash
./scripts/batch.sh /path/to/videos --profile standard-playback
```

### Dry run (preview what would be processed)
```bash
./scripts/batch.sh /path/to/videos --profile live-h264-linux --dry-run
```

### Check/set config
```bash
./scripts/config.sh show
./scripts/config.sh set-profile live-h264-linux
./scripts/config.sh set-output-dir ~/Videos/processed
```

## Speed Presets

```bash
# Fast (3-4 hrs for 2-hour video)
./scripts/transcode.sh video.mov --profile live-h264-linux --preset fast

# Normal/balanced (4-6 hrs for 2-hour video) - DEFAULT
./scripts/transcode.sh video.mov --profile live-h264-linux --preset normal

# Slow/high-quality (6-10 hrs for 2-hour video)
./scripts/transcode.sh video.mov --profile live-h264-linux --preset slow
```

## Profile Quick Reference

| Profile | Codec | Use Case | Speed |
|---------|-------|----------|-------|
| **live-h264-linux** | H.264 | Live event playback (QLab-like) | Medium |
| **standard-playback** | H.264 | General playback, archive | Medium |
| **stream-hd** | H.265 | 1080p streaming (smaller files) | Medium |
| **stream-4k** | H.265 | 4K streaming | Slow |
| **archival-lossless** | FFv1 | Long-term storage (future-proof) | Slow |
| **web-compat** | H.264 | Web/old browsers | Fast |

## Common Workflows

### Workflow 1: Single File for QLab
```bash
# Analyze first
./scripts/analyze.sh incoming.mov

# Transcode for live playback
./scripts/transcode.sh incoming.mov --profile live-h264-linux --preset fast

# Output: incoming__processed__live-h264-linux.mp4
```

### Workflow 2: Batch Ingest
```bash
# Preview what will be processed
./scripts/batch.sh /mnt/camera_footage --profile standard-playback --dry-run

# Process all files
./scripts/batch.sh /mnt/camera_footage --profile standard-playback --output-dir ./processed

# Check results
ls -lh processed/
```

### Workflow 3: Archive (Lossless)
```bash
# Encode once, future-proof
./scripts/transcode.sh master.mov --profile archival-lossless --preset slow

# Store on LTO tape or cold storage
# Output is ~300-500 MB per hour, uncompressed quality forever
```

## Troubleshooting

### "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora/RHEL
sudo dnf install ffmpeg
```

### Transcode is slow or no progress shown
```bash
# This is normal. Video metadata might be missing.
# Use --verbose to see ffmpeg output:
./scripts/transcode.sh video.mov --profile live-h264-linux --verbose

# Check CPU is being used:
top
# If ffmpeg is using >50% CPU, it's working fine.
```

### Output file is corrupted
```bash
# Try a different profile with fast preset:
./scripts/transcode.sh video.mov --profile web-compat --preset fast

# Or check disk space:
df -h
```

### Script permissions error
```bash
# Make scripts executable:
chmod +x scripts/*.sh
```

## Next Steps

- **Read full docs:** `cat README.md`
- **Test a transcode:** `./scripts/transcode.sh /path/to/test.mov --profile live-h264-linux --verbose`
- **Add to PATH:** `echo 'export PATH="'$(pwd)'/scripts:$PATH"' >> ~/.bashrc && source ~/.bashrc`
- **Customize profiles:** Edit `profiles.json`
- **Ask questions:** Check GitHub issues or README FAQ

---

**Made in Chicago** 🎬 | MIT License
