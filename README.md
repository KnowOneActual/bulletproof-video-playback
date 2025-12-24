
# **!!This is still in the early stages of development, and many great ideas in the pipeline. Currently, it might not work as intended!!**

# bulletproof-video-playback

[![Tests](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml/badge.svg)](https://github.com/KnowOneActual/bulletproof-video-playback/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Professional video transcoding for live playback, streaming, and archival. Uses ffmpeg under the hood with seven prebuilt profiles optimized for different use cases.

## Features

- **7 Transcoding Profiles**: Prebuilt profiles for live playback (ProRes/H.264), streaming (H.265), and archival
- **Three Interfaces**: CLI, TUI (interactive), and Python API
- **Batch Processing**: Transcode entire directories of videos
- **Video Analysis**: Inspect video codec, resolution, fps, audio specs
- **Professional Codecs**: ProRes HQ, ProRes LT, H.264, H.265
- **CI/CD Ready**: Includes GitHub Actions workflows for testing and releases

## Installation

### Requirements
- Python 3.9+
- ffmpeg (`brew install ffmpeg` on macOS, `apt install ffmpeg` on Linux)
- ffprobe (usually included with ffmpeg)

### From PyPI

```bash
pip install bulletproof-video-playback
```

### From GitHub (Development)

```bash
git clone https://github.com/KnowOneActual/bulletproof-video-playback
cd bulletproof-video-playback
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# List available profiles
bulletproof transcode --list-profiles

# Transcode single file with profile
bulletproof transcode input.mov --profile live-qlab --output output.mov

# Analyze video specs
bulletproof analyze input.mov

# Batch process directory
bulletproof batch ./videos --profile standard-playback --output-dir ./output
```

### TUI (Interactive Mode)

```bash
bulletproof tui
# Navigate with prompts to select file, profile, and output location
```

### Python API

```python
from bulletproof.core import TranscodeJob, get_profile
from pathlib import Path

# Get a profile
profile = get_profile("live-qlab")

# Create and execute a job
job = TranscodeJob(
    input_file=Path("input.mov"),
    output_file=Path("output.mov"),
    profile=profile
)

if job.execute():
    print(f"Success! Output: {job.output_file}")
else:
    print(f"Failed: {job.error_message}")
```

## Profiles

| Name | Codec | Use Case | File Size |
|------|-------|----------|----------|
| live-qlab | ProRes HQ | QLab on Mac (best quality) | Very Large |
| live-prores-lt | ProRes LT | Live playback (smaller) | Large |
| live-h264 | H.264 | Cross-platform live playback | Medium |
| standard-playback | H.264 | Miccia, VLC, preview | Small |
| stream-hd | H.265 | 1080p streaming | Tiny |
| stream-4k | H.265 | 4K streaming | Tiny |
| archival | ProRes HQ | Long-term storage | Very Large |

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=bulletproof tests/

# Format code
black bulletproof tests
```

## Development

### Adding a New Profile

Edit `bulletproof/core/profile.py` and add to `BUILT_IN_PROFILES`:

```python
BUILT_IN_PROFILES["my-profile"] = TranscodeProfile(
    name="my-profile",
    codec="h265",
    preset="medium",
    quality=85,
    max_bitrate="10M",
    # ... other settings
)
```

### Adding a New Command

Create `bulletproof/cli/commands/my_command.py`:

```python
import click

@click.command()
@click.argument("input_file")
def my_command(input_file):
    """Description of my command."""
    # Implementation
    pass
```

Then register in `bulletproof/cli/main.py`:

```python
cli.add_command(my_command)
```

## Releases

To release a new version:

```bash
# Tag a release
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will:
# 1. Run tests
# 2. Build package
# 3. Create GitHub release
# 4. Upload to PyPI (requires PYPI_API_TOKEN secret)
```

## Architecture

```
bulletproof/
├── core/              # Transcode logic
│   ├── profile.py     # Profile definitions
│   └── job.py         # Transcode execution
├── cli/               # Command-line interface
│   ├── main.py        # CLI entry point
│   └── commands/      # Subcommands
├── tui/               # Terminal UI
└── utils/             # Utilities (validation, etc)

tests/                # Test suite
.github/workflows/    # CI/CD
```

## License

MIT License - see LICENSE file

## Author

Beau Bremer ([@KnowOneActual](https://github.com/KnowOneActual))

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass and code is formatted
5. Submit a pull request
