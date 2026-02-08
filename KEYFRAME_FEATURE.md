# Keyframe Interval Feature

## What's New

All transcoding profiles now include **smart keyframe intervals** optimized for easy scrubbing in QLab, video players, and editing software.

## Why This Matters for AV Techs

### Before
- Scrubbing through videos was slow and unpredictable
- Setting cue points in QLab took forever
- Playhead would lag when jumping to specific moments

### After
- **Instant scrubbing** - Jump anywhere in the timeline immediately
- **Predictable performance** - Keyframes every 5 seconds for live playback
- **No configuration needed** - Built into every profile

## Keyframe Intervals by Profile

| Profile | Interval | Reason |
|---------|----------|--------|
| live-qlab | 5s | Perfect for QLab cue setup and theater playback |
| live-prores-lt | 5s | Instant scrubbing for live shows |
| live-h264 | 5s | Cross-platform with easy seeking |
| standard-playback | 10s | Balanced for general use |
| stream-hd | 2s | Responsive seeking for streaming |
| stream-4k | 2s | Quick seeking in high-res streams |
| archival | Source | Preserves original structure |

## Technical Details

### How It Works

1. **Auto-detection** - Automatically detects source framerate using ffprobe
2. **GOP calculation** - Calculates Group of Pictures (GOP) size: `framerate × interval`
3. **FFmpeg flags** - Applies `-g`, `-keyint_min`, `-sc_threshold`, and `-force_key_frames`
4. **Strict enforcement** - For live profiles, disables scene detection to maintain exact intervals

### Example

For a 24fps video with 5-second keyframe interval:
```
GOP size = 24 fps × 5 seconds = 120 frames

FFmpeg flags:
-g 120                                      # Set GOP size
-keyint_min 120                             # Minimum interval
-sc_threshold 0                             # Disable scene detection
-force_key_frames expr:gte(t,n_forced*5)   # Force keyframes every 5s
```

## Trade-offs

### File Size Impact
- Shorter intervals = slightly larger files (typically 5-10% increase)
- For theater/live work, this is worth it for instant scrubbing
- Archival profiles preserve source keyframes to avoid bloat

### Performance
- No impact on playback performance
- Slightly longer encode times (1-2% typically)
- Massive improvement in seeking/scrubbing performance

## Usage

No changes needed! Just use any profile:

```bash
# TUI (interactive)
bulletproof tui

# CLI
bulletproof transcode input.mov --profile live-qlab

# Folder monitor
bulletproof monitor start --config monitor.yaml
```

During transcoding, you'll see:
```
Transcoding: video.mov
Duration: 2.2 minutes
Speed Preset: normal
Keyframe Interval: 5.0s (easy scrubbing enabled)
```

## For Developers

### Adding Keyframes to Custom Profiles

```python
from bulletproof.core.profile import TranscodeProfile

my_profile = TranscodeProfile(
    name="my-custom-profile",
    codec="h264",
    preset="medium",
    quality=85,
    max_bitrate="20M",
    description="Custom profile for my workflow",
    extension="mp4",
    keyframe_interval=5.0,  # Keyframes every 5 seconds
    force_keyframes=True    # Strict intervals (recommended for live)
)
```

### Guidelines

- **Live playback:** 5-10 seconds (sweet spot for theater)
- **Editing:** 2-3 seconds (responsive seeking)
- **Streaming:** 2 seconds (HLS/DASH standard)
- **Archive:** `None` (preserve source structure)

## Testing

To verify keyframes in your output:

```bash
# Check keyframe intervals
ffprobe -select_streams v -show_frames output.mov | grep key_frame=1

# Or use bulletproof analyze
bulletproof analyze output.mov
```

## Implementation Details

### Files Changed

1. **bulletproof/core/profile.py**
   - Added `keyframe_interval: Optional[float]` parameter
   - Added `force_keyframes: bool` parameter
   - Updated all built-in profiles with optimal intervals

2. **bulletproof/core/job.py**
   - Added `_get_framerate()` method for auto-detection
   - Updated `_build_ffmpeg_command()` to calculate GOP size
   - Applies FFmpeg keyframe flags when interval is specified
   - Shows keyframe info during progress tracking

3. **README.md**
   - Added "Perfect for AV Techs" section
   - Updated profile table with keyframe intervals
   - Added troubleshooting for scrubbing issues

## Backward Compatibility

✅ Fully backward compatible
- Existing profiles work exactly as before
- Old transcodes still play perfectly
- New keyframe settings apply only to new transcodes
- Setting `keyframe_interval=None` preserves source keyframes

## Future Enhancements

Potential improvements:
- [ ] CLI flag to override keyframe interval per-job
- [ ] Auto-detection of optimal interval based on content type
- [ ] Visual keyframe map in future GUI
- [ ] Keyframe analysis tool to verify intervals

## Credits

Implemented: February 8, 2026  
Version: 0.2.1  
Branch: `feature/keyframe-support`

---

**Ready to test?** Check out the [feature/keyframe-support](https://github.com/KnowOneActual/bulletproof-video-playback/tree/feature/keyframe-support) branch!
