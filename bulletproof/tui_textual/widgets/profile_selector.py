"""Profile selector widget for choosing transcode profiles."""

from textual.widgets import Static, DataTable
from textual.containers import ScrollableContainer, Vertical
from textual.reactive import reactive
from bulletproof.core import list_profiles


class ProfileSelector(Static):
    """Widget for selecting and displaying transcoding profiles."""

    selected_profile: reactive[str | None] = reactive(None)

    def compose(self):
        """Render the profile selector."""
        profiles = list_profiles()

        # Create data table with profile information
        table = DataTable(id="profile-table")
        table.add_columns(
            "Profile", "Codec", "Use Case", "Speed", "Ext"
        )

        for name, profile in profiles.items():
            # Estimate speed: ProRes fast, H.264 slow, H.265 medium
            if "prores" in name.lower() or "proxy" in name.lower():
                speed = "Fast"
            elif "h264" in name.lower():
                speed = "Slow"
            elif "h265" in name.lower() or "stream" in name.lower():
                speed = "Medium"
            else:
                speed = "Medium"

            # Get codec name from profile
            codec = profile.codec.upper() if hasattr(profile, 'codec') else "Unknown"
            description = profile.description if hasattr(profile, 'description') else ""
            ext = profile.extension if hasattr(profile, 'extension') else ".mp4"

            table.add_row(
                f"[bold]{name}[/bold]",
                codec,
                description[:20] + "..." if len(description) > 20 else description,
                speed,
                ext,
                key=name,
            )

        # Set default row
        if "live-qlab" in profiles:
            table.cursor_location = (0, 0)  # Select first row
            self.selected_profile = "live-qlab"

        yield Vertical(
            table,
            Static(
                "[dim]Use ↑↓ to navigate, Enter to select[/dim]",
                id="profile-help",
            ),
        )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        table = self.query_one("#profile-table", DataTable)
        row_key = table.get_row_at(event.cursor_row)
        self.selected_profile = row_key[0] if row_key else None
