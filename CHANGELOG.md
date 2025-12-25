# Changelog

All notable changes to bulletproof-video-playback are documented in this file.

## [Unreleased]

## [0.1.0] - 2024-12-25

### 🎉 Added

#### Core Features
- **Real-Time Progress Tracking** - Live progress bar during transcoding using ffmpeg's progress output
- **Duration Detection** - Automatically fetches video duration via ffprobe for accurate progress calculation
- **Smart Output Naming** - Auto-generates output filenames with:
  - Correct file extensions based on codec (`.mov` for ProRes, `.mp4` for H.264/H.265)
  - Profile name for easy identification (`__live-qlab`, `__stream-4k`)
  - `__processed__` marker to distinguish transcoded from original files
- **Safety Features**:
  - Prevents accidental overwrite of input files
  - Warns before overwriting existing output files
  - Auto-cleans incomplete files on Ctrl+C cancellation
  - Graceful error handling with clear messages

#### Profiles
- **7 Transcoding Profiles** (all codec-aware with auto-extension mapping):
  - `live-qlab` - ProRes Proxy for QLab on macOS (QLab recommended)
  - `live-prores-lt` - ProRes LT for live playback with smaller files
  - `live-h264` - H.264 for cross-platform theater
  - `standard-playback` - H.264 for Miccia Player, VLC, general use
  - `stream-hd` - H.265 for 1080p streaming
  - `stream-4k` - H.265 for 4K streaming
  - `archival` - ProRes HQ for long-term storage

#### Interfaces
- **TUI (Terminal User Interface)**:
  - Interactive mode with smart defaults
  - File path input with shell escape sequence handling
  - Profile selection with descriptions
  - Real-time progress display during transcode
  - Ctrl+C support with automatic cleanup
  - Same-folder output defaults
- **CLI (Command-Line Interface)**:
  - `bulletproof transcode` - Single file transcoding
  - `bulletproof analyze` - Video file analysis
  - `bulletproof batch` - Batch directory processing
  - `bulletproof tui` - Launch interactive TUI
- **Python API**:
  - `TranscodeJob` class for programmatic use
  - `list_profiles()` - Get all available profiles
  - `get_profile()` - Get profile by name
  - Progress tracking via `job.progress` attribute
  - Status tracking (pending, running, complete, error, cancelled)

#### Developer Experience
- Full test suite with pytest
- Black code formatting
- GitHub Actions CI/CD workflows:
  - Automated testing on every push
  - Automated releases to PyPI on version tags
- Type hints throughout codebase
- Comprehensive docstrings

### 💨 Technical Details

- **ffmpeg Integration**:
  - Dynamic command building based on profile
  - ProRes preset mapping (proxy=0, lt=1, hq=4)
  - H.264/H.265 preset support
  - Pixel format, frame rate, and scale filtering
  - Audio codec configuration
- **Progress Parsing**:
  - Regex-based extraction of elapsed time from ffmpeg output
  - Real-time progress bar with percentage and time display
  - Fallback to no-progress mode if duration unavailable
- **File Handling**:
  - Proper Path object usage for cross-platform compatibility
  - Shell escape sequence handling for filenames with special characters
  - Home directory expansion (`~`) support
  - Atomic file operations with cleanup on failure

### 🇑 Documentation

- Comprehensive README with quick start guides
- QUICK_REFERENCE.md for common tasks
- CHANGELOG.md (this file)
- Inline code documentation and docstrings
- Usage examples for all three interfaces
- Troubleshooting guide

### 🚧 Known Limitations

- Progress bar may not appear for videos without duration metadata (MOV files sometimes)
- Windows support untested (developed on macOS)
- ffprobe timing out defaults to no-progress mode gracefully

---

## Version History

### v0.1.0 - Initial Release
- Complete video transcoding suite with 7 profiles
- Three interfaces (CLI, TUI, Python API)
- Real-time progress tracking
- Safety features and smart defaults
- Professional-grade code quality
- CI/CD ready with GitHub Actions

---

## Contributing

See README.md for contribution guidelines.

## License

MIT License - see LICENSE file
