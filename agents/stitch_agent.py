"""
Stage 6 — Asset Stitching & Video Assembly Agent
Uses FFmpeg to combine scene clips, voiceover, text overlays, transitions, and logo.
Outputs: output/ad_draft.mp4
"""

import json
import subprocess
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    OUTPUT_DIR,
    VOICE_DIR,
    SCENE_CLIPS_DIR,
    MUSIC_DIR,
    ASSETS_DIR,
    FFMPEG_BIN,
    ensure_dirs,
)


def create_text_overlay_clip(
    video_path: Path,
    text: str,
    start_time: float,
    duration: float,
    output_path: Path,
    font_size: int = 48,
    color: str = "white",
    stroke_color: str = "black",
) -> bool:
    """Add text overlay to a clip using FFmpeg."""
    # Simple approach - put text in center bottom area
    vf = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={color}:borderw=3:bordercolor={stroke_color}:x=(w-text_w)/2:y=h-150"

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i",
        str(video_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-c:a",
        "copy",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.returncode == 0


def add_fade_transition(
    input_path: Path, output_path: Path, fade_in: float = 0.3, fade_out: float = 0.3
) -> bool:
    """Add fade in/out transitions to a clip."""
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i",
        str(input_path),
        "-vf",
        f"fade=t=in:st=0:d={fade_in},fade=t=out:st=-{fade_out}:d={fade_out}",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-c:a",
        "copy",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.returncode == 0


def concat_clips_with_transitions(
    clip_paths: list[Path], output_path: Path, transition_frames: int = 6
) -> bool:
    """Concatenate clips with crossfade transitions using FFmpeg."""
    if len(clip_paths) == 1:
        shutil.copy2(str(clip_paths[0]), str(output_path))
        return True

    # Create filter complex for crossfade
    filter_parts = []
    for i, clip in enumerate(clip_paths):
        filter_parts.append("-i")
        filter_parts.append(str(clip))

    # Build crossfade filter - simpler approach
    if len(clip_paths) == 2:
        crossfade = "[0:v][1:v]xfade=transition=fade:duration=0.25:offset=0.25[v]"
    elif len(clip_paths) == 3:
        crossfade = "[0:v][1:v]xfade=transition=fade:duration=0.25:offset=0.25[v01];[v01][2:v]xfade=transition=fade:duration=0.25[v]"
    elif len(clip_paths) == 4:
        crossfade = "[0:v][1:v]xfade=transition=fade:duration=0.25:offset=0.25[v01];[v01][2:v]xfade=transition=fade:duration=0.25[v02];[v02][3:v]xfade=transition=fade:duration=0.25[v]"
    elif len(clip_paths) == 5:
        crossfade = "[0:v][1:v]xfade=transition=fade:duration=0.25:offset=0.25[v01];[v01][2:v]xfade=transition=fade:duration=0.25[v02];[v02][3:v]xfade=transition=fade:duration=0.25[v03];[v03][4:v]xfade=transition=fade:duration=0.25[v]"
    else:
        # Too many clips, use simple concat
        return simple_concat(clip_paths, output_path)

    cmd = (
        [
            FFMPEG_BIN,
            "-y",
        ]
        + filter_parts
        + [
            "-filter_complex",
            crossfade,
            "-map",
            "[v]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
    )

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"      ⚠️  Crossfade failed: {result.stderr[:200]}")
        return simple_concat(clip_paths, output_path)
    return True

    # Create filter complex for crossfade
    filter_parts = []
    for i, clip in enumerate(clip_paths):
        filter_parts.append(f"-i", str(clip))

    # Build crossfade filter
    crossfade = ""
    if len(clip_paths) == 2:
        crossfade = f"[0:v][1:v]xfade=transition=fade:duration=0.25:offset={transition_frames / 24}[v]"
    else:
        # Multiple clips - chain xfades
        chain = "[0:v][1:v]xfade=transition=fade:duration=0.25:offset=0[v01];"
        for i in range(2, len(clip_paths)):
            chain += (
                f"[v{i - 1:02d}][{i}:v]xfade=transition=fade:duration=0.25[v{i:02d}];"
            )
        chain = chain.rstrip(";")
        crossfade = chain

    cmd = [
        FFMPEG_BIN,
        "-y",
        *filter_parts,
        "-filter_complex",
        crossfade,
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        # Fallback: simple concat without transitions
        return simple_concat(clip_paths, output_path)
    return True


def simple_concat(clip_paths: list[Path], output_path: Path) -> bool:
    """Simple concatenation without transitions."""
    list_file = OUTPUT_DIR / "clips_list.txt"
    with open(list_file, "w") as f:
        for clip in clip_paths:
            f.write(f"file '{clip.resolve()}'\n")

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode == 0


def add_audio(
    video_path: Path, voiceover_path: Path, bg_music_path: Path, output_path: Path
) -> bool:
    """Mix voiceover + optional background music into the video."""
    if bg_music_path and bg_music_path.exists():
        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(voiceover_path),
            "-i",
            str(bg_music_path),
            "-filter_complex",
            "[1:a]volume=1.0[vo];[2:a]volume=0.15,afade=t=out:st=25:d=5[bg];[vo][bg]amix=inputs=2:duration=first[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ]
    else:
        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(voiceover_path),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode == 0


def add_subtitles(video_path: Path, srt_path: Path, output_path: Path) -> bool:
    """Burn subtitles into the video."""
    if not srt_path.exists():
        print("   ⚠️  No subtitles file found, skipping...")
        shutil.copy2(str(video_path), str(output_path))
        return True

    srt_in_output = OUTPUT_DIR / "subtitles.srt"
    shutil.copy2(str(srt_path), str(srt_in_output))

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i",
        str(video_path.name),
        "-vf",
        "subtitles=subtitles.srt",
        "-c:v",
        "libx264",
        "-c:a",
        "copy",
        str(output_path.name),
    ]

    result = subprocess.run(
        cmd, cwd=str(OUTPUT_DIR), capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"   ⚠️  Subtitle error: {result.stderr[:500]}")
        shutil.copy2(str(video_path), str(output_path))
        print("   ℹ️  Copied video without subtitles as fallback")
        return False
    return True


def run(clips_dir: Path = None) -> dict:
    """Run the Stitch Agent."""
    ensure_dirs()

    clips_dir = clips_dir or SCENE_CLIPS_DIR
    voiceover_path = VOICE_DIR / "voiceover.mp3"
    srt_path = VOICE_DIR / "subtitles.srt"
    bg_music_path = MUSIC_DIR / "background.mp3"
    draft_path = OUTPUT_DIR / "ad_draft.mp4"

    # Load script for text overlays
    script = None
    script_path = OUTPUT_DIR / "script.json"
    if script_path.exists():
        with open(script_path, "r") as f:
            script = json.load(f)

    print("\n" + "=" * 60)
    print("  🔗  Stage 6 — Asset Stitching & Assembly (FFmpeg)")
    print("=" * 60)

    # Get all scene clips
    clips = sorted(clips_dir.glob("scene_*.mp4"))
    if not clips:
        raise FileNotFoundError(f"No scene clips found in {clips_dir}")

    print(f"\n   📹 Found {len(clips)} scene clips")

    # Step 1: Add text overlays to each clip
    print("\n   📝 Step 1: Adding text overlays to clips...")
    processed_clips = []

    if script and "scenes" in script:
        current_time = 0.0
        for i, clip in enumerate(clips):
            scene = next((s for s in script["scenes"] if s["scene_id"] == i + 1), None)
            text = scene.get("on_screen_text", "") if scene else ""
            duration = scene.get("duration_seconds", 3) if scene else 3

            processed_clip = OUTPUT_DIR / f"clip_with_text_{i + 1}.mp4"

            if text:
                success = create_text_overlay_clip(
                    clip, text, 0, duration, processed_clip
                )
                if success:
                    print(f"      ✅ Scene {i + 1}: Added text '{text}'")
                    processed_clips.append(processed_clip)
                else:
                    print(f"      ⚠️  Failed to add text to Scene {i + 1}")
                    processed_clips.append(clip)
            else:
                processed_clips.append(clip)

            current_time += duration

    if not processed_clips:
        processed_clips = clips

    # Step 2: Add fade transitions to clips
    print("\n   ✨ Step 2: Adding fade transitions...")
    faded_clips = []
    for i, clip in enumerate(processed_clips):
        faded_clip = OUTPUT_DIR / f"clip_faded_{i + 1}.mp4"
        # First clip: fade in only, Last clip: fade out only
        if i == 0:
            cmd = [
                FFMPEG_BIN,
                "-y",
                "-i",
                str(clip),
                "-vf",
                f"fade=t=in:st=0:d=0.5",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-c:a",
                "copy",
                str(faded_clip),
            ]
        else:
            shutil.copy2(str(clip), str(faded_clip))
        subprocess.run(cmd, capture_output=True)
        faded_clips.append(faded_clip)

    # Add fade out to last clip
    if faded_clips:
        last_clip = faded_clips[-1]
        last_faded = OUTPUT_DIR / f"clip_faded_out.mp4"
        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i",
            str(last_clip),
            "-vf",
            f"fade=t=out:st=-0.5:d=0.5",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            str(last_faded),
        ]
        subprocess.run(cmd, capture_output=True)
        faded_clips[-1] = last_faded

    print(f"      ✅ Added transitions to {len(faded_clips)} clips")

    # Step 3: Concatenate clips
    print("\n   🔗 Step 3: Concatenating clips...")
    merged_path = OUTPUT_DIR / "merged_clips.mp4"
    concat_clips_with_transitions(faded_clips, merged_path)
    print(f"      ✅ Merged: {merged_path}")

    # Step 4: Add audio
    print("\n   🎵 Step 4: Adding voiceover + background music...")
    audio_path = OUTPUT_DIR / "ad_with_audio.mp4"
    if voiceover_path.exists():
        add_audio(merged_path, voiceover_path, bg_music_path, audio_path)
        print(f"      ✅ Audio mixed: {audio_path}")
    else:
        print("      ⚠️  No voiceover found")
        audio_path = merged_path

    # Step 5: Add subtitles
    print("\n   📝 Step 5: Burning subtitles...")
    add_subtitles(audio_path, srt_path, draft_path)
    print(f"      ✅ Draft complete: {draft_path}")

    result = {
        "draft_video": str(draft_path),
        "merged_clips": str(merged_path),
    }

    print(f"\n✅ Stitching complete: {draft_path}")
    return result


if __name__ == "__main__":
    run()
