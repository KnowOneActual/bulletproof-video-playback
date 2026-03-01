# Bulletproof Video Playback - Linux Port

> Professional video transcoding for live playback, streaming, and archival on Linux
>
> **No Python required** — Pure Bash + FFmpeg workflow

## Overview

This is a **Linux-native** implementation of bvp video playback, designed for users who:
- Can't install Python on machines they don't own
- Need a lightweight transcoding workflow without dependencies
- Want battle-tested ffmpeg profiles optimized for live playback and streaming
- Prefer simple shell scripts they can audit and modify

**Key differences from the macOS/Python version:**
- ✅ No ProRes requirement (uses H.264/H.265 instead)
- ✅ Pure Bash + FFmpeg (no Python)
- ✅ Portable across Debian, Ubuntu, Fedora, and other Linux distributions
- ✅ Simple JSON-based profile catalog
- ✅ Four core scripts: `transcode.sh`, `batch.sh`, `analyze.sh`, `config.sh`

---

## Installation

### Prerequisites

**Required:**
- `bash` (included on all Linux systems)
- `ffmpeg` (video transcoding)
- `ffprobe` (video analysis, bundled with ffmpeg)
- `jq` (JSON parsing, lightweight utility)

**Optional:**
- `column` (better output formatting in `list-profiles.sh`)

### Linux Distribution Setup

#### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y ffmpeg jq
```

#### Fedora / RHEL / CentOS

```bash
sudo dnf install -y ffmpeg jq
```

#### Alpine

```bash
apk add --no-cache bash ffmpeg jq
```

#### Verify Installation

```bash
ffmpeg -version        # Should print version info
ffprobe -version       # Should print version info
jq --version          # Should print version info
```

### Getting the Scripts

#### Option 1: Clone the Repository

```bash
git clone https://github.com/KnowOneActual/bulletproof-video-playback.git
cd bulletproof-video-playback/linux/scripts
chmod +x *.sh
```

#### Option 2: Add to PATH (Recommended)

Make scripts available globally:

```bash
# Copy scripts to a directory in your PATH
cp /path/to/bulletproof-video-playback/linux/scripts/*.sh ~/.local/bin/
cp /path/to/bulletproof-video-playback/linux/profiles.json ~/.bvp-linux/

# Or symlink for easy updates
ln -s /path/to/bulletproof-video-playback/linux/scripts/*.sh ~/.local/bin/

# Ensure ~/.local/bin is in PATH (add to ~/.bashrc if needed)
export PATH="$HOME/.local/bin:$PATH"
```

---

## Quick Start

### 1. List Available Profiles

```bash
./list-profiles.sh
```

Output:
```
Available Transcoding Profiles for Linux
=========================================

Name                      Codec      Ext    Description
---                       ---        ---    ---
live-h264-linux           h264       mp4    H.264 for cross-platform live playback on Linux
standard-playback         h264       mp4    H.264 for general-purpose playback on Linux
stream-hd                 hevc       mp4    H.265/HEVC for 1080p streaming
stream-4k                 hevc       mp4    H.265/HEVC for 4K streaming
archival-lossless         ffv1       mkv    FFv1 lossless codec for long-term archival
archival-prores-alt       prores     mov    ProRes HQ for archive with broad compatibility
web-compat                h264       mp4    H.264 Baseline for maximum web compatibility

Speed Presets: fast | normal (default) | slow
Use ./transcode.sh --help for transcoding examples.
```

### 2. Analyze a Video File

Before transcoding, inspect the source video:

```bash
./analyze.sh video.mov
```

Output:
```
Video Analysis: video.mov
=

File Information:
  Size: 2048 MB
  Duration: 7200 seconds
  Bitrate: 4500 kbps
  Container: mov,mp4,m4a,3gp,3g2,mj2

Video Stream:
  Codec: h264 (profile: high)
  Resolution: 1920x1080
  Frame Rate: 30000/1001
  Pixel Format: yuv420p
  Bitrate: 4000 Mbps

Audio Stream(s):
  Stream 0: aac | 2ch @ 48000Hz | 192 kbps

Subtitle Stream(s):
  No subtitle stream found

TIP: Use this data to choose an appropriate transcoding profile.
```

### 3. Transcode a Single File

```bash
# Basic usage
./transcode.sh video.mov --profile live-h264-linux

# Custom output and preset
./transcode.sh video.mov --profile standard-playback --output playback.mp4 --preset fast

# Show full command (verbose mode)
./transcode.sh video.mov --profile live-h264-linux --verbose
```

**Output:**
```
Bulletproof Video Playback - Linux Transcoder
=
Profile:       live-h264-linux
Input:         video.mov
Output:        video__processed__live-h264-linux.mp4
Codec:         h264 (profile: high)
Bitrate:       15M
Speed Preset:  normal (ffmpeg: medium)

Processing...

✓ Transcode complete!
  Output: video__processed__live-h264-linux.mp4 (1.2G)

Next steps:
  1. Test playback on your target device
  2. Keep original file for archival
  3. Delete if satisfied (output marked with __processed__ for easy identification)
```

### 4. Batch Process a Directory

```bash
# Batch transcode all files in a directory
./batch.sh ./videos --profile standard-playback

# Dry run first (preview what will be processed)
./batch.sh ./videos --profile live-h264-linux --dry-run

# Process specific file types
./batch.sh ./footage --profile standard-playback --pattern "*.mov"

# Transcode to a different output directory
./batch.sh ./raw_footage --profile live-h264-linux --output-dir ./processed
```

### 5. Manage Configuration

```bash
# View current settings
./config.sh show

# Set a default profile
./config.sh set-profile live-h264-linux

# Set a default output directory
./config.sh set-output-dir ~/Videos/processed

# Reset to defaults
./config.sh reset
```

Configuration is stored in `~/.bvp-linux/config.json`.

---

## Profiles Reference

### Live Playback

**`live-h264-linux`** (Recommended for live event playback/QLab replacement)
- Codec: H.264 (High profile)
- Bitrate: 15 Mbps
- Extension: `.mp4`
- Quality: 85/100
- Speed: 4–6 hours for 2-hour video (normal preset)
- Use case: Cross-platform live playback (QLab-like, Miccia Player, any H.264-capable player)
- Notes: Universal codec, widely supported on Linux, streaming clients, and embedded systems.

**`standard-playback`**
- Codec: H.264 (Main profile)
- Bitrate: 10 Mbps
- Extension: `.mp4`
- Quality: 75/100
- Speed: 5–7 hours for 2-hour video (normal preset)
- Use case: Archive playback, bandwidth-constrained networks
- Notes: Good balance of quality and file size.

### Streaming

**`stream-hd`**
- Codec: H.265/HEVC (Main profile)
- Bitrate: 6 Mbps
- Extension: `.mp4`
- Quality: 80/100
- Speed: 6–8 hours for 2-hour video (normal preset)
- Use case: 1080p streaming, OTT platforms
- Notes: Smaller file sizes, but requires modern client support (check compatibility).

**`stream-4k`**
- Codec: H.265/HEVC (Main 10-bit profile)
- Bitrate: 15 Mbps
- Extension: `.mp4`
- Quality: 90/100
- Speed: 8–12 hours for 2-hour video (normal preset)
- Use case: 4K streaming, high-bandwidth networks
- Notes: Requires ffmpeg built with libx265; modern clients only.

### Archival

**`archival-lossless`** (Best for long-term storage)
- Codec: FFv1 (Lossless)
- Bitrate: Unlimited (typically 100–300 Mbps)
- Extension: `.mkv`
- Quality: 100/100
- Speed: 10–15 hours for 2-hour video (slow preset)
- Use case: Long-term digital preservation, legal archival
- Notes: Lossless, royalty-free, no licensing concerns. File sizes are large but future-proof.

**`archival-prores-alt`** (If available)
- Codec: ProRes HQ
- Bitrate: 500 Mbps
- Extension: `.mov`
- Quality: 98/100
- Speed: 7–10 hours for 2-hour video (slow preset)
- Use case: Professional archival, migration from macOS workflows
- Notes: Requires ffmpeg compiled with libprores. Check with `ffmpeg -codecs | grep prores`.

### Web / Maximum Compatibility

**`web-compat`**
- Codec: H.264 (Baseline profile)
- Bitrate: 3 Mbps
- Extension: `.mp4`
- Quality: 60/100
- Speed: 3–4 hours for 2-hour video (fast preset)
- Use case: Web embedding, older browsers, mobile devices
- Notes: Baseline profile ensures maximum compatibility at the cost of quality.

---

## Speed Presets Explained

Each profile can be encoded at different speeds:

| Preset | ffmpeg Setting | Quality Loss | When to Use |
|--------|----------------|--------------|-------------|
| **fast** | veryfast | -5% to -10% | Live event deadline is tight, minimal quality loss acceptable |
| **normal** | medium | baseline | Most use cases, default, good quality-to-time tradeoff |
| **slow** | slow | +5% (better) | Archival, maximum quality, encode time is not critical |

**Examples:**

```bash
# Fast encode for urgent live playback (30 min for 1-hour video)
./transcode.sh long_video.mov --profile live-h264-linux --preset fast

# Balanced encode (default, ~45 min for 1-hour video)
./transcode.sh long_video.mov --profile live-h264-linux --preset normal

# Slow, high-quality encode for archival (1.5 hrs for 1-hour video)
./transcode.sh long_video.mov --profile archival-lossless --preset slow
```

---

## Workflow Examples

### Scenario 1: Live Event Playback (QLab Replacement)

```bash
# 1. Analyze the incoming video
./analyze.sh incoming_footage.mov

# 2. Transcode for live playback
./transcode.sh incoming_footage.mov --profile live-h264-linux --preset fast

# 3. Test on playback system (QLab, Miccia, or VLC)
# If OK, keep output; if issues, try different profile

# 4. Archive original
mv incoming_footage.mov /archive/originals/
```

### Scenario 2: Batch Ingest + Archive

```bash
# 1. Dry run to see what will be processed
./batch.sh /mnt/camera_footage --profile standard-playback --dry-run

# 2. Process all MOV files to processed directory
./batch.sh /mnt/camera_footage --profile standard-playback --output-dir ./processed --pattern "*.mov"

# 3. Verify outputs in processed/ directory
# 4. Move originals to archival storage
```

### Scenario 3: Streaming Preparation

```bash
# 1. Analyze source
./analyze.sh master_edit.mov

# 2. Encode for 1080p streaming (H.265, smaller files)
./transcode.sh master_edit.mov --profile stream-hd

# 3. Upload to CDN
upload_to_cdn master_edit__processed__stream-hd.mp4
```

### Scenario 4: Long-Term Archival (Lossless)

```bash
# 1. Transcode to lossless FFv1 (future-proof)
./transcode.sh raw_footage.mov --profile archival-lossless --preset slow

# 2. Verify output integrity
ffprobe raw_footage__processed__archival-lossless.mkv

# 3. Store on archival media (LTO tape, cold storage, etc.)
```

---

## Troubleshooting

### "ffmpeg not found"

**Error:**
```
Error: ffmpeg is required but not installed.
```

**Solution:**
```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# Fedora/RHEL
sudo dnf install ffmpeg

# Verify
ffmpeg -version
```

### "jq not found"

**Error:**
```
Error: jq is required but not installed.
```

**Solution:**
```bash
# Debian/Ubuntu
sudo apt install jq

# Fedora/RHEL
sudo dnf install jq

# Verify
jq --version
```

### Transcode is very slow or doesn't show progress

**Symptom:** Transcode runs but no progress bar appears, takes much longer than expected.

**Cause:** ffmpeg needs to read video metadata. Some MOV files lack duration information.

**Solution:**
1. Let the transcode continue (it's working!)
2. Check CPU usage with `top` or `htop` — if ffmpeg is using CPU, it's transcoding
3. Use `--verbose` flag to see ffmpeg output:
   ```bash
   ./transcode.sh video.mov --profile live-h264-linux --verbose
   ```
4. For future files, re-encode the source with a tool like HandBrake first (adds metadata)

### Output file is corrupted or won't play

**Cause:** Transcode was interrupted or failed (power loss, Ctrl+C, disk full).

**Solution:**
1. Delete the incomplete output file (marked with `__processed__` in filename)
2. Re-run transcode with `--preset fast` to test quickly
3. If still failing, try a different profile:
   ```bash
   ./transcode.sh video.mov --profile web-compat --preset fast
   ```
4. Check disk space:
   ```bash
   df -h
   ```

### "Profile not found in profiles.json"

**Error:**
```
Error: Profile 'custom-profile' not found in profiles.json
```

**Solution:**
1. List available profiles:
   ```bash
   ./list-profiles.sh
   ```
2. Use one of the listed profiles
3. To add a custom profile, edit `profiles.json` directly (see Custom Profiles section below)

### File already exists error

**Error:**
```
Error: Output file already exists: output.mp4
Use --overwrite to replace it, or specify a different --output filename.
```

**Solution:**

Option 1: Use `--overwrite` flag (replace existing file):
```bash
./transcode.sh video.mov --profile live-h264-linux --overwrite
```

Option 2: Specify a new output filename:
```bash
./transcode.sh video.mov --profile live-h264-linux --output output_v2.mp4
```

### Performance troubleshooting

If transcoding is slower than expected:

1. **Check CPU usage:**
   ```bash
   top  # Press 'q' to exit
   # Or use htop (apt install htop)
   ```
   If ffmpeg is NOT using CPU, something is blocking it (I/O, memory).

2. **Check disk I/O:**
   ```bash
   iostat -x 1  # Shows disk utilization every 1 second
   ```
   If `%util` is 100%, disk is bottleneck. Try moving output to faster storage.

3. **Check available disk space:**
   ```bash
   df -h
   ```
   Need at least 2–3x the video file size free for temporary encoding.

4. **Try a faster preset:**
   ```bash
   ./transcode.sh video.mov --profile live-h264-linux --preset fast
   ```

5. **Check system load:**
   ```bash
   uptime
   ```
   If load average is very high, other processes are consuming resources. Close them if possible.

---

## Custom Profiles

You can add custom transcoding profiles by editing `profiles.json`. Each profile is a JSON object in the `.profiles` section.

### Profile Template

```json
"my-custom-profile": {
  "name": "my-custom-profile",
  "codec": "h264",
  "codec_profile": "high",
  "bitrate": "10M",
  "preset": "medium",
  "extension": "mp4",
  "quality": 80,
  "description": "My custom transcoding profile",
  "use_case": "Describe when to use this profile",
  "speed_estimate": "Medium (5-6 hrs for 2hr video)",
  "notes": "Any additional notes or requirements"
}
```

### Example: Add a Mobile-Optimized Profile

Edit `profiles.json` and add under `.profiles`:

```json
"mobile-hd": {
  "name": "mobile-hd",
  "codec": "h264",
  "codec_profile": "baseline",
  "bitrate": "2M",
  "preset": "fast",
  "extension": "mp4",
  "quality": 70,
  "description": "H.264 for mobile streaming (small file size)",
  "use_case": "Mobile device delivery, limited bandwidth",
  "speed_estimate": "Fast (2-3 hrs for 2hr video)",
  "notes": "Baseline profile for maximum mobile compatibility"
}
```

Then use it:
```bash
./transcode.sh video.mov --profile mobile-hd
```

### Supported Codecs in transcode.sh

Currently implemented:
- `h264` — H.264 (via libx264)
- `hevc` — H.265/HEVC (via libx265)
- `ffv1` — FFv1 lossless (via ffv1 encoder)
- `prores` — ProRes (via prores_hq)

To add a new codec:
1. Add profile to `profiles.json`
2. Edit `transcode.sh` and add a `case` block in the ffmpeg command builder section
3. Test the new profile

---

## Advanced Usage

### Using with Shell Scripts / Automation

The scripts are fully scriptable. Example cron job to transcode nightly:

```bash
#!/bin/bash
# nightly-transcode.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="/mnt/incoming/footage"
OUTPUT_DIR="/mnt/archive/processed"
PROFILE="standard-playback"
LOG_FILE="/var/log/transcode.log"

echo "[$(date)] Starting batch transcode..." >> "$LOG_FILE"

"${SCRIPT_DIR}/batch.sh" "$INPUT_DIR" \
    --profile "$PROFILE" \
    --output-dir "$OUTPUT_DIR" \
    --preset normal >> "$LOG_FILE" 2>&1

echo "[$(date)] Batch transcode complete." >> "$LOG_FILE"
```

Then add to crontab:
```bash
crontab -e
# Add line:
# 0 2 * * * /usr/local/bin/nightly-transcode.sh
```

### GPU Acceleration (Optional)

If your system has an NVIDIA or AMD GPU, you can use GPU-accelerated encoding:

**NVIDIA NVENC:**
```bash
# Check if hardware is available
ffmpeg -codecs | grep h264_nvenc

# Modify transcode.sh, change h264 case to use h264_nvenc:
# "-c:v" "h264_nvenc" instead of "libx264"
```

**AMD AMF:**
```bash
ffmpeg -codecs | grep h264_amf
```

GPU encoding is much faster but quality/bitrate control is different. Requires ffmpeg built with GPU support.

### Docker Usage

Run scripts in Docker container with all dependencies:

```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y ffmpeg jq curl
COPY linux/scripts /app/scripts
COPY linux/profiles.json /app/
WORKDIR /app
CMD ["/app/scripts/list-profiles.sh"]
```

Build and run:
```bash
docker build -t bvp-linux .
docker run -v /path/to/videos:/videos bvp-linux /app/scripts/transcode.sh /videos/input.mov --profile live-h264-linux
```

---

## Differences from macOS/Python Version

| Feature | macOS (Python) | Linux (Bash) |
|---------|----------------|---------------|
| Language | Python 3.9+ | Bash (no Python) |
| Dependencies | Python, ffmpeg, ffprobe | ffmpeg, ffprobe, jq |
| ProRes Support | Full (macOS native) | Optional (if ffmpeg has libprores) |
| Installation | `pip install bulletproof-video-playback` | Copy scripts + chmod +x |
| Profiles | Python-defined | JSON catalog |
| TUI (Interactive) | Yes (click-based) | No (CLI only, but simple) |
| Config | ~/.bvp/config.json | ~/.bvp-linux/config.json |
| Customization | Edit Python files | Edit JSON + Bash scripts |
| Output | Real-time progress bar | FFmpeg progress (--verbose) |

---

## FAQ

**Q: Can I use this on machines I don't own (without installing Python)?**

A: Yes! This is the main use case. Only ffmpeg, ffprobe, and jq are required (often already installed on Linux systems).

**Q: What if ffmpeg is not installed and I can't use `apt` / `dnf`?**

A: You have a few options:
1. Compile ffmpeg from source (if you have build tools)
2. Use a pre-built static ffmpeg binary (ffmpeg.org)
3. Use Docker/Podman with a pre-built image containing ffmpeg
4. Use the macOS/Python version (if on a Mac where you can install Python)

**Q: Can I modify the profiles?**

A: Yes, edit `profiles.json` directly. Add new profiles, change bitrates, etc. Re-run scripts and changes are reflected.

**Q: How do I check if a codec (e.g., ProRes) is available?**

A: Run:
```bash
ffmpeg -codecs | grep prores   # For ProRes
ffmpeg -codecs | grep h264     # For H.264
ffmpeg -codecs | grep hevc      # For H.265
```

**Q: Can I automate batch processing?**

A: Yes, use cron jobs or systemd timers with the `batch.sh` script (see Advanced Usage section).

**Q: What's the difference between "normal" and "slow" presets?**

A: "slow" uses better encoding algorithms and takes 1.5–2x longer but produces slightly better quality. "fast" is quicker but slightly lower quality. "normal" is a balance.

---

## Contributing

Have improvements or new profiles? Open a pull request on [GitHub](https://github.com/KnowOneActual/bulletproof-video-playback).

---

## License

MIT License — See parent repository for details.

---

## Support & Resources

- **GitHub Issues:** [bulletproof-video-playback issues](https://github.com/KnowOneActual/bulletproof-video-playback/issues)
- **FFmpeg Documentation:** [ffmpeg.org](https://ffmpeg.org)
- **FFmpeg Wiki:** [trac.ffmpeg.org](https://trac.ffmpeg.org)

---

**Last Updated:** December 2025
**Version:** 1.0.0
**Tested On:** Ubuntu 22.04 LTS, Fedora 39, Debian 12
