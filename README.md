# Bulletproof Video Playback 🎬

Professional video transcoding and optimization for theater playback (QLab, PlaybackPro, Miccia Player) and streaming platforms. CLI + TUI interface with ffmpeg integration.

## Features

✅ **Multi-Platform Support**
- Theater/Live Event Playback (QLab, PlaybackPro)
- Standard Playback (Miccia Player, VLC, etc.)
- Streaming Optimization (H.264, H.265)

✅ **Smart Codec Selection**
- ProRes (HQ, LT, Proxy) for theater on macOS
- H.264/H.265 for cross-platform compatibility
- VP9 for web streaming
- Intelligent quality scaling

✅ **Dual Interface**
- **CLI**: Fast, scriptable, automation-friendly
- **TUI**: Interactive, progress tracking, real-time stats

✅ **Production Ready**
- Unit + integration tests
- GitHub Actions CI/CD
- Semantic versioning & releases
- Comprehensive error handling
- Performance profiling

✅ **Quality of Life**
- Preset profiles (theater, cinema, streaming, archival)
- Batch processing with progress tracking
- Video analysis (codec detection, validation)
- Configuration files (.bulletproof.yaml)
- Color-coded terminal output

## Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/KnowOneActual/bulletproof-video-playback.git
cd bulletproof-video-playback

# Install (requires Python 3.9+, ffmpeg)
pip install -e .

# Verify
bulletproof --version
```

### CLI Usage

```bash
# Quick transcode with profile
bulletproof transcode input.mov --profile theater-qlab --output output.mov

# Analyze video
bulletproof analyze video.mov

# Batch process
bulletproof batch transcode --config jobs.yaml

# Get help
bulletproof --help
bulletproof transcode --help
```

### TUI Usage

```bash
# Interactive interface
bulletproof tui
```

Navigate with arrow keys, select presets, monitor real-time encoding stats.

## Profiles

| Profile | Codec | Container | Use Case |
|---------|-------|-----------|----------|
| `theater-qlab` | ProRes HQ | MOV | QLab on macOS (best quality) |
| `theater-prores-lt` | ProRes LT | MOV | QLab, reduced file size |
| `theater-h264` | H.264 | MP4 | Cross-platform theater |
| `standard-playback` | H.264 | MP4 | Miccia, VLC, general use |
| `stream-hd` | H.265 | MP4 | Streaming (1080p) |
| `stream-4k` | H.265 | MP4 | Streaming (2160p) |
| `archival` | ProRes HQ | MOV | Long-term storage |

## Configuration

Create `.bulletproof.yaml` in your project root:

```yaml
profiles:
  custom-theater:
    codec: prores
    preset: hq
    quality: 100
    max_bitrate: null
    frame_rate: 23.976

batch:
  max_concurrent: 2
  verify_output: true
  cleanup_on_error: false

output:
  naming: "{basename}_{profile}_{timestamp}{ext}"
  directory: "./transcoded"
```

## Architecture

```
bulletproof/
├── core/           # Codec & ffmpeg logic
├── cli/            # Click CLI interface
├── tui/            # Rich TUI interface
├── profiles/       # Preset configurations
├── utils/          # Validation, analysis
├── tests/          # Unit + integration tests
└── config/         # Config file handling
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Code quality
black bulletproof/
flake8 bulletproof/
mypy bulletproof/

# Build distribution
python -m build
```

## Requirements

- **Python**: 3.9+
- **ffmpeg**: 4.4+
- **ffprobe**: Bundled with ffmpeg

Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

## Performance

Real-time encoding stats & progress:
- Encoding speed (fps, %)
- ETA calculation
- File size estimation
- CPU/Memory usage (Linux/macOS)

## CI/CD

GitHub Actions:
- ✅ Pytest on Python 3.9-3.12
- ✅ Linting (Black, Flake8)
- ✅ Type checking (MyPy)
- ✅ Auto-release on tag
- ✅ Upload to PyPI

## Philosophy

> What actually matters is understanding why each codec exists and when to use it. ProRes is not objectively better, but it is better for QLab on Mac. H.265 is not a downgrade, it is just optimized for a different platform.
>
> Once you stop asking "what is the best codec" and start asking "what does this system need," everything gets less frustrating.

This tool automates that question-asking process.

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Roadmap

- [ ] GPU acceleration detection (NVIDIA/AMD)
- [ ] Real-time frame preview
- [ ] Audio-only extraction & optimization
- [ ] Subtitle handling
- [ ] WebUI dashboard
- [ ] Integration with CasparCG workflows

## Support

Issues, PRs, and discussions welcome on GitHub!

