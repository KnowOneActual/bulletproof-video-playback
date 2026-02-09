# TUI Deprecation Notice

## ⚠️ The TUI is Being Removed

The Terminal User Interface (TUI) has been **deprecated** and will be **removed in v3.0.0**.

## Why?

1. **Limited Use Case** - Most workflows use CLI or automation
2. **Better Alternatives** - Web Dashboard (Phase 3.1) provides superior UX
3. **Maintenance Burden** - Resources better spent on core features
4. **User Preference** - Power users prefer CLI, casual users want GUI

## Migration Path

### For Single File Transcoding

**Old (TUI):**
```bash
bulletproof tui
# Interactive prompts...
```

**New (CLI):**
```bash
bulletproof transcode input.mov --profile live-qlab
bulletproof transcode input.mov --profile stream-hd --output custom_output.mp4
```

### For Analyzing Videos

**Old (TUI):**
```bash
bulletproof tui
# Select "Analyze a video file"
```

**New (CLI):**
```bash
bulletproof analyze input.mov
```

### For Batch Processing

**Old (TUI):**
```bash
bulletproof tui
# Select "Batch process a folder"
```

**New (CLI):**
```bash
bulletproof batch /path/to/videos --profile live-qlab
```

**Or (Folder Monitor):**
```bash
# Create monitor.yaml
bulletproof monitor start --config monitor.yaml
```

### For Interactive Workflows

**Coming Soon:**
Phase 3.1 Web Dashboard will provide:
- Visual file browser
- Real-time progress monitoring
- Drag-and-drop interface
- Queue management
- Much better UX than terminal-based TUI

## Timeline

| Version | Status | Action |
|---------|--------|--------|
| v2.5.0 | Current | TUI works with deprecation warning |
| v2.6.0 | Next | TUI continues to work, documentation updated |
| v3.0.0 | Future | **TUI REMOVED** (breaking change) |

## What Happens Now?

- **v2.5.0+**: TUI shows deprecation warning on startup
- Users must confirm to continue using TUI
- All documentation updated to recommend CLI/Monitor
- `feature/textual-tui` branch deleted (experimental rewrite cancelled)

## Need Help Migrating?

See:
- [CLI Documentation](../README.md#cli-command-line-interface)
- [Quick Reference](../QUICK_REFERENCE.md)
- [Monitor Documentation](../docs/phase-3.1/)

## Questions?

Open an issue: https://github.com/KnowOneActual/bulletproof-video-playback/issues
