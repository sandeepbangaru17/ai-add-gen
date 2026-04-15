"""
AutoMail ULTRA PREMIUM 30-Second Ad Generator
============================================================
Full pipeline:
  1. Ultra-detailed image generation (Pollinations AI / Flux)
  2. Pillow post-processing: color grade, vignette, sharpening
  3. Premium text overlays with brand colors + typography
  4. Cinematic Ken Burns video clips per scene
  5. AriaNeural professional voiceover (edge-tts)
  6. SRT subtitle generation
  7. xfade cross-dissolve transitions between clips
  8. Cinematic FFmpeg color grade (orange/teal split-tone)
  9. Multi-format export: 16:9 · 9:16 · 1:1
============================================================
"""

import io
import json
import sys
import time
import subprocess
import shutil
import asyncio
import requests
from pathlib import Path
from PIL import (
    Image, ImageDraw, ImageFont,
    ImageEnhance, ImageFilter, ImageOps
)

# ── Windows UTF-8 fix ────────────────────────────────────────────────
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths ────────────────────────────────────────────────────────────
BASE   = Path(__file__).parent
OUT    = BASE / "output"
IMGS   = OUT  / "scene_images"
CLIPS  = OUT  / "scene_clips"
VOICE  = OUT  / "voice"
DEMO   = BASE / "demo"

for d in [OUT, IMGS, CLIPS, VOICE, DEMO]:
    d.mkdir(parents=True, exist_ok=True)

# ── FFmpeg ───────────────────────────────────────────────────────────
_FF_DIR = Path(
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1-full_build\bin"
)
FFMPEG  = str(_FF_DIR / "ffmpeg.exe")
FFPROBE = str(_FF_DIR / "ffprobe.exe")

# ── Brand palette ────────────────────────────────────────────────────
ORANGE    = (255, 107,  53)   # #FF6B35
DARK_BLUE = ( 45,  49,  66)   # #2D3142
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)

# ── Windows font paths ───────────────────────────────────────────────
FONT_DIR  = Path("C:/Windows/Fonts")
FONT_BOLD = FONT_DIR / "arialbd.ttf"
FONT_REG  = FONT_DIR / "arial.ttf"
FONT_ITAL = FONT_DIR / "ariali.ttf"

# ── AutoMail Script ──────────────────────────────────────────────────
SCRIPT = {
    "product_name": "AutoMail",
    "tagline": "Write Less. Connect More. Grow Faster.",
    "total_duration_seconds": 30,
    "scenes": [
        {
            "scene_number": 1,
            "label": "HOOK",
            "duration_seconds": 5,
            "voiceover": "You built something great. But no one's opening your emails.",
            "on_screen_text": "Your emails go unread.",
            "effect": "zoom_in",
        },
        {
            "scene_number": 2,
            "label": "SOLUTION",
            "duration_seconds": 9,
            "voiceover": (
                "AutoMail uses AI to write personalized campaigns "
                "that actually get read — in minutes."
            ),
            "on_screen_text": "AI emails. Written for you.",
            "effect": "pan_right",
        },
        {
            "scene_number": 3,
            "label": "BENEFITS",
            "duration_seconds": 11,
            "voiceover": (
                "Three times higher open rates. Five hours saved every week. "
                "Real results — zero writing skills needed."
            ),
            "on_screen_text": "3x opens. 5hrs saved. Zero effort.",
            "effect": "zoom_out",
        },
        {
            "scene_number": 4,
            "label": "CTA",
            "duration_seconds": 5,
            "voiceover": "Start free today. Your next campaign writes itself.",
            "on_screen_text": "Start Free. AutoMail.ai",
            "effect": "slow_zoom_in",
        },
    ],
}

# ── Ultra-Premium Cinematic Image Prompts ────────────────────────────
ULTRA_PROMPTS = [
    # Scene 1 – HOOK: exhausted entrepreneur at midnight
    (
        "cinematic close-up portrait of exhausted female entrepreneur in her early 30s "
        "sitting alone at a cluttered dark wooden desk at midnight, one hand pressed to "
        "forehead in despair, laptop screen casting cold blue light on her tired weary "
        "face showing harsh email analytics dashboard with a brutal 9 percent open rate "
        "highlighted in red, crumpled papers scattered around, half-empty coffee mug, "
        "phone with silenced notification pings, only light source is laptop screen "
        "creating dramatic cold blue shadows and rim light, dark moody home office "
        "background completely blurred, 85mm portrait lens bokeh, extreme shallow depth "
        "of field, film grain cinematic texture, deep shadow contrast, ultra realistic "
        "commercial photography, 8K resolution, award winning portrait, Adobe Lightroom "
        "color grade, professional advertising quality"
    ),
    # Scene 2 – SOLUTION: discovery moment with AutoMail
    (
        "cinematic medium shot of confident young businesswoman in her 30s leaning "
        "forward with an expression of pure amazement and relief at a sleek modern desk, "
        "MacBook Pro screen displaying a stunning dark navy email marketing dashboard "
        "with vibrant glowing orange UI buttons and AI copywriting animation streaming "
        "live text onto the screen, large floor-to-ceiling office windows behind her "
        "with warm golden late-afternoon sunlight creating a beautiful rim light halo "
        "around her silhouette, lush green plants and minimalist white shelves softly "
        "blurred in background, orange screen glow reflecting warmly on her amazed face, "
        "shallow depth of field 50mm lens, cinematic color grade warm orange shadows, "
        "ultra realistic lifestyle commercial photography, 8K sharp focus, premium "
        "advertising quality, perfect exposure, professional studio grade"
    ),
    # Scene 3 – BENEFITS: team celebration over results
    (
        "cinematic lifestyle photography of three diverse jubilant business owners "
        "celebrating around a modern standing desk in a bright contemporary office, "
        "laptop screen prominently showing AutoMail analytics dashboard with a dramatic "
        "upward spike email open-rate graph labeled 3x in bold orange text, one person "
        "pointing excitedly at the glowing screen, others raising fists in triumph with "
        "huge smiles, professional business casual attire, massive floor-to-ceiling "
        "windows with blurred city skyline golden hour bokeh, warm amber studio key "
        "light with orange rim lighting, medium shot with slight shallow depth of field, "
        "ultra realistic commercial photography, cinematic orange-teal color grade, "
        "8K sharp focus, premium advertising quality, motion energy captured, "
        "editorial lifestyle brand photography"
    ),
    # Scene 4 – CTA: premium brand hero shot
    (
        "cinematic premium product hero shot, slim MacBook Pro open on pristine white "
        "marble desk, screen displaying sleek AutoMail app interface in deep navy with "
        "a large pulsing glowing orange call-to-action button reading Start Free in "
        "clean sans-serif font, small floating email envelope icons and subtle orange "
        "light particles drifting around the laptop in zero-gravity, deep black "
        "gradient studio background with cool dark blue ambient glow behind product, "
        "single dramatic overhead spotlight creating perfect reflections on marble "
        "surface, symmetrical composition, premium advertising product photography, "
        "Apple-style minimalist aesthetic, ultra realistic, 8K resolution, razor sharp "
        "focus on screen, luxury brand identity hero shot, commercial studio lighting"
    ),
]

# ── Scene-specific FFmpeg vf strings ────────────────────────────────
def get_vf(effect: str, duration: int) -> str:
    fps   = 24
    total = duration * fps
    if effect == "zoom_in":
        return (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            f"zoompan=z='min(zoom+0.0015,1.12)':x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={fps}"
        )
    elif effect == "zoom_out":
        return (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            f"zoompan=z='if(eq(on,1),1.15,max(zoom-0.0012,1.0))'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={fps}"
        )
    elif effect == "pan_right":
        return (
            "scale=2200:1237:force_original_aspect_ratio=increase,"
            "crop=1920:1080:'(iw-1920)*t/" + str(duration * 1.5) + "':0"
        )
    elif effect == "slow_zoom_in":
        return (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            f"zoompan=z='min(zoom+0.001,1.06)':x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={fps}"
        )
    else:
        return "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"


# ════════════════════════════════════════════════════════════════════
# STEP 1 — Generate Images
# ════════════════════════════════════════════════════════════════════

def generate_image(prompt: str, path: Path, scene: int, seed: int = 0) -> bool:
    """Download image from Pollinations AI Flux model."""
    quality_suffix = (
        ", masterpiece, best quality, highly detailed, ultra sharp, "
        "professional lighting, commercial photography, photorealistic"
    )
    full_prompt = prompt + quality_suffix

    seeds = [seed, seed + 77, seed + 137, seed + 333, seed + 999]
    for attempt, s in enumerate(seeds):
        try:
            url = (
                "https://image.pollinations.ai/prompt/"
                + requests.utils.quote(full_prompt)
                + f"?width=1280&height=720&seed={s}&model=flux&nologo=true"
            )
            print(f"   [IMG] Scene {scene} attempt {attempt+1}/5 (seed={s})")
            resp = requests.get(url, timeout=180)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                img.save(str(path), "PNG")
                print(f"   [OK]  Saved raw: {path.name}")
                return True
            print(f"   [WARN] HTTP {resp.status_code}")
        except Exception as e:
            print(f"   [ERR] {e}")
        time.sleep(8)
    return False


# ════════════════════════════════════════════════════════════════════
# STEP 2 — Post-process Images (enhance + vignette + color grade)
# ════════════════════════════════════════════════════════════════════

def apply_vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    """Add a smooth cinematic vignette."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    for i in range(min(w, h) // 2):
        alpha = int(255 * (i / (min(w, h) / 2)) ** 1.8)
        draw.ellipse(
            [i, i * h // w, w - i, h - i * h // w],
            fill=min(255, alpha)
        )
    vignette = Image.new("RGB", (w, h), (0, 0, 0))
    img     = img.convert("RGB")
    result  = Image.composite(img, vignette, mask)
    return Image.blend(img, result, strength)


def cinematic_grade(img: Image.Image) -> Image.Image:
    """Apply subtle orange-shadow / cool-highlight cinematic grade."""
    import numpy as np

    arr   = np.array(img, dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # Lift shadows slightly orange
    shadows = 1.0 - np.clip(r * 1.5, 0, 1)
    r  = r + shadows * 0.04
    g  = g + shadows * 0.015
    b  = b - shadows * 0.01

    # Cool down highlights slightly (teal)
    highlights = np.clip((r + g + b) / 3.0 - 0.65, 0, 1)
    r  = r - highlights * 0.015
    g  = g + highlights * 0.005
    b  = b + highlights * 0.02

    arr = np.stack([r, g, b], axis=-1)
    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def enhance_image(img: Image.Image) -> Image.Image:
    """Full post-processing pipeline for one image."""
    # Sharpness
    img = ImageEnhance.Sharpness(img).enhance(1.6)
    # Slight unsharp mask for crispness
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=180, threshold=2))
    # Contrast boost
    img = ImageEnhance.Contrast(img).enhance(1.12)
    # Vibrance (subtle saturation)
    img = ImageEnhance.Color(img).enhance(1.08)
    # Brightness fine-tune
    img = ImageEnhance.Brightness(img).enhance(1.03)
    # Cinematic color grade
    try:
        img = cinematic_grade(img)
    except ImportError:
        pass  # numpy optional
    # Vignette
    img = apply_vignette(img, strength=0.45)
    return img


# ════════════════════════════════════════════════════════════════════
# STEP 3 — Premium Text Overlays
# ════════════════════════════════════════════════════════════════════

def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        return ImageFont.load_default()


def add_premium_overlay(
    img: Image.Image,
    on_screen_text: str,
    label: str,
    scene_num: int,
    total_scenes: int = 4,
    is_cta: bool = False,
) -> Image.Image:
    """
    Draw premium text overlay:
      - Orange accent bar
      - On-screen headline text (centered, bold white)
      - Scene label badge (top-left)
      - Tagline bottom right
    """
    w, h   = img.size
    img    = img.convert("RGBA")
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # ── Bottom gradient bar ──────────────────────────────────────────
    bar_h = 220
    for y in range(bar_h):
        t     = y / bar_h
        alpha = int(210 * (1.0 - t) ** 1.6)
        draw.rectangle(
            [(0, h - bar_h + y), (w, h - bar_h + y + 1)],
            fill=(0, 0, 0, alpha),
        )

    # ── Orange accent line (4px) ─────────────────────────────────────
    draw.rectangle(
        [(0, h - bar_h - 4), (w, h - bar_h)],
        fill=(*ORANGE, 255),
    )

    # ── On-screen headline ───────────────────────────────────────────
    if is_cta:
        font_size = 88
        text_y_frac = 0.82
    else:
        font_size = 72
        text_y_frac = 0.84

    font_h = load_font(FONT_BOLD, font_size)

    # Measure
    bbox   = draw.textbbox((0, 0), on_screen_text, font=font_h)
    tw     = bbox[2] - bbox[0]
    th     = bbox[3] - bbox[1]
    tx     = (w - tw) // 2
    ty     = int(h * text_y_frac)

    # Drop shadow
    for ox, oy in [(-3, 3), (3, 3), (0, 4), (-2, 2), (2, 2)]:
        draw.text((tx + ox, ty + oy), on_screen_text, font=font_h, fill=(0, 0, 0, 160))

    # Orange highlight under text (word underline for CTA only)
    if is_cta:
        draw.rectangle(
            [(tx - 20, ty + th + 6), (tx + tw + 20, ty + th + 14)],
            fill=(*ORANGE, 220),
        )

    # Main white text
    draw.text((tx, ty), on_screen_text, font=font_h, fill=(*WHITE, 255))

    # ── Scene label badge (top-left) ─────────────────────────────────
    badge_font = load_font(FONT_BOLD, 26)
    badge_text = f"  {label}  "
    bb         = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw         = bb[2] - bb[0] + 8
    bh         = bb[3] - bb[1] + 8
    draw.rounded_rectangle(
        [(40, 40), (40 + bw, 40 + bh)],
        radius=6,
        fill=(*ORANGE, 220),
    )
    draw.text((44, 44), badge_text, font=badge_font, fill=(*WHITE, 255))

    # ── Product name (top-right) ─────────────────────────────────────
    brand_font = load_font(FONT_BOLD, 32)
    brand_text = "AutoMail"
    bb2        = draw.textbbox((0, 0), brand_text, font=brand_font)
    bw2        = bb2[2] - bb2[0]
    draw.text(
        (w - bw2 - 44, 46),
        brand_text,
        font=brand_font,
        fill=(*ORANGE, 230),
    )

    # ── Progress dots (bottom-right) ────────────────────────────────
    dot_r   = 6
    dot_gap = 22
    dot_y   = h - 40
    start_x = w - (total_scenes * dot_gap) - 36
    for i in range(total_scenes):
        cx = start_x + i * dot_gap
        if i < scene_num:
            draw.ellipse([(cx - dot_r, dot_y - dot_r), (cx + dot_r, dot_y + dot_r)],
                         fill=(*ORANGE, 230))
        else:
            draw.ellipse([(cx - dot_r, dot_y - dot_r), (cx + dot_r, dot_y + dot_r)],
                         outline=(*WHITE, 140), width=2)

    result = Image.alpha_composite(img, canvas).convert("RGB")
    return result


# ════════════════════════════════════════════════════════════════════
# STEP 4 — Ken Burns Video Clips
# ════════════════════════════════════════════════════════════════════

def create_ken_burns_clip(
    img_path: Path,
    out_path: Path,
    duration: int,
    effect: str,
    fps: int = 24,
) -> bool:
    vf  = get_vf(effect, duration)
    # Add fade-in (0.4s) and fade-out (0.4s) per clip
    fin  = int(fps * 0.4)
    fout = int(fps * 0.4)
    fout_start = duration * fps - fout
    vf += (
        f",fade=type=in:st=0:d={fin/fps}:color=black"
        f",fade=type=out:st={fout_start/fps}:d={fout/fps}:color=black"
    )

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", vf,
        "-t", str(duration),
        "-r", str(fps),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "16",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   [FFmpeg ERR] {result.stderr[-300:]}")
    return result.returncode == 0


# ════════════════════════════════════════════════════════════════════
# STEP 5 — Voiceover + Subtitles
# ════════════════════════════════════════════════════════════════════

async def _tts(text: str, voice: str, out: Path):
    import edge_tts
    comm = edge_tts.Communicate(text, voice)
    await comm.save(str(out))


def generate_voiceover(scenes: list) -> tuple:
    """Generate AriaNeural voiceover + SRT per scene, then concat."""
    import edge_tts

    voice = "en-US-AriaNeural"
    print(f"   [VOICE] Using {voice}")

    files = []
    for i, sc in enumerate(scenes):
        out = VOICE / f"scene_{i+1}.mp3"
        print(f"   [TTS] Scene {i+1}: {sc['voiceover'][:55]}...")
        asyncio.run(_tts(sc["voiceover"], voice, out))
        files.append(out)

    # Concat list
    list_f = VOICE / "files.txt"
    with open(list_f, "w") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")

    merged = VOICE / "voiceover.mp3"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c", "copy", str(merged)],
        capture_output=True,
    )
    print(f"   [OK]  Merged voiceover: {merged.name}")

    # SRT
    srt = VOICE / "subtitles.srt"
    t   = 0.0
    with open(srt, "w", encoding="utf-8") as f:
        for i, sc in enumerate(scenes):
            end = t + sc["duration_seconds"]
            def fmt(x):
                ms = int((x % 1) * 1000)
                s  = int(x) % 60
                m  = int(x) // 60 % 60
                h  = int(x) // 3600
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            f.write(f"{i+1}\n{fmt(t)} --> {fmt(end)}\n{sc['on_screen_text']}\n\n")
            t = end
    print(f"   [OK]  Subtitles: {srt.name}")
    return merged, srt


# ════════════════════════════════════════════════════════════════════
# STEP 6 — Assemble with xfade transitions
# ════════════════════════════════════════════════════════════════════

def assemble_with_transitions(clips: list, audio: Path, output: Path) -> bool:
    """
    Concat 4 clips using xfade cross-dissolve transitions (0.4s each),
    then mix in voiceover.
    """
    FADE = 0.4
    scenes = SCRIPT["scenes"]

    # Build filter_complex for 4 clips with chained xfade
    #   offset_n = sum(durations[0..n-1]) - n * FADE
    offsets = []
    cumul   = 0.0
    for i, sc in enumerate(scenes[:-1]):
        cumul += sc["duration_seconds"]
        offsets.append(cumul - (i + 1) * FADE)

    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]

    fc  = (
        f"[0][1]xfade=transition=fade:duration={FADE}:offset={offsets[0]:.3f}[v01];"
        f"[v01][2]xfade=transition=fade:duration={FADE}:offset={offsets[1]:.3f}[v012];"
        f"[v012][3]xfade=transition=fade:duration={FADE}:offset={offsets[2]:.3f}[vfinal]"
    )

    merged = output.parent / "_merged_transitions.mp4"
    cmd = (
        [FFMPEG, "-y"]
        + inputs
        + ["-filter_complex", fc, "-map", "[vfinal]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "medium", "-crf", "16",
           str(merged)]
    )
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   [WARN] xfade failed, falling back to simple concat")
        print(f"   {r.stderr[-400:]}")
        return _fallback_concat(clips, audio, output)

    print("   [OK]  xfade transitions applied")

    # Measure merged video duration
    r_dur = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json",
         "-show_format", str(merged)],
        capture_output=True, text=True,
    )
    import json as _json
    vid_dur = float(_json.loads(r_dur.stdout)["format"]["duration"])
    print(f"   [INFO] Video duration: {vid_dur:.3f}s")

    # Add voiceover — pad audio with silence so it fills the full video
    with_audio = output.parent / "_with_audio.mp4"
    subprocess.run(
        [FFMPEG, "-y",
         "-i", str(merged), "-i", str(audio),
         "-filter_complex",
         f"[1:a]apad=whole_dur={vid_dur}[aout]",
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(vid_dur),
         str(with_audio)],
        capture_output=True,
    )
    print("   [OK]  Audio mixed (padded to video duration)")

    # Cinematic color grade via FFmpeg curves + vignette
    grade = (
        "curves="
        "r='0/0 0.25/0.22 0.75/0.80 1/0.96':"
        "g='0/0 0.25/0.23 0.75/0.77 1/0.95':"
        "b='0/0.04 0.25/0.26 0.75/0.73 1/0.92',"
        "vignette=PI/5"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", str(with_audio),
        "-vf", grade,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "16",
        "-c:a", "copy",
        str(output),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   [WARN] Color grade failed, using ungraded")
        shutil.copy(str(with_audio), str(output))
    else:
        print("   [OK]  Cinematic color grade applied")

    return True


def _fallback_concat(clips: list, audio: Path, output: Path) -> bool:
    """Simple concat fallback if xfade fails."""
    list_f = OUT / "_clips.txt"
    with open(list_f, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    merged = OUT / "_merged_simple.mp4"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c:v", "libx264", "-pix_fmt", "yuv420p",
         str(merged)],
        capture_output=True,
    )
    subprocess.run(
        [FFMPEG, "-y",
         "-i", str(merged), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(output)],
        capture_output=True,
    )
    print("   [OK]  Fallback concat done")
    return True


# ════════════════════════════════════════════════════════════════════
# STEP 7 — Multi-format Export
# ════════════════════════════════════════════════════════════════════

def export_formats(src: Path):
    formats = {
        "16x9": (1920, 1080),
        "9x16": (1080, 1920),
        "1x1":  (1080, 1080),
    }
    for label, (w, h) in formats.items():
        out = OUT / f"automail_premium_{label}.mp4"
        vf  = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
        )
        subprocess.run(
            [FFMPEG, "-y", "-i", str(src),
             "-vf", vf,
             "-c:v", "libx264", "-crf", "18", "-preset", "medium",
             "-c:a", "aac", "-b:a", "192k",
             str(out)],
            capture_output=True,
        )
        size_mb = out.stat().st_size / 1_048_576 if out.exists() else 0
        print(f"   [OK]  {label}: {out.name} ({size_mb:.1f} MB)")


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

def main():
    banner = "=" * 64
    print(banner)
    print("  AutoMail ULTRA PREMIUM Ad Generator — 30 Seconds")
    print(banner)

    scenes = SCRIPT["scenes"]
    total  = sum(s["duration_seconds"] for s in scenes)
    print(f"\n[INFO] Scenes: {len(scenes)} | Total: {total}s\n")

    # ── STEP 1+2+3: Images ──────────────────────────────────────────
    print(banner)
    print("  STEP 1/4 — Generating & Processing Images")
    print(banner)

    processed_imgs = []
    clips          = []

    for i, (scene, prompt) in enumerate(zip(scenes, ULTRA_PROMPTS)):
        n    = scene["scene_number"]
        dur  = scene["duration_seconds"]
        fx   = scene["effect"]
        raw  = IMGS / f"automail_raw_{n}.png"
        proc = IMGS / f"automail_proc_{n}.png"
        clip = CLIPS / f"automail_clip_{n}.mp4"

        print(f"\n[Scene {n}] {scene['label']} ({dur}s) — {fx}")

        # Generate image
        if not raw.exists():
            ok = generate_image(prompt, raw, n, seed=n * 42)
            if not ok:
                print(f"   [FATAL] Image gen failed for scene {n}")
                sys.exit(1)
        else:
            print(f"   [SKIP] Raw image exists: {raw.name}")

        # Post-process
        print(f"   [POST] Enhancing + color grade + vignette...")
        img = Image.open(str(raw)).convert("RGB")
        img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
        img = enhance_image(img)
        img = add_premium_overlay(
            img,
            on_screen_text=scene["on_screen_text"],
            label=scene["label"],
            scene_num=n,
            total_scenes=len(scenes),
            is_cta=(scene["label"] == "CTA"),
        )
        img.save(str(proc), "PNG")
        print(f"   [OK]  Processed: {proc.name}")
        processed_imgs.append(proc)

        # Ken Burns clip
        print(f"   [CLIP] Creating {dur}s Ken Burns clip ({fx})...")
        ok = create_ken_burns_clip(proc, clip, dur, fx)
        if ok:
            print(f"   [OK]  Clip: {clip.name}")
            clips.append(clip)
        else:
            print(f"   [ERR] Clip failed for scene {n}")
            sys.exit(1)

    # ── STEP 5: Voiceover ───────────────────────────────────────────
    print(f"\n{banner}")
    print("  STEP 2/4 — Generating AriaNeural Voiceover")
    print(banner)

    audio, srt = generate_voiceover(scenes)

    # ── STEP 6: Assemble ────────────────────────────────────────────
    print(f"\n{banner}")
    print("  STEP 3/4 — Assembling with xfade Transitions")
    print(banner)

    final = OUT / "automail_final.mp4"
    ok = assemble_with_transitions(clips, audio, final)
    if not ok or not final.exists():
        print("[FATAL] Assembly failed")
        sys.exit(1)

    size_mb = final.stat().st_size / 1_048_576
    print(f"\n   [OK]  Master: {final.name} ({size_mb:.1f} MB)")

    # ── STEP 7: Multi-format export ─────────────────────────────────
    print(f"\n{banner}")
    print("  STEP 4/4 — Exporting Multi-Format Versions")
    print(banner)
    export_formats(final)

    # Copy to demo
    demo = DEMO / "automail_ultra_premium.mp4"
    shutil.copy(str(final), str(demo))

    print(f"\n{banner}")
    print("  ULTRA PREMIUM VIDEO COMPLETE!")
    print(banner)
    print(f"""
  Master (16:9)  : output/automail_final.mp4
  Instagram Reel : output/automail_premium_9x16.mp4
  Square Post    : output/automail_premium_1x1.mp4
  Widescreen     : output/automail_premium_16x9.mp4
  Demo copy      : demo/automail_ultra_premium.mp4
""")


if __name__ == "__main__":
    main()
