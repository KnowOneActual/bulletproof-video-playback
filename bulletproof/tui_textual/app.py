"""Main Textual application for Bulletproof Video Playback."""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding
from textual.reactive import reactive

from bulletproof.core import list_profiles
from bulletproof.tui_textual.screens.home import HomeScreen
from bulletproof.tui_textual.screens.transcode import TranscodeScreen
from bulletproof.tui_textual.screens.settings import SettingsScreen
from bulletproof.tui_textual.screens.about import AboutScreen


class BulletproofApp(App):
    """Professional video transcoding application with Textual TUI."""

    TITLE = "Bulletproof Video Playback"
    SUB_TITLE = "Professional transcoding for live playback"

    CSS_PATH = "styles/app.css"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+h", "show_help", "Help", show=True),
        Binding("d", "toggle_dark", "Dark mode", show=True),
        Binding("1", "screen_home", "Home", show=True),
        Binding("2", "screen_settings", "Settings", show=True),
        Binding("3", "screen_about", "About", show=True),
    ]

    current_profile: reactive[str] = reactive("live-qlab")
    input_file: reactive[Path | None] = reactive(None)
    output_file: reactive[Path | None] = reactive(None)
    speed_preset: reactive[str] = reactive("normal")

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Set initial profile to first available or live-qlab
        profiles = list_profiles()
        if "live-qlab" in profiles:
            self.current_profile = "live-qlab"
        elif profiles:
            self.current_profile = list(profiles.keys())[0]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield HomeScreen()
        yield Footer()

    def action_show_help(self) -> None:
        """Show help information."""
        self.push_screen(AboutScreen())

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_screen_home(self) -> None:
        """Switch to home screen."""
        self.app.pop_screen()
        self.app.push_screen(HomeScreen())

    def action_screen_settings(self) -> None:
        """Switch to settings screen."""
        self.app.pop_screen()
        self.app.push_screen(SettingsScreen())

    def action_screen_about(self) -> None:
        """Switch to about screen."""
        self.app.pop_screen()
        self.app.push_screen(AboutScreen())


def run_tui() -> None:
    """Entry point for Textual TUI."""
    app = BulletproofApp()
    app.run()


if __name__ == "__main__":
    run_tui()
