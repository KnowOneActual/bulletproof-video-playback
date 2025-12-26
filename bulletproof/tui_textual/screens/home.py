"""Home screen with profile and file selection."""

from pathlib import Path
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header,
    Static,
    Button,
    Select,
    Label,
    Input,
    DataTable,
)
from textual.binding import Binding
from textual.message import Message
from textual.worker import work
import asyncio

from bulletproof.core import list_profiles, TranscodeJob, get_profile
from bulletproof.tui_textual.widgets.profile_selector import ProfileSelector
from bulletproof.tui_textual.widgets.file_picker_widget import FilePickerWidget
from bulletproof.tui_textual.screens.transcode import TranscodeScreen


class TranscodeStarted(Message):
    """Posted when user starts a transcode."""

    def __init__(self, input_file: Path, profile: str, output_file: Path, preset: str):
        super().__init__()
        self.input_file = input_file
        self.profile = profile
        self.output_file = output_file
        self.preset = preset


class HomeScreen(Screen):
    """Main home screen for selecting profiles and files."""

    TITLE = "Bulletproof - Home"
    BINDINGS = [
        Binding("ctrl+n", "new_transcode", "New Transcode"),
        Binding("ctrl+b", "batch_process", "Batch Process"),
        Binding("ctrl+s", "show_settings", "Settings"),
    ]

    def compose(self):
        """Compose the home screen."""
        yield Vertical(
            Label("📹 Professional Video Transcoding", id="title"),
            Horizontal(
                # Left panel: Profile selection
                Vertical(
                    Label("[bold]1. Select Profile[/bold]"),
                    ProfileSelector(id="profile-selector"),
                    id="left-panel",
                ),
                # Right panel: File selection
                Vertical(
                    Label("[bold]2. Select Files[/bold]"),
                    FilePickerWidget(id="file-picker"),
                    id="right-panel",
                ),
                id="main-content",
            ),
            # Bottom panel: Actions
            Vertical(
                Label("[bold]3. Options & Start[/bold]"),
                Horizontal(
                    Label("Speed Preset:"),
                    Select(
                        [
                            ("Fast", "fast"),
                            ("Normal (Default)", "normal"),
                            ("Slow", "slow"),
                        ],
                        id="speed-preset",
                    ),
                ),
                Horizontal(
                    Button("Start Transcode", id="start-btn", variant="primary"),
                    Button("Batch Process", id="batch-btn"),
                    Button("Settings", id="settings-btn"),
                    Button("Quit", id="quit-btn"),
                ),
                id="bottom-panel",
            ),
            id="home-screen",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "start-btn":
            self.action_start_transcode()
        elif event.button.id == "batch-btn":
            self.action_batch_process()
        elif event.button.id == "settings-btn":
            self.action_show_settings()
        elif event.button.id == "quit-btn":
            self.app.exit()

    def action_start_transcode(self) -> None:
        """Start transcoding with selected options."""
        profile_selector = self.query_one("#profile-selector", ProfileSelector)
        file_picker = self.query_one("#file-picker", FilePickerWidget)
        speed_select = self.query_one("#speed-preset", Select)

        profile_name = profile_selector.selected_profile
        input_file = file_picker.input_file
        output_file = file_picker.output_file
        preset = speed_select.value if speed_select.value else "normal"

        if not profile_name:
            self.notify("⚠️ Please select a profile", severity="warning")
            return

        if not input_file or not Path(input_file).exists():
            self.notify("⚠️ Please select a valid input file", severity="warning")
            return

        if not output_file:
            self.notify("⚠️ Please specify an output file", severity="warning")
            return

        # Get the profile object
        try:
            profile = get_profile(profile_name)
        except KeyError:
            self.notify(f"❌ Profile '{profile_name}' not found", severity="error")
            return

        # Create TranscodeJob
        job = TranscodeJob(
            input_file=Path(input_file),
            output_file=Path(output_file),
            profile=profile,
            speed_preset=preset,
        )

        # Navigate to transcode screen with job
        transcode_screen = TranscodeScreen(job=job)
        self.app.push_screen(transcode_screen)

    def action_batch_process(self) -> None:
        """Open batch processing dialog."""
        self.app.notify("📦 Batch processing coming soon!", timeout=3)

    def action_show_settings(self) -> None:
        """Show settings screen."""
        from bulletproof.tui_textual.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())
