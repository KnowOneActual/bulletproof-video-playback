"""Terminal User Interface - Interactive transcode wizard."""

from pathlib import Path
from bulletproof.core import TranscodeJob, list_profiles


class TUIApp:
    """Interactive CLI-based TUI for bulletproof transcode."""

    def __init__(self):
        """Initialize TUI."""
        self.profiles = list_profiles()
        self.input_file = None
        self.selected_profile = "standard-playback"

    def run(self):
        """Run the interactive TUI."""
        print("\n" + "=" * 60)
        print("  bulletproof-video-playback Interactive Transcode")
        print("=" * 60)

        # Input file selection
        while True:
            input_path = input("\nEnter input file path: ").strip()
            if Path(input_path).exists():
                self.input_file = Path(input_path)
                break
            print("File not found. Try again.")

        # Profile selection
        print("\nAvailable profiles:")
        for i, (name, prof) in enumerate(self.profiles.items(), 1):
            print(f"  {i}. {name} - {prof.description}")

        while True:
            try:
                choice = int(input("\nSelect profile (number): ")) - 1
                self.selected_profile = list(self.profiles.keys())[choice]
                break
            except (ValueError, IndexError):
                print("Invalid selection. Try again.")

        # Output file
        default_output = (
            self.input_file.parent / f"{self.input_file.stem}_output.mov"
        )
        output_input = input(f"\nOutput file path [{default_output}]: ").strip()
        output_file = Path(output_input) if output_input else default_output

        # Confirm and execute
        print(f"\nPrepared transcode:")
        print(f"  Input:   {self.input_file}")
        print(f"  Profile: {self.selected_profile}")
        print(f"  Output:  {output_file}")

        if input("\nProceed? (y/n): ").lower() == "y":
            profile = self.profiles[self.selected_profile]
            job = TranscodeJob(self.input_file, output_file, profile)
            print("\nStarting transcode...")
            if job.execute():
                print(f"✓ Complete!")
                print(f"  Output: {output_file}")
            else:
                print(f"✗ Failed: {job.error_message}")
        else:
            print("Cancelled.")


def main():
    """Entry point for TUI."""
    app = TUIApp()
    app.run()


if __name__ == "__main__":
    main()
