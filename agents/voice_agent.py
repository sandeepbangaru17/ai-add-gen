"""
Stage 3 — Voice Generation Agent
Uses edge-tts (free, no API key) to generate voiceover audio + subtitles.
Outputs: output/voice/voiceover.mp3, output/voice/subtitles.srt, per-scene files
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, VOICE_DIR, VOICE_MAP, FFMPEG_BIN, ensure_dirs

try:
    import edge_tts
except ImportError:
    print("❌ Please install edge-tts: pip install edge-tts")
    sys.exit(1)


def select_voice(tone: str) -> str:
    """Select the best voice based on the ad tone."""
    tone_lower = tone.lower()
    for key, voice in VOICE_MAP.items():
        if key in tone_lower:
            return voice
    return VOICE_MAP["default"]


async def generate_scene_voice(
    text: str, voice: str, output_path: Path, srt_path: Path = None
):
    """Generate voice audio for a single scene with optional subtitle data."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    # Generate subtitle data if path provided
    if srt_path:
        submaker = edge_tts.SubMaker()
        async for chunk in edge_tts.Communicate(text, voice).stream():
            if chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
        srt_content = submaker.get_srt()
        if srt_content:
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)


async def merge_audio_files(audio_files: list[Path], output_path: Path):
    """Merge multiple audio files into one using FFmpeg directly."""
    list_file = VOICE_DIR / "audio_list.txt"
    with open(list_file, "w") as f:
        for af in audio_files:
            # Use forward slashes and absolute paths for FFmpeg compatibility
            f.write(f"file '{af.resolve()}'\n")

    proc = await asyncio.create_subprocess_exec(
        FFMPEG_BIN,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(output_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(f"   Warning: FFmpeg merge issue: {stderr.decode()[:200]}")


def generate_srt_from_script(script: dict) -> str:
    """Generate SRT subtitles from script - shows on_screen_text + voiceover."""
    srt_lines = []
    current_time = 0.0

    for i, scene in enumerate(script["scenes"]):
        start = current_time
        end = current_time + scene["duration_seconds"]

        # Format timestamps
        start_ts = format_srt_time(start)
        end_ts = format_srt_time(end)

        # Use on_screen_text if available, otherwise voiceover
        text = scene.get("on_screen_text", "")
        if not text:
            text = scene.get("voiceover", "")

        srt_lines.append(f"{i + 1}")
        srt_lines.append(f"{start_ts} --> {end_ts}")
        srt_lines.append(text)
        srt_lines.append("")

        current_time = end

    return "\n".join(srt_lines)


def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


async def _run_async(script: dict, tone: str) -> dict:
    """Async implementation of the voice generation pipeline."""
    voice = select_voice(tone)
    print(f"   🎙️  Using voice: {voice}")

    scene_files = []

    for scene in script["scenes"]:
        sid = scene["scene_id"]
        text = scene["voiceover"]
        out_path = VOICE_DIR / f"scene_{sid}_voice.mp3"

        print(f'   Generating voice for Scene {sid}: "{text[:40]}..."')
        await generate_scene_voice(text, voice, out_path)
        scene_files.append(out_path)

    # Merge all scene audio into one file
    merged_path = VOICE_DIR / "voiceover.mp3"
    print(f"\n   🔗 Merging {len(scene_files)} scene audio files...")
    await merge_audio_files(scene_files, merged_path)

    # Generate SRT subtitles from script timing
    srt_content = generate_srt_from_script(script)
    srt_path = VOICE_DIR / "subtitles.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    result = {
        "merged_audio": str(merged_path),
        "subtitles": str(srt_path),
        "scene_files": [str(f) for f in scene_files],
        "voice_used": voice,
    }

    print(f"\n✅ Voice generation complete:")
    print(f"   Merged: {merged_path}")
    print(f"   Subtitles: {srt_path}")
    print(f"   Scene files: {len(scene_files)}")

    return result


def run(script: dict = None) -> dict:
    """Run the Voice Agent."""
    ensure_dirs()

    # Load script if not provided
    if script is None:
        script_path = OUTPUT_DIR / "script.json"
        if not script_path.exists():
            raise FileNotFoundError(
                f"Script not found at {script_path}. Run Stage 2 first."
            )
        with open(script_path, "r", encoding="utf-8") as f:
            script = json.load(f)

    # Load brief for tone
    brief_path = OUTPUT_DIR / "brief.json"
    tone = "professional"
    if brief_path.exists():
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
            tone = brief.get("tone", "professional")

    print("\n" + "=" * 60)
    print("  🎙️  Stage 3 — Voice Generation (edge-tts)")
    print("=" * 60)

    return asyncio.run(_run_async(script, tone))


if __name__ == "__main__":
    run()
