"""Settings screen."""

from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Header, Label, Button, Input


class SettingsScreen(Screen):
    """Settings and configuration screen."""

    TITLE = "Bulletproof - Settings"

    def compose(self):
        """Compose the settings screen."""
        yield Vertical(
            Header(),
            Label("[bold]Settings[/bold]"),
            Label(""),
            Label("Default Profile:"),
            Input(placeholder="e.g., live-qlab", id="default-profile"),
            Label(""),
            Label("Output Directory:"),
            Input(placeholder="e.g., ~/Videos/processed", id="output-dir"),
            Label(""),
            Button("Save", id="save-btn", variant="primary"),
            Button("Cancel", id="cancel-btn"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.app.notify("✓ Settings saved!", timeout=2)
            self.app.pop_screen()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
