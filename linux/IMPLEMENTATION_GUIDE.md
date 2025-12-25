# Linux Port Implementation Guide

## Overview

This document explains the structure of the Linux port and how to integrate, maintain, and extend it.

## Architecture

```
linux/
├── install.sh                 # Setup script (dependency check + config init)
├── profiles.json              # Profile catalog (7 prebuilt profiles)
├── README.md                  # Full documentation (installation, usage, troubleshooting)
├── QUICK_START.md             # Quick reference (1-liners, common workflows)
├── IMPLEMENTATION_GUIDE.md    # This file (technical integration guide)
└── scripts/
    ├── transcode.sh           # Single-file transcoding (main utility)
    ├── batch.sh               # Batch directory processing
    ├── analyze.sh             # Video inspection (ffprobe wrapper)
    ├── list-profiles.sh       # Display available profiles
    └── config.sh              # Config management (defaults, settings)
```

## File Purposes

### `profiles.json` (Core Profile Catalog)

**Purpose:** Single source of truth for all transcoding profiles and speed presets.

**Structure:**
```json
{
  "version": "1.0.0",
  "metadata": { ... },
  "profiles": {
    "profile-name": {
      "name": "profile-name",
      "codec": "h264",
      "codec_profile": "high",
      "bitrate": "15M",
      "preset": "fast|medium|slow",
      "extension": "mp4|mkv|mov",
      "quality": 1-100,
      "description": "Human description",
      "use_case": "When to use this profile",
      "speed_estimate": "Expected encode time",
      "notes": "Additional notes"
    }
  },
  "speed_presets": {
    "fast": { ... },
    "normal": { ... },
    "slow": { ... }
  }
}
```

**How Scripts Use It:**
- `transcode.sh` reads profile codec and parameters
- `list-profiles.sh` displays available profiles
- `config.sh` validates against available profiles
- All scripts use `jq` to parse JSON

**To Add a New Profile:**
1. Add entry to `profiles.json` under `.profiles`
2. If new codec, update `transcode.sh` with ffmpeg command builder
3. Run `./list-profiles.sh` to verify

### Script Responsibilities

#### `transcode.sh` (Main Transcoding Engine)

**Responsibilities:**
- Parse CLI arguments (input, profile, output, preset)
- Load profile from `profiles.json`
- Validate inputs (file exists, not overwriting, etc.)
- Build ffmpeg command based on codec
- Execute transcode with progress tracking
- Output filename auto-generation with `__processed__` marker
- Safety features (no overwrite without --overwrite, prevent input==output)

**Codec Handlers:**
Each codec has a case block that sets ffmpeg arguments:
```bash
case "$CODEC" in
    h264)
        FFMPEG_ARGS=(
            "-c:v" "libx264"
            "-preset" "$FFMPEG_PRESET"
            "-profile:v" "$CODEC_PROFILE"
            "-b:v" "$BITRATE"
            "-c:a" "aac"
            "-b:a" "192k"
        )
        ;;
    # ... more codecs
esac
```

**To Add a New Codec:**
1. Add profile to `profiles.json` with new codec name
2. Add case block to `transcode.sh` with ffmpeg command
3. Test with sample video
4. Update README.md with codec notes

#### `batch.sh` (Batch Processing)

**Responsibilities:**
- Find files matching pattern in directory
- Call `transcode.sh` for each file
- Track success/failure counts
- Handle Ctrl+C cleanup
- Create output directory if needed
- Dry-run mode for preview

**Key Features:**
- Trap handler for graceful cleanup on interrupt
- File discovery via `find` with glob patterns
- Progress counter (N/TOTAL)
- Error handling and summary

#### `analyze.sh` (Video Inspection)

**Responsibilities:**
- Call ffprobe to extract metadata
- Display human-readable or JSON output
- Show codec, resolution, fps, bitrate, audio, subtitles

**Key Features:**
- Optional `--json` flag for machine parsing
- Uses jq for output formatting
- Informative help for profile selection

#### `list-profiles.sh` (Profile Display)

**Responsibilities:**
- Parse `profiles.json`
- Display profiles in table format
- Optional verbose mode with full details

**Key Features:**
- Uses `jq` for JSON parsing
- Column formatting for clean output
- Shows speed presets

#### `config.sh` (Configuration Management)

**Responsibilities:**
- Initialize `~/.bulletproof-linux/config.json`
- Get/set default profile
- Get/set default output directory
- Reset to defaults

**Key Features:**
- Validates profile exists in `profiles.json`
- Path expansion (~ to $HOME)
- JSON editing via jq

### `install.sh` (Setup Utility)

**Responsibilities:**
- Check for ffmpeg, ffprobe, jq
- Make scripts executable
- Create config directory
- Symlink profiles.json to config directory
- Provide installation guidance

**Key Features:**
- Detects Linux distribution
- Suggests appropriate install commands
- Colored output for readability
- Non-blocking (allows missing deps with warning)

---

## Integration with Main Repository

### Current Branch: `linux-port-dev`

All Linux port code is in a separate branch. To integrate:

1. **Test on multiple Linux distros:**
   - Ubuntu 22.04 LTS
   - Fedora 39
   - Debian 12
   - Alpine (if container use-case)

2. **Merge strategy:**
   - When stable, merge to `main`
   - OR keep as feature branch for parallel development
   - OR merge and maintain `linux/` as separate subsystem

3. **Update main README:**
   - Add section linking to `linux/README.md`
   - Mention "Linux users: See `linux/` directory"
   - Keep macOS/Python version as primary for backward compatibility

### Directory Structure in Main Repo

**Option A: Keep separate (recommended for parallel development)**
```
bulletproof-video-playback/
├── README.md                      # Main readme
├── CHANGELOG.md
├── bulletproof/                   # Python macOS/cross-platform
│   ├── core/
│   ├── cli/
│   └── tui/
├── linux/                         # Linux-native bash scripts
│   ├── README.md
│   ├── QUICK_START.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── install.sh
│   ├── profiles.json
│   └── scripts/
│       ├── transcode.sh
│       ├── batch.sh
│       ├── analyze.sh
│       ├── list-profiles.sh
│       └── config.sh
└── tests/
```

**Option B: Merge into main (future, post-v1.0)**
```
bulletproof-video-playback/
├── README.md                      # Links to both
├── setup.sh                       # Multi-platform setup
├── python/                        # Renamed from bulletproof/
└── bash/                          # Renamed from linux/
```

## Development Workflow

### Adding a New Profile

1. **Edit `linux/profiles.json`:**
   ```json
   "my-profile": {
     "name": "my-profile",
     "codec": "h264",
     "codec_profile": "high",
     "bitrate": "12M",
     "preset": "medium",
     "extension": "mp4",
     "quality": 80,
     "description": "My custom profile",
     "use_case": "When to use",
     "speed_estimate": "Time estimate",
     "notes": "Any notes"
   }
   ```

2. **If new codec, update `linux/scripts/transcode.sh`:**
   ```bash
   "my-new-codec")
       FFMPEG_ARGS=(
           "-c:v" "my_encoder"
           "-preset" "$FFMPEG_PRESET"
           # ... more options
       )
       ;;
   ```

3. **Test:**
   ```bash
   ./scripts/list-profiles.sh                    # Should show new profile
   ./scripts/transcode.sh test.mov --profile my-profile --verbose
   ```

4. **Document:**
   - Add to README.md profiles table
   - Update any examples if relevant

### Adding Support for a New Codec

1. **Verify ffmpeg supports it:**
   ```bash
   ffmpeg -codecs | grep codec_name
   ```

2. **Create profile(s) in `profiles.json`**

3. **Add case block to `transcode.sh`:**
   ```bash
   "new-codec")
       FFMPEG_ARGS=(
           "-c:v" "encoder_name"
           # ffmpeg-specific options
       )
       ;;
   ```

4. **Test with sample video**

5. **Document codec in README** (requirements, compatibility, etc.)

### Testing Checklist

- [ ] Dependencies installed on clean system
- [ ] `./install.sh` runs without errors
- [ ] `./scripts/list-profiles.sh` shows all profiles
- [ ] `./scripts/analyze.sh test.mov` works
- [ ] `./scripts/transcode.sh test.mov --profile live-h264-linux` works
- [ ] `./scripts/batch.sh ./test_dir --profile standard-playback` works
- [ ] `./scripts/config.sh show` works
- [ ] Output file naming correct (`__processed__` marker)
- [ ] Ctrl+C cleanup works (incomplete files deleted)
- [ ] Error messages are helpful
- [ ] `--help` on all scripts is clear

### Testing on Multiple Distros

```bash
# Docker test (Ubuntu 22.04)
docker run -it ubuntu:22.04 bash
apt update && apt install -y git ffmpeg jq
git clone https://github.com/KnowOneActual/bulletproof-video-playback.git
cd bulletproof-video-playback/linux && bash install.sh
./scripts/list-profiles.sh

# Fedora
docker run -it fedora:39 bash
dnf install -y git ffmpeg jq
# ... repeat steps
```

---

## Performance Considerations

### FFmpeg Encoding Speed

**Bottlenecks (in order of impact):**
1. **CPU** - Main bottleneck. FFmpeg is single-threaded per encoding instance
2. **Disk I/O** - Input read speed, output write speed
3. **Memory** - Usually not a constraint unless system is swapping

**Optimization Tips:**
- Fast preset uses veryfast (faster encode, lower quality)
- Slow preset uses slow (slower encode, better quality)
- For 2-hour video: ~15-20 minutes per quality tier difference
- Parallel encodes can be done via multiple batch.sh instances (different profiles/output dirs)

### Script Performance

**Bash script overhead is minimal:**
- `transcode.sh`: ~50ms to parse and launch ffmpeg
- `batch.sh`: ~500ms-1s per file discovery and setup
- `analyze.sh`: ~100-200ms (ffprobe call)

Bottleneck is always ffmpeg encoding itself, not script overhead.

---

## Maintenance

### Regular Updates

1. **Monitor ffmpeg updates** - New codecs, performance improvements
2. **Update profiles.json** if new profiles would be useful
3. **Review issues** - User feedback on profiles, codec support
4. **Test on new distro versions** (Ubuntu 24.04, Fedora 40, etc.)

### Backward Compatibility

- Keep existing profile names (don't rename)
- Add new profiles instead of modifying existing ones
- If you must change a profile, create a migration note in CHANGELOG
- Scripts should always handle missing codecs gracefully

### Version Numbering

Use semantic versioning in `profiles.json.version`:
- `1.0.0` - Current version
- `1.0.1` - Bug fix (new profile, codec fix)
- `1.1.0` - Minor feature (new script command)
- `2.0.0` - Breaking change (rename profile, remove old codec)

---

## FAQ for Maintainers

**Q: Should ProRes be supported?**
A: Only if ffmpeg has libprores support and user explicitly needs it. Currently archival-prores-alt is optional.

**Q: What about GPU acceleration?**
A: Not in default scripts, but documented as optional. Users can modify transcode.sh to add `-c:v h264_nvenc` etc.

**Q: Why Bash and not Python?**
A: Users can't install Python on machines they don't own. Pure Bash + FFmpeg removes that barrier.

**Q: Why JSON for profiles instead of YAML or TOML?**
A: jq is standard on Linux systems and more portable than Python/YAML parsers.

**Q: How do I handle Windows users?**
A: Windows ffmpeg tools exist (ffmpeg.org, Chocolatey). Bash scripts work on WSL2. But this is outside current Linux port scope.

**Q: Should we create a Docker image?**
A: Yes, as optional convenience. Maintains portability while simplifying dependency issues.

---

## Future Enhancements

1. **GPU acceleration** (NVIDIA NVENC, AMD AMF) - optional profiles
2. **Hardware-specific presets** (RPi, Jetson, etc.)
3. **Interactive TUI** - If demand exists, write a simple bash TUI
4. **systemd service** - Background transcoding daemon
5. **Docker image** - Pre-built container with all dependencies
6. **Package distribution** - AUR, Copr, PPAs
7. **Monitoring/logging** - Better progress tracking, log files
8. **Resume capability** - Pause/resume transcodes

---

## Contributing Guidelines

1. **Fork the repo**
2. **Branch from `linux-port-dev`:**
   ```bash
   git checkout -b linux-port-dev
   git checkout -b my-feature
   ```
3. **Test thoroughly** (see Testing Checklist)
4. **Document changes** (update README if new feature)
5. **Submit PR** against `linux-port-dev` branch
6. **Wait for review** - Maintainers test on multiple distros

---

## License

Linux port maintains MIT license from parent project.

All contributions retain MIT license.

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Maintained By:** KnowOneActual (Beau Bremer)
