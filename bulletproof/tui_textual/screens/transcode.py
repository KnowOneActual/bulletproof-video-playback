"""Transcode progress screen."""

from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Header, Label, ProgressBar, Static
from textual.reactive import reactive


class TranscodeScreen(Screen):
    """Screen showing transcode progress in real-time."""

    TITLE = "Bulletproof - Transcoding..."

    progress: reactive[float] = reactive(0.0)
    status_text: reactive[str] = reactive("Initializing...")

    def compose(self):
        """Compose the transcode screen."""
        yield Vertical(
            Header(),
            Label("[bold]Transcoding in Progress[/bold]"),
            Label(id="status-label"),
            Label(""),
            Label("Progress:"),
            ProgressBar(id="progress-bar", total=100.0),
            Label(""),
            Label("[dim]Press Ctrl+C to cancel[/dim]"),
        )

    def on_mount(self) -> None:
        """Set initial values when mounted."""
        self.progress = 0.0

    def watch_progress(self, new_progress: float) -> None:
        """Update progress bar."""
        bar = self.query_one("#progress-bar", ProgressBar)
        bar.progress = new_progress

    def watch_status_text(self, new_status: str) -> None:
        """Update status label."""
        label = self.query_one("#status-label", Label)
        label.update(new_status)
