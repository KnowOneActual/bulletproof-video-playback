# 📥 PHASE 3.1 - QUICKSTART (DAY-BY-DAY)

**Start Date:** Monday, December 30, 2025  
**Duration:** 15 days  
**Outcome:** Production-ready web dashboard  

---

## 🗣️ Before You Start

### **Prerequisites**
```bash
# 1. Phase 2.4 must be complete
git checkout feature/folder-monitor
pytest tests/ -v
# Must show: 32/32 passed ✅

# 2. Python 3.11+
python --version

# 3. Node.js 18+ (for frontend)
node --version

# 4. Git clean
git status
# Must be clean (nothing uncommitted)
```

---

## 🗓️ WEEK 1: MVP Backend

### **DAY 1 (Monday): Setup + FastAPI Server**

**Time:** 2-3 hours  
**Goal:** FastAPI running locally

#### **Step 1: Create branch**
```bash
git checkout feature/folder-monitor
git checkout -b feature/dashboard
git push -u origin feature/dashboard
```

#### **Step 2: Install dependencies**
```bash
# Add to pyproject.toml
add fastapi==0.104.1
add uvicorn[standard]==0.24.0
add pydantic==2.5.0
add sqlalchemy==2.0.23
add aiosqlite==0.19.0
add python-multipart==0.0.6

pip install -e .
```

#### **Step 3: Create backend structure**
```bash
mkdir -p bulletproof/dashboard
mkdir -p bulletproof/dashboard/api
mkdir -p bulletproof/dashboard/models
mkdir -p bulletproof/dashboard/web

touch bulletproof/dashboard/__init__.py
touch bulletproof/dashboard/api.py
touch bulletproof/dashboard/models.py
touch bulletproof/dashboard/server.py
```

#### **Step 4: Create FastAPI server** (`bulletproof/dashboard/server.py`)
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

app = FastAPI(title="Bulletproof Dashboard")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "3.1.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **Step 5: Test it works**
```bash
# Terminal 1
python -m bulletproof.dashboard.server

# Terminal 2
curl http://localhost:8000/api/health
# Expected: {"status": "healthy", "version": "3.1.0"}
```

#### **Step 6: Commit**
```bash
git add bulletproof/dashboard/
git add pyproject.toml
git commit -m "feat: Add FastAPI server skeleton for dashboard

- FastAPI app running on localhost:8000
- CORS enabled for local development
- Health check endpoint working
- Ready for API endpoints

Day 1 complete"
```

**Checklist:**
- [ ] FastAPI server runs
- [ ] Health endpoint works
- [ ] Changes committed
- [ ] `pytest tests/ -v` still passes (32/32)

---

### **DAY 2 (Tuesday): REST API Endpoints**

**Time:** 2-3 hours  
**Goal:** 8+ REST endpoints working

#### **Step 1: Create data models** (`bulletproof/dashboard/models.py`)
```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class JobStatus(str):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobModel(BaseModel):
    id: str
    filename: str
    status: str
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    profile: str = "default"

class StatsModel(BaseModel):
    total_jobs: int
    successful: int
    failed: int
    avg_duration: float
    in_progress: int

class ConfigModel(BaseModel):
    monitor_folder: str
    output_folder: str
    max_workers: int = 4
```

#### **Step 2: Add endpoints** (update `bulletproof/dashboard/api.py`)
```python
from fastapi import APIRouter
from typing import List
from .models import JobModel, StatsModel, ConfigModel

router = APIRouter(prefix="/api")

# Mock data for now
MOCK_JOBS = [
    JobModel(id="1", filename="video1.mov", status="processing", progress=0.45),
    JobModel(id="2", filename="video2.mov", status="queued"),
]

@router.get("/jobs", response_model=List[JobModel])
async def get_jobs():
    """Get all jobs"""
    return MOCK_JOBS

@router.get("/jobs/{job_id}", response_model=JobModel)
async def get_job(job_id: str):
    """Get single job"""
    for job in MOCK_JOBS:
        if job.id == job_id:
            return job
    raise HTTPException(status_code=404)

@router.get("/stats", response_model=StatsModel)
async def get_stats():
    """Get overall stats"""
    return StatsModel(
        total_jobs=100,
        successful=93,
        failed=7,
        avg_duration=120.5,
        in_progress=2
    )

@router.get("/config", response_model=ConfigModel)
async def get_config():
    """Get current configuration"""
    return ConfigModel(
        monitor_folder="./videos/incoming",
        output_folder="./videos/output",
    )

@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause a job"""
    return {"job_id": job_id, "action": "paused"}

@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume a job"""
    return {"job_id": job_id, "action": "resumed"}

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a job"""
    return {"job_id": job_id, "action": "cancelled"}
```

#### **Step 3: Update server to use router**
```python
from .api import router

app.include_router(router)
```

#### **Step 4: Test endpoints**
```bash
# Run server
python -m bulletproof.dashboard.server

# In another terminal, test endpoints
curl http://localhost:8000/api/jobs
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/config
```

#### **Step 5: Commit**
```bash
git add bulletproof/dashboard/api.py
git add bulletproof/dashboard/models.py
git commit -m "feat: Add 8 REST API endpoints with mock data

- GET /api/jobs - List all jobs
- GET /api/jobs/{id} - Get single job
- POST /api/jobs/{id}/pause - Pause job
- POST /api/jobs/{id}/resume - Resume job
- POST /api/jobs/{id}/cancel - Cancel job
- GET /api/stats - Get statistics
- GET /api/config - Get configuration
- All using mock data for now

Day 2 complete"
```

**Checklist:**
- [ ] All 8 endpoints respond with 200
- [ ] Mock data returns correctly
- [ ] All tests still pass (32/32)
- [ ] Changes committed

---

### **DAY 3 (Wednesday): WebSocket Real-Time Updates**

**Time:** 2-3 hours  
**Goal:** WebSocket real-time connection

#### **Step 1: Add WebSocket endpoint**
```python
from fastapi import WebSocket
import asyncio
import json

active_connections = []

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Send mock updates every 2 seconds
            await asyncio.sleep(2)
            
            update = {
                "type": "job_update",
                "data": {
                    "in_progress": 2,
                    "queued": 1,
                    "completed": 45
                }
            }
            await websocket.send_json(update)
    except:
        active_connections.remove(websocket)

async def broadcast_update(message: dict):
    """Send update to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass
```

#### **Step 2: Update endpoints to broadcast**
```python
# When pausing a job
@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    await broadcast_update({
        "type": "job_paused",
        "job_id": job_id
    })
    return {"job_id": job_id, "action": "paused"}
```

#### **Step 3: Test WebSocket**
```bash
# Use websocat (install: cargo install websocat)
websocat ws://localhost:8000/ws/updates
# Should see JSON updates every 2 seconds
```

#### **Step 4: Commit**
```bash
git commit -m "feat: Add WebSocket endpoint for real-time updates

- /ws/updates WebSocket endpoint
- Broadcasts job state changes
- All connected clients receive updates
- Mock data updates every 2 seconds

Day 3 complete"
```

**Checklist:**
- [ ] WebSocket connects
- [ ] Receives JSON updates
- [ ] Updates every 2 seconds
- [ ] All tests still pass (32/32)
- [ ] Changes committed

---

### **DAY 4 (Thursday): Database Integration**

**Time:** 2-3 hours  
**Goal:** Real data from database

#### **Step 1: Create SQLAlchemy models**
```python
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    filename = Column(String)
    status = Column(String)
    progress = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(String, nullable=True)
    profile = Column(String)
```

#### **Step 2: Create database connection**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = "sqlite+aiosqlite:///./dashboard.db"

engine = create_async_engine(DATABASE_URL)

async def get_db():
    async with AsyncSession(engine) as session:
        yield session
```

#### **Step 3: Update endpoints to use database**
```python
@router.get("/jobs", response_model=List[JobModel])
async def get_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return [JobModel.from_orm(job) for job in jobs]
```

#### **Step 4: Commit**
```bash
git commit -m "feat: Add SQLAlchemy database integration

- SQLite database for persistent storage
- Job model with timestamps
- Async queries with SQLAlchemy
- Database migrations ready

Day 4 complete"
```

**Checklist:**
- [ ] Database file created
- [ ] Tables initialized
- [ ] Queries work
- [ ] All tests still pass (32/32)
- [ ] Changes committed

---

### **DAY 5 (Friday): React Frontend Skeleton**

**Time:** 2-3 hours  
**Goal:** Frontend loading and connecting

#### **Step 1: Create React app**
```bash
mkdir -p bulletproof/dashboard/web
cd bulletproof/dashboard/web
npm init -y
npm install react react-dom
npm install -D vite @vitejs/plugin-react
```

#### **Step 2: Create index.html**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulletproof Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white">
    <div id="root"></div>
    <script type="module" src="/main.jsx"></script>
</body>
</html>
```

#### **Step 3: Create main component**
```jsx
import { useEffect, useState } from 'react'

function App() {
    const [stats, setStats] = useState(null)
    const [jobs, setJobs] = useState([])
    
    useEffect(() => {
        // Fetch stats
        fetch('/api/stats')
            .then(r => r.json())
            .then(data => setStats(data))
        
        // Connect to WebSocket
        const ws = new WebSocket('ws://localhost:8000/ws/updates')
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            console.log('Update:', data)
        }
        
        return () => ws.close()
    }, [])
    
    return (
        <div className="p-8">
            <h1 className="text-4xl font-bold mb-8">Bulletproof Dashboard</h1>
            {stats && (
                <div className="grid grid-cols-4 gap-4">
                    <div className="bg-blue-900 p-4 rounded">
                        <p className="text-gray-400">Total</p>
                        <p className="text-2xl font-bold">{stats.total_jobs}</p>
                    </div>
                    <div className="bg-green-900 p-4 rounded">
                        <p className="text-gray-400">Success</p>
                        <p className="text-2xl font-bold">{stats.successful}</p>
                    </div>
                    <div className="bg-red-900 p-4 rounded">
                        <p className="text-gray-400">Failed</p>
                        <p className="text-2xl font-bold">{stats.failed}</p>
                    </div>
                    <div className="bg-purple-900 p-4 rounded">
                        <p className="text-gray-400">In Progress</p>
                        <p className="text-2xl font-bold">{stats.in_progress}</p>
                    </div>
                </div>
            )}
        </div>
    )
}

export default App
```

#### **Step 4: Update vite config to proxy API**
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/api': 'http://localhost:8000',
            '/ws': {
                target: 'ws://localhost:8000',
                ws: true
            }
        }
    }
})
```

#### **Step 5: Run and test**
```bash
# Terminal 1: Backend
python -m bulletproof.dashboard.server

# Terminal 2: Frontend
cd bulletproof/dashboard/web
npm run dev

# Visit http://localhost:5173
```

#### **Step 6: Commit**
```bash
git commit -m "feat: Add React frontend skeleton

- Vite + React setup
- TailwindCSS styling
- Connects to API endpoints
- WebSocket real-time updates
- Dashboard loading with stats

Day 5 complete - MVP functional!"
```

**Checklist:**
- [ ] Frontend loads at localhost:5173
- [ ] Stats display correctly
- [ ] WebSocket connects
- [ ] Shows real data from backend
- [ ] All tests still pass (32/32)
- [ ] Changes committed

---

## ✅ WEEK 1 COMPLETE!

**Outcome:** Functional MVP dashboard with:
- ✅ FastAPI backend
- ✅ 8 REST API endpoints
- ✅ Real-time WebSocket updates
- ✅ React frontend
- ✅ TailwindCSS styling
- ✅ Database integration

**Statistics:**
- **Lines of Code:** ~500
- **Files Created:** ~10
- **Tests Passing:** 32/32
- **API Endpoints:** 8
- **WebSocket Connections:** Working

---

## 🗓️ WEEK 2: Features (Days 6-10)

### **DAY 6: Job Controls**
- Implement pause/resume/cancel with real database updates
- Update WebSocket to broadcast actual state changes
- Add loading states to UI

### **DAY 7: Config Editor**
- Add config form component
- POST /api/config endpoint
- Validate and save configuration
- Show success/error messages

### **DAY 8: Historical Charts**
- Add Chart.js
- Create jobs-over-time chart
- Create duration distribution chart
- Add date range filter

### **DAY 9: Error Handling**
- Add error messages to UI
- Handle API failures
- WebSocket reconnection logic
- User-friendly error display

### **DAY 10: UI Polish**
- Responsive design (mobile/tablet)
- Dark mode (already there)
- Icon library (Heroicons)
- Loading animations
- Better color scheme

---

## 🗓️ WEEK 3: Production (Days 11-15)

### **DAY 11: Security**
- API key authentication
- CORS hardening
- Rate limiting
- Input validation

### **DAY 12: Docker**
- Multi-stage Dockerfile
- Docker Compose setup
- Production config
- Health checks

### **DAY 13: Documentation**
- API docs (Swagger)
- User guide
- Deployment guide
- Architecture document

### **DAY 14: Performance**
- Query optimization
- Caching strategy
- Frontend bundle optimization
- Load testing

### **DAY 15: Final Testing + Merge**
- Full integration testing
- Edge case handling
- Performance verification
- Merge to main
- Tag v3.1.0

---

## 📄 Success Checklist

### **Daily**
- [ ] Changes committed (meaningful messages)
- [ ] `pytest tests/ -v` still shows 32/32
- [ ] No phase 2.4 functionality broken
- [ ] Feature tested locally
- [ ] Code clean and documented

### **Weekly**
- [ ] Week goal complete
- [ ] All endpoints tested
- [ ] WebSocket working
- [ ] UI responsive
- [ ] Zero test failures

### **Final (Day 15)**
- [ ] Production-ready code
- [ ] Security hardened
- [ ] Docker working
- [ ] Documentation complete
- [ ] Merged to main
- [ ] v3.1.0 tagged

---

## 🎉 You're Ready!

This is your roadmap. Follow it step by step. Each day is 2-3 hours of focused work.

**Start Monday. Ship by Friday of Week 3.**

Let's go! 🚀
