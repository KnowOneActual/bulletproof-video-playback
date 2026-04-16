# 🗺️ Bulletproof Video Playback - Roadmap

## Current Phase: 3.1 🚀 IN PROGRESS (Day 6/15 Complete - Frontend Dashboard Built)

---

## 🎯 Strategic Direction

Short- to medium-term, Bulletproof is optimizing for:

- **AV appliance workflows:** A "bvp playback prep box" for theaters and AV teams, built around profiles, folder monitoring, and a minimal but powerful dashboard.
- **On-prem service + API:** A stable, scriptable queue and monitoring layer that other tools can integrate with via REST/WebSocket.
- **Narrow, high-value personas:** Live show operators, video engineers, and archivists—not generic consumer video conversion.

Enterprise features (clustering, RBAC, compliance, etc.) remain future exploration, only to be pulled forward if real-world demand shows up.

---

## ✅ COMPLETED PHASES

### Phase 1: Core Transcode Engine
- [x] Profile system (ProRes, H.264, H.265, custom speeds)
- [x] FFmpeg integration with progress parsing
- [x] Speed presets (fast/normal/slow with preset adjustment)
- [x] CLI command: `bvp transcode`
- [x] Comprehensive profile library

### Phase 2: UI & Automation Layers

#### Phase 2.1: Async Transcode Core ✅
- [x] AsyncGenerator-based transcode execution
- [x] Real-time FFmpeg progress parsing
- [x] ProgressData class (FPS, bitrate, speed, ETA)
- [x] Non-blocking UI updates

#### Phase 2.2: TUI (Shelved) ⏸️
- [x] HomeScreen with profile selection
- [x] TranscodeScreen with real-time progress
- [x] Full integration (tested)
- **Decision:** Shelved - TUI complexity too high, ROI too low
- **Better Direction:** Folder monitoring automation

#### Phase 2.3: Folder Monitor Infrastructure ✅
- [x] **FolderMonitor** - File detection with stability tracking
- [x] **TranscodeQueue** - In-memory queue + JSON persistence
- [x] **RuleEngine** - Pattern-based profile assignment
- [x] Unit tests for all components

#### Phase 2.4: MonitorService & CLI Integration ✅
- [x] MonitorService orchestration (combine monitor + queue + rules)
- [x] Configuration system (YAML config with sensible defaults)
- [x] CLI integration (`bvp monitor --config config.yaml`)
- [x] Comprehensive testing (33/33 tests passing)
- [x] Error handling and recovery
- [x] Bug fix: Rule matching (Path vs string)
- [x] Production-ready (zero known bugs)
- [x] Ready for Phase 3.1

**Status:** Phase 2.4 is 100% COMPLETE ✅ (v2.4.1 - February 10, 2026)

---

## 🚀 CURRENT PHASE: Phase 3.1 (Web Dashboard) - IN PROGRESS

### Phase 3.1: Web Dashboard - Day 3/15 Complete ✅

**Status:** Building! Started February 10, 2026

#### 3.1.0 Dashboard MVP Definition

The first web dashboard release focuses on a thin, lovable slice:

- Queue list with job status and basic details.
- Global monitor status (running/paused) and queue health.
- Essential job controls: cancel, retry, pause/resume processing.
- Real-time updates via WebSocket.

No complex charts, advanced analytics, or full config editor in v3.1.0—those will only ship after real AV workflows prove out the basics.

#### 3.1.1: MVP Backend (Week 1) - 60% Complete
- [x] **Day 1:** FastAPI server with REST endpoints ✅
  - [x] Health check endpoint
  - [x] Monitor status endpoint
  - [x] Queue status endpoint
  - [x] Job history endpoint
  - [x] Rules configuration endpoint
  - [x] Individual job details endpoint
  - [x] WebSocket real-time streaming
  - [x] Interactive Swagger UI documentation
  - [x] Pydantic data models (8 models)
  - [x] CORS middleware for development
  - [x] Enhanced queue system (IDs, priorities, progress)
  - [x] Complete example script
  - [x] API quickstart documentation

- [x] **Day 2:** Job control endpoints ✅
  - [x] Fixed critical queuing bug in MonitorService
  - [x] POST /api/v1/jobs/{id}/cancel - Cancel a job
  - [x] POST /api/v1/jobs/{id}/retry - Retry failed job
  - [x] POST /api/v1/queue/clear - Clear pending jobs
  - [x] POST /api/v1/queue/pause - Pause processing
  - [x] POST /api/v1/queue/resume - Resume processing
  - [x] Added `CANCELLED` status to job logic

- [x] **Day 3:** Configuration management ✅
  - [x] GET /api/v1/config - Get current config
  - [x] PATCH /api/v1/config - Update configuration live
  - [x] POST /api/v1/config/validate - Validate config
  - [x] GET /api/v1/profiles - List available profiles
  - [x] **Ruthless Refactor:** Core job execution is now truly async/non-blocking.

- [x] **Day 4:** Enhanced WebSocket ✅
  - [x] Job progress updates (frame-by-frame)
  - [x] File detection notifications
  - [x] Error alerts
  - [x] Multiple concurrent clients (broadcasting)
  - [x] **Fix:** FastAPI lifespan integration for background monitor service.

- [x] **Day 5:** Polish & Testing
  - [x] Unit tests for all endpoints
  - [x] Integration tests
  - [x] Error handling improvements
  - [x] Performance optimization
  - [x] Documentation updates
  - **Estimated:** 3-4 hours

**Week 1 Status:** 5/5 days complete (100%)
**Timeline:** Days 1-5
**Expected:** Functional backend API with job controls

#### 3.1.2: Features (Week 2) - COMPLETE ✅
- [x] **Dashboard Frontend UI**: Built responsive HTML/CSS/JS dashboard with Bulma CSS
- [x] **Job control buttons**: Cancel, Retry, Details actions for each job
- [x] **Progress bars and animations**: Real-time progress bars for processing jobs
- [x] **Error notifications**: WebSocket error events and UI alerts
- [x] **Real-time updates**: WebSocket integration for live queue updates
- [x] **Queue statistics**: Total, pending, processing, complete, error counts
- [x] **Job details modal**: Detailed job information view
- [x] **Monitor controls**: Pause/Resume/Clear queue buttons
- [x] **WebSocket status indicator**: Connection status with auto-reconnect

**Timeline:** Days 6-10
**Expected:** Feature-complete dashboard UI ✅ Achieved

### 🎭 QLab & AV Performance (v3.2.0) - COMPLETE ✅
- [x] **Dedicated Audio Profile:** `audio-qlab` for MP3/AAC replacement.
- [x] **Resolution Overrides:** `--resolution` flag for exact screen matching.
- [x] **Sample Rate Overrides:** `--audio-sample-rate` for hardware matching.
- [x] **Audio-Only Core Support:** `codec="none"` handling in `TranscodeJob`.

---

## 📋 RECENT COMPLETIONS

### April 15, 2026 - Phase 3.1 Day 6
- ✅ Built complete frontend dashboard UI in `/bulletproof/static/dashboard/`
- ✅ Implemented real-time WebSocket updates and job controls
- ✅ Added job details modal and progress visualizations
- ✅ Integrated with existing backend API
- ✅ Updated documentation and examples

**Status:** Dashboard MVP feature-complete. Ready for user testing.

### March 29, 2026 - Phase 3.1 Day 5
- ✅ Completed comprehensive API test suite (`tests/test_api.py`).
- ✅ Ensured all new API endpoints are thoroughly tested.
- ✅ Fixed several bugs and improved API robustness based on test findings.

**Status:** Ahead of schedule on performance features. Day 3 completely finished!

---

## Phase 3.1 Decision Gate
...
**Last Updated:** April 15, 2026  
**Current Status:** Phase 3.1 Day 6 Complete ✅ (50% of Phase 3.1)  
**Next Session:** Phase 3.1.3 Polish & Testing
**Confidence Level:** 100% (Events are firing perfectly)

