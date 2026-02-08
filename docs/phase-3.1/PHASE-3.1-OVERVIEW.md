# 🎯 PHASE 3.1 - WEB DASHBOARD OVERVIEW

**Phase:** 3.1 - Web Dashboard  
**Timeline:** 2-3 weeks (December 30 - January 17)  
**Status:** Planning Complete ✅  
**Start Date:** Monday, December 30, 2025  

---

## 🎬 The Vision

You've built a production-ready **folder monitor** in Phase 2.4. Now build the **web dashboard** to control it.

### **What You'll Create**

```
http://localhost:8000
┌─────────────────────────────────────┐
│   Bulletproof Video Dashboard       │
├─────────────────────────────────────┤
│  📊 Stats         🎬 Live Monitor  │
│  ├─ Total: 242    ├─ 3 processing  │
│  ├─ Success: 235  ├─ 2 queued      │
│  ├─ Error: 7      ├─ 5 completed   │
│  └─ Avg Time: 2m  ├─ 1 failed      │
│                   └─ 0 paused      │
├─────────────────────────────────────┤
│  ⚙️  Config Editor                  │
│  monitor_folder: ./videos/incoming  │
│  output_folder: ./videos/processed  │
│  [SAVE]  [RESET]                   │
├─────────────────────────────────────┤
│  Job Controls                       │
│  [Pause]  [Resume]  [Cancel]       │
└─────────────────────────────────────┘
```

---

## 🔄 The Architecture

### **Three Layers**

1. **Backend (FastAPI)**
   - REST API endpoints
   - WebSocket for real-time updates
   - Database connection
   - Video transcoding service integration

2. **Frontend (React/TypeScript)**
   - Dashboard UI
   - Real-time job monitoring
   - Config editor
   - Job controls

3. **Connection (WebSocket)**
   - Server → Client: Live updates
   - Client → Server: Commands
   - Zero latency monitoring

---

## 📊 By The Numbers

| Metric | Value |
|--------|-------|
| **Estimated Time** | 2-3 weeks |
| **Backend Endpoints** | 8-10 REST API |
| **Frontend Views** | 4 main views |
| **WebSocket Messages** | Real-time updates |
| **Database Tables** | 2-3 new tables |
| **Code Files to Create** | ~15 files |
| **Code Files to Modify** | ~5 existing files |
| **Lines of Code** | ~2000 total |
| **Tests to Add** | 20-30 integration tests |
| **Existing Tests Broken** | 0 (backward compatible) |

---

## 🗓️ Timeline

### **Week 1: MVP Backend (Days 1-5)**
```
Mon: FastAPI server + REST endpoints
Tue: WebSocket setup + real-time updates  
Wed: Database models + integration
Thu: Testing + bug fixes
Fri: Basic React frontend + CSS
```
**Outcome:** Functional dashboard with live data

### **Week 2: Features (Days 6-10)**
```
Mon: Job controls (pause, cancel, requeue)
Tue: Config editor
Wed: Historical stats + charts
Thu: Error handling + alerts
Fri: UI polish + responsive design
```
**Outcome:** Feature-complete dashboard

### **Week 3: Production (Days 11-15)**
```
Mon: Security hardening
Tue: Docker support
Wed: Full documentation
Thu: Performance optimization
Fri: Final testing + merge to main
```
**Outcome:** Production-ready, merged to main

---

## 🎨 Core Views

### **1. Dashboard (Main View)**
- Real-time stats
- Live job list with progress
- Quick status indicators
- Refresh rate: 1-2 seconds

### **2. Job Monitor**
- All jobs in queue + completed
- Progress bars
- Estimated time remaining
- Error messages
- Action buttons

### **3. Configuration Editor**
- Edit monitor folder
- Edit output folder
- Save/reset buttons
- Validation on save

### **4. Historical Stats**
- Chart: Jobs over time
- Chart: Processing time distribution
- Table: Top performed videos
- Filters by date range

---

## 🔌 API Endpoints

### **Stats Endpoints**
```
GET /api/stats/summary         # Overall stats
GET /api/stats/history         # Historical data
GET /api/stats/timeline        # Timeline chart data
```

### **Job Endpoints**
```
GET    /api/jobs              # All jobs
GET    /api/jobs/{id}         # Single job
POST   /api/jobs/{id}/pause   # Pause job
POST   /api/jobs/{id}/resume  # Resume job
POST   /api/jobs/{id}/cancel  # Cancel job
DELETE /api/jobs/{id}         # Delete job
```

### **Config Endpoints**
```
GET    /api/config            # Get current config
POST   /api/config            # Update config
DELETE /api/config/reset      # Reset to defaults
```

### **WebSocket Endpoint**
```
WS /ws/updates                # Real-time updates
  - Job progress updates
  - Stats updates
  - Error notifications
```

---

## 🧬 Tech Stack

### **Backend**
- **Framework:** FastAPI 0.104+
- **Database:** SQLite (built-in)
- **ORM:** SQLAlchemy
- **WebSocket:** FastAPI WebSocket
- **Validation:** Pydantic v2
- **Testing:** Pytest + async fixtures

### **Frontend**
- **Framework:** React 18
- **Language:** TypeScript (optional)
- **Styling:** TailwindCSS
- **Charts:** Chart.js
- **Real-time:** WebSocket
- **HTTP:** Fetch API

### **DevOps**
- **Docker:** Multi-stage builds
- **Compose:** Local development
- **Database:** SQLite + auto-migration
- **Secrets:** Environment variables

---

## 🎯 Success Criteria

### **By End of Week 1**
- [ ] FastAPI server runs locally
- [ ] 8+ REST endpoints working
- [ ] WebSocket real-time updates working
- [ ] React frontend loads
- [ ] Live job monitoring working
- [ ] All Phase 2.4 tests still passing

### **By End of Week 2**
- [ ] All 10 API endpoints working
- [ ] Config editor functional
- [ ] Job controls (pause/cancel) working
- [ ] Charts + stats displaying
- [ ] Responsive UI (mobile/desktop)
- [ ] All new integration tests passing

### **By End of Week 3**
- [ ] Production-ready code
- [ ] Security hardened
- [ ] Docker image builds
- [ ] Full documentation complete
- [ ] Merged to main
- [ ] Deployed test version
- [ ] Phase 3.2 ready to start

---

## 🚀 Integration Points

### **With Phase 2.4**
- Dashboard queries `MonitorService` for live jobs
- Dashboard submits job commands to queue
- Dashboard reads config from same file
- Dashboard uses same database schema (extended)

### **No Breaking Changes**
- Phase 2.4 CLI still works unchanged
- Config files still compatible
- Database schema backward compatible
- All existing tests still pass

---

## 📈 Data Models

### **Job Model**
```python
class Job:
    id: str
    filename: str
    status: str          # queued, processing, completed, failed
    progress: float      # 0.0 to 1.0
    started_at: datetime
    completed_at: datetime
    error: Optional[str]
    profile: str
```

### **Stats Model**
```python
class Stats:
    total_jobs: int
    successful: int
    failed: int
    avg_duration: float
    last_24h: List[JobCount]
```

### **Config Model**
```python
class Config:
    monitor_folder: Path
    output_folder: Path
    rules: List[Rule]
    max_workers: int
```

---

## 🔐 Security

- **Auth:** Optional API key (configurable)
- **CORS:** Configurable origins
- **Rate Limiting:** 100 req/min per endpoint
- **Validation:** All inputs validated
- **Secrets:** No hardcoded credentials

---

## 📦 Deliverables

### **Code**
- ✅ FastAPI backend
- ✅ React frontend
- ✅ Integration tests
- ✅ Docker setup

### **Documentation**
- ✅ API documentation
- ✅ Deployment guide
- ✅ User guide
- ✅ Architecture document

### **Operational**
- ✅ Docker image
- ✅ Production config
- ✅ Health check endpoints
- ✅ Monitoring logs

---

## ❓ FAQ

**Q: Will dashboard work without real ffmpeg?**  
A: Yes! The mock system will generate fake jobs. Perfect for development.

**Q: Can I add more stats later?**  
A: Absolutely. Architecture supports adding more endpoints easily.

**Q: How real-time is the WebSocket?**  
A: Updates push within 500ms of job state change.

**Q: Do I need to know React?**  
A: Basic knowledge helps, but we start simple. Grow with it.

**Q: Can I use a different frontend framework?**  
A: Yes! Backend stays identical. Frontend is independent.

**Q: Will this break Phase 2.4?**  
A: No. Fully backward compatible. Phase 2.4 tests stay green.

**Q: How long will it take?**  
A: 40-50 hours over 3 weeks for full production system.

**Q: Can I deploy this?**  
A: Yes. Docker setup included. Ready for production week 3.

---

## 🎓 Learning Path

If you're new to any tech:

1. **FastAPI:** 2 hour intro → build along with phase
2. **React:** 2 hour intro → build along with phase
3. **WebSocket:** 30 min intro → implement in day 4
4. **TailwindCSS:** 1 hour intro → use while styling

All learning happens through building. No separate course needed.

---

## 💪 Confidence Level

**98% confident this plan works** because:
- ✅ Phase 2.4 is stable foundation
- ✅ Tech choices are proven
- ✅ Timeline is realistic
- ✅ Architecture is solid
- ✅ No external dependencies
- ✅ Backward compatible
- ✅ Testing framework ready

---

## 🏁 The Finish Line

When Phase 3.1 is done:

```bash
# Start the dashboard
python -m bulletproof.dashboard

# Visit in browser
http://localhost:8000

# See real-time monitoring
# Control jobs from UI
# View historical stats
# Edit config from UI
# All in one place
```

---

## 📞 Next Steps

1. **Read:** PHASE-3.1-TECH-DECISIONS.md (understand choices)
2. **Review:** PHASE-3.1-WEB-DASHBOARD.md (see full plan)
3. **Study:** PHASE-3.1-QUICKSTART.md (get ready)
4. **Start:** Monday, December 30

---

**Status:** Ready to Start 🚀  
**Next:** PHASE-3.1-TECH-DECISIONS.md  
**Start Date:** December 30, 2025  

Let's build something great! 🎉
