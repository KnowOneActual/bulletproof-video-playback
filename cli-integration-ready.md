# ✅ CLI Integration Complete - Quick Start Guide

## What's Ready Now

The `bulletproof tui-textual` command is now fully integrated and ready to use!

## Installation & Setup

```bash
# Make sure you're on the feature branch
git checkout feature/textual-tui

# Install with all dependencies
pip install -e "."

# Or with dev tools (includes pytest, black, etc.)
pip install -e ".[dev]"

# Update dependencies if needed
pip install textual>=0.70.0
```

## Running the Textual TUI

```bash
# Simple command
bulletproof tui-textual

# With help
bulletproof tui-textual --help

# See all commands
bulletproof --help
```

## What You'll See

When you run `bulletproof tui-textual`, you'll get a rich terminal interface:

```
┌─ Bulletproof Video Playback ─────────────────────────────────────────┐
│                                                                         │
│  📹 Professional Video Transcoding                                     │
│                                                                         │
│  ┌─────────────────────────────┬──────────────────────────────────┐  │
│  │ 1. Select Profile           │ 2. Select Files                  │  │
│  │ ┌──────────────────────────┐│ ┌────────────────────────────┐  │  │
│  │ │ Profile  │ Codec │ Use   ││ Input File                 │  │  │
│  │ │──────────┼───────┼───────││ ┌──────────────────────────┐│  │  │
│  │ │ live-ql  │ PRORES│ QLab  ││ │ /path/to/video.mov       ││  │  │
│  │ │ live-h26│ H.264 │ Cross ││ └──────────────────────────┘│  │  │
│  │ │ stream-h│ H.265 │ Stream││ ✓ Valid video file        │  │  │
│  │ └──────────────────────────┘│                             │  │  │
│  │                             │ Output File                 │  │  │
│  │                             │ ┌──────────────────────────┐│  │  │
│  │                             │ │ /path/output__processe...││  │  │
│  │                             │ └──────────────────────────┘│  │  │
│  │                             │ ✓ Output: video_processed  │  │  │
│  │                             └────────────────────────────┘│  │  │
│  └─────────────────────────────┴──────────────────────────────┘  │
│                                                                         │
│  3. Options & Start                                                    │
│  Speed Preset: [Normal (Default) ▼]                                   │
│                                                                         │
│  [ Start Transcode ] [ Batch Process ] [ Settings ] [ Quit ]          │
│                                                                         │
│  Ctrl+Q=Quit  Ctrl+H=Help  D=Dark  1=Home  2=Settings  3=About       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Keyboard Controls

| Shortcut | Action |
|----------|--------|
| **Ctrl+Q** | Quit |
| **Ctrl+H** | Help & About |
| **Ctrl+N** | New Transcode |
| **Ctrl+B** | Batch Process |
| **D** | Toggle Dark Mode |
| **1** | Home Screen |
| **2** | Settings Screen |
| **3** | About Screen |
| **↑/↓** | Navigate |
| **Enter** | Select |

## Files Changed in `feature/textual-tui` Branch

### New Files Created
```
bulletproof/tui_textual/
├── __init__.py
├── app.py
├── screens/
│   ├── __init__.py
│   ├── home.py
│   ├── transcode.py
│   ├── settings.py
│   └── about.py
├── widgets/
│   ├── __init__.py
│   ├── profile_selector.py
│   └── file_picker_widget.py
└── styles/
    ├── __init__.py
    └── app.css

bulletproof/cli/commands/tui_textual.py
```

### Modified Files
```
bulletproof/cli/commands/__init__.py      (added tui_textual import)
bulletproof/cli/main.py                   (registered tui_textual command)
pyproject.toml                            (added Textual dependency + packages)
```

## Testing the Implementation

### Test 1: Command Recognition
```bash
bulletproof --help
# Should see: tui-textual  Rich Textual Terminal UI...
```

### Test 2: Launch App
```bash
bulletproof tui-textual
# Should see: Rich Textual UI interface with Header/Footer
```

### Test 3: Navigate Screens
```
1. Press '2' → Settings screen
2. Press 'ctrl+h' → About screen
3. Press '1' → Back to home screen
4. Press 'D' → Toggle dark mode
```

### Test 4: Select a Profile
```
1. Use arrow keys to navigate profile table
2. Press Enter to select
3. Notice it highlights the selected profile
```

### Test 5: File Selection
```
1. Click or type in "Input File" field
2. Enter a valid video file path (e.g., /path/to/video.mov)
3. Should show green checkmark: ✓ Valid video file
```

## Recent Fixes

### 🔧 Fixed in Latest Commit
- ✅ Removed non-existent `Tabs` import from `app.py` (Textual compatibility)
- ✅ Added explicit command name `tui-textual` in Click decorator
- ✅ Removed unused `ScrollableContainer` import from `home.py`

## Commits in Feature Branch

```
✅ Latest Fixes:
- 11db44e - fix(tui_textual): Remove non-existent Tabs import from app.py
- 2c14986 - fix(cli): Add explicit command name 'tui-textual' for proper Click registration
- b3aa4de - fix(tui_textual): Remove unused ScrollableContainer import from home screen

✅ Original Implementation:
- e709bd7 - feat(tui_textual): Initialize Textual TUI module
- 44d8b5c - feat(tui_textual): Create main BulletproofApp class
- cf8118f - feat(tui_textual): Create screens module
- f1e511f - feat(tui_textual): Create home screen with profile and file selection
- 9a3e076 - feat(tui_textual): Create widgets module
- f3b2c9b - feat(tui_textual): Add ProfileSelector widget with data table
- 945878f - feat(tui_textual): Add FilePickerWidget for input/output selection
- 4b3aec6 - feat(tui_textual): Add TranscodeScreen for progress monitoring
- eedb302 - feat(tui_textual): Add SettingsScreen
- 9ebbb3f - feat(tui_textual): Add AboutScreen with help information
- a9702a4 - feat(tui_textual): Add CSS styling for TUI app
- 23e6d9f - feat(tui_textual): Initialize styles module
- b0fe728 - feat(cli): Add tui-textual command for Textual TUI
- 6c49e39 - feat(cli): Export tui_textual command
- 9110aef - feat(cli): Register tui_textual command in main CLI
- 4bc71b0 - build: Update pyproject.toml with Textual dependency and tui_textual packages
```

## Troubleshooting

### "No such command 'tui-textual'"
Make sure you:
1. `git checkout feature/textual-tui`
2. `pip install -e "."` (reinstall with new packages)
3. Verify: `bulletproof --help` (should show tui-textual)

### "ModuleNotFoundError: No module named 'textual'"
```bash
pip install textual>=0.70.0
# Or reinstall entire package
pip install -e "."
```

### "ImportError: cannot import name 'Tabs'"
This is now fixed! The error was from an old import. If you still see it:
```bash
git pull origin feature/textual-tui
pip install -e "."
```

### "CSS file not found"
Make sure you're running from the repo root:
```bash
cd /path/to/bulletproof-video-playback
bulletproof tui-textual
```

## Next Steps (Phase 2)

### High Priority
1. **Add Async Support to TranscodeJob**
   - Create `execute_async()` method that yields progress updates
   - File: `bulletproof/core/job.py`
   - Allows TUI to show live progress without blocking

2. **Wire Up Start Button**
   - Connect HomeScreen "Start Transcode" to TranscodeJob
   - Display progress on TranscodeScreen
   - Show completion/error messages

3. **Settings Persistence**
   - Wire settings screen to config manager
   - Save/load default profile and output directory

### Phase 2 Tasks
- [ ] Async transcode execution with progress
- [ ] Home screen → TranscodeScreen routing
- [ ] Real-time progress bar updates
- [ ] Settings save/restore
- [ ] Batch processing UI
- [ ] Video analysis widget
- [ ] Web version (`textual serve` support)

## Key Implementation Details

### BulletproofApp
- Main Textual app class
- Manages screen navigation
- Handles keyboard bindings (Ctrl+Q, Ctrl+H, D, 1-3)
- Reactive state management

### Screens
- **HomeScreen**: Profile + file selection, speed preset
- **TranscodeScreen**: Progress monitoring (not yet wired)
- **SettingsScreen**: Configuration management
- **AboutScreen**: Help & keyboard shortcuts

### Widgets
- **ProfileSelector**: Interactive profile data table
- **FilePickerWidget**: File selection with validation

### Styling
- **app.css**: Responsive terminal UI styling
- Support for dark mode toggle
- Flexbox-like layout system

## Command Name Note

💡 **Sidenote about command naming:**

Click CLI automatically converts underscores to hyphens in command names. So:
- Python function: `tui_textual()`
- Click command name: `tui-textual`
- CLI usage: `bulletproof tui-textual`

We explicitly set `name="tui-textual"` in the decorator to ensure this works correctly.

## Resources

- **Textual Docs**: [https://textual.textualize.io/](https://textual.textualize.io/)
- **Textual Examples**: [https://github.com/Textualize/textual/tree/main/examples](https://github.com/Textualize/textual/tree/main/examples)
- **Your Repo**: [https://github.com/KnowOneActual/bulletproof-video-playback](https://github.com/KnowOneActual/bulletproof-video-playback)
- **Feature Branch**: `feature/textual-tui`

---

## Summary

✅ **CLI Integration**: Complete  
✅ **TUI Structure**: Complete  
✅ **UI Components**: Complete  
✅ **Profile Selection**: Working  
✅ **File Validation**: Working  
✅ **Navigation**: Working  
✅ **Dark Mode**: Working  
✅ **Import Errors**: Fixed  
✅ **Command Name**: Fixed  

⏳ **Async Transcode**: Next step  
⏳ **Progress Monitoring**: Next step  
⏳ **Batch Processing**: Next step  

**Status**: Ready for testing and Phase 2 development! 🚀
