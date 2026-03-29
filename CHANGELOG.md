# Changelog

All notable changes to bulletproof-video-playback are documented in this file.
## [3.0.0] - 2026-02-28

### ⚡️ CLI Command Renamed: `bulletproof` → `bvp`

#### ⚠️ Breaking Changes
- **CLI Rename**: The main command-line interface has been renamed from `bulletproof` to `bvp` for easier typing and better ergonomics.
  - *Old:* `bulletproof transcode input.mov`
  - *New:* `bvp transcode input.mov`
- **Config Directory Rename**: Local configuration directories have been renamed to match the new command:
  - `~/.bulletproof` → `~/.bvp`
  - `~/.bulletproof-linux` → `~/.bvp-linux`
- **TUI Removal**: The deprecated Terminal User Interface has been completely removed.
- **Dependency Changes**: `textual` is no longer a dependency.

### 🧹 Repository Cleanup & Organization

#### Removed
- **TUI (Terminal User Interface)**:
  - Removed `bvp tui` command.
...
  - Deleted `bulletproof/tui` and `bulletproof/tui_textual` modules.
  - Removed `textual` dependency from `pyproject.toml`.
  - Deleted `docs/TUI_DEPRECATION.md` (no longer needed as a standalone guide).
- **Redundant Config**:
  - Deleted `setup.cfg` (settings consolidated in `pyproject.toml`).
- **Internal Tooling Tracking**:
  - Removed `GEMINI.md` and `.gemini/` directory from Git tracking (now local-only via `.gitignore`).

#### Fixed
- **.gitignore**:
  - Updated to properly ignore `.ruff_cache/`, `test_videos/`, and local AI tooling files.
  - Standardized structure and comments.

## [3.2.0] - 2026-03-17

### 🎭 QLab Performance Integration & Enhanced WebSockets

#### Added
- **Enhanced WebSockets**: Refactored the dashboard API to be fully event-driven.
    - **Broadcasting**: Added `ConnectionManager` to support multiple concurrent dashboard clients.
    - **Real-time Events**: WebSocket now pushes instant notifications for `file_detected`, `job_queued`, `job_started`, `job_progress`, `job_complete`, and `job_error`.
    - **Throttled Progress**: Job progress updates are now pushed frame-by-frame (throttled to 0.5% increments) for smooth UI updates without network congestion.
- **Dedicated Audio Profile**: Added `audio-qlab` profile for converting MP3/AAC/MP4 cues into uncompressed `pcm_s24le` 48kHz WAV audio.
- **Resolution Override**: Added `--resolution` flag to match exact projector/screen sizes.
- **Audio Sample Rate Override**: Added `--audio-sample-rate` flag to match hardware sample rates.

#### Fixed
- **Double Logging**: Prevented `MonitorService` from creating redundant log handlers when integrated with FastAPI.
- **Service Lifecycle**: Fixed a bug where the monitor service was not starting correctly within the FastAPI lifespan.

#### Changed
- **MonitorService Events**: Added a flexible callback-based event system to the core monitor service.
- **FastAPI Lifespan**: The backend API now automatically manages the background monitor task using the standard FastAPI lifespan protocol.
- **Profile Dataclass**: Expanded `TranscodeProfile` to support `audio_sample_rate` and `codec="none"` for audio-only workflows.

### [3.2.1] - 2026-03-29

#### 🛡️ CI/CD Pipeline Stabilization & Security Hardening

##### CI/CD Pipeline Fixes
- **Security Workflow Activation**: Fixed `pip-audit: command not found` error by adding proper virtual environment activation in `.github/workflows/security.yml`.
- **Formatting Enforcement**: Fixed `ruff format --check` failures by reformatting 3 files:
  - `bulletproof/api/models.py` - Fixed ConfigDict indentation
  - `bulletproof/api/server.py` - Fixed inline comment spacing  
  - `tests/test_api.py` - Fixed string quotes and line length
- **Test Dependencies**: Added `httpx>=0.27.0,<1.0` to dev dependencies to fix `ModuleNotFoundError: No module named 'httpx'` in API tests.
- **Version Consistency**: Updated API code to use `__version__` from package instead of hardcoded `"3.1.0"`:
  - `bulletproof/api/models.py` - HealthResponse now uses dynamic version
  - `bulletproof/api/server.py` - FastAPI app and root endpoint use dynamic version
  - `bulletproof/api/routes.py` - Health endpoint returns correct version

##### Security & Tooling
- **AGENTS.md**: Created comprehensive guide for agentic coding assistants with build/lint/test commands, code style guidelines, and project structure.
- **Gitignore Updates**: Added `AGENTS.md` to `.gitignore` under "AI Tooling (Local Only)" section.
- **Environment Variables**: Added `.env` file template with `DEEPSEEK_API_KEY` placeholder for AI tooling integration.

##### Test Results
- **All Tests Passing**: 57/57 tests pass after fixes
- **Security Pipeline**: All security checks pass (gitleaks, bandit, pip-audit)
- **Formatting**: 33/33 files properly formatted with ruff
- **Linting**: All checks pass with ruff

### [3.1.0] - 2026-03-07

### 🛡️ Security Hardening & Modernization
- **Security CI/CD**: Added `.github/workflows/security.yml` implementing a multi-layered security audit on every push and PR:
    - **Secret Scanning**: Integrated `gitleaks` to detect accidentally committed credentials and tokens.
    - **Static Analysis (SAST)**: Integrated `bandit` to identify insecure Python coding patterns (e.g., shell injection, insecure bindings).
    - **Dependency Auditing (SCA)**: Integrated `pip-audit` to scan third-party packages for known vulnerabilities (CVEs).
- **API Server Hardening**:
    - **Secure by Default**: Changed default API host from `0.0.0.0` (all interfaces) to `127.0.0.1` (localhost) to prevent unintentional network exposure.
    - **Configurable Binding**: Added `--api-host` and `--api-port` options to CLI and configuration.
- **Local Security Tooling**: Added `bandit` and `pip-audit` to `dev` dependencies.
- **Security Logging**: Created `docs/SECURITY_LOG.md` to track audits and remediation history.

#### 🐍 Python 3.10+ Modernization
- **Dropped Python 3.9**: Bumped minimum version to 3.10 following its EOL.
- **Modern Typing**: Refactored entire codebase to use Python 3.10 syntax:
    - Replaced `Optional[T]` with `T | None`.
    - Replaced `Union[A, B]` with `A | B`.
    - Adopted lowercase `list[]`, `dict[]`, etc., for type hints.
- **CI/CD Cleanup**: Updated test matrices and security workflows to target modern Python versions (3.10-3.12).

#### 🧹 Documentation & TUI Cleanup
- **Complete TUI Removal**: Scrubbed all remaining references to the deprecated Terminal User Interface from documentation, troubleshooting guides, and architecture diagrams.
- **Documentation Refresh**:
    - Updated `README.md` with new **Security**, **Quality Assurance**, and **Development Workflow** sections.
    - Updated all version references and Python requirements across `QUICK_REFERENCE.md`, `scripts/README.md`, and Linux guides.

---

### 🚀 Phase 3.1 - Web Dashboard API (Day 5 Complete - 2026-03-29)

#### 🧪 API Test Coverage & Stability
- **Comprehensive API Tests**: Added `tests/test_api.py` with 24 passing tests covering critical API endpoints:
    - System health and status (`/health`, `/status`)
    - Queue management (`/queue`, `/queue/pause`, `/queue/resume`, `/queue/clear`)
    - Job lifecycle (`/jobs/{job_id}/cancel`, `/jobs/{job_id}/retry`, `/jobs/{job_id}`)
    - Configuration management (`/config`, `/config/validate`)
    - Profile listing (`/profiles`)
- **Synchronous Testing**: Migrated API tests to use `fastapi.testclient.TestClient` for improved stability and predictable execution.
- **Robust Mocking**: Enhanced `MonitorService` mocking to handle `pathlib.Path` operations (`exists`, `is_dir`, `mkdir`) and simulate live configuration updates (`update_config`).

#### 🐛 API Fixes & Improvements
- **Correct `Rule` Object Access**: Fixed `TypeError` in `GET /api/v1/config` by accessing `Rule` object attributes directly instead of dictionary-style keys.
- **Accurate File Status Counts**: Corrected `detected_files` calculation in `GET /api/v1/status` to accurately reflect files with "detected" status.
- **API Instance Exposure**: Modified `bulletproof/api/server.py` to expose the FastAPI application instance (`api_app`) correctly for external modules and testing.

---

### 🚀 Phase 3.1 - Web Dashboard API (Day 3 Complete - 2026-03-06)

#### 🛠️ Architectural Refactor: Truly Async Transcoding
- **Async Transcode Core**: Refactored `TranscodeJob` to use `asyncio.create_subprocess_exec` for non-blocking execution.
- **Concurrent Monitoring**: Updated `MonitorService` to manage transcoding in background tasks, ensuring 100% responsiveness for file scanning and job control even during heavy processing.
- **Progress Streaming Support**: Implemented async progress callbacks for real-time updates without blocking the event loop.
- **Slop Removal**: Eliminated all `print()` statements from core libraries in favor of proper `logging` calls.

#### ⚙️ Configuration Management API
- **Live Updates**: Implemented `PATCH /api/v1/config` to allow updating rules, poll intervals, and log levels live without service restarts.
- **Persistence**: Added support for persisting live configuration changes back to the original YAML/JSON file.
- **Profile Discovery**: Added `GET /api/v1/profiles` to expose transcoding profile technical details for the UI.
- **Validation**: Added `POST /api/v1/config/validate` for pre-flight configuration checks.

#### 📢 Professional Logging & UI Upgrade
- **Standardized Logs**: Refactored all log messages to a professional, high-signal technical tone with standardized key-value formatting.
- **CLI Refresh**: Swapped emojis and casual phrasing for technical status reports in `monitor`, `transcode`, and `batch` commands.
- **DRY API Models**: Consolidated job conversion logic into `JobResponse.from_queued_job()`.

#### Technical Details
- **Sync Wrapper**: Added `sync_execute()` to `TranscodeJob` to maintain consistent behavior for CLI tools while sharing the async core.
- **Persistence Tracking**: `MonitorConfig` now tracks its `_original_path` for reliable configuration saving.

---

### 🚀 Phase 3.1 - Web Dashboard API (Day 2 Complete - 2026-02-27)

#### Added
- **Job Control API Endpoints**:
  - `POST /api/v1/queue/pause` - Pause transcode queue processing
  - `POST /api/v1/queue/resume` - Resume transcode queue processing
  - `POST /api/v1/queue/clear` - Clear all pending jobs from the queue
  - `POST /api/v1/jobs/{job_id}/cancel` - Cancel a pending job
  - `POST /api/v1/jobs/{job_id}/retry` - Retry a failed or completed job

- **Queue Enhancements**:
  - Added `CANCELLED` state to `JobStatus`.
  - Cancelled jobs are correctly moved to history and tracked in status responses.
  - Implemented logic in `MonitorService` to support queue pausing.

#### Fixed
- **MonitorService Queuing Bug**:
  - Fixed an issue where stable files were detected and matched to a rule, but the job was never added to the `TranscodeQueue`.
  - Jobs are now correctly generated and enqueued.

### 🚀 Phase 3.1 - Web Dashboard API (Day 1 Complete - 2026-02-10)

#### Added
- **FastAPI REST API Backend** - Production-ready web API for dashboard
  - 8 REST endpoints for monitoring and control
  - Real-time WebSocket streaming (updates every 2 seconds)
  - Interactive Swagger UI documentation at `/docs`
  - Pydantic data models for type-safe responses
  - CORS middleware for development
  - Application lifecycle management
  
- **API Endpoints**:
  - `GET /api/v1/health` - Health check with uptime
  - `GET /api/v1/status` - Monitor service status
  - `GET /api/v1/queue` - Queue status and all jobs
  - `GET /api/v1/history` - Processing history
  - `GET /api/v1/rules` - Active rule configuration
  - `GET /api/v1/jobs/{job_id}` - Individual job details
  - `WS /api/v1/stream` - Real-time WebSocket updates
  - `GET /docs` - Interactive API documentation

- **Enhanced Queue System**:
  - Job ID generation (UUID-based)
  - Priority field for job ordering
  - Progress tracking (0-100%)
  - `get_current()` - Get currently processing job
  - `get_job(job_id)` - Retrieve job by ID
  - `clear()` - Clear all pending jobs

- **Documentation**:
  - `docs/API_QUICKSTART.md` - Comprehensive API guide
  - `docs/PHASE_3.1_DAY_1_COMPLETE.md` - Day 1 completion summary
  - `examples/dashboard_example.py` - Working example script
  - Response examples for all endpoints
  - Testing instructions (curl, Python, JavaScript)

#### Technical Details
- **New Files**:
  - `bulletproof/api/__init__.py` - API package
  - `bulletproof/api/models.py` - Pydantic response models (8 models)
  - `bulletproof/api/routes.py` - REST + WebSocket endpoints
  - `bulletproof/api/server.py` - FastAPI app creation
  - `examples/dashboard_example.py` - Complete example

- **Dependencies**:
  - fastapi>=0.104.0
  - uvicorn[standard]>=0.24.0
  - websockets>=12.0
  - pydantic>=2.5.0

#### Use Cases
- Remote monitoring of transcoding jobs
- Real-time status updates via WebSocket
- Integration with custom frontends
- Mobile app backends
- Multi-user monitoring dashboards

#### Status
- ✅ Day 1/15 complete (Week 1: MVP Backend)
- ✅ ~800 lines of code written
- ✅ All linting passing (black, isort, flake8)
- ✅ 33 existing tests still passing
- ✅ Ready for Day 2: Job control endpoints

---

## [2.4.1] - 2026-02-10

### 🐛 Fixed - Phase 2.4 Bug Fix

#### MonitorService Rule Matching
- **Fixed**: `MonitorService._create_job_for_file()` was passing Path object to `RuleEngine.match()`
- **Root Cause**: `RuleEngine.match()` expects filename string, not Path object
- **Solution**: Changed `rule_engine.match(file_info.path)` → `rule_engine.match(file_info.path.name)`
- **Impact**: Pattern matching (glob/regex/exact) now works correctly
- **Files Changed**: `bulletproof/services/monitor_service.py` (line 178)
- **Commit**: `11d451bf`

#### What Was Broken
- CLI command `bvp monitor start --config` would crash
- Files in watch directory wouldn't match any rules
- No jobs would be queued for processing

#### What Works Now
- ✅ File detection and pattern matching
- ✅ Rule-based profile selection
- ✅ Job queue creation
- ✅ Automatic transcoding
- ✅ All 33 tests passing

### 📝 Changed

- **Documentation Updates**:
  - `docs/Current Status Report.md` - Updated to 100% complete
  - `docs/PHASE_2.4_COMPLETION.md` - Added completion milestone
  - `docs/features/FRAMERATE_HANDLING.md` - Design decisions documented

### 🚀 Production Status
- Phase 2.4 is now **PRODUCTION READY**
- Zero known bugs
- All tests passing (33/33)
- Ready for live event workflows

---

## [2.6.0] - 2026-02-09

### 🐧 Added - MKV Profiles for Linux Live Events

#### New Profiles
- **live-linux-hevc-mkv** - H.265 MKV for Linux live playback
  - Codec: H.265 (libx265) with CRF 20 quality
  - Container: MKV for superior seeking reliability vs MP4
  - Keyframes: 5-second intervals for instant scrubbing in live cue systems
  - Audio: AAC 192k for broad compatibility
  - Target applications: mpv, VLC, Linux Show Player
  - GPU acceleration support: VA-API, VDPAU, NVDEC

- **archival-linux-mkv** - H.265 10-bit MKV for Linux archival
  - Codec: H.265 10-bit (yuv422p10le) matching ProRes 422 color depth
  - Quality: CRF 18 for visually lossless output
  - Audio: Uncompressed PCM 24-bit for maximum fidelity
  - File size: ~60-80% smaller than ProRes 422 HQ
  - Use case: ProRes 422 replacement for Linux workflows
  - Preserves source keyframes for maximum quality

#### FFmpeg Enhancements
- **CRF Mode Support** - Quality-based encoding for H.265
  - Uses `-crf` flag instead of bitrate when `quality` is numeric
  - Maintains existing bitrate mode when `max_bitrate` is specified
  - Better quality control for variable content

- **10-bit Encoding** - Full 10-bit color depth support
  - yuv422p10le pixel format for archival workflows
  - Matches ProRes 422 color space
  - Professional-grade color preservation

- **MKV Container Optimization**
  - `+faststart` flag for improved streaming
  - Better seeking performance in live playback systems
  - More reliable than MP4 for long-form content

- **H.265 Compatibility**
  - `hvc1` tag for broader player support
  - Works with more hardware decoders
  - Enhanced cross-platform playback

#### Linux Integration
- **Bash Script Updates** - `linux/scripts/transcode.sh`
  - CRF mode support for quality-based encoding
  - Keyframe interval support with `-g` flag
  - Pixel format overrides for 10-bit encoding
  - Audio codec/bitrate configuration from profiles
  - MKV faststart support

- **Profile Catalog** - `scripts/profiles.json`
  - Added `live-linux-hevc-mkv` profile definition
  - Added `archival-linux-mkv` profile definition
  - Full CRF and keyframe configuration
  - Backward compatible with existing profiles

#### Documentation
- **README.md Updates**
  - New "Linux MKV Profiles" section
  - Usage examples for live event workflows
  - ProRes 422 replacement guidance
  - GPU acceleration testing commands
  - Linux Show Player integration examples
  - Updated profiles comparison table (9 profiles total)

- **Profile Count** - Now 9 profiles (7 original + 2 new MKV)
  - live-qlab (ProRes Proxy)
  - live-prores-lt (ProRes LT)
  - live-h264 (H.264)
  - **live-linux-hevc-mkv (H.265 MKV)** ← NEW
  - standard-playback (H.264)
  - stream-hd (H.265)
  - stream-4k (H.265)
  - archival (ProRes HQ)
  - **archival-linux-mkv (H.265 10-bit MKV)** ← NEW

### 🧪 Testing
- **Test Suite Updates** - All 31 tests passing
  - Updated `test_list_profiles` to expect 9 profiles
  - Added `test_get_profile_live_linux_hevc_mkv`
  - Added `test_get_profile_archival_linux_mkv`
  - Added MKV extension tests to `test_codec_extensions`
  - Comprehensive validation of profile attributes
  - CRF mode, keyframes, and pixel format testing

### 🎯 Use Cases
- **Linux Live Events** - mpv and Linux Show Player with 5s keyframes
- **ProRes Replacement** - 10-bit H.265 instead of ProRes 422 on Linux
- **GPU Acceleration** - Hardware-accelerated decode on Linux systems
- **File Size Reduction** - 60-80% smaller than ProRes with same quality
- **Cross-Platform Archival** - MKV plays everywhere, unlike ProRes

### 📝 Changed
- Profile count increased from 7 to 9
- CODEC_EXTENSIONS mapping now includes MKV alternatives
- Terminology consistently uses "live" instead of "theater"

### 🚀 Production Status
- ✅ All 31 tests passing
- ✅ Python and Bash implementations updated
- ✅ Comprehensive documentation
- ✅ Backward compatible with existing workflows
- ✅ Ready for Linux live event production use

---

## [2.5.0] - 2026-02-08

### 🎬 Added - Keyframe Interval Control

#### New Features
- **Keyframe Interval Support** - Professional-grade GOP (Group of Pictures) control
  - `keyframe_interval` parameter for TranscodeProfile (in seconds)
  - `force_keyframes` flag for strict keyframe placement
  - Automatic GOP size calculation based on frame rate
  - Frame-accurate seeking and scrubbing support
- **FFmpeg Integration**
  - Dynamic GOP size calculation: `GOP = framerate × interval`
  - `-g` flag for GOP size
  - `-keyint_min` for minimum keyframe interval
  - `-sc_threshold 0` to disable scene change detection
  - `-force_key_frames` with time-based expression
- **Profile Enhancement**
  - Added `keyframe_interval` field to TranscodeProfile dataclass
  - Added `force_keyframes` boolean flag
  - Backward compatible (optional parameters with None defaults)

#### Use Cases
- **Live Event Playback** - Easy scrubbing during live theater performances
- **Streaming** - Improved seek performance in HLS/DASH workflows
- **Video Editing** - Frame-accurate timeline navigation
- **QLab Integration** - Precise cue point timing for theater productions

#### Documentation
- Added `docs/KEYFRAME_FEATURE.md` with:
  - Feature overview and technical details
  - FFmpeg command examples
  - Use case scenarios
  - Testing guide with sample commands
- Updated README.md with keyframe interval feature highlights
- Added testing script: `scripts/test_keyframe_interval.sh`

#### Technical Details
- Supports all codecs (H.264, H.265, ProRes)
- Works with variable and constant frame rates
- Automatic frame rate detection via ffprobe
- Graceful handling when frame rate cannot be determined

### 🔧 Fixed - CI/CD and Code Quality

#### Linting Configuration
- **Added `.flake8` config** - Line length set to 100 characters (matching Black)
- **Added `setup.cfg`** - Configured isort and flake8 for consistency
  - `isort` profile set to "black" for compatibility
  - Line length standardized to 100 across all tools
  - Proper exclusions for build artifacts

#### Code Quality Fixes
- **Black Formatting** - All files reformatted to 100-character line length
  - Fixed `bulletproof/core/job.py`
  - Fixed `bulletproof/core/monitor.py`
  - Fixed `bulletproof/cli/commands/config.py`
- **Import Sorting (isort)** - All 30 files properly sorted
  - Alphabetized imports
  - Grouped by standard lib, third-party, local
  - Consistent with Black formatting
- **Unused Code Cleanup**
  - Removed unused `frame_pattern` variable in `job.py`
  - Removed unused `job` variable in `monitor_service.py`
  - Removed unused imports across 25 files via autoflake
  - Fixed f-strings without placeholders (F541)

#### CI/CD Pipeline
- ✅ All linting checks now passing:
  - Black (100-char line length)
  - isort (import sorting)
  - flake8 (style guide enforcement)
  - pytest (all tests passing)
- ✅ Multi-Python version support:
  - Python 3.9
  - Python 3.10
  - Python 3.11
  - Python 3.12

### 📝 Changed

- **Terminology Update** - Replaced "theater" references with "live" for broader appeal
  - Profile names now use "live-" prefix
  - Documentation updated throughout
  - More inclusive for non-theater live event use cases

### 🛠️ Development

- **Tools Added**:
  - `autoflake` for unused import removal
  - Comprehensive linting workflow documented
  - Local testing guide before pushing to CI

- **Configuration Files**:
  - `.flake8` - Flake8 settings
  - `setup.cfg` - isort and flake8 unified config
  - `pyproject.toml` - Black settings (existing, now aligned with others)

### 🚀 Production Status

- ✅ All 30 files passing linting
- ✅ CI/CD pipeline green across all Python versions
- ✅ Keyframe feature tested and documented
- ✅ Code quality at professional standard
- ✅ Ready for production deployment

---

## [2.4.0] - 2025-12-28

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
- `bvp monitor` - Start the folder monitor
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
  - `bvp transcode` - Single file transcoding
  - `bvp analyze` - Video file analysis
  - `bvp batch` - Batch directory processing
  - `bvp tui` - Launch interactive TUI
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

### Unreleased - Security & Modernization (2026-03-07)
- Automated Security CI/CD (Gitleaks, Bandit, pip-audit)
- API server hardened (localhost by default)
- Python 3.9 dropped; full codebase modernized to Python 3.10+
- Complete documentation scrub (removed all TUI references)

### Unreleased - Phase 3.1 Web Dashboard API (Day 3 Complete - 2026-03-06)
- Architectural Refactor: Truly async core and concurrent monitor service
- Live Configuration API with persistence and profile technical discovery
- Professional logging upgrade across all layers (standardized technical tone)
- Consolidated API response models (DRY)

### Unreleased - Phase 3.1 Web Dashboard API (Day 2 Complete - 2026-02-27)
- Job control endpoints (pause, resume, clear, cancel, retry)
- MonitorService queuing bug fix
- Added `CANCELLED` job status

### v2.4.1 - Phase 2.4 Bug Fix (2026-02-10)
- Fixed MonitorService rule matching (Path vs string)
- Phase 2.4 now production-ready
- All 33 tests passing
- Zero known bugs

### v2.6.0 - MKV Profiles for Linux Live Events (2026-02-09)
- H.265 MKV profiles for Linux live playback and archival
- CRF mode support for quality-based encoding
- 10-bit color depth support (ProRes 422 replacement)
- GPU acceleration compatibility (VA-API/VDPAU/NVDEC)
- 9 total profiles (7 original + 2 new MKV)
- MKV container optimization for live event seeking
- Comprehensive test coverage (31 tests passing)

### v2.5.0 - Keyframe Interval Control + CI/CD Fixes (2026-02-08)
- Professional keyframe/GOP control for easy video scrubbing
- Complete CI/CD pipeline fixes (all Python versions passing)
- Code quality improvements (Black, isort, flake8)
- 100-character line length standardization
- Production-ready code quality

### v2.4.0 - Folder Monitor + Queue System (2025-12-28)
- Automatic folder monitoring for video files
- Async job queue with worker pool
- Pattern-based rule engine for video routing
- Configuration management with sensible defaults
- 32 comprehensive tests, all passing
- Foundation for Phase 3.1 Web Dashboard

### v0.2.0 - Linux Bash Port + Universal Tools (2025-12-25)
- Complete Linux implementation with pure Bash
- Cross-platform universal tools (analyze, list-profiles)
- 7 Linux-optimized profiles
- Symlink-based architecture for single-source maintenance
- Comprehensive Linux documentation
- Production-ready on Fedora, Ubuntu, Debian

### v0.1.0 - Initial Release (2024-12-25)
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
