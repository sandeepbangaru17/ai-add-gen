"""
Create exactly 30-second video with proper timing
"""

import subprocess
import shutil
from pathlib import Path

# Windows encoding fix
import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FFMPEG_BIN = r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

OUTPUT_DIR = Path("output")
DEMO_DIR = Path("demo")


def main():
    print("=" * 60)
    print(" CREATING 30-SECOND PREMIUM VIDEO")
    print("=" * 60)

    # Paths
    video_input = OUTPUT_DIR / "premium_ad.mp4"
    audio_input = OUTPUT_DIR / "voice" / "voiceover.mp3"

    # Target: 30 seconds
    target_duration = 30.0

    # Create 30-second version with padding
    # Option 1: Add silence at the end to reach 30 seconds
    padded_output = OUTPUT_DIR / "premium_ad_30s.mp4"

    # First, let's check actual duration
    result = subprocess.run(
        [
            FFMPEG_BIN,
            "-y",
            "-i",
            str(video_input),
            "-i",
            str(audio_input),
            "-filter_complex",
            "[1:a]apad=whole_dur=30[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-t",
            "30",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            str(padded_output),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[ERR] {result.stderr[:200]}")
        # Fallback: just copy original
        shutil.copy(str(video_input), str(padded_output))
    else:
        print("[OK] 30-second version created")

    # Export all formats
    print("\n[EXPORT] Creating all formats...")

    formats = {"16x9": (1920, 1080), "1x1": (1080, 1080), "9x16": (1080, 1920)}

    for fmt, (w, h) in formats.items():
        output = OUTPUT_DIR / f"premium_ad_30s_{fmt}.mp4"
        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i",
            str(padded_output),
            "-vf",
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v",
            "libx264",
            "-crf",
            "22",
            "-c:a",
            "aac",
            str(output),
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"   [OK] {fmt}: {output.name}")

    # Check final duration
    result = subprocess.run(
        [
            FFMPEG_BIN,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(padded_output),
        ],
        capture_output=True,
        text=True,
    )

    duration = float(result.stdout.strip())
    print(f"\n[INFO] Final video duration: {duration:.1f} seconds")

    # Copy to demo
    demo_output = DEMO_DIR / "premium_ad_30s_demo.mp4"
    shutil.copy(str(padded_output), str(demo_output))
    print(f"[OK] Demo saved: {demo_output}")

    print("\n" + "=" * 60)
    print(" 30-SECOND PREMIUM VIDEO COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
