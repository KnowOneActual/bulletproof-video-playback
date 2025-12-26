"""About and help screen."""

from textual.screen import Screen
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Header, Label, Button


class AboutScreen(Screen):
    """About and help information screen."""

    TITLE = "Bulletproof - About & Help"

    def compose(self):
        """Compose the about screen."""
        yield Vertical(
            Header(),
            ScrollableContainer(
                Label("[bold]Bulletproof Video Playback[/bold]"),
                Label("Professional video transcoding for live playback"),
                Label(""),
                Label("[bold]Version:[/bold] 0.1.0"),
                Label("[bold]Author:[/bold] Beau Bremer (@KnowOneActual)"),
                Label(""),
                Label("[bold]Keyboard Shortcuts:[/bold]"),
                Label("  Ctrl+Q - Quit"),
                Label("  Ctrl+H - Help"),
                Label("  Ctrl+N - New Transcode"),
                Label("  Ctrl+B - Batch Process"),
                Label("  D      - Toggle Dark Mode"),
                Label("  1      - Home Screen"),
                Label("  2      - Settings"),
                Label("  3      - About"),
                Label(""),
                Label("[bold]Getting Started:[/bold]"),
                Label("  1. Select a transcode profile"),
                Label("  2. Choose your input video file"),
                Label("  3. Set the output path (auto-generated if empty)"),
                Label("  4. Choose a speed preset (fast/normal/slow)"),
                Label("  5. Click 'Start Transcode'"),
                Label(""),
                Label("[bold]Available Profiles:[/bold]"),
                Label("  • live-qlab: ProRes Proxy for QLab (recommended)"),
                Label("  • live-prores-lt: ProRes LT for smaller files"),
                Label("  • live-h264: H.264 for cross-platform playback"),
                Label("  • stream-hd: H.265 for 1080p streaming"),
                Label("  • stream-4k: H.265 for 4K streaming"),
                Label("  • archival: ProRes HQ for long-term storage"),
                Label(""),
                Label("[bold]More Information:[/bold]"),
                Label("  GitHub: https://github.com/KnowOneActual/bulletproof-video-playback"),
            ),
            Button("Back", id="back-btn", variant="primary"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
