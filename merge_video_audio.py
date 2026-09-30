"""
merge_video_audio.py
Automatically attaches the generated 7-part voiceover (full_voiceover.mp3)
to the recorded MP4 screen capture from Windows Game Bar (C:\\Users\\<user>\\Videos\\Captures)
and exports the final merged video: FINAL_DEMO_SUBMISSION.mp4 in the project root directory.
"""

from __future__ import annotations
import os
import sys
import glob
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

from moviepy import VideoFileClip, AudioFileClip


def find_latest_capture(captures_dir: str | None = None) -> str:
    """Finds the most recently created or modified MP4 file across common recording directories."""
    candidate_dirs = [
        str(Path.home() / "Videos" / "Captures"),          # Xbox Game Bar default
        str(Path.home() / "Videos" / "Screen Recordings"), # Windows 11 Snipping Tool default
        str(Path.home() / "Videos"),                       # OBS / Loom default
        str(Path.home() / "Desktop"),
        str(Path.cwd()),
    ]
    if captures_dir:
        candidate_dirs.insert(0, captures_dir)

    all_mp4s: list[str] = []
    for d in candidate_dirs:
        if os.path.exists(d):
            files = glob.glob(os.path.join(d, "*.mp4"))
            # Exclude previously generated output files
            files = [
                f for f in files
                if not f.endswith("FINAL_DEMO_SUBMISSION.mp4")
                and not f.endswith("test_screen.mp4")
            ]
            all_mp4s.extend(files)

    if not all_mp4s:
        raise FileNotFoundError(
            "No .mp4 screen capture files found in Captures, Screen Recordings, or Videos.\n"
            "Please ensure you have recorded a video (via Win+Alt+R, Snipping Tool Win+Shift+R, or OBS).\n"
            "You can also pass your recording path directly: python merge_video_audio.py <path_to_video.mp4>"
        )

    # Sort by modification time descending
    latest_file = max(all_mp4s, key=os.path.getmtime)
    return latest_file


def merge_video_and_audio(
    video_path: str | None = None,
    audio_path: str = "full_voiceover.mp3",
    output_path: str = "FINAL_DEMO_SUBMISSION.mp4"
) -> str:
    print("=" * 70)
    print("  Post-Processing: Merging Screen Capture with Voiceover Audio")
    print("=" * 70)

    # 1. Resolve Audio Path
    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"Voiceover audio '{audio_path}' not found.\n"
            f"Please run '.venv\\Scripts\\python generate_audio.py' first."
        )

    # 2. Resolve Video Path
    resolved_video_path = video_path or find_latest_capture()

    print(f"\n[Source Video]: {resolved_video_path}")
    print(f"  File Size: {os.path.getsize(resolved_video_path) / (1024 * 1024):.2f} MB")
    print(f"[Source Audio]: {audio_path}")
    print(f"  File Size: {os.path.getsize(audio_path) / 1024:.1f} KB")

    # 3. Load Clips
    print("\nLoading media clips into MoviePy...")
    video_clip = VideoFileClip(resolved_video_path)
    audio_clip = AudioFileClip(audio_path)

    v_dur: float = float(video_clip.duration) if video_clip.duration is not None else 0.0
    a_dur: float = float(audio_clip.duration) if audio_clip.duration is not None else 0.0
    print(f"  Video Duration: {v_dur:.2f}s | Audio Duration: {a_dur:.2f}s")

    # 4. Synchronize Durations
    # If video is slightly longer or shorter, trim to the common boundary
    target_duration: float = min(v_dur, a_dur)
    if abs(v_dur - a_dur) > 0.5:
        print(f"  Aligning media streams to {target_duration:.2f}s...")
        video_clip = video_clip.subclipped(0, target_duration)
        audio_clip = audio_clip.subclipped(0, target_duration)

    # 5. Attach Audio to Video
    final_clip = video_clip.with_audio(audio_clip)

    # 6. Render Output Video
    print(f"\nRendering final submission video to '{output_path}'...")
    final_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=video_clip.fps or 30,
        preset="medium"
    )

    # 7. Cleanup
    video_clip.close()
    audio_clip.close()
    final_clip.close()

    out_size_mb = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0.0
    print("\n" + "=" * 70)
    print("  🎉 FINAL SUBMISSION VIDEO CREATED SUCCESSFULLY!")
    print(f"  Output Path: {os.path.abspath(output_path)}")
    print(f"  Duration:    {target_duration:.2f}s ({target_duration / 60.0:.2f} minutes)")
    print(f"  File Size:   {out_size_mb:.2f} MB")
    print("=" * 70)
    return output_path


if __name__ == "__main__":
    v_in: str | None = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    merge_video_and_audio(video_path=v_in)
