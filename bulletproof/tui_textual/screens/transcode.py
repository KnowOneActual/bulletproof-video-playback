"""Transcode progress screen."""

from pathlib import Path
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Label, ProgressBar, Static, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.worker import Worker
import asyncio

from bulletproof.core import TranscodeJob, ProgressData


class TranscodeScreen(Screen):
    """Screen showing transcode progress in real-time."""

    TITLE = "Bulletproof - Transcoding..."
    BINDINGS = [
        Binding("ctrl+c", "cancel_transcode", "Cancel", show=True),
    ]

    progress: reactive[float] = reactive(0.0)
    status_text: reactive[str] = reactive("Initializing...")
    fps_text: reactive[str] = reactive("FPS: 0.0")
    bitrate_text: reactive[str] = reactive("Bitrate: 0.0 kbps")
    speed_text: reactive[str] = reactive("Speed: 0.0x")
    elapsed_text: reactive[str] = reactive("Elapsed: 00:00:00")
    eta_text: reactive[str] = reactive("ETA: --:--:--")

    def __init__(self, job: TranscodeJob):
        """Initialize with a TranscodeJob."""
        super().__init__()
        self.job = job
        self._cancel_requested = False
        self._transcode_worker = None

    def compose(self):
        """Compose the transcode screen."""
        yield Vertical(
            Header(),
            Label(f"🎬 Transcoding: {self.job.input_file.name}"),
            Label(f"Profile: {self.job.profile.name} | Speed: {self.job.speed_preset}"),
            Label(""),
            # Progress bar
            Label("Progress:"),
            ProgressBar(id="progress-bar", total=100.0),
            Label(id="status-label"),
            Label(""),
            # Stats
            Horizontal(
                Label(id="fps-label"),
                Label(id="bitrate-label"),
                Label(id="speed-label"),
            ),
            Horizontal(
                Label(id="elapsed-label"),
                Label(id="eta-label"),
            ),
            Label(""),
            Button("Cancel", id="cancel-btn", variant="error"),
        )

    def on_mount(self) -> None:
        """Start transcode when screen mounts."""
        self.progress = 0.0
        self.status_text = "Starting transcode..."
        # Launch transcode in background worker
        self._transcode_worker = self.run_worker(self.run_transcode_task())

    def on_button_pressed(self, event) -> None:
        """Handle cancel button."""
        if event.button.id == "cancel-btn":
            self.action_cancel_transcode()

    async def run_transcode_task(self) -> None:
        """Run the transcode job with progress updates."""
        try:
            async for progress in self.job.execute_async():
                if self._cancel_requested:
                    break

                # Update reactive properties (triggers watch methods)
                self.progress = progress.percent
                self.status_text = f"[bold]{progress.percent:.1f}%[/bold] complete"
                self.fps_text = f"FPS: {progress.fps:.1f}"
                self.bitrate_text = f"Bitrate: {progress.bitrate}"
                self.speed_text = f"Speed: {progress.speed}"
                self.elapsed_text = f"Elapsed: {progress.elapsed_string}"
                self.eta_text = f"ETA: {progress.eta_string}"
                # Yield to let UI update
                await asyncio.sleep(0.1)

            # Transcode complete
            if not self._cancel_requested:
                self.status_text = "[green]✓ Transcode complete![/green]"
                self.progress = 100.0
        except Exception as e:
            self.status_text = f"[red]✗ Error: {str(e)[:50]}[/red]"
            self.job.status = "error"
            self.job.error_message = str(e)

    def watch_progress(self, new_progress: float) -> None:
        """Update progress bar."""
        try:
            bar = self.query_one("#progress-bar", ProgressBar)
            bar.progress = new_progress
        except Exception:
            pass

    def watch_status_text(self, new_status: str) -> None:
        """Update status label."""
        try:
            label = self.query_one("#status-label", Label)
            label.update(new_status)
        except Exception:
            pass

    def watch_fps_text(self, new_text: str) -> None:
        """Update FPS label."""
        try:
            label = self.query_one("#fps-label", Label)
            label.update(new_text)
        except Exception:
            pass

    def watch_bitrate_text(self, new_text: str) -> None:
        """Update bitrate label."""
        try:
            label = self.query_one("#bitrate-label", Label)
            label.update(new_text)
        except Exception:
            pass

    def watch_speed_text(self, new_text: str) -> None:
        """Update speed label."""
        try:
            label = self.query_one("#speed-label", Label)
            label.update(new_text)
        except Exception:
            pass

    def watch_elapsed_text(self, new_text: str) -> None:
        """Update elapsed time label."""
        try:
            label = self.query_one("#elapsed-label", Label)
            label.update(new_text)
        except Exception:
            pass

    def watch_eta_text(self, new_text: str) -> None:
        """Update ETA label."""
        try:
            label = self.query_one("#eta-label", Label)
            label.update(new_text)
        except Exception:
            pass

    def action_cancel_transcode(self) -> None:
        """Cancel the transcode."""
        self._cancel_requested = True
        self.status_text = "[yellow]⚠ Cancelling...[/yellow]"
        # Return to home screen
        self.app.pop_screen()
