# 🗺️ Bulletproof Video Playback - Roadmap

## Current Phase: 3.1 🚀 IN PROGRESS (Day 3/15 Complete)

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

- [ ] **Day 4:** Enhanced WebSocket
  - [ ] Job progress updates (frame-by-frame)
  - [ ] File detection notifications
  - [ ] Error alerts
  - [ ] Multiple concurrent clients
  - **Estimated:** 2-3 hours

- [ ] **Day 5:** Polish & Testing
  - [ ] Unit tests for all endpoints
  - [ ] Integration tests
  - [ ] Error handling improvements
  - [ ] Performance optimization
  - [ ] Documentation updates
  - **Estimated:** 3-4 hours

**Week 1 Status:** 3/5 days complete (60%)
**Timeline:** Days 1-5
**Expected:** Functional backend API with job controls

#### 3.1.2: Features (Week 2) - Not Started
...
- [ ] Job control buttons
- [ ] Progress bars and animations
- [ ] Error notifications

**Timeline:** Days 6-10
**Expected:** Feature-complete dashboard UI

### 🎭 QLab & AV Performance (v3.2.0) - COMPLETE ✅
- [x] **Dedicated Audio Profile:** `audio-qlab` for MP3/AAC replacement.
- [x] **Resolution Overrides:** `--resolution` flag for exact screen matching.
- [x] **Sample Rate Overrides:** `--audio-sample-rate` for hardware matching.
- [x] **Audio-Only Core Support:** `codec="none"` handling in `TranscodeJob`.

---

## 📋 COMPLETED TODAY (March 17, 2026)

### QLab Performance Integration (v3.2.0)
- ✅ Implemented `audio-qlab` profile (48kHz 24-bit PCM WAV).
- ✅ Added `--resolution` and `--audio-sample-rate` CLI flags.
- ✅ Updated `TranscodeJob` to handle audio-only transcodes and sample rate flags.
- ✅ Updated `live-qlab` to default to 48kHz.
- ✅ Verified with tests and documentation.

### Phase 3.1 Day 3 (March 6, 2026)
- ✅ Fixed critical bug in `MonitorService` where transcode was blocking the event loop.
- ✅ Implemented `GET /api/v1/config` and `PATCH /api/v1/config`.
- ✅ Implemented `GET /api/v1/profiles` and `POST /api/v1/config/validate`.
- ✅ Refactored `TranscodeJob` to be async-first.

**Status:** Ahead of schedule on performance features. Day 3 completely finished!

---

## Phase 3.1 Decision Gate
...
**Last Updated:** March 17, 2026, 10:00 AM CST  
**Current Status:** Phase 3.1 Day 3 Complete ✅ (20% of Phase 3.1)  
**Next Session:** Day 4 - Enhanced WebSocket  
**Confidence Level:** 100% (Async foundation is solid)

