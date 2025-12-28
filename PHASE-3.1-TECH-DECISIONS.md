# 🧠 PHASE 3.1 - TECH DECISIONS

This document explains **why** we picked each major technology and pattern for the Phase 3.1 web dashboard.

--- 

## 1. Backend Framework: FastAPI

### Options Considered
- Flask
- Django REST Framework
- FastAPI ✅

### Why FastAPI
- Async-first (great for WebSocket + IO-bound operations)
- Built-in OpenAPI/Swagger docs
- Pydantic for validation (already familiar)
- Excellent performance

### Tradeoffs
- Slightly newer ecosystem than Flask/Django
- But perfect match for this project size

--- 

## 2. Frontend: React 18 (+ optional TypeScript)

### Options Considered
- Vanilla JS + HTMX
- Vue
- React ✅

### Why React
- Rich ecosystem and docs
- Easy integration with WebSocket
- JSX is a good fit for a dynamic dashboard

### Why TypeScript (Optional in 3.1, required in 3.2+)
- Strong typing for API responses
- Easier refactoring later

--- 

## 3. Styling: TailwindCSS

### Options Considered
- Raw CSS
- Bootstrap
- TailwindCSS ✅

### Why Tailwind
- Fast to iterate UI
- Utility-first works well for dashboards
- Easy dark-mode support

### Tradeoffs
- Class-heavy markup
- But fine for an internal tool

--- 

## 4. Real-Time: WebSocket

### Options Considered
- Polling (`setInterval` + REST)
- Server-Sent Events
- WebSocket ✅

### Why WebSocket
- True real-time updates
- Bi-directional communication
- Lower overhead than polling

### Implementation
- FastAPI `WebSocket`
- Browser `WebSocket` API from React

--- 

## 5. Database: SQLite + SQLAlchemy

### Options Considered
- No DB (in-memory only)
- SQLite + raw SQL
- SQLite + SQLAlchemy ✅

### Why SQLite
- Zero external dependencies
- Perfect for local + single-node deploy

### Why SQLAlchemy
- Async support
- Portable ORM
- Easy to swap to Postgres later

--- 

## 6. API Style: REST + WebSocket

### Why REST for most things
- Simple CRUD
- Browser and CLI friendly
- Easy to test with curl/httpie

### Why WebSocket for live updates
- Push-based progress updates
- Job status changes in real time
- Good UX for monitoring

--- 

## 7. Deployment: Docker + Compose (Week 3)

### Why Docker
- Reproducible environment
- Easy to ship to any server

### Why Compose
- Orchestrate backend + frontend + DB
- One command to spin up full stack

--- 

## 8. Testing Strategy

- Keep existing pytest suite intact (Phase 2.4)
- Add new tests only in `tests/test_dashboard_*.py`
- Use HTTPX + WebSocket test clients for FastAPI
- Prefer integration tests over heavy unit tests for the dashboard

--- 

## 9. Compatibility With Phase 2.4

### Non‑negotiables
- No breaking changes to monitor/CLI
- No DB schema breaking changes without migration
- All existing tests must stay green

### Integration Pattern
- Dashboard reads from existing monitor interfaces
- Any new DB tables are additive only
- CLI workflows remain exactly the same

--- 

## 10. Future‑Proofing

These choices let you later:
- Add user auth with JWT
- Swap SQLite for Postgres with minimal code changes
- Add more dashboards/views without rewriting the backend
- Scale out read traffic behind a reverse proxy

--- 

If a tool or library starts feeling heavy, this document is your reason to either stick with it for 3.1 or consciously swap it out in a later phase.
