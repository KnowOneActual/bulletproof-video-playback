"""File picker widget for selecting input and output files."""

from pathlib import Path
from textual.widgets import Static, Input, Button, Label
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

VIDEO_EXTENSIONS = {".mov", ".mp4", ".avi", ".mkv", ".flv", ".wmv", ".webm"}


class FilePickerWidget(Static):
    """Widget for selecting input and output video files."""

    input_file: reactive[str | None] = reactive(None)
    output_file: reactive[str | None] = reactive(None)

    def compose(self):
        """Render the file picker."""
        yield Vertical(
            Label("[bold]Input File[/bold]"),
            Horizontal(
                Input(
                    placeholder="Enter input file path or click Browse...",
                    id="input-file-input",
                ),
                Button("Browse", id="input-browse-btn", variant="default"),
            ),
            Label("[dim id='input-file-label']", id="input-file-label"),
            Label(""),  # Spacing
            Label("[bold]Output File[/bold]"),
            Horizontal(
                Input(
                    placeholder="Output file path (auto-generated if not set)",
                    id="output-file-input",
                ),
                Button("Browse", id="output-browse-btn", variant="default"),
            ),
            Label("[dim id='output-file-label']", id="output-file-label"),
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes."""
        if event.input.id == "input-file-input":
            file_path = event.value.strip()
            if file_path and Path(file_path).exists():
                if Path(file_path).suffix.lower() in VIDEO_EXTENSIONS:
                    self.input_file = file_path
                    label = self.query_one("#input-file-label", Label)
                    label.update(f"[green]✓ Valid video file: {Path(file_path).name}[/green]")
                else:
                    label = self.query_one("#input-file-label", Label)
                    label.update(f"[red]✗ Not a video file: {Path(file_path).name}[/red]")
            elif file_path:
                label = self.query_one("#input-file-label", Label)
                label.update(f"[red]✗ File not found[/red]")

        elif event.input.id == "output-file-input":
            file_path = event.value.strip()
            if file_path:
                # Check if directory exists
                parent_dir = Path(file_path).parent
                if parent_dir.exists():
                    self.output_file = file_path
                    label = self.query_one("#output-file-label", Label)
                    label.update(f"[green]✓ Output: {Path(file_path).name}[/green]")
                else:
                    label = self.query_one("#output-file-label", Label)
                    label.update(f"[yellow]⚠ Directory doesn't exist yet[/yellow]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle browse button presses."""
        if event.button.id == "input-browse-btn":
            self.app.notify("📁 File browser coming soon!", timeout=2)
        elif event.button.id == "output-browse-btn":
            self.app.notify("📁 File browser coming soon!", timeout=2)
