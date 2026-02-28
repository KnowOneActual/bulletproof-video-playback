# Frame Rate Handling Design

## Overview

This document explains how bulletproof-video-playback handles frame rates and why the current design is optimal for video stability and playback performance.

**Decision Date:** February 10, 2026  
**Status:** Finalized - No frame rate conversion needed

---

## Current Implementation

### Frame Rate Detection

Frame rate detection is **already implemented** in `bulletproof/core/job.py`:

```python
def _get_framerate(self) -> Optional[float]:
    """Get video framerate using ffprobe."""
```

This method:
- Uses ffprobe to automatically detect source frame rates
- Parses fractional frame rates (e.g., "30000/1001" for 29.97 fps)
- Returns accurate frame rate for GOP (Group of Pictures) calculations
- Is used specifically for keyframe interval calculations

### Frame Rate Preservation

**All profiles default to `frame_rate: None`** which preserves the source frame rate during transcoding.

#### Live Playback Profiles
These profiles preserve source frame rates:
- `live-qlab` - ProRes Proxy for QLab
- `live-prores-lt` - ProRes LT for live events
- `live-h264` - H.264 cross-platform
- `live-linux-hevc-mkv` - H.265 MKV for Linux live events
- `standard-playback` - H.264 general playback

#### Archival Profiles
These profiles preserve source frame rates for accuracy:
- `archival` - ProRes HQ
- `archival-linux-mkv` - H.265 10-bit MKV

#### Streaming Profiles (Exception)
These profiles standardize frame rates for streaming consistency:
- `stream-hd` - Fixed at 29.97 fps (1080p)
- `stream-4k` - Fixed at 29.97 fps (4K)

---

## Why We Don't Convert Frame Rates

### 1. Stability Through Consistency

**Preserving source frame rates provides better stability** because:
- No frame blending artifacts
- No motion judder from rate conversion
- Original timing preserved exactly
- Fewer transcoding errors
- Faster encode times (no interpolation needed)

### 2. Modern Playback Systems Handle Variable Frame Rates

Professional playback systems handle frame rate changes seamlessly:
- **QLab** (macOS) - Automatically adapts to source frame rate
- **mpv** (Linux) - Native support for variable frame rates
- **Linux Show Player** - Handles mixed frame rate playlists
- **VLC** - Universal frame rate support

### 3. Live Event Workflows

In live event environments:
- Different source videos legitimately have different frame rates (24p, 30p, 60p)
- Converting all content to one frame rate introduces unnecessary processing
- Source material timing must be preserved (musical cues, sync to audio)
- Frame rate conversion can cause A/V sync drift

### 4. Quality Preservation

Frame rate conversion introduces artifacts:
- **Frame blending** - Adjacent frames mixed, causing motion blur
- **Judder** - Uneven motion from frame duplication/dropping
- **Temporal aliasing** - Strobing effects on fast motion
- **Increased file size** - More frames to encode

---

## Frame Rate and Keyframe Stability

### The Real Stability Factor: Keyframe Intervals

Your **keyframe interval system** is what provides scrubbing stability, not frame rate standardization.

#### How It Works

Keyframe intervals are **time-based**, not frame-based:
- 5-second intervals for live playback
- 2-second intervals for streaming
- Works with any source frame rate

#### Automatic GOP Calculation

The system calculates GOP size dynamically:

```python
# From bulletproof/core/job.py
fps = self.profile.frame_rate if self.profile.frame_rate else self._get_framerate()
gop_size = int(fps * self.profile.keyframe_interval)
```

**Result:** Consistent scrubbing behavior across all frame rates.

#### Examples

| Source FPS | Keyframe Interval | GOP Size | Result |
|------------|-------------------|----------|--------|
| 24 fps | 5 seconds | 120 frames | Jump every 5s |
| 29.97 fps | 5 seconds | 150 frames | Jump every 5s |
| 60 fps | 5 seconds | 300 frames | Jump every 5s |

**Users experience the same 5-second scrubbing** regardless of source frame rate.

---

## Use Case Analysis

### Should All Clips Be The Same Frame Rate?

**It depends on your workflow:**

#### ✅ Live Events (Primary Use Case)
**NO - Preserve source frame rates**

Reasons:
- Mixed source content is normal (24p film, 30p video, 60p slow-mo)
- Playback systems handle transitions automatically
- Original timing preservation is critical
- Conversion introduces latency in prep workflows

#### ✅ General Playback
**NO - Preserve source frame rates**

Reasons:
- Maximum quality preservation
- Faster transcoding
- No artifacts
- Universal player compatibility

#### ⚠️ Streaming/Broadcast
**MAYBE - Consider standardization**

Your streaming profiles already handle this with fixed frame rates (29.97 fps).

Benefits of standardization:
- Consistent HLS/DASH segment durations
- Predictable bandwidth usage
- Easier CDN caching
- Uniform player buffer behavior

#### ✅ Archival
**NO - Preserve source frame rates**

Reasons:
- Historical accuracy
- Future-proofing
- Maximum fidelity to original content

---

## Technical Implementation Details

### Profile Configuration

From `bulletproof/core/profile.py`:

```python
@dataclass
class TranscodeProfile:
    name: str
    codec: str
    preset: str
    quality: int
    frame_rate: Optional[float]  # None = preserve source
    keyframe_interval: Optional[float]  # Time-based (seconds)
    force_keyframes: bool  # Strict interval enforcement
    # ... other fields
```

### FFmpeg Command Generation

From `bulletproof/core/job.py`:

```python
# Keyframe interval settings
if self.profile.keyframe_interval is not None:
    fps = self.profile.frame_rate if self.profile.frame_rate else self._get_framerate()
    
    if fps:
        gop_size = int(fps * self.profile.keyframe_interval)
        cmd.extend(["-g", str(gop_size)])
        cmd.extend(["-keyint_min", str(gop_size)])
        
        if self.profile.force_keyframes:
            cmd.extend(["-sc_threshold", "0"])
            cmd.extend(["-force_key_frames", f"expr:gte(t,n_forced*{interval})"])

# Frame rate (only if specified in profile)
if self.profile.frame_rate:
    cmd.extend(["-r", str(self.profile.frame_rate)])
```

**Key points:**
- Frame rate detection is automatic
- GOP calculation adapts to source or target frame rate
- Frame rate conversion only happens if explicitly configured

---

## Future Considerations

### Optional CLI Override (Not Currently Needed)

If users request frame rate control, consider adding:

```bash
# Optional override for special cases
bvp transcode input.mov --profile live-qlab --force-framerate 30
```

**Implementation guidance:**
- Keep it optional, not default
- Add warning about potential quality loss
- Document use cases clearly

### Frame Rate Analysis Tool

Consider adding to `bvp analyze`:

```bash
bvp analyze video.mov

Output:
  Frame Rate: 29.97 fps (30000/1001)
  Frame Count: 7200
  Duration: 240.24 seconds
  GOP Size: 150 frames (5.0s intervals)
```

---

## Best Practices

### For AV Technicians

1. **Don't worry about mixed frame rates** - Your profiles handle this automatically
2. **Trust the keyframe intervals** - They provide consistent scrubbing regardless of FPS
3. **Use appropriate profiles**:
   - Live events → `live-qlab`, `live-linux-hevc-mkv` (preserves source FPS)
   - Streaming → `stream-hd`, `stream-4k` (standardizes to 29.97 fps)
   - Archive → `archival`, `archival-linux-mkv` (preserves source FPS)

### For Developers

1. **Never force frame rate conversion without user request**
2. **Always detect source frame rate for GOP calculations**
3. **Document frame rate handling in profile descriptions**
4. **Test keyframe intervals with various source frame rates** (24p, 29.97p, 30p, 60p)

---

## Testing Frame Rate Handling

### Verify Source Frame Rate Detection

```bash
# Check what ffprobe detects
ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 input.mov

# Test with bvp analyze
bvp analyze input.mov
```

### Verify Frame Rate Preservation

```bash
# Transcode with source preservation
bvp transcode input.mov --profile live-qlab -o output.mov

# Verify output matches input
ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 output.mov
```

### Verify Keyframe Intervals with Mixed Frame Rates

Test with videos at different frame rates:
- 24 fps source → 120-frame GOP with 5s interval
- 30 fps source → 150-frame GOP with 5s interval  
- 60 fps source → 300-frame GOP with 5s interval

All should provide consistent 5-second scrubbing behavior.

---

## Conclusion

### Design Decision: ✅ NO FRAME RATE CONVERSION NEEDED

**Rationale:**
1. Keyframe intervals (not frame rate standardization) provide scrubbing stability
2. Modern playback systems handle variable frame rates seamlessly
3. Frame rate preservation maximizes quality and minimizes artifacts
4. Time-based GOP calculation works with any source frame rate
5. Streaming profiles already handle the one case where standardization helps

**Current implementation is production-ready and optimal for the target use cases.**

---

## Related Documentation

- [KEYFRAME_FEATURE.md](./KEYFRAME_FEATURE.md) - Keyframe interval system details
- [TESTING_KEYFRAMES.md](../testing/TESTING_KEYFRAMES.md) - How to test keyframe behavior
- [QUICK_REFERENCE.md](../../QUICK_REFERENCE.md) - Common command examples

---

**Document Version:** 1.0  
**Last Updated:** February 10, 2026  
**Author:** Beau Bremer ([@KnowOneActual](https://github.com/KnowOneActual))
