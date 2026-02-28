# Scripts Directory Structure - Option 2 Implementation

## Overview

We've implemented **Option 2** to make universal tools (video analysis, profile browsing) visible at root level while maintaining platform-specific implementations.

---

## New Directory Structure

```
bulletproof-video-playback/
├── README.md                          # Main project readme
├── SCRIPTS_STRUCTURE.md              # This file (structural overview)
├── LINUX_PORT_SUMMARY.md             # Linux port overview
├── scripts/                           # 🕫 UNIVERSAL TOOLS (new!)
│   ├── README.md                     # Guide to scripts
│   ├── analyze.sh                    # 🔍 Analyze video (works on macOS+Linux)
│   ├── list-profiles.sh              # 📋 List profiles (works on macOS+Linux)
│   ├── profiles.json                 # 📄 Profile catalog (shared source)
│   └── linux/ → (symlinks to above)
├── linux/                            # Linux Bash implementation
│   ├── README.md
│   ├── QUICK_START.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── install.sh                    # Setup script (now creates symlinks)
│   ├── profiles.json                 # Symlink to ../scripts/profiles.json
│   └── scripts/
│       ├── transcode.sh                 # Linux-specific transcoder
│       ├── batch.sh                    # Linux-specific batch processor
│       ├── config.sh                   # Linux-specific config manager
│       ├── analyze.sh → ../../scripts/analyze.sh      (symlink)
│       ├── list-profiles.sh → ../../scripts/list-profiles.sh (symlink)
│       └── profiles.json → ../profiles.json (symlink)
├── bulletproof/                       # Python macOS/cross-platform
│   ├── __main__.py
│   ├── core/
│   ├── cli/
│   └── tui/
└── tests/
```

---

## What Changed

### 1. **New Root `scripts/` Directory**

```bash
scripts/
├── analyze.sh          # Video inspection (cross-platform)
├── list-profiles.sh    # Profile browser (cross-platform)
├── profiles.json       # Profile catalog (single source of truth)
└── README.md           # Guide to choosing tools by platform
```

**Benefits:**
- Visible in root directory on GitHub
- Mac users see tools immediately
- Shared `profiles.json` (no duplication)
- Universal tools work on any OS with ffmpeg + jq

### 2. **Symlinks in `linux/scripts/`**

Universal tools in `linux/scripts/` are now symlinks to `../../scripts/`:

```bash
linux/scripts/analyze.sh → ../../scripts/analyze.sh
linux/scripts/list-profiles.sh → ../../scripts/list-profiles.sh
linux/scripts/profiles.json → ../profiles.json
```

**Benefits:**
- Single source of truth (no duplication)
- Updates to root `scripts/` automatically reflected in `linux/scripts/`
- Maintains backward compatibility (users still run from `linux/scripts/`)
- Clean, transparent to users

### 3. **Updated `linux/install.sh`**

Install script now:
1. Creates symlinks for universal tools
2. Explains the structure
3. Maintains all existing functionality

```bash
# New logic in install.sh
ROOT_DIR="$(cd .. && pwd)"
ln -s "${ROOT_DIR}/scripts/analyze.sh" "scripts/analyze.sh"
ln -s "${ROOT_DIR}/scripts/list-profiles.sh" "scripts/list-profiles.sh"
```

---

## User Workflows

### Mac User Landing on Repo

1. Sees root `scripts/` folder
2. Reads `scripts/README.md`
3. Learns about Python version in main README
4. Uses Python version OR universal tools if desired

```bash
# Can use universal tools if ffmpeg installed
./scripts/analyze.sh video.mov
./scripts/list-profiles.sh

# Or use Python version (recommended)
pip install bulletproof-video-playback
python3 -m bvp
```

### Linux User Landing on Repo

1. Sees root `scripts/` folder with universal tools
2. Goes to `linux/` folder for full suite
3. Runs `bash install.sh` (sets up symlinks)
4. Gets access to both universal + Linux-specific tools

```bash
cd linux
bash install.sh

# Universal tools (now available via symlinks)
./scripts/analyze.sh video.mov
./scripts/list-profiles.sh

# Linux-specific tools
./scripts/transcode.sh video.mov --profile live-h264-linux
./scripts/batch.sh /path/to/videos --profile standard-playback
./scripts/config.sh show
```

### Both Platforms

Can use universal analysis tools without platform-specific setup:

```bash
# Just analyze (any platform with ffmpeg + jq)
chmod +x scripts/analyze.sh scripts/list-profiles.sh
./scripts/analyze.sh video.mov
./scripts/list-profiles.sh --verbose
```

---

## File Sharing Strategy

### Source of Truth

| File | Location | Why |
|------|----------|-----|
| `analyze.sh` | `scripts/analyze.sh` | Universal tool, maintain once |
| `list-profiles.sh` | `scripts/list-profiles.sh` | Universal tool, maintain once |
| `profiles.json` | `scripts/profiles.json` | Shared catalog, single source |
| `transcode.sh` | `linux/scripts/transcode.sh` | Linux-only, full path |
| `batch.sh` | `linux/scripts/batch.sh` | Linux-only, full path |
| `config.sh` | `linux/scripts/config.sh` | Linux-only, full path |

### Symlink Strategy

- Root `scripts/` = originals for universal tools
- `linux/scripts/` = symlinks for universal tools
- `linux/profiles.json` = symlink to root version
- Linux-specific scripts (transcode, batch, config) = originals in `linux/scripts/`

---

## Benefits of This Approach

✅ **Discoverability** - Mac users see tools immediately at root  
✅ **No Duplication** - Universal tools maintained in one place  
✅ **Backward Compatible** - Linux users still run from `linux/scripts/`  
✅ **Clean Structure** - Separation of concerns (universal vs platform-specific)  
✅ **Easy Maintenance** - Updates to root `scripts/` auto-reflected  
✅ **Cross-Platform** - Users on any OS can analyze videos without installing dependencies  
✅ **Future Proof** - Easy to add Windows/native support later  

---

## Implementation Details

### Symlink Creation

Done automatically by `linux/install.sh`:

```bash
#!/bin/bash
ROOT_DIR="$(cd .. && pwd)"

# Create symlinks for universal tools
ln -s "${ROOT_DIR}/scripts/analyze.sh" "scripts/analyze.sh"
ln -s "${ROOT_DIR}/scripts/list-profiles.sh" "scripts/list-profiles.sh"
```

### Path Resolution

Scripts use relative paths, so symlinks work transparently:

```bash
# In list-profiles.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILES_FILE="${SCRIPT_DIR}/profiles.json"  # Works from any location
```

### Verification

To verify symlinks are set up correctly:

```bash
cd linux/scripts
ls -la
# Should show:
# analyze.sh -> ../../scripts/analyze.sh
# list-profiles.sh -> ../../scripts/list-profiles.sh
```

---

## Potential Issues & Solutions

### Issue: Symlinks Don't Work on Windows

**Solution:** Windows users should use:
- WSL2 with Linux tools, OR
- Python version (native Windows support)

### Issue: Relative Symlinks Break After Move

**Solution:** Symlinks are relative, so moving repo maintains functionality.
Just keep the relative directory structure.

### Issue: Need to Update Universal Tool

**Solution:** Update in `scripts/` (source), automatically reflected everywhere.

```bash
# Edit once
vim scripts/analyze.sh

# Works in both locations
./scripts/analyze.sh  # root
./linux/scripts/analyze.sh  # via symlink
```

---

## Future Enhancements

1. **Add Windows Scripts** (when ready)
   ```
   windows/
   ├── transcode.ps1
   ├── batch.ps1
   └── (symlinks to universal tools)
   ```

2. **Create Wrapper Script**
   ```bash
   ./bulletproof.sh  # Auto-detects OS and runs correct version
   ```

3. **Package Distribution**
   - AUR, Copr, PPAs (Linux)
   - Homebrew (macOS)
   - Chocolatey (Windows)

---

## File Changes Summary

**New Files:**
- `scripts/README.md` — Guide to scripts
- `scripts/analyze.sh` — Universal video analysis
- `scripts/list-profiles.sh` — Universal profile browser
- `scripts/profiles.json` — Shared profile catalog

**Modified Files:**
- `linux/install.sh` — Now creates symlinks

**Symlinked Files:**
- `linux/scripts/analyze.sh` → `../../scripts/analyze.sh`
- `linux/scripts/list-profiles.sh` → `../../scripts/list-profiles.sh`
- `linux/profiles.json` → `../profiles.json` (already symlinked)

---

## Testing

### Quick Test

```bash
# From root
chmod +x scripts/*.sh
./scripts/analyze.sh /path/to/video.mov
./scripts/list-profiles.sh

# From linux/
cd linux
bash install.sh
./scripts/analyze.sh /path/to/video.mov  # Via symlink
./scripts/transcode.sh /path/to/video.mov --profile live-h264-linux
```

### Symlink Verification

```bash
cd linux/scripts
ls -la
# Output should show:
# analyze.sh -> ../../scripts/analyze.sh
# list-profiles.sh -> ../../scripts/list-profiles.sh
```

---

## Questions?

See:
- `scripts/README.md` — User-facing guide
- `linux/README.md` — Linux-specific documentation
- `LINUX_PORT_SUMMARY.md` — Overall port overview
- `linux/IMPLEMENTATION_GUIDE.md` — Technical details

---

**Implementation Date:** December 25, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete
