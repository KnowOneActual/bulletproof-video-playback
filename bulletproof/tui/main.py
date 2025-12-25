"""Terminal User Interface - Interactive transcode wizard."""

import os
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
            # Handle shell escape sequences
            input_path = input_path.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")
            # Expand ~ if present
            input_path = os.path.expanduser(input_path)
            if Path(input_path).exists() and Path(input_path).is_file():
                self.input_file = Path(input_path)
                break
            print("File not found or is not a file. Try again.")

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

        # Get profile to determine output extension
        profile = self.profiles[self.selected_profile]
        extension = profile.extension

        # Generate smart default output filename
        default_output = (
            self.input_file.parent
            / f"{self.input_file.stem}__{self.selected_profile}.{extension}"
        )

        # Output file selection with safety checks
        while True:
            output_input = input(
                f"\nOutput file path [{default_output}]: "
            ).strip()

            # If user pressed Enter (empty), use default
            if not output_input:
                output_file = default_output
            else:
                # User provided a path
                output_path_raw = output_input.replace("\\ ", " ").replace(
                    "\\(", "("
                ).replace("\\)", ")")
                output_file = Path(os.path.expanduser(output_path_raw))

            # Safety check: prevent accidental overwrite of input
            if output_file == self.input_file:
                print(
                    "\n⚠️  ERROR: Output would overwrite input file!"
                )
                print(f"   Refusing to overwrite: {self.input_file}")
                print("   Please choose a different output filename.\n")
                continue

            # Warn if output already exists
            if output_file.exists():
                overwrite = input(
                    f"⚠️  Output file already exists. Overwrite? (y/n): "
                )
                if overwrite.lower() != "y":
                    print("   Cancelled. Choose a different filename.\n")
                    continue

            # All checks passed
            break

        # Confirm and execute
        print(f"\nPrepared transcode:")
        print(f"  Input:   {self.input_file}")
        print(f"  Profile: {self.selected_profile}")
        print(f"  Output:  {output_file}")

        if input("\nProceed? (y/n): ").lower() == "y":
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
