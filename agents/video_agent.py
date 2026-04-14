"""
Stage 5 — AI Video Generation Agent
Uses Hugging Face free Inference API for image generation + FFmpeg Ken Burns for motion.
Fallback: generates styled images with Pillow if HF API is unavailable.
Outputs: output/scene_images/, output/scene_clips/
"""

import io
import json
import sys
import time
import asyncio
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    OUTPUT_DIR,
    SCENE_IMAGES_DIR,
    SCENE_CLIPS_DIR,
    RAW_CLIPS_DIR,
    HF_TOKEN,
    HF_IMAGE_MODEL,
    VIDEO_FPS,
    FFMPEG_BIN,
    ensure_dirs,
)

try:
    import requests
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Please install: pip install requests Pillow")
    sys.exit(1)


# ─── Pollinations AI Image Generation (Free, no API key) ──────────────


def generate_image_pollinations(
    prompt: str, output_path: Path, retries: int = 3
) -> bool:
    """Generate an image using Pollinations AI (free, no API key)."""
    for attempt in range(retries):
        try:
            # Use flux model for better quality
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=576&seed={42 + attempt}&model=flux&nologo=true"
            response = requests.get(url, timeout=120)

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
                image.save(str(output_path), quality=95)
                return True

            print(f"      ⚠️  Pollinations error {response.status_code}")
        except Exception as e:
            print(f"      ⚠️  Request error: {e}")

        if attempt < retries - 1:
            time.sleep(5)

    return False


def generate_image_hf(prompt: str, output_path: Path, retries: int = 3) -> bool:
    """Generate an image using HuggingFace (fallback if Pollinations fails)."""
    if not HF_TOKEN:
        return False

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1920,
            "height": 1080,
            "num_inference_steps": 30,
        },
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                HF_API_URL, headers=headers, json=payload, timeout=120
            )

            if response.status_code == 503:
                wait_time = response.json().get("estimated_time", 30)
                print(f"      ⏳ Model loading, waiting {wait_time:.0f}s...")
                time.sleep(min(wait_time, 60))
                continue

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image.save(str(output_path), quality=95)
                return True

            print(
                f"      ⚠️  HF API error {response.status_code}: {response.text[:100]}"
            )

        except Exception as e:
            print(f"      ⚠️  Request error: {e}")

        if attempt < retries - 1:
            time.sleep(5)

    return False


# ─── Pillow Fallback Image Generation ────────────────────────────────


def generate_image_pillow(
    prompt: str, scene_id: int, output_path: Path, brand_colors: list = None
):
    """Generate a styled placeholder image with Pillow when HF API is unavailable."""
    colors = brand_colors or ["#1A1AFF", "#0D0D2B"]

    # Create gradient background
    img = Image.new("RGB", (1920, 1080))
    draw = ImageDraw.Draw(img)

    # Parse colors
    c1 = tuple(int(colors[0].lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    c2 = tuple(int(colors[-1].lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    # Draw gradient
    for y in range(1080):
        ratio = y / 1080
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (1920, y)], fill=(r, g, b))

    # Add decorative elements
    # Circles
    for i in range(5):
        x = 200 + i * 350
        y = 300 + (i % 3) * 150
        radius = 40 + i * 15
        opacity_color = (255, 255, 255)
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            outline=opacity_color,
            width=2,
        )

    # Add scene text
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Scene label
    draw.text((80, 80), f"Scene {scene_id}", fill="white", font=font_large)

    # Prompt text (wrap it)
    words = prompt.split()
    lines = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if len(test) > 70:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)

    y_pos = 500
    for text_line in lines[:5]:  # Max 5 lines
        draw.text((80, y_pos), text_line, fill=(200, 200, 255), font=font_small)
        y_pos += 40

    img.save(str(output_path), quality=95)


# ─── Ken Burns Effect (Image → Video) ────────────────────────────────


def apply_ken_burns(
    image_path: Path, output_path: Path, duration: float, effect: str = "zoom_in"
):
    """Apply Ken Burns pan/zoom effect to create video from a still image."""
    # Different motion effects for variety
    effects = {
        "zoom_in": "zoompan=z='min(zoom+0.0015,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps={fps}",
        "zoom_out": "zoompan=z='if(eq(on,1),1.4,max(zoom-0.0015,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps={fps}",
        "pan_right": "zoompan=z='1.2':x='if(eq(on,1),0,min(x+2,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps={fps}",
        "pan_left": "zoompan=z='1.2':x='if(eq(on,1),iw-iw/zoom,max(x-2,0))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps={fps}",
    }

    frames = int(duration * VIDEO_FPS)
    vf = effects.get(effect, effects["zoom_in"])
    vf = vf.format(frames=frames, fps=VIDEO_FPS)

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
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"      ⚠️  FFmpeg error: {result.stderr[:200]}")
        return False
    return True


def run(scene_prompts: dict = None) -> dict:
    """Run the Video Agent."""
    ensure_dirs()

    # Load scene prompts if not provided
    if scene_prompts is None:
        prompts_path = OUTPUT_DIR / "scene_prompts.json"
        if not prompts_path.exists():
            raise FileNotFoundError(
                f"Scene prompts not found at {prompts_path}. Run Stage 4 first."
            )
        with open(prompts_path, "r", encoding="utf-8") as f:
            scene_prompts = json.load(f)

    # Load brief for brand colors
    brand_colors = ["#1A1AFF", "#FFFFFF"]
    brief_path = OUTPUT_DIR / "brief.json"
    if brief_path.exists():
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
            brand_colors = brief.get("brand_colors", brand_colors)

    print("\n" + "=" * 60)
    print("  🎬  Stage 5 — AI Video Generation")
    print("=" * 60)

    effects = ["zoom_in", "zoom_out", "pan_right", "pan_left"]
    clips = []

    for i, scene in enumerate(scene_prompts["scenes"]):
        sid = scene["scene_id"]
        prompt = scene["video_prompt"]
        duration = scene["duration_seconds"]

        print(f"\n   📸 Scene {sid} ({duration}s):")
        print(f"      Prompt: {prompt[:60]}...")

        # Generate image
        img_path = SCENE_IMAGES_DIR / f"scene_{sid}.png"
        clip_path = SCENE_CLIPS_DIR / f"scene_{sid}.mp4"

        # Try Pollinations AI first (free, no API key)
        print(f"      Generating image via Pollinations AI...")
        success = generate_image_pollinations(prompt, img_path)

        if not success and HF_TOKEN:
            print(f"      Trying HuggingFace API as fallback...")
            success = generate_image_hf(prompt, img_path)

        if not success:
            print(f"      Using Pillow fallback for image generation...")
            generate_image_pillow(prompt, sid, img_path, brand_colors)

        # Apply Ken Burns effect to create video clip
        effect = effects[i % len(effects)]
        print(f"      Applying Ken Burns ({effect}) → {duration}s clip...")
        kb_success = apply_ken_burns(img_path, clip_path, duration, effect)

        if kb_success:
            clips.append(str(clip_path))
            print(f"      ✅ Clip generated: {clip_path}")
        else:
            print(f"      ❌ Failed to generate clip for Scene {sid}")

    result = {
        "clips": clips,
        "images_dir": str(SCENE_IMAGES_DIR),
        "clips_dir": str(SCENE_CLIPS_DIR),
    }

    print(f"\n✅ Video generation complete: {len(clips)} clips created")
    return result


if __name__ == "__main__":
    run()
