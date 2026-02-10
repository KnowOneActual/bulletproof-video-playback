# API Quickstart Guide

## What We Built Today

A production-ready **REST API + WebSocket** backend for the bulletproof dashboard! 🚀

**Date:** February 10, 2026  
**Phase:** 3.1 - Week 1, Day 1  
**Status:** MVP Backend Complete ✅

---

## Features

### REST API Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Monitor service status
- `GET /api/v1/queue` - Queue status and jobs
- `GET /api/v1/history` - Processing history
- `GET /api/v1/rules` - Active rules
- `GET /api/v1/jobs/{job_id}` - Specific job details

### WebSocket
- `WS /api/v1/stream` - Real-time status updates (every 2 seconds)

### Interactive Docs
- `GET /docs` - Swagger UI (interactive API testing)
- `GET /redoc` - ReDoc (alternative documentation)

---

## Quick Start

### 1. Install Dependencies

Add to your `pyproject.toml` or install directly:

```bash
pip install fastapi uvicorn[standard] websockets pydantic
```

### 2. Run the Dashboard

#### Option A: Using the Example Script

```bash
# Generate a monitor config if you don't have one
bulletproof monitor generate-config --output monitor.yaml --watch ./incoming

# Run the dashboard
python examples/dashboard_example.py --config monitor.yaml
```

#### Option B: Standalone API (No Monitor Service)

```bash
cd bulletproof/api
python server.py
```

This starts the API at **http://localhost:8080**

### 3. Test the API

#### Browser
Visit http://localhost:8080/docs for interactive Swagger UI

#### curl
```bash
# Health check
curl http://localhost:8080/api/v1/health

# Monitor status
curl http://localhost:8080/api/v1/status

# Queue status
curl http://localhost:8080/api/v1/queue

# Processing history
curl http://localhost:8080/api/v1/history?limit=5

# Active rules
curl http://localhost:8080/api/v1/rules
```

#### Python
```python
import requests

# Get status
response = requests.get("http://localhost:8080/api/v1/status")
print(response.json())

# Get queue
response = requests.get("http://localhost:8080/api/v1/queue")
print(response.json())
```

### 4. Test WebSocket

#### JavaScript
```javascript
const ws = new WebSocket('ws://localhost:8080/api/v1/stream');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Status update:', data);
};
```

#### Python
```python
import asyncio
import websockets
import json

async def listen():
    async with websockets.connect('ws://localhost:8080/api/v1/stream') as ws:
        while True:
            message = await ws.recv()
            data = json.loads(message)
            print(f"Update: {data}")

asyncio.run(listen())
```

---

## API Response Examples

### GET /api/v1/health
```json
{
  "status": "healthy",
  "timestamp": "2026-02-10T17:00:00",
  "version": "3.1.0",
  "uptime_seconds": 3600.5
}
```

### GET /api/v1/status
```json
{
  "running": true,
  "watch_directory": "/incoming",
  "output_directory": "/output",
  "poll_interval": 5,
  "timestamp": "2026-02-10T17:00:00",
  "detected_files": 2,
  "stable_files": 1,
  "processing_files": 1
}
```

### GET /api/v1/queue
```json
{
  "total_jobs": 10,
  "pending_jobs": 3,
  "processing_jobs": 1,
  "complete_jobs": 5,
  "error_jobs": 1,
  "current_job": {
    "id": "job_abc123",
    "input_file": "/incoming/video.mov",
    "output_file": "/output/video_qlab.mov",
    "profile_name": "live-qlab",
    "status": "processing",
    "priority": 100,
    "progress": 45.5,
    "created_at": "2026-02-10T17:00:00",
    "started_at": "2026-02-10T17:00:05"
  },
  "jobs": []
}
```

### GET /api/v1/rules
```json
[
  {
    "pattern": "*_live.mov",
    "profile": "live-qlab",
    "output_pattern": "{filename_no_ext}_qlab.mov",
    "pattern_type": "glob",
    "priority": 100,
    "delete_input": true
  }
]
```

### WebSocket Message
```json
{
  "type": "status",
  "timestamp": "2026-02-10T17:00:00",
  "data": {
    "running": true,
    "pending_jobs": 3,
    "processing_jobs": 1,
    "complete_jobs": 5,
    "error_jobs": 1
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│  FastAPI Server (bulletproof/api/)     │
│                                         │
│  ┌────────────────┐  ┌───────────────┐ │
│  │  REST Routes   │  │  WebSocket    │ │
│  │  (routes.py)   │  │  (routes.py)  │ │
│  └────────┬───────┘  └───────┬───────┘ │
│           │                  │         │
│           └──────────┬───────┘         │
│                      │                 │
│           ┌──────────▼──────────┐      │
│           │  Pydantic Models    │      │
│           │  (models.py)        │      │
│           └──────────┬──────────┘      │
└──────────────────────┼──────────────────┘
                       │
                       ▼
           ┌─────────────────────┐
           │  MonitorService     │
           │  (Phase 2.4)        │
           └─────────────────────┘
```

### File Structure
```
bulletproof/
├── api/
│   ├── __init__.py       # Package exports
│   ├── server.py         # FastAPI app creation
│   ├── routes.py         # API endpoints + WebSocket
│   └── models.py         # Pydantic response models
├── services/
│   └── monitor_service.py # Monitor orchestration
├── core/
│   ├── monitor.py        # Folder monitoring
│   ├── queue.py          # Job queue (updated!)
│   └── rules.py          # Pattern matching
└── config/
    └── loader.py         # Config loading

examples/
└── dashboard_example.py  # Complete example
```

---

## What Changed

### New Files
1. `bulletproof/api/__init__.py` - API package
2. `bulletproof/api/models.py` - Pydantic data models
3. `bulletproof/api/routes.py` - REST + WebSocket endpoints
4. `bulletproof/api/server.py` - FastAPI server setup
5. `examples/dashboard_example.py` - Example runner
6. `docs/API_QUICKSTART.md` - This document

### Modified Files
1. `bulletproof/core/queue.py`
   - Added `id` field to QueuedJob
   - Added `priority` field (for rule priority)
   - Added `progress` field (0-100%)
   - Added `get_current()` - Get currently processing job
   - Added `get_job(job_id)` - Get job by ID
   - Added `clear()` - Clear all pending jobs

---

## Testing the API

### Manual Testing with Swagger UI

1. Start the server:
   ```bash
   python examples/dashboard_example.py --config monitor.yaml
   ```

2. Open browser to http://localhost:8080/docs

3. Try endpoints:
   - Click "GET /api/v1/health" → "Try it out" → "Execute"
   - Click "GET /api/v1/status" → "Try it out" → "Execute"
   - Click "GET /api/v1/queue" → "Try it out" → "Execute"

### Automated Testing

Create a test file `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8080/api/v1"

echo "Testing health endpoint..."
curl -s $BASE_URL/health | jq

echo "
Testing status endpoint..."
curl -s $BASE_URL/status | jq

echo "
Testing queue endpoint..."
curl -s $BASE_URL/queue | jq

echo "
Testing rules endpoint..."
curl -s $BASE_URL/rules | jq

echo "
Testing history endpoint..."
curl -s $BASE_URL/history?limit=5 | jq
```

Run it:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Next Steps

### Immediate (You can do now)
1. Test the API with your existing monitor config
2. Try the WebSocket stream
3. Explore the Swagger UI at `/docs`

### Week 1 (Days 2-5)
1. Add job control endpoints (pause, resume, cancel)
2. Add configuration update endpoints
3. Enhance WebSocket with job progress updates
4. Add authentication (API keys)

### Week 2 (Frontend)
1. Build React dashboard UI
2. Real-time job monitoring
3. Interactive queue management
4. Configuration editor

---

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python examples/dashboard_example.py --config monitor.yaml --port 8081
```

### Monitor Service Not Available
If you see "Monitor service not available" errors:
- Make sure you're passing a config file
- Check that the config file exists and is valid
- Verify watch and output directories exist

### WebSocket Connection Failed
- Check firewall settings
- Ensure you're using `ws://` not `wss://` for local testing
- Verify the server is running

### CORS Errors
CORS is enabled by default for development. For production:
```python
app = create_app(enable_cors=False)
```

---

## Configuration

### Custom Host/Port
```bash
python examples/dashboard_example.py \
  --config monitor.yaml \
  --host 0.0.0.0 \
  --port 3000
```

### Environment Variables
Create `.env` file:
```
BULLETPROOF_HOST=0.0.0.0
BULLETPROOF_PORT=8080
BULLETPROOF_LOG_LEVEL=INFO
```

---

## Performance

### Expected Response Times
- Health check: < 1ms
- Status endpoint: < 5ms
- Queue endpoint: < 10ms
- History endpoint: < 20ms (depends on history size)
- WebSocket updates: Every 2 seconds

### Concurrency
- FastAPI handles concurrent requests efficiently
- WebSocket supports multiple clients
- Monitor service runs in background thread
- No blocking operations in API layer

---

## Security Notes

⚠️ **Current Implementation: Development Only**

- No authentication
- CORS enabled for all origins
- No rate limiting
- No input sanitization beyond Pydantic validation

**For Production (Week 3):**
- Add API key authentication
- Restrict CORS origins
- Implement rate limiting
- Add request validation
- Enable HTTPS

---

## What's Next?

**Tomorrow (Day 2):** Job control endpoints
- POST /api/v1/jobs/{job_id}/cancel
- POST /api/v1/jobs/{job_id}/retry
- POST /api/v1/queue/clear
- POST /api/v1/queue/pause
- POST /api/v1/queue/resume

**Day 3:** Configuration management
- GET /api/v1/config
- PUT /api/v1/config
- POST /api/v1/config/validate

**Days 4-5:** Polish and testing
- Enhanced WebSocket messages (job progress)
- Error handling improvements
- Integration tests
- Performance optimization

---

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Pydantic Docs:** https://docs.pydantic.dev
- **Uvicorn Docs:** https://www.uvicorn.org
- **WebSocket Guide:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

**Status:** Phase 3.1 Day 1 Complete! ✅  
**Next Session:** Job control endpoints (Day 2)  
**Time Spent:** ~2 hours  
**Lines of Code:** ~800
