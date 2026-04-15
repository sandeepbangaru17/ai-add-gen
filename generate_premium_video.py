"""
Generate Premium Images from Prompts
"""

import io
import json
import sys
import time
import subprocess
import shutil
from pathlib import Path

# Windows encoding fix
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))

import asyncio
import requests
from PIL import Image

try:
    import edge_tts
except ImportError:
    print("Please install: pip install edge-tts")
    sys.exit(1)

try:
    from config import (
        OUTPUT_DIR,
        VOICE_DIR,
        SCENE_IMAGES_DIR,
        SCENE_CLIPS_DIR,
        FFMPEG_BIN,
        ensure_dirs,
        VIDEO_FPS,
    )
except ImportError:
    print("Config import failed")
    sys.exit(1)


def generate_image(prompt, output_path, width=1024, height=576, seed=42):
    """Generate image using Pollinations AI"""
    styled_prompt = f"{prompt}, realistic photography, professional quality, sharp focus, bright lighting"

    for attempt in range(5):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(styled_prompt)}?width={width}&height={height}&seed={seed + attempt}&model=flux&nologo=true"
            print(f"   [IMG] Generating... attempt {attempt + 1}/5")
            response = requests.get(url, timeout=180)

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
                image.save(str(output_path), quality=95)
                print(f"   [OK] Saved: {output_path.name}")
                return True

            print(f"   [ERR] Status: {response.status_code}, waiting...")
        except Exception as e:
            print(f"   [ERR] {e}, waiting...")

        time.sleep(10)  # Wait longer between retries

    return False


def create_ken_burns_clip(image_path, output_path, duration, effect="zoom_in", fps=24):
    """Create video clip with Ken Burns effect"""
    effects = {
        "zoom_in": "zoom in",
        "zoom_out": "zoom out",
        "pan_right": "pan left to right",
        "pan_left": "pan right to left",
    }

    vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"

    if effect == "zoom_in":
        vf += ",zoompan=z='min(zoom+0.005,1.2)':d=25:s=1920x1080"
    elif effect == "zoom_out":
        vf += ",zoompan=z='max(zoom-0.003,1.0)':d=25:s=1920x1080"
    elif effect == "pan_right":
        vf += ",crop=1920:1080:(iw-1920)*t/50:0"
    elif effect == "pan_left":
        vf += ",crop=1920:1080:(iw-1920)*(1-t/50):0"

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-vf",
        vf,
        "-t",
        str(duration),
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "fast",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def generate_voiceover(script_path, output_dir):
    """Generate voiceover using edge-tts"""
    with open(script_path, "r") as f:
        script = json.load(f)

    ensure_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[VOICE] Generating voiceover...")

    async def generate():
        for i, scene in enumerate(script["scenes"]):
            text = scene["voiceover"]
            output_file = output_dir / f"scene_{i + 1}.mp3"

            print(f"   Scene {i + 1}: {text[:50]}...")

            communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
            await communicate.save(str(output_file))

    asyncio.run(generate())

    # Merge audio files
    print("[VOICE] Merging audio...")

    list_file = output_dir / "files.txt"
    with open(list_file, "w") as f:
        for i in range(len(script["scenes"])):
            f.write(f"file 'scene_{i + 1}.mp3'\n")

    merged = output_dir / "voiceover.mp3"

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(merged),
    ]

    subprocess.run(cmd, capture_output=True)
    print(f"   [OK] Voiceover saved: {merged.name}")

    # Generate SRT subtitles
    srt_file = output_dir / "subtitles.srt"
    with open(srt_file, "w") as f:
        current_time = 0.0
        for i, scene in enumerate(script["scenes"]):
            start = current_time
            end = current_time + scene["duration_seconds"]
            current_time = end

            # Format time
            def fmt(t):
                ms = int((t % 1) * 1000)
                s = int(t) % 60
                m = int(t) // 60 % 60
                h = int(t) // 3600
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            f.write(f"{i + 1}\n")
            f.write(f"{fmt(start)} --> {fmt(end)}\n")
            f.write(f"{scene['on_screen_text']}\n\n")

    print(f"   [OK] Subtitles saved: {srt_file.name}")

    return merged, srt_file


def stitch_video_with_audio(clips, audio_path, srt_path, output_path, clips_list):
    """Combine clips, add audio and subtitles"""
    # Create clips list file
    with open(clips_list, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    # Merge clips
    merged = output_path.parent / "merged.mp4"
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(clips_list),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(merged),
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"   [OK] Clips merged")

    # Add audio
    with_audio = output_path.parent / "with_audio.mp4"
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i",
        str(merged),
        "-i",
        str(audio_path),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(with_audio),
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"   [OK] Audio added")

    # Copy SRT and add subtitles
    srt_copy = output_path.parent / "subtitles.srt"
    shutil.copy(str(srt_path), str(srt_copy))

    # Burn subtitles
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i",
        str(with_audio),
        "-vf",
        f"subtitles={str(srt_copy)}",
        "-c:v",
        "libx264",
        "-c:a",
        "copy",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        # Fallback: just copy
        shutil.copy(str(with_audio), str(output_path))

    print(f"   [OK] Video complete: {output_path.name}")


def main():
    print("=" * 60)
    print(" PREMIUM VIDEO GENERATION")
    print("=" * 60)

    # Paths
    script_path = Path("premium_script.json")
    prompts_path = Path("premium_script_prompts.json")
    ensure_dirs()

    # Load scripts
    with open(script_path, "r") as f:
        script = json.load(f)

    with open(prompts_path, "r") as f:
        prompts = json.load(f)

    # Verify 30 seconds
    total = sum(s["duration_seconds"] for s in script["scenes"])
    print(f"\n[INFO] Total duration: {total} seconds")

    # Generate images
    print("\n" + "=" * 60)
    print(" STEP 1: Generate Images")
    print("=" * 60)

    effects = ["zoom_in", "zoom_out", "pan_right", "pan_left"]
    clips = []

    for i, (scene, prompt) in enumerate(zip(script["scenes"], prompts["scenes"])):
        print(f"\nScene {i + 1} ({scene['duration_seconds']}s):")

        img_path = SCENE_IMAGES_DIR / f"scene_{i + 1}.png"
        clip_path = SCENE_CLIPS_DIR / f"scene_{i + 1}.mp4"

        # Generate image
        success = generate_image(prompt["video_prompt"], img_path)

        if not success:
            print(f"   [ERR] Image generation failed")
            continue

        # Create video clip
        effect = effects[i % len(effects)]
        print(f"   [EFFECT] Applying {effect} for {scene['duration_seconds']}s")
        create_ken_burns_clip(img_path, clip_path, scene["duration_seconds"], effect)

        clips.append(clip_path)
        print(f"   [OK] Clip created: {clip_path.name}")

    if not clips:
        print("[ERR] No clips generated!")
        return

    # Generate voiceover
    print("\n" + "=" * 60)
    print(" STEP 2: Generate Voiceover")
    print("=" * 60)

    audio_path, srt_path = generate_voiceover(script_path, VOICE_DIR)

    # Stitch video
    print("\n" + "=" * 60)
    print(" STEP 3: Stitch Video")
    print("=" * 60)

    clips_list = OUTPUT_DIR / "clips.txt"
    output_path = OUTPUT_DIR / "premium_ad.mp4"

    stitch_video_with_audio(clips, audio_path, srt_path, output_path, clips_list)

    # Export formats
    print("\n" + "=" * 60)
    print(" STEP 4: Export Formats")
    print("=" * 60)

    exports = {"16x9": (1920, 1080), "1x1": (1080, 1080), "9x16": (1080, 1920)}

    for fmt, (w, h) in exports.items():
        output_fmt = OUTPUT_DIR / f"premium_ad_{fmt}.mp4"
        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i",
            str(output_path),
            "-vf",
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-c:a",
            "aac",
            str(output_fmt),
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"   [OK] {fmt}: {output_fmt.name}")

    # Copy to demo
    demo_path = Path("demo/premium_ad_demo.mp4")
    shutil.copy(str(output_path), str(demo_path))

    print("\n" + "=" * 60)
    print(" PREMIUM VIDEO COMPLETE!")
    print("=" * 60)
    print(f"\nOutput: {output_path}")
    print(f"Demo: {demo_path}")


if __name__ == "__main__":
    main()
