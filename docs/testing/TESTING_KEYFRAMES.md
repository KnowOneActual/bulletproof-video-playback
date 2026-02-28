# Testing Keyframe Feature

## Quick Test

To test the keyframe feature with a sample video:

### Step 1: Checkout the Branch

```bash
git checkout feature/keyframe-support
pip install -e .
```

### Step 2: Get a Test Video

You can use any video file you have, or create a test video:

```bash
# Create a 30-second test video (requires ffmpeg)
ffmpeg -f lavfi -i testsrc=duration=30:size=1280x720:rate=24 \
       -pix_fmt yuv420p test_video.mp4
```

### Step 3: Run the Test Script

```bash
python test_keyframes.py test_video.mp4
```

The script will:
1. ✅ Analyze the source video
2. 🔄 Transcode using `live-qlab` profile (5-second keyframes)
3. 📊 Analyze the output keyframes
4. ✅ Verify intervals match expected 5 seconds

### Expected Output

```
============================================================
🎬 KEYFRAME INTERVAL TEST
============================================================

📹 Input video: test_video.mp4

📊 SOURCE VIDEO ANALYSIS
------------------------------------------------------------
  Framerate: 24.00 fps
  Duration: 30.00 seconds
  Keyframes found: 15
  Average interval: 2.00 seconds
  ✅ Source keyframe interval: 2.00s

🔄 TRANSCODING WITH KEYFRAMES
------------------------------------------------------------
  Profile: live-qlab (5-second keyframe interval)
  Output: test_video__keyframe_test.mov
  Expected keyframe interval: 5.0s
  Force keyframes: True

Transcoding: test_video.mp4
Duration: 0.5 minutes
Speed Preset: fast
Keyframe Interval: 5.0s (easy scrubbing enabled)

Progress: |██████████████████████████████████████████████████| 100.0%

✅ Transcode complete!

📊 OUTPUT VIDEO ANALYSIS
------------------------------------------------------------
  Framerate: 24.00 fps
  Duration: 30.00 seconds
  Keyframes found: 7
  Average interval: 5.00 seconds
  First 10 intervals: ['5.00', '5.00', '5.00', '5.00', '5.00', '5.00']

🔍 VERIFICATION
------------------------------------------------------------
  Expected interval: 5.0s
  Actual avg interval: 5.00s
  Tolerance: ±0.5s

✅ SUCCESS! Keyframe intervals are correct!
   Keyframes every ~5.0s (target: 5.0s)

📋 SUMMARY
------------------------------------------------------------
  Input file: test_video.mp4
  Output file: test_video__keyframe_test.mov
  Output size: 12.5 MB
  Keyframes in output: 7
  Average interval: 5.00s
  Min interval: 5.00s
  Max interval: 5.00s

============================================================
```

## Manual Testing

You can also test manually:

### Test with CLI

```bash
# Transcode with live-qlab profile
bvp transcode input.mov --profile live-qlab --output output.mov

# Check keyframes in output
ffprobe -select_streams v -show_frames output.mov | grep "pict_type=I"
```

### Test with TUI

```bash
bvp tui
# Select your video and live-qlab profile
# Watch for "Keyframe Interval: 5.0s" message during transcode
```

### Test with Folder Monitor

```bash
# Create config
bvp monitor generate-config --output test_monitor.yaml --watch ./input

# Start monitoring
bvp monitor start --config test_monitor.yaml

# Drop video in ./input folder
# Check output for keyframes
```

## Verifying Keyframes Manually

### Method 1: Count I-frames

```bash
ffprobe -select_streams v -show_frames output.mov 2>/dev/null | \
  grep "pict_type=I" | wc -l
```

### Method 2: Show I-frame timestamps

```bash
ffprobe -select_streams v -show_entries frame=pict_type,pts_time \
  -of csv output.mov 2>/dev/null | grep "I,"
```

### Method 3: Visual with MediaInfo

If you have MediaInfo installed:

```bash
mediainfo --Details=1 output.mov | grep "keyframe"
```

## What to Look For

### ✅ Success Indicators

1. **During transcode**: See "Keyframe Interval: 5.0s (easy scrubbing enabled)"
2. **After transcode**: Test script shows "SUCCESS! Keyframe intervals are correct!"
3. **In output**: Keyframes appear every ~5 seconds (within 0.5s tolerance)
4. **Scrubbing test**: Open output.mov in VLC or QLab - scrubbing should be instant

### ❌ Failure Indicators

1. **No keyframe message**: Keyframe setting not applied
2. **Wrong interval**: Keyframes not at 5-second intervals
3. **Too many keyframes**: Every frame is a keyframe (wasteful)
4. **Too few keyframes**: Original keyframe structure preserved (feature not working)

## Testing Different Profiles

```bash
# Test live-qlab (5s keyframes)
python test_keyframes.py input.mov

# Manually test streaming profile (2s keyframes)
bvp transcode input.mov --profile stream-hd --output stream_test.mp4
ffprobe -select_streams v -show_entries frame=pict_type,pts_time \
  -of csv stream_test.mp4 2>/dev/null | grep "I,"
```

## Real-World Test: QLab Scrubbing

### Before vs After Comparison

1. **Convert your show video**:
   ```bash
   bvp transcode show_video.mov --profile live-qlab --output show_qlab.mov
   ```

2. **Import both to QLab**:
   - Original: `show_video.mov`
   - Transcoded: `show_qlab.mov`

3. **Test scrubbing**:
   - Drag the playhead in both
   - Transcoded version should respond instantly
   - Original may lag or stutter

4. **Test cue points**:
   - Set cues at specific times
   - Jump between cues
   - Transcoded version should be instant

## Troubleshooting

### Issue: Test script fails to import bvp

**Solution:**
```bash
pip install -e .
```

### Issue: ffprobe not found

**Solution:**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Issue: Keyframe intervals wrong

**Check:**
1. Are you on the `feature/keyframe-support` branch?
2. Did you reinstall after checking out? (`pip install -e .`)
3. Is ffprobe detecting framerate correctly?

### Issue: Output file huge

**Expected:** ProRes files are large (that's the point - high quality)
- 1080p 30s video: ~50-100 MB
- 4K 30s video: ~200-400 MB

This is normal for ProRes Proxy.

## CI/CD Testing

To add this to CI/CD:

```yaml
# .github/workflows/test-keyframes.yml
name: Test Keyframes
on: [push, pull_request]

jobs:
  test-keyframes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
          pip install -e .
      - name: Create test video
        run: |
          ffmpeg -f lavfi -i testsrc=duration=30:size=1280x720:rate=24 \
                 -pix_fmt yuv420p test_video.mp4
      - name: Test keyframes
        run: python test_keyframes.py test_video.mp4
```

## Questions?

If keyframes aren't working as expected:
1. Run `python test_keyframes.py <your_video>`
2. Check the output for error messages
3. Post the full output in a GitHub issue

---

**Ready to test!** Just run: `python test_keyframes.py <your_video>`
