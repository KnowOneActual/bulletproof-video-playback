# Changelog

All notable changes to bulletproof-video-playback are documented in this file.

## [Unreleased]

### 🔄 Phase 3.1 - Web Dashboard (In Planning)

#### Added
- Complete Phase 3.1 planning documentation:
  - `PHASE-3.1-START-HERE.md` - Quick entry point
  - `PHASE-3.1-OVERVIEW.md` - Complete vision and timeline
  - `PHASE-3.1-QUICKSTART.md` - Day-by-day execution guide (15 days)
  - `PHASE-3.1-WEB-DASHBOARD.md` - Detailed technical specifications
  - `PHASE-3.1-TECH-DECISIONS.md` - Architecture and technology rationale
  - `PHASE-3.1-RESOURCES.md` - Curated external learning resources

#### Details
- Web dashboard for real-time monitoring of video transcoding
- Technology stack: FastAPI (backend) + React 18 (frontend) + WebSocket (real-time)
<<<<<<< HEAD
- Scope: MVP → Features → Production-ready
=======
- Timeline: 2-3 weeks (December 30, 2025 - January 17, 2026)
- Scope: MVP → Features → Production-ready
- Status: Ready to start building Monday, December 30
>>>>>>> 52b2595b245a368c63eda3a98f66381012ced8e1

---

## [2.4.0] - 2025-12-28 (In Progress)

### 🎉 Added - Phase 2.4: Folder Monitor + Queue System

#### Core Features
- **Folder Monitor** - Watch a folder for new video files
  - Hot-folder pattern for automatic video processing
  - Configuration-driven monitor setup
  - Real-time file detection
- **Job Queue** - Process videos asynchronously
  - FIFO queue management
  - Parallel job processing with worker pool
  - Job status tracking (pending, running, completed, failed)
  - Progress monitoring during transcoding
- **Rule Engine** - Route videos based on pattern matching
  - Glob-style pattern matching (*.mov, *.mp4, etc.)
  - Profile selection based on filename patterns
  - Graceful handling of zero rules
- **Configuration Management** - YAML-based configuration
  - Monitor folder path
  - Output folder path
  - Transcoding profiles
  - Rule definitions
  - Default fallback values

#### Architecture
- **MonitorService** - File system monitoring
- **JobQueue** - Job state and ordering
- **RuleEngine** - Pattern matching logic
- **ConfigLoader** - Configuration file parsing
- **Async/Await** - Non-blocking operations throughout

#### Testing
- 32 comprehensive test cases
  - Configuration loading and defaults
  - Rule engine pattern matching
  - Job queue operations
  - Monitor service integration
  - Edge cases (empty rules, missing config defaults)
- All tests passing: ✅ 32/32

#### CLI Integration
- `bulletproof monitor` - Start the folder monitor
- `--config` - Specify configuration file
- `--dry-run` - Test configuration without processing
- Full integration with existing transcoding profiles

### 📝 Changed

- **ConfigLoader Enhancement**:
  - Now sets sensible defaults when config values are missing
  - Default monitor folder: `./videos/incoming`
  - Default output folder: `./videos/output`
  - Prevents KeyError crashes on missing configuration keys
  - Fully backward compatible with existing config files

- **RuleEngine Robustness**:
  - Gracefully handles empty rules list
  - Returns `None` for passthrough mode (no matching rule)
  - No longer crashes on zero rules scenario
  - Supports optional rule configurations

### 🧪 Testing

- Fixed incomplete test files (cleaned up test output)
- All 32 tests passing with clean output
- No pytest warnings or noise
- Ready for production deployment

### 🚀 Production Readiness

- ✅ All tests passing (32/32)
- ✅ No known bugs or edge cases
- ✅ Graceful error handling
- ✅ Configuration with sensible defaults
- ✅ Comprehensive documentation
- ✅ Ready for Phase 3.1 (Web Dashboard)

---

## [0.2.0] - 2025-12-25

### 🎉 Added

#### Linux Bash Port 🐧
- **Pure Bash Implementation** - No Python required for Linux systems
  - 5 core scripts: `transcode.sh`, `batch.sh`, `analyze.sh`, `config.sh`, `list-profiles.sh`
  - Works on Debian, Ubuntu, Fedora, RHEL, CentOS, Alpine
  - Minimal dependencies: bash, ffmpeg, jq only
- **Universal Cross-Platform Tools** - Root `scripts/` folder
  - `analyze.sh` - Video analysis (works on macOS, Linux, WSL2)
  - `list-profiles.sh` - Profile browser (works on macOS, Linux, WSL2)
  - `profiles.json` - Shared profile catalog
- **Symlink Architecture** - Single-source maintenance
  - Linux scripts symlink to universal tools
  - Profile updates propagate automatically
  - No file duplication
- **Linux-Specific Profiles**:
  - `live-h264-linux` - H.264 for cross-platform live playback
  - `standard-playback` - H.264 for general playback
  - `stream-hd` - H.265 for 1080p streaming
  - `stream-4k` - H.265 for 4K streaming
  - `archival-lossless` - FFv1 lossless for long-term preservation
  - `archival-prores-alt` - ProRes HQ if available
  - `web-compat` - H.264 Baseline for maximum web compatibility
- **Production-Ready Installation**
  - `linux/install.sh` - Automated setup with dependency checking
  - Detects missing ffmpeg, ffprobe, jq
  - Provides OS-specific install instructions (apt, dnf, apk)
  - Creates symlinks automatically
  - Sets up config directory
- **Comprehensive Documentation**
  - `linux/QUICK_START.md` - User-facing guide with workflow examples
  - `linux/IMPLEMENTATION_GUIDE.md` - Technical details for developers
  - `SCRIPTS_STRUCTURE.md` - Architecture and symlink explanation
  - Updated main README with platform selection

#### Features
- Batch transcoding with `batch.sh`
- Video analysis with `analyze.sh`
- Configuration management with `config.sh`
- Speed presets (fast/normal/slow) on all platforms
- Cross-platform profile compatibility
- Smart output naming with `__processed__` marker

### 📝 Changed

- Updated main README.md to include Linux section
  - Added "Choose Your Platform" section
  - Explained Python vs Bash versions
  - Linked to Linux documentation
- Reorganized documentation structure for clarity

### 🔧 Technical

- New folder structure:
  - `linux/` - Linux Bash implementation
  - `scripts/` - Universal cross-platform tools
- Symlink strategy for zero duplication
- TSV-based output parsing for reliable formatting
- Compatible with existing Python implementation

### 🚀 Use Cases Enabled

- Transcoding on machines without Python installed
- Restricted environments where you can't install packages
- CI/CD pipelines that need lightweight transcoding
- Docker containers without Python
- WSL2 environments
- Systems where you can't modify installed software

---

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

### 📚 Documentation

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

## Version History Summary

### v2.4.0 - Folder Monitor + Queue System (In Progress)
- Automatic folder monitoring for video files
- Async job queue with worker pool
- Pattern-based rule engine for video routing
- Configuration management with sensible defaults
- 32 comprehensive tests, all passing
- Foundation for Phase 3.1 Web Dashboard

### v0.2.0 - Linux Bash Port + Universal Tools
- Complete Linux implementation with pure Bash
- Cross-platform universal tools (analyze, list-profiles)
- 7 Linux-optimized profiles
- Symlink-based architecture for single-source maintenance
- Comprehensive Linux documentation
- Production-ready on Fedora, Ubuntu, Debian

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
