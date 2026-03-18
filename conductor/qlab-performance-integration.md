# QLab Performance Integration Plan

## Objective
Integrate performance optimization advice from QLab into Bulletproof Video Playback. This includes explicitly matching audio sample rates to hardware, matching exact output resolutions, and adding an audio-only conversion profile for MP3/AAC replacement.

## Key Files & Context
- `bulletproof/core/profile.py`
- `bulletproof/core/job.py`
- `bulletproof/cli/commands/transcode.py`
- `bulletproof/cli/commands/batch.py`

## Implementation Steps

### 1. Add `audio_sample_rate` to Profiles
- In `bulletproof/core/profile.py`, add `audio_sample_rate: str | None = None` to the `TranscodeProfile` dataclass.
- Update `BUILT_IN_PROFILES["live-qlab"]` to default to `audio_sample_rate="48000"`.

### 2. Support Audio-Only Profiles
- In `bulletproof/core/profile.py`, support `codec="none"`.
- Add a new profile: `audio-qlab`
  - `codec="none"`
  - `audio_codec="pcm_s24le"`
  - `audio_sample_rate="48000"`
  - `extension="wav"`
  - `description="Uncompressed 24-bit 48kHz WAV audio for QLab"`

### 3. Update FFmpeg Command Builder
- In `bulletproof/core/job.py`, update `_build_ffmpeg_command()`:
  - If `self.profile.codec == "none"`, omit all video flags and append `-vn`.
  - If `self.profile.audio_sample_rate` is set, append `-ar {self.profile.audio_sample_rate}`.

### 4. Expose CLI Overrides (`transcode` and `batch`)
- In `bulletproof/cli/commands/transcode.py` and `bulletproof/cli/commands/batch.py`:
  - Add `@click.option("--resolution", help="Override output resolution (e.g., 1920:1080)")`.
  - Add `@click.option("--audio-sample-rate", help="Override audio sample rate (e.g., 48000)")`.
  - Apply these overrides to the profile instance before passing to `TranscodeJob`.

## Verification
- Test video transcode with `--resolution` and `--audio-sample-rate` overrides.
- Test video transcode with `--profile audio-qlab` to verify correct `.wav` output.
- Run `pytest` to ensure no existing tests are broken.
