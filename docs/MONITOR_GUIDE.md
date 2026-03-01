# Folder Monitor Guide (Phase 2.4)

**Monitor a folder for video files and automatically transcode them based on rules.**

Perfect for: live events, streaming, broadcast, archive prep, batch processing, automated workflows.

---

## Quick Start

### 1. Generate a Configuration File

```bash
bvp monitor generate-config \
  --output monitor.yaml \
  --watch /incoming \
  --profile live-qlab
```

### 2. Edit the Configuration

```yaml
watch_directory: /incoming
output_directory: /output
poll_interval: 5
delete_input: true
log_level: INFO

rules:
  - pattern: "*_live.mov"
    profile: live-qlab
    output_pattern: "{filename_no_ext}_qlab.mov"
    priority: 100
  
  - pattern: "archive_*.mov"
    profile: archive-prores
    output_pattern: "masters/{filename}"
    priority: 90
```

### 3. Start Monitoring

```bash
bvp monitor start --config monitor.yaml
```

Drop videos in `/incoming` and they'll automatically transcode to `/output`!

---

## Configuration

### Global Settings

```yaml
watch_directory: /path/to/watch
  # Required: Directory to monitor for video files

output_directory: /path/to/output
  # Required: Where to save transcoded files
  # Created automatically if it doesn't exist

poll_interval: 5
  # Optional: How often to check for new files (seconds)
  # Default: 5

delete_input: true
  # Optional: Delete input file after successful transcode
  # Default: true

log_level: INFO
  # Optional: DEBUG, INFO, WARNING, ERROR
  # Default: INFO

log_file: /path/to/monitor.log
  # Optional: Write logs to file
  # If not specified, only console output

persist_path: /path/to/queue.json
  # Optional: Where to save queue state
  # Queue survives crashes if specified
```

### Rules

Rules match video files to profiles. They're checked in priority order (highest first).

```yaml
rules:
  - pattern: "*_live.mov"
    profile: live-qlab
    output_pattern: "{filename_no_ext}_qlab.mov"
    priority: 100
    delete_input: true          # Optional: override global delete_input
```

#### Pattern Types

**Glob patterns** (default, case-insensitive):
```yaml
pattern: "*_live.mov"      # Matches: anything_live.mov, foo_live.mov
pattern: "archive_*.mov"   # Matches: archive_old.mov, archive_new.mov
pattern: "*.mov"           # Matches: any .mov file
```

**Regex patterns**:
```yaml
pattern: ".*_live_\d{4}\.mov"
pattern_type: regex
```

**Exact match**:
```yaml
pattern: "myspecific_video.mov"
pattern_type: exact
```

#### Output Path Templates

Templates support variable substitution:

```yaml
output_pattern: "{filename}"           # Same as input
output_pattern: "{filename_no_ext}_qlab.mov"
output_pattern: "masters/{filename}"
output_pattern: "{filename_no_ext}_{profile}.mov"
```

Available variables:
- `{filename}` - Original filename (e.g., "video.mov")
- `{filename_no_ext}` - Filename without extension (e.g., "video")
- `{profile}` - Profile name (e.g., "live-qlab")

---

## CLI Commands

### Start Monitoring

```bash
bvp monitor start --config monitor.yaml

# Override config settings
bvp monitor start \
  --config monitor.yaml \
  --watch /different/input \
  --output /different/output \
  --poll-interval 10 \
  --log-level DEBUG
```

**Options:**
- `--config, -c` - Config file path (YAML or JSON)
- `--watch, -w` - Override watch directory
- `--output, -o` - Override output directory  
- `--poll-interval, -p` - Override poll interval
- `--log-level, -l` - Override log level (DEBUG, INFO, WARNING, ERROR)

### Check Queue Status

```bash
bvp monitor status --queue queue.json
```

Shows:
- Pending jobs
- Currently processing
- Completed
- Errors
- Recent error details

### Clear Queue

```bash
bvp monitor clear-queue --queue queue.json
```

Prompts for confirmation before clearing.

### Generate Config Template

```bash
bvp monitor generate-config \
  --output monitor.yaml \
  --watch /input \
  --profile live-qlab
```

---

## Example Configurations

### Live Event Broadcasting

```yaml
watch_directory: /incoming
output_directory: /output
poll_interval: 2
delete_input: true
log_file: /var/log/monitor.log

rules:
  # Live broadcast files (highest priority)
  - pattern: "*_live.mov"
    profile: live-qlab
    output_pattern: "{filename_no_ext}_qlab.mov"
    priority: 100
  
  # Archive masters (lower priority)
  - pattern: "archive_*.mov"
    profile: archive-prores
    output_pattern: "masters/{filename}"
    priority: 50
  
  # Everything else as H.264
  - pattern: "*.mov"
    profile: h264-streaming
    output_pattern: "misc/{filename_no_ext}_h264.mp4"
    priority: 1
```

### Archive Preparation

```yaml
watch_directory: /incoming
output_directory: /masters
poll_interval: 5
delete_input: false  # Keep originals
log_file: /var/log/monitor.log

rules:
  # All files → ProRes master
  - pattern: "*"
    profile: archive-prores
    output_pattern: "{filename}"
    priority: 100
```

### Mixed Format Processing

```yaml
watch_directory: /incoming
output_directory: /output
poll_interval: 5

rules:
  # MOV files → ProRes
  - pattern: "*.mov"
    profile: archive-prores
    output_pattern: "{filename_no_ext}_prores.mov"
    priority: 100
  
  # MP4 files → H.264
  - pattern: "*.mp4"
    profile: h264-streaming
    output_pattern: "{filename_no_ext}_h264.mp4"
    priority: 100
  
  # MXF files → DNxHD
  - pattern: "*.mxf"
    profile: dnxhd-qlab
    output_pattern: "{filename_no_ext}_qlab.mov"
    priority: 100
```

### Streaming Pipeline

```yaml
watch_directory: /stream/incoming
output_directory: /stream/ready
poll_interval: 3
delete_input: true

rules:
  # Livestream prep
  - pattern: "stream_*.mov"
    profile: h264-streaming
    output_pattern: "hls/{filename_no_ext}.mp4"
    priority: 100
```

---

## How It Works

### Main Loop

```
Every poll_interval seconds:
  1. Scan watch_directory for new files
  2. Check if files are "stable" (finished uploading)
  3. Match files to rules (by pattern)
  4. Create transcode jobs
  5. Process jobs sequentially
  6. Delete input (if configured)
  7. Log results
```

### File Stability Detection

Before transcoding, the monitor checks if a file is "stable":
- File hasn't been modified for 2 consecutive polls
- File size hasn't changed
- This prevents transcoding incomplete uploads

### Job Persistence

If `persist_path` is set:
- Queue state is saved to JSON after each change
- Survives service crashes/restarts
- Queue resumes where it left off

---

## Troubleshooting

### Files Not Being Detected

1. Check watch directory exists:
   ```bash
   ls -la /incoming
   ```

2. Check file permissions:
   ```bash
   ls -la /incoming/*.mov
   ```

3. Enable DEBUG logging:
   ```bash
   bvp monitor start --config monitor.yaml --log-level DEBUG
   ```

4. Files might not be stable yet (wait 2+ poll cycles)

### Transcodes Failing

1. Check output directory writable:
   ```bash
   touch /output/test.txt && rm /output/test.txt
   ```

2. Check profile exists:
   ```bash
   bvp config list
   ```

3. Check logs:
   ```bash
   tail -f /var/log/monitor.log
   ```

4. Check disk space:
   ```bash
   df -h /output
   ```

### Queue Not Persisting

1. Ensure persist_path in config:
   ```yaml
   persist_path: /path/to/queue.json
   ```

2. Check directory writable:
   ```bash
   touch /path/to/queue.json && rm /path/to/queue.json
   ```

3. Check queue file exists after first transcode:
   ```bash
   ls -la /path/to/queue.json
   ```

---

## Best Practices

### 1. Use Specific Patterns

Good:
```yaml
pattern: "*_live.mov"     # Matches all _live.mov files
pattern: "archive_*.mov"  # Matches archive prefix
```

Less ideal:
```yaml
pattern: "specific_video_20250101_001.mov"  # Too specific
```

### 2. Set Appropriate Poll Intervals

- **2-5 seconds**: High-throughput (live events, streaming)
- **10-15 seconds**: Normal (batch processing, standard workflows)
- **30+ seconds**: Low-resource (overnight batch, archival)

### 3. Use Priority Ordering

```yaml
rules:
  - pattern: "*_urgent.mov"
    priority: 200      # Checked first
  
  - pattern: "*_live.mov"
    priority: 100      # Checked second
  
  - pattern: "*.mov"
    priority: 1        # Checked last (catch-all)
```

### 4. Separate Concerns

Use different watch directories:
```
/incoming/live    → /output/live
/incoming/archive → /output/archive
/incoming/web     → /output/web
```

Run separate monitor services:
```bash
bvp monitor start --config live.yaml &
bvp monitor start --config archive.yaml &
bvp monitor start --config web.yaml &
```

### 5. Monitor the Monitor

Set up cron job to check status:
```bash
0 8 * * * bvp monitor status --queue /var/lib/bvp/queue.json
```

---

## Performance Tuning

### For Fast Turnaround

```yaml
poll_interval: 2          # Check frequently
delete_input: true        # Free up space quickly
```

### For Resource Efficiency

```yaml
poll_interval: 30         # Check less often
delete_input: false       # Keep originals (don't use disk)
```

### For Large Files

```yaml
poll_interval: 10         # Balance responsiveness
delete_input: true        # Essential to manage disk
```

---

## Integration with Systemd

Create `/etc/systemd/system/bvp-monitor.service`:

```ini
[Unit]
Description=Bulletproof Video Monitor
After=network.target

[Service]
Type=simple
User=video
WorkingDirectory=/var/lib/bvp
ExecStart=/usr/local/bin/bvp monitor start --config /etc/bulletproof/monitor.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start:
```bash
sudo systemctl start bvp-monitor
sudo systemctl enable bvp-monitor
```

Check status:
```bash
sudo systemctl status bvp-monitor
sudo journalctl -u bvp-monitor -f
```

---

## Use Cases

- **Live Broadcasting** - Transcode incoming feeds in real-time
- **Streaming Services** - Batch prepare content for distribution
- **Archive Preparation** - Convert submissions to preservation formats
- **Post-Production** - Automate dailies transcoding
- **Content Distribution** - Multi-format output for different platforms
- **Quality Control** - Standardize incoming file formats
- **Batch Processing** - Handle large volumes efficiently
- **Hybrid Workflows** - Mix of live and archival processing

---

## Next Steps

### Phase 3.1: Web Dashboard
- Visual queue status
- Live monitoring
- Job history

### Phase 3.2: Notifications
- Slack messages on completion
- Email alerts on errors
- Webhooks for integration

---

**Questions?** Check the main [README.md](../README.md) or open an issue!
