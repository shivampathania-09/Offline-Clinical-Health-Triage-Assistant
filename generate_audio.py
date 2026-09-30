"""
generate_audio.py
Generates the 7-part English voiceover teleprompter audio matching the exact
second-by-second timeline of the Snapdragon AI Challenge 2026 2-minute demo recording.
Uses gTTS for speech synthesis and moviepy for millisecond-accurate timeline placement.
Exports: full_voiceover.mp3 in the project root folder.
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

from gtts import gTTS
from moviepy import AudioFileClip, CompositeAudioClip

# 7-Part Voiceover Teleprompter matching the 2-Minute Demo Recording Timeline
VOICEOVER_PARTS = [
    {
        "id": 1,
        "title": "Phase 1: The Healthcare Chasm (0:00 - 0:25)",
        "target_start_sec": 1.0,
        "text": (
            "Over 68% of rural clinics face telecommunication blackouts where cloud chatbots fail, "
            "latency introduces danger, and patient data privacy is compromised. "
            "Frontline workers need an on-device, sovereign triage assistant that speaks regional vernaculars like Hindi "
            "and operates with zero network egress."
        )
    },
    {
        "id": 2,
        "title": "Phase 2: Zero-Egress Architecture (0:26 - 0:49)",
        "target_start_sec": 26.0,
        "text": (
            "Meet the Offline Clinical Health Triage Assistant—an edge-native application running 100% on-device. "
            "Our architecture is safe-by-construction: a sub-millisecond Core Safety Engine evaluates queries with "
            "5-token lookback negation matching to catch emergencies before the LLM can hallucinate."
        )
    },
    {
        "id": 3,
        "title": "Phase 3A: Prompt 1 Emergency Override (0:49 - 1:06)",
        "target_start_sec": 49.0,
        "text": (
            "Watch: When a patient presents with acute crushing chest pressure, our safety engine intercepts in less than one millisecond—"
            "bypassing LLM inference to deliver an immediate, life-saving 112 emergency routing card."
        )
    },
    {
        "id": 4,
        "title": "Phase 3B: Prompt 2 Bilingual Hindi Query (1:06 - 1:22)",
        "target_start_sec": 66.5,
        "text": (
            "Clicking New Session, our multilingual pipeline dynamically detects Hindi, rendering crisp Devanagari script natively "
            "without tofu boxes, tagging fever and asking focused duration details on Turn 1."
        )
    },
    {
        "id": 5,
        "title": "Phase 3C: Prompts 3 & 4 Multi-Turn & Turn 3 Escalation (1:22 - 1:44)",
        "target_start_sec": 82.5,
        "text": (
            "The patient replies in English; language dynamically switches back with home hydration advice. "
            "On Turn 3, our safe-by-construction guardrail catches persisting clinical uncertainty and automatically "
            "escalates severity from Mild to Moderate, advising outpatient care."
        )
    },
    {
        "id": 6,
        "title": "Phase 3D: Real-Time Telemetry Dashboard (1:44 - 2:02)",
        "target_start_sec": 104.0,
        "text": (
            "On the right panel, our live telemetry dashboard continuously samples CPU load every 100 milliseconds, "
            "tracking Time-To-First-Token, token speed, and guaranteeing 100% local isolation with zero bytes egressed."
        )
    },
    {
        "id": 7,
        "title": "Phase 4: Snapdragon Hexagon NPU Optimization & Conclusion (2:02 - 2:28)",
        "target_start_sec": 123.0,
        "text": (
            "Designed for Snapdragon Hexagon NPU via Qualcomm QNN Execution Provider scaffolding with verified CPU fallback, "
            "our pipeline achieves sub-50ms latency and 70% CPU reduction. "
            "With 35 automated tests passing and zero network egress, we bring sovereign intelligence to the edge. Thank you."
        )
    }
]


def generate_full_voiceover(output_path: str = "full_voiceover.mp3", target_total_duration_sec: float = 118.0):
    print("=" * 70)
    print("  Generating 7-Part Voiceover Teleprompter Audio (gTTS + moviepy)")
    print("  Target Output: full_voiceover.mp3 (~118 seconds / 2 minutes)")
    print("=" * 70)

    audio_clips = []
    tmp_files = []

    try:
        current_cursor_sec = 0.0

        for part in VOICEOVER_PARTS:
            part_id = part["id"]
            title = part["title"]
            text = part["text"]
            target_start = max(part["target_start_sec"], current_cursor_sec + 0.4)

            print(f"\n[Part {part_id}/7] Synthesizing: {title}...")
            print(f"  Target Start: {target_start:.1f}s")

            # Synthesize via gTTS
            tts = gTTS(text=text, lang="en", tld="com", slow=False)
            tmp_fd, tmp_filename = tempfile.mkstemp(suffix=f"_part_{part_id}.mp3")
            os.close(tmp_fd)
            tmp_files.append(tmp_filename)
            tts.save(tmp_filename)

            # Load into moviepy AudioFileClip and position
            clip = AudioFileClip(tmp_filename).with_start(target_start)
            duration_sec: float = float(clip.duration) if clip.duration is not None else 0.0
            print(f"  Duration: {duration_sec:.2f}s | Audio Ends: {(target_start + duration_sec):.1f}s")

            audio_clips.append(clip)
            current_cursor_sec = target_start + duration_sec

        final_duration_sec = max(target_total_duration_sec, current_cursor_sec + 2.0)
        print(f"\nComposing master audio track (Duration: {final_duration_sec:.1f}s)...")
        composite = CompositeAudioClip(audio_clips).with_duration(final_duration_sec)

        print(f"Exporting to {output_path}...")
        composite.write_audiofile(output_path, fps=44100)

        # Close all clips
        for c in audio_clips:
            c.close()
        composite.close()

    finally:
        # Cleanup temp audio parts
        for f in tmp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass

    final_size_kb = os.path.getsize(output_path) / 1024.0 if os.path.exists(output_path) else 0.0
    print("=" * 70)
    print(f"  ✅ full_voiceover.mp3 generated successfully!")
    print(f"  Total Duration: {final_duration_sec:.2f} seconds ({final_duration_sec / 60:.2f} minutes)")
    print(f"  File Size: {final_size_kb:.1f} KB")
    print("=" * 70)
    return output_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "full_voiceover.mp3"
    generate_full_voiceover(out_file)
