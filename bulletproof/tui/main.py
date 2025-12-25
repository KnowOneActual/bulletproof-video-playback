"""Terminal User Interface - Interactive transcode wizard."""

import os
import subprocess
from pathlib import Path
from bulletproof.core import TranscodeJob, list_profiles


class TUIApp:
    """Interactive CLI-based TUI for bulletproof transcode."""

    def __init__(self):
        """Initialize TUI."""
        self.profiles = list_profiles()
        self.input_file = None
        self.selected_profile = "standard-playback"

    def main_menu(self):
        """Show main menu and get user choice."""
        print("\n" + "=" * 60)
        print("  bulletproof-video-playback")
        print("=" * 60)
        print("\nWhat would you like to do?")
        print("  1. Transcode a video file")
        print("  2. Analyze a video file")
        print("  3. Batch process a folder")
        print("  4. Exit")

        while True:
            choice = input("\nSelect option (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            print("Invalid selection. Try again.")

    def transcode_single(self):
        """Transcode a single video file."""
        self._get_input_file()
        self._get_profile()
        self._get_output_file()
        self._execute_transcode()

    def analyze_video(self):
        """Analyze a video file."""
        while True:
            input_path = input("\nEnter video file path: ").strip()
            input_path = input_path.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")
            input_path = os.path.expanduser(input_path)
            if Path(input_path).exists() and Path(input_path).is_file():
                break
            print("File not found or is not a file. Try again.")

        print("\nAnalyzing video...\n")
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                str(input_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"Error analyzing video: {result.stderr}")
        except FileNotFoundError:
            print("ffprobe not found. Install ffmpeg to use this feature.")

    def batch_process(self):
        """Batch process all videos in a folder."""
        while True:
            folder_path = input("\nEnter folder path: ").strip()
            folder_path = folder_path.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")
            folder_path = os.path.expanduser(folder_path)
            if Path(folder_path).exists() and Path(folder_path).is_dir():
                break
            print("Folder not found or is not a directory. Try again.")

        # Find video files
        video_extensions = {".mov", ".mp4", ".mkv", ".avi", ".flv", ".wmv"}
        video_files = [
            f
            for f in Path(folder_path).iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]

        if not video_files:
            print(f"No video files found in {folder_path}")
            return

        print(f"\nFound {len(video_files)} video file(s):")
        for i, f in enumerate(video_files, 1):
            print(f"  {i}. {f.name}")

        self._get_profile()

        output_dir = input(f"\nOutput folder [{folder_path}]: ").strip()
        output_dir = Path(os.path.expanduser(output_dir)) if output_dir else Path(folder_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        if input(f"\nProcess {len(video_files)} file(s)? (y/n): ").lower() == "y":
            profile = self.profiles[self.selected_profile]
            for i, input_file in enumerate(video_files, 1):
                output_file = (
                    output_dir
                    / f"{input_file.stem}__processed__{self.selected_profile}.{profile.extension}"
                )
                print(f"\n[{i}/{len(video_files)}] Processing: {input_file.name}")
                job = TranscodeJob(input_file, output_file, profile)
                if job.execute():
                    print(f"✓ Complete")
                else:
                    print(f"✗ Failed: {job.error_message}")
        else:
            print("Cancelled.")

    def _get_input_file(self):
        """Get input file path from user."""
        while True:
            input_path = input("\nEnter input file path: ").strip()
            input_path = input_path.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")
            input_path = os.path.expanduser(input_path)
            if Path(input_path).exists() and Path(input_path).is_file():
                self.input_file = Path(input_path)
                break
            print("File not found or is not a file. Try again.")

    def _get_profile(self):
        """Get profile selection from user."""
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

    def _get_output_file(self):
        """Get output file path with safety checks."""
        profile = self.profiles[self.selected_profile]
        extension = profile.extension

        default_output = (
            self.input_file.parent
            / f"{self.input_file.stem}__processed__{self.selected_profile}.{extension}"
        )

        while True:
            output_input = input(f"\nOutput file path [{default_output}]: ").strip()

            if not output_input:
                self.output_file = default_output
            else:
                output_path_raw = (
                    output_input.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")
                )
                self.output_file = Path(os.path.expanduser(output_path_raw))

            if self.output_file == self.input_file:
                print("\n⚠️  ERROR: Output would overwrite input file!")
                print(f"   Refusing to overwrite: {self.input_file}")
                print("   Please choose a different output filename.\n")
                continue

            if self.output_file.exists():
                overwrite = input(f"⚠️  Output file already exists. Overwrite? (y/n): ")
                if overwrite.lower() != "y":
                    print("   Cancelled. Choose a different filename.\n")
                    continue

            break

    def _execute_transcode(self):
        """Execute the transcode job."""
        profile = self.profiles[self.selected_profile]

        print(f"\nPrepared transcode:")
        print(f"  Input:   {self.input_file}")
        print(f"  Profile: {self.selected_profile}")
        print(f"  Output:  {self.output_file}")

        if input("\nProceed? (y/n): ").lower() == "y":
            job = TranscodeJob(self.input_file, self.output_file, profile)
            print("\nStarting transcode...")
            if job.execute():
                print(f"✓ Complete!")
                print(f"  Output: {self.output_file}")
            else:
                print(f"✗ Failed: {job.error_message}")
        else:
            print("Cancelled.")

    def run(self):
        """Main TUI loop."""
        while True:
            choice = self.main_menu()
            if choice == "1":
                self.transcode_single()
            elif choice == "2":
                self.analyze_video()
            elif choice == "3":
                self.batch_process()
            elif choice == "4":
                print("\nGoodbye!\n")
                break


def main():
    """Entry point for TUI."""
    app = TUIApp()
    app.run()


if __name__ == "__main__":
    main()
