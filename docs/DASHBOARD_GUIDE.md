# 📊 Dashboard Quick Start Guide

**Last Updated:** April 15, 2026  
**Phase:** 3.1 (Web Dashboard)  
**Status:** Feature Complete ✅

---

## 🚀 Start the Dashboard in 60 Seconds

### Prerequisites
- Python 3.10+
- FFmpeg installed (`brew install ffmpeg` / `apt install ffmpeg`)
- Bulletproof installed with API extras:

```bash
# Install from GitHub (development)
pip install -e ".[api]"

# Or install globally with pipx
pipx install "bulletproof-video-playback[api] @ git+https://github.com/KnowOneActual/bulletproof-video-playback.git"
```

### Quick Start (No Folder Monitor)

Start the dashboard API server:

```bash
python -m bulletproof.api.server --host 127.0.0.1 --port 8000
```

Open your browser to: **http://localhost:8000/dashboard/**

You'll see the dashboard UI with:
- Real-time queue statistics
- Job table (empty initially)
- WebSocket connection indicator
- Monitor controls

### With Folder Monitoring

Create a monitor configuration:

```bash
# Generate a sample config
bvp monitor generate-config --output monitor.yaml --watch ./incoming

# Edit monitor.yaml to set output directory
# (Optional) Add pattern rules for automatic transcoding
```

Start the dashboard with monitoring enabled:

```bash
python examples/dashboard_example.py --config monitor.yaml
```

The dashboard will:
1. Start the API server on `http://localhost:8000`
2. Mount the web dashboard at `/dashboard/`
3. Start folder monitoring based on your config
4. Begin processing any files in the watch directory

---

## 🎨 Dashboard Features

### Real-time Monitoring
- **Queue Statistics**: Total, pending, processing, completed, and failed jobs
- **Progress Bars**: Live progress for active transcoding jobs
- **Job Details**: Click any job to see detailed information
- **WebSocket Updates**: Instant notifications for all job state changes

### Job Controls
- **Cancel**: Stop a running or pending job
- **Retry**: Re‑queue a failed job
- **Details**: View job parameters, progress, and error messages
- **Queue Management**: Pause/resume/clear the entire processing queue

### Monitor Controls
- **Monitor Status**: See if folder monitoring is active
- **Start/Stop**: Control the folder monitor service
- **Configuration**: View and update monitor settings via API

### Responsive Design
- Works on desktop, tablet, and mobile
- Clean, professional interface using Bulma CSS
- Dark theme optimized for control rooms

---

## 🔌 API Integration

The dashboard is built on top of the Bulletproof REST API:

### Key Endpoints
- `GET /api/v1/status` - System and monitor status
- `GET /api/v1/queue` - Job queue with full details
- `POST /api/v1/jobs/{id}/cancel` - Cancel a specific job
- `POST /api/v1/jobs/{id}/retry` - Retry a failed job
- `POST /api/v1/queue/pause` - Pause all processing
- `POST /api/v1/queue/resume` - Resume processing
- `GET /api/v1/config` - Current monitor configuration
- `PATCH /api/v1/config` - Update configuration live

### WebSocket Stream
- `ws://localhost:8000/stream` - Real-time events
- Events include: `job_started`, `job_progress`, `job_completed`, `job_failed`, `file_detected`
- The dashboard automatically reconnects if the connection drops

### OpenAPI Documentation
Visit **http://localhost:8000/docs** for interactive API documentation with live testing.

---

## 🛠️ Advanced Usage

### Custom Dashboard Port
```bash
python -m bulletproof.api.server --host 0.0.0.0 --port 8080
```

### Different Static Directory
```bash
python examples/dashboard_example.py --config monitor.yaml --static-dir /path/to/custom/dashboard
```

### API-Only Mode (No Dashboard)
```bash
# Start just the API server without serving static files
python -m bulletproof.api.server --host 127.0.0.1 --port 8000 --no-static
```

### Docker Deployment
```dockerfile
# Example Dockerfile (simplified)
FROM python:3.11-slim
RUN pip install bulletproof-video-playback[api]
COPY monitor.yaml /app/
WORKDIR /app
CMD ["python", "-m", "bulletproof.api.server", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🐛 Troubleshooting

### Dashboard Not Loading
- **Check port**: Ensure port 8000 is free (`lsof -i :8000`)
- **Check dependencies**: `pip list | grep bulletproof`
- **Check API**: Visit `http://localhost:8000/api/v1/status` - should return JSON

### WebSocket Not Connecting
- **Browser console**: Check for WebSocket errors (F12 → Console)
- **Server logs**: Look for WebSocket connection messages
- **Firewall**: Ensure WebSocket connections are allowed (ws://)

### Jobs Not Appearing
- **Monitor status**: Check `http://localhost:8000/api/v1/status`
- **Queue endpoint**: Check `http://localhost:8000/api/v1/queue`
- **File detection**: Ensure files are in the correct watch directory

### Missing Dependencies
```bash
# Install missing packages
pip install fastapi uvicorn[standard] websockets pyyaml
```

---

## 📚 Related Documentation

- [API Quick Start](../docs/API_QUICKSTART.md) - Detailed API reference
- [Roadmap](../docs/ROADMAP.md) - Project status and future plans
- [Monitor Guide](../docs/MONITOR_GUIDE.md) - Folder monitoring configuration
- [Keyframe Feature](../docs/features/KEYFRAME_FEATURE.md) - Professional keyframe control

---

## 🎯 Next Steps

1. **Test with real videos**: Drop a video in your watch directory and watch it process
2. **Customize configuration**: Edit `monitor.yaml` to match your workflow
3. **Integrate with other tools**: Use the REST API for automation
4. **Provide feedback**: Report issues or suggest improvements

---

**Enjoy your new dashboard!** 🎬

> *Built for live event production where "no show-day embarrassments" is the primary mandate.*