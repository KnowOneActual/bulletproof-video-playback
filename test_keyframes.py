#!/usr/bin/env python3
"""Test script to verify keyframe intervals are working correctly.

Usage:
    python test_keyframes.py <input_video.mov>

This script will:
1. Transcode the video using the live-qlab profile (5s keyframes)
2. Analyze the output to verify keyframe intervals
3. Report success or failure
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def analyze_keyframes(video_path: Path) -> dict:
    """Analyze keyframes in a video file."""
    print(f"\n📊 Analyzing keyframes in: {video_path.name}")
    
    try:
        # Get video info
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate,duration",
            "-of", "json",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        info = json.loads(result.stdout)
        
        # Parse framerate
        fps_str = info['streams'][0]['r_frame_rate']
        if '/' in fps_str:
            num, denom = fps_str.split('/')
            fps = float(num) / float(denom)
        else:
            fps = float(fps_str)
        
        duration = float(info['streams'][0].get('duration', 0))
        
        print(f"  Framerate: {fps:.2f} fps")
        print(f"  Duration: {duration:.2f} seconds")
        
        # Get keyframe information
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "frame=pict_type,pts_time",
            "-of", "json",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        frames = json.loads(result.stdout)
        
        # Find I-frames (keyframes)
        keyframe_times = []
        for frame in frames.get('frames', []):
            if frame.get('pict_type') == 'I' and 'pts_time' in frame:
                keyframe_times.append(float(frame['pts_time']))
        
        if len(keyframe_times) < 2:
            return {
                'fps': fps,
                'duration': duration,
                'keyframe_count': len(keyframe_times),
                'intervals': [],
                'avg_interval': 0,
                'error': 'Not enough keyframes to analyze'
            }
        
        # Calculate intervals between keyframes
        intervals = []
        for i in range(1, len(keyframe_times)):
            interval = keyframe_times[i] - keyframe_times[i-1]
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        print(f"  Keyframes found: {len(keyframe_times)}")
        print(f"  Average interval: {avg_interval:.2f} seconds")
        print(f"  First 10 intervals: {[f'{i:.2f}' for i in intervals[:10]]}")
        
        return {
            'fps': fps,
            'duration': duration,
            'keyframe_count': len(keyframe_times),
            'keyframe_times': keyframe_times,
            'intervals': intervals,
            'avg_interval': avg_interval
        }
    
    except Exception as e:
        print(f"  ❌ Error analyzing keyframes: {e}")
        return {'error': str(e)}


def test_transcode_with_keyframes(input_file: Path):
    """Test transcoding with keyframe intervals."""
    print("\n" + "="*60)
    print("🎬 KEYFRAME INTERVAL TEST")
    print("="*60)
    
    # Verify input file exists
    if not input_file.exists():
        print(f"\n❌ Input file not found: {input_file}")
        return False
    
    print(f"\n📹 Input video: {input_file.name}")
    
    # Analyze source video
    print("\n📊 SOURCE VIDEO ANALYSIS")
    print("-" * 60)
    source_analysis = analyze_keyframes(input_file)
    
    if 'error' in source_analysis:
        print(f"  ⚠️  Source analysis: {source_analysis['error']}")
    else:
        print(f"  ✅ Source keyframe interval: {source_analysis['avg_interval']:.2f}s")
    
    # Create output filename
    output_file = input_file.parent / f"{input_file.stem}__keyframe_test.mov"
    
    print(f"\n🔄 TRANSCODING WITH KEYFRAMES")
    print("-" * 60)
    print(f"  Profile: live-qlab (5-second keyframe interval)")
    print(f"  Output: {output_file.name}")
    print("")
    
    # Import bulletproof after path is set
    try:
        from bulletproof.core import TranscodeJob, get_profile
    except ImportError:
        print("❌ Cannot import bulletproof. Make sure you've installed it:")
        print("   pip install -e .")
        return False
    
    # Create transcode job
    profile = get_profile("live-qlab")
    
    print(f"  Expected keyframe interval: {profile.keyframe_interval}s")
    print(f"  Force keyframes: {profile.force_keyframes}")
    print("")
    
    job = TranscodeJob(
        input_file=input_file,
        output_file=output_file,
        profile=profile,
        speed_preset="fast"  # Use fast preset for testing
    )
    
    # Execute transcode
    success = job.execute(show_progress=True)
    
    if not success:
        print(f"\n❌ Transcode failed: {job.error_message}")
        return False
    
    print(f"\n✅ Transcode complete!")
    
    # Analyze output video
    print("\n📊 OUTPUT VIDEO ANALYSIS")
    print("-" * 60)
    output_analysis = analyze_keyframes(output_file)
    
    if 'error' in output_analysis:
        print(f"\n❌ Output analysis failed: {output_analysis['error']}")
        return False
    
    # Verify keyframe intervals
    print("\n🔍 VERIFICATION")
    print("-" * 60)
    
    expected_interval = 5.0
    actual_interval = output_analysis['avg_interval']
    tolerance = 0.5  # Allow 0.5 second deviation
    
    print(f"  Expected interval: {expected_interval}s")
    print(f"  Actual avg interval: {actual_interval:.2f}s")
    print(f"  Tolerance: ±{tolerance}s")
    
    if abs(actual_interval - expected_interval) <= tolerance:
        print(f"\n✅ SUCCESS! Keyframe intervals are correct!")
        print(f"   Keyframes every ~{actual_interval:.1f}s (target: {expected_interval}s)")
        success = True
    else:
        print(f"\n⚠️  WARNING: Keyframe interval outside tolerance")
        print(f"   Expected: {expected_interval}s ± {tolerance}s")
        print(f"   Got: {actual_interval:.2f}s")
        success = False
    
    # Additional checks
    print("\n📋 SUMMARY")
    print("-" * 60)
    print(f"  Input file: {input_file.name}")
    print(f"  Output file: {output_file.name}")
    print(f"  Output size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  Keyframes in output: {output_analysis['keyframe_count']}")
    print(f"  Average interval: {actual_interval:.2f}s")
    
    # Show interval distribution
    if output_analysis['intervals']:
        intervals = output_analysis['intervals']
        min_interval = min(intervals)
        max_interval = max(intervals)
        print(f"  Min interval: {min_interval:.2f}s")
        print(f"  Max interval: {max_interval:.2f}s")
    
    print("\n" + "="*60)
    
    return success


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_keyframes.py <input_video>")
        print("\nExample:")
        print("  python test_keyframes.py sample_video.mov")
        print("\nThis will:")
        print("  1. Transcode using live-qlab profile (5s keyframes)")
        print("  2. Analyze keyframe intervals")
        print("  3. Verify they match expected 5-second intervals")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    success = test_transcode_with_keyframes(input_file)
    
    sys.exit(0 if success else 1)
