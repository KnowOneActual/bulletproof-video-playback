# 🌐 PHASE 3.1 - WEB DASHBOARD (DETAILED PLAN)

This document is the **deep technical plan** for implementing the Phase 3.1 web dashboard.

For a lighter overview, see:
- `PHASE-3.1-START-HERE.md`
- `PHASE-3.1-OVERVIEW.md`
- `PHASE-3.1-TECH-DECISIONS.md`

For execution steps, see:
- `PHASE-3.1-QUICKSTART.md`

---

## 1. High-Level Architecture

### 1.1 Components

- **FastAPI App**: HTTP + WebSocket server
- **Monitor Integration Layer**: Bridges existing monitor service with dashboard
- **Database Layer**: Stores job and stats history
- **React Frontend**: Dashboard UI
- **WebSocket Channel**: Real-time events

### 1.2 Data Flow

1. Monitor service processes jobs (Phase 2.4)
2. Dashboard backend:
   - Reads job state from queue / monitor
   - Persists snapshots to DB
   - Exposes REST + WebSocket interface
3. Frontend:
   - Fetches initial data via REST
   - Subscribes to updates via WebSocket

---

## 2. Backend Details

### 2.1 Package Layout

```text
bulletproof/dashboard/
  __init__.py
  server.py       # FastAPI app, WebSocket, static files
  api.py          # APIRouter, endpoints
  models.py       # Pydantic models
  db.py           # SQLAlchemy models + engine
  services.py     # Integration with monitor + queue
  config.py       # Dashboard-specific config
```

### 2.2 Pydantic Models (Request/Response)

Key models already outlined in `PHASE-3.1-OVERVIEW.md`.

Additional fields to add during implementation:
- `JobModel.duration` (seconds)
- `JobModel.bitrate` (optional)
- `JobModel.resolution` (optional)

### 2.3 SQLAlchemy Models

**Job**
- ID (string)
- Filename
- Status
- Progress
- Started/Completed timestamps
- Error message
- Profile
- Duration

**JobEvent** (optional Phase 3.1, definite Phase 3.2)
- Event ID
- Job ID
- Event type (created/started/completed/failed/paused/resumed)
- Event timestamp

### 2.4 Services Layer

`services.py` will:
- Provide functions like:
  - `get_current_jobs()`
  - `get_stats()`
  - `pause_job(job_id)`
  - `resume_job(job_id)`
  - `cancel_job(job_id)`
- Use existing monitor/queue from Phase 2.4 (no rewrite)

---

## 3. Frontend Details

### 3.1 Views & Routes

Single-page app with main sections:

- `/` – Dashboard overview
- `/jobs` – Job list + detail
- `/config` – Configuration editor
- `/stats` – Historical charts

Can be implemented either as:
- A single-page React app with conditional rendering
- Or with React Router (optional)

### 3.2 Components

Core components:
- `<DashboardLayout>` – Shell
- `<StatsCards>` – Top stats
- `<JobsTable>` – Main jobs table
- `<JobRow>` – Row with actions
- `<ConfigForm>` – Config editor
- `<HistoryChart>` – Chart.js graph
- `<Alerts>` – Error/success messages

### 3.3 State Management

Keep it simple for Phase 3.1:
- useState/useEffect for local state
- Context or small state container if needed later

Real-time updates:
- REST for initial state
- WebSocket for incremental updates

---

## 4. API Contract (Backend ↔ Frontend)

### 4.1 Job List

`GET /api/jobs`

Response:
```json
[
  {
    "id": "1",
    "filename": "video1.mov",
    "status": "processing",
    "progress": 0.45,
    "started_at": "2025-12-30T12:34:56",
    "completed_at": null,
    "error": null,
    "profile": "live_stream",
    "duration": 120.5
  }
]
```

### 4.2 Stats Summary

`GET /api/stats`

Response:
```json
{
  "total_jobs": 242,
  "successful": 235,
  "failed": 7,
  "avg_duration": 118.4,
  "in_progress": 3
}
```

### 4.3 Config

`GET /api/config`

`POST /api/config`

Request:
```json
{
  "monitor_folder": "./videos/incoming",
  "output_folder": "./videos/output",
  "max_workers": 4
}
```

### 4.4 WebSocket Messages

Connection: `WS /ws/updates`

Server → Client messages:

```json
{
  "type": "job_update",
  "job": { ... JobModel ... }
}
```

```json
{
  "type": "stats_update",
  "stats": { ... StatsModel ... }
}
```

Client → Server messages (optional Phase 3.1):
```json
{
  "type": "ping"
}
```

```json
{
  "type": "subscribe",
  "channels": ["jobs", "stats"]
}
```

---

## 5. Phasing Detail (How It Evolves)

### 5.1 Phase 3.1 Scope

Implement:
- Basic DB tables
- Mapping from existing monitor to REST endpoints
- Periodic refresh from queue → DB
- Simple WebSocket broadcasting snapshots
- Basic React UI, single page

### 5.2 Later Phases (3.2+)

Add:
- Metrics per profile
- Detailed error views with logs
- Multi-node monitor aggregation
- Authentication + roles
- Theme customization

---

## 6. Risk & Mitigation

### Risk 1: WebSocket Complexity
- **Mitigation:** Start with mock updates (already in QUICKSTART), integrate real later.

### Risk 2: DB Sync Accuracy
- **Mitigation:** Prefer deriving stats directly from queue state where possible.

### Risk 3: Frontend Scope Creep
- **Mitigation:** Stick to minimal viable set of features for Phase 3.1.

---

## 7. Definition of Done (Phase 3.1)

Backend:
- [ ] FastAPI app with REST and WebSocket
- [ ] SQLite DB with job history
- [ ] Stable API contract

Frontend:
- [ ] Dashboard view with live stats
- [ ] Jobs table with status + actions
- [ ] Config editor

System:
- [ ] All Phase 2.4 tests passing
- [ ] New backend tests passing
- [ ] Dashboard usable from browser

---

This doc is the **truth source** for how Phase 3.1 should look end-to-end.

If you ever feel lost while building, come back here and realign.
