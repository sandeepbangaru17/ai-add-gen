"""
AutoMail ULTRA PREMIUM v2 — Complete Rebuild
================================================
Fixes from v1:
  [FIX 1] PIL frame-by-frame Ken Burns → LANCZOS per frame = zero blur
  [FIX 2] Fade-to-black transitions → eliminates all text overlap
  [FIX 3] Scene-specific premium text layouts (not just a bottom bar)
  [FIX 4] Larger source images (1920x1080 from Pollinations)
  [FIX 5] No FFmpeg subtitle burning — text lives in the image frames only
  [FIX 6] Per-scene unique visual design for maximum impact
================================================
"""

import io, json, sys, time, subprocess, shutil, asyncio, requests, struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Directories ──────────────────────────────────────────────────────
BASE  = Path(__file__).parent
OUT   = BASE / "output"
IMGS  = OUT  / "scene_images"
CLIPS = OUT  / "scene_clips"
VOICE = OUT  / "voice"
DEMO  = BASE / "demo"
for d in [OUT, IMGS, CLIPS, VOICE, DEMO]:
    d.mkdir(parents=True, exist_ok=True)

# ── FFmpeg ───────────────────────────────────────────────────────────
_FF = (
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1-full_build\bin"
)
FFMPEG  = str(Path(_FF) / "ffmpeg.exe")
FFPROBE = str(Path(_FF) / "ffprobe.exe")

# ── Brand ────────────────────────────────────────────────────────────
ORANGE    = (255, 107,  53)
DARK_BLUE = ( 45,  49,  66)
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
GRAY      = (180, 180, 180)
OUT_W, OUT_H = 1920, 1080
FPS = 24

# ── Fonts ────────────────────────────────────────────────────────────
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

SEGOE_BLACK  = "C:/Windows/Fonts/seguibl.ttf"
SEGOE_BOLD   = "C:/Windows/Fonts/segoeuib.ttf"
SEGOE_REG    = "C:/Windows/Fonts/segoeui.ttf"
ARIAL_BOLD   = "C:/Windows/Fonts/arialbd.ttf"

# ════════════════════════════════════════════════════════════════════
# SCRIPT
# ════════════════════════════════════════════════════════════════════
SCRIPT = {
    "product_name": "AutoMail",
    "tagline": "Write Less. Connect More. Grow Faster.",
    "total_duration_seconds": 30,
    "scenes": [
        {
            "scene_number": 1, "label": "HOOK", "duration_seconds": 5, "effect": "zoom_in",
            "voiceover": "You built something great. But no one's opening your emails.",
            "on_screen_text": "Your emails go unread.",
        },
        {
            "scene_number": 2, "label": "SOLUTION", "duration_seconds": 9, "effect": "pan_right",
            "voiceover": "AutoMail uses AI to write personalized campaigns that actually get read — in minutes.",
            "on_screen_text": "AI emails. Written for you.",
        },
        {
            "scene_number": 3, "label": "BENEFITS", "duration_seconds": 11, "effect": "zoom_out",
            "voiceover": "Three times higher open rates. Five hours saved every week. Real results — zero writing skills needed.",
            "on_screen_text": "3x opens. 5hrs saved. Zero effort.",
        },
        {
            "scene_number": 4, "label": "CTA", "duration_seconds": 5, "effect": "slow_zoom_in",
            "voiceover": "Start free today. Your next campaign writes itself.",
            "on_screen_text": "Start Free. AutoMail.ai",
        },
    ],
}

# ════════════════════════════════════════════════════════════════════
# ULTRA-PREMIUM IMAGE PROMPTS  (fresh seeds, higher res)
# ════════════════════════════════════════════════════════════════════
PROMPTS = [
    # Scene 1 — HOOK
    (
        "cinematic close-up portrait photograph of exhausted young businesswoman "
        "at cluttered wooden desk at midnight, one hand on forehead, eyes staring "
        "at laptop screen glowing cold blue light, laptop shows email dashboard "
        "with 9% open rate in large red text, scattered papers and cold coffee mug "
        "on desk, dark moody room, blue light as only source casting deep shadows, "
        "shallow depth of field 85mm, film grain, ultra realistic, 8K commercial "
        "photography, photorealistic, editorial quality"
    ),
    # Scene 2 — SOLUTION
    (
        "cinematic medium shot of confident professional woman in her 30s smiling "
        "with genuine amazement at her laptop, modern bright open-plan office, "
        "laptop screen displays clean dark navy email marketing interface with "
        "vibrant orange glowing buttons and AI writing animation, golden afternoon "
        "sunlight streaming through floor-to-ceiling windows creating warm rim "
        "light around her, soft bokeh of green plants and white shelves in "
        "background, orange screen glow on face, shallow depth of field, "
        "ultra realistic 8K commercial photography, professional advertising"
    ),
    # Scene 3 — BENEFITS
    (
        "cinematic wide shot of three diverse business professionals celebrating "
        "in a bright modern penthouse office, laptop on standing desk shows "
        "email analytics with dramatic upward spike graph in orange labeled 3x, "
        "one person pointing at screen enthusiastically, others with arms raised "
        "in triumph, massive city skyline with golden sunset visible through "
        "floor-to-ceiling glass walls, warm amber studio lighting, "
        "medium shot shallow depth of field, ultra realistic 8K photography, "
        "premium commercial advertising, editorial lifestyle"
    ),
    # Scene 4 — CTA
    (
        "cinematic premium product photography, sleek open laptop on pristine "
        "polished white marble surface, screen shows clean dark navy app interface "
        "with large glowing orange button, floating glowing email envelope icons "
        "and soft orange light particles drifting in air around the laptop, "
        "deep black studio background with soft blue gradient glow, "
        "single overhead dramatic spotlight creating perfect marble reflection, "
        "perfect centered symmetrical composition, Apple-style luxury product shot, "
        "ultra realistic 8K sharp focus commercial photography, premium brand hero"
    ),
]

# ════════════════════════════════════════════════════════════════════
# STEP 1 — Image Generation
# ════════════════════════════════════════════════════════════════════

def generate_image(prompt: str, path: Path, scene: int, seed: int = 0) -> bool:
    quality = (
        ", masterpiece, best quality, hyper detailed, ultra sharp focus, "
        "professional studio lighting, photorealistic, commercial grade"
    )
    full = prompt + quality
    seeds = [seed, seed + 500, seed + 1000, seed + 1500, seed + 2000]
    for attempt, s in enumerate(seeds):
        try:
            url = (
                "https://image.pollinations.ai/prompt/"
                + requests.utils.quote(full)
                + f"?width=1920&height=1080&seed={s}&model=flux&nologo=true"
            )
            print(f"   [IMG] Scene {scene} attempt {attempt+1}/5 (seed={s})")
            r = requests.get(url, timeout=180)
            if r.status_code == 200:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                img.save(str(path), "PNG")
                print(f"   [OK]  {path.name}  {img.size}")
                return True
            print(f"   [WARN] HTTP {r.status_code}")
        except Exception as e:
            print(f"   [ERR] {e}")
        time.sleep(8)
    return False


# ════════════════════════════════════════════════════════════════════
# STEP 2 — Image Post-Processing  (no text yet)
# ════════════════════════════════════════════════════════════════════

def _vignette(img: Image.Image, strength: float = 0.50) -> Image.Image:
    w, h = img.size
    from PIL import ImageDraw as ID
    mask  = Image.new("L", (w, h), 255)
    mdraw = ID.Draw(mask)
    steps = 120
    for i in range(steps):
        ratio  = i / steps
        alpha  = int(255 * (1.0 - ratio ** 1.6))
        shrink = ratio * min(w, h) * 0.55
        mdraw.ellipse(
            [shrink, shrink * h / w, w - shrink, h - shrink * h / w],
            fill=alpha,
        )
    black = Image.new("RGB", (w, h), (0, 0, 0))
    result = Image.composite(img, black, mask)
    return Image.blend(img, result, strength)


def _cinematic_grade(img: Image.Image) -> Image.Image:
    try:
        import numpy as np
        a = np.array(img, dtype=np.float32) / 255.0
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        lum = r * 0.299 + g * 0.587 + b * 0.114
        # Warm orange lift in shadows
        shadow = np.clip(1.0 - lum * 2, 0, 1)
        r = r + shadow * 0.06
        g = g + shadow * 0.02
        b = b - shadow * 0.02
        # Cool teal push in highlights
        hi = np.clip(lum * 2 - 1.0, 0, 1)
        r = r - hi * 0.02
        b = b + hi * 0.025
        a = np.stack([np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)], -1)
        return Image.fromarray((a * 255).astype("uint8"), "RGB")
    except ImportError:
        return img


def postprocess(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Sharpness(img).enhance(1.7)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=160, threshold=3))
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = ImageEnhance.Color(img).enhance(1.06)
    img = _cinematic_grade(img)
    img = _vignette(img, 0.40)
    return img


# ════════════════════════════════════════════════════════════════════
# STEP 3 — Premium Scene-Specific Text Overlays
# ════════════════════════════════════════════════════════════════════

def _draw_text_shadow(draw, pos, text, fnt, shadow_col=(0,0,0,180), offset=4):
    for dx, dy in [(-offset,offset),(offset,offset),(0,offset),(offset,-offset),(-offset,-offset)]:
        draw.text((pos[0]+dx, pos[1]+dy), text, font=fnt, fill=shadow_col)


def overlay_scene1_hook(img: Image.Image, scene: dict) -> Image.Image:
    """
    HOOK: Dark moody overlay. Pain text — large, stark, centered vertically.
    """
    W, H = img.size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # Dark center overlay (not full frame, more cinematic letter-box feel)
    draw.rectangle([(0, 0), (W, H)], fill=(0, 0, 0, 100))

    # Top orange micro-line accent
    draw.rectangle([(0, 0), (W, 5)], fill=(*ORANGE, 255))

    # Main pain text — centred, upper-mid
    fnt_big  = font(SEGOE_BLACK, 90)
    fnt_sub  = font(SEGOE_BOLD, 46)

    line1 = "You built something great."
    line2 = "But no one's opening your emails."

    # line1
    bb1 = draw.textbbox((0,0), line1, font=fnt_sub)
    x1  = (W - (bb1[2]-bb1[0])) // 2
    y1  = int(H * 0.36)
    _draw_text_shadow(draw, (x1, y1), line1, fnt_sub)
    draw.text((x1, y1), line1, font=fnt_sub, fill=(*GRAY, 230))

    # line2
    bb2 = draw.textbbox((0,0), line2, font=fnt_big)
    x2  = (W - (bb2[2]-bb2[0])) // 2
    y2  = y1 + (bb1[3]-bb1[1]) + 30
    _draw_text_shadow(draw, (x2, y2), line2, fnt_big)
    draw.text((x2, y2), line2, font=fnt_big, fill=(*WHITE, 255))

    # Orange underline under line2
    uw = bb2[2]-bb2[0]
    draw.rectangle([(x2, y2 + (bb2[3]-bb2[1]) + 12), (x2 + uw, y2 + (bb2[3]-bb2[1]) + 19)],
                   fill=(*ORANGE, 230))

    # Bottom brand bar
    bar_h = 90
    draw.rectangle([(0, H - bar_h), (W, H)], fill=(0, 0, 0, 200))
    brand_fnt  = font(SEGOE_BOLD, 36)
    brand_text = "AutoMail  ·  Write Less. Connect More. Grow Faster."
    bb_br      = draw.textbbox((0,0), brand_text, font=brand_fnt)
    bx         = (W - (bb_br[2]-bb_br[0])) // 2
    by         = H - bar_h + (bar_h - (bb_br[3]-bb_br[1])) // 2
    draw.text((bx, by), brand_text, font=brand_fnt, fill=(*ORANGE, 200))

    result = Image.alpha_composite(img.convert("RGBA"), canvas)
    return result.convert("RGB")


def overlay_scene2_solution(img: Image.Image, scene: dict) -> Image.Image:
    """
    SOLUTION: Clean reveal. 'AI emails.' huge orange. 'Written for you.' white.
    AutoMail logo top-right corner.
    """
    W, H = img.size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # Bottom gradient (tall)
    bar_h = 340
    for y in range(bar_h):
        t = y / bar_h
        alpha = int(230 * (1.0 - t) ** 1.4)
        draw.rectangle([(0, H-bar_h+y), (W, H-bar_h+y+1)], fill=(10, 12, 20, alpha))

    # Orange accent line above bar
    draw.rectangle([(0, H-bar_h-5), (W, H-bar_h)], fill=(*ORANGE, 255))

    fnt_huge = font(SEGOE_BLACK, 110)
    fnt_big  = font(SEGOE_BOLD,  68)
    fnt_tag  = font(SEGOE_BOLD,  34)

    # "AI emails." — orange
    t1 = "AI emails."
    bb1 = draw.textbbox((0,0), t1, font=fnt_huge)
    x1  = 90
    y1  = H - bar_h + 30
    _draw_text_shadow(draw, (x1, y1), t1, fnt_huge, offset=5)
    draw.text((x1, y1), t1, font=fnt_huge, fill=(*ORANGE, 255))

    # "Written for you." — white
    t2 = "Written for you."
    bb2 = draw.textbbox((0,0), t2, font=fnt_big)
    x2  = x1 + (bb1[2]-bb1[0]) + 40
    y2  = y1 + ((bb1[3]-bb1[1]) - (bb2[3]-bb2[1]))  # vertically align bottoms
    _draw_text_shadow(draw, (x2, y2), t2, fnt_big, offset=4)
    draw.text((x2, y2), t2, font=fnt_big, fill=(*WHITE, 255))

    # Tagline below
    tag  = "Powered by AutoMail AI  ·  automail.ai"
    bbt  = draw.textbbox((0,0), tag, font=fnt_tag)
    xt   = x1
    yt   = y1 + (bb1[3]-bb1[1]) + 18
    draw.text((xt, yt), tag, font=fnt_tag, fill=(*GRAY, 180))

    # Top-right logo area
    logo_fnt = font(SEGOE_BLACK, 42)
    lx, ly = W - 260, 36
    draw.rounded_rectangle([(lx-14, ly-8), (lx+220, ly+52)], radius=8,
                            fill=(0, 0, 0, 140))
    draw.text((lx, ly), "AutoMail", font=logo_fnt, fill=(*ORANGE, 255))

    result = Image.alpha_composite(img.convert("RGBA"), canvas)
    return result.convert("RGB")


def overlay_scene3_benefits(img: Image.Image, scene: dict) -> Image.Image:
    """
    BENEFITS: Three metric cards at bottom — 3x · 5hrs · Zero — each in orange.
    Full-width info bar with proof points.
    """
    W, H = img.size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # Strong dark bottom overlay
    bar_h = 300
    for y in range(bar_h):
        t = y / bar_h
        alpha = int(240 * (1.0 - t) ** 1.2)
        draw.rectangle([(0, H-bar_h+y), (W, H-bar_h+y+1)], fill=(5, 7, 15, alpha))

    # Orange top accent bar
    draw.rectangle([(0, H-bar_h-6), (W, H-bar_h)], fill=(*ORANGE, 255))

    fnt_metric = font(SEGOE_BLACK, 100)
    fnt_label  = font(SEGOE_BOLD,  36)
    fnt_desc   = font(SEGOE_REG,   30)

    METRICS = [
        ("3x",    "Higher Open Rates"),
        ("5hrs",  "Saved Every Week"),
        ("Zero",  "Writing Skills Needed"),
    ]
    card_w = W // 3
    for i, (val, desc) in enumerate(METRICS):
        cx = i * card_w + card_w // 2
        y_val  = H - bar_h + 22

        # Metric number
        bbv = draw.textbbox((0,0), val, font=fnt_metric)
        vw  = bbv[2]-bbv[0]
        _draw_text_shadow(draw, (cx - vw//2, y_val), val, fnt_metric, offset=5)
        draw.text((cx - vw//2, y_val), val, font=fnt_metric, fill=(*ORANGE, 255))

        # Description
        bbd = draw.textbbox((0,0), desc, font=fnt_label)
        dw  = bbd[2]-bbd[0]
        y_d = y_val + (bbv[3]-bbv[1]) + 10
        draw.text((cx - dw//2, y_d), desc, font=fnt_label, fill=(*WHITE, 220))

        # Divider (between cards, not after last)
        if i < 2:
            div_x = (i+1) * card_w
            draw.rectangle([(div_x-1, H-bar_h+15), (div_x+1, H-20)],
                           fill=(*ORANGE, 100))

    # Top-right AutoMail badge
    logo_fnt = font(SEGOE_BLACK, 40)
    lx, ly = W - 255, 36
    draw.rounded_rectangle([(lx-14, ly-8), (lx+216, ly+50)], radius=8,
                            fill=(0, 0, 0, 150))
    draw.text((lx, ly), "AutoMail", font=logo_fnt, fill=(*ORANGE, 255))

    result = Image.alpha_composite(img.convert("RGBA"), canvas)
    return result.convert("RGB")


def overlay_scene4_cta(img: Image.Image, scene: dict) -> Image.Image:
    """
    CTA: Centred full-screen overlay. Large AutoMail.ai. Orange CTA button.
    """
    W, H = img.size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # Deep dark overlay for contrast
    draw.rectangle([(0, 0), (W, H)], fill=(0, 0, 0, 155))

    # Orange top+bottom edge bars
    draw.rectangle([(0, 0),   (W, 6)],   fill=(*ORANGE, 255))
    draw.rectangle([(0, H-6), (W, H)],   fill=(*ORANGE, 255))

    fnt_brand   = font(SEGOE_BLACK, 100)
    fnt_tagline = font(SEGOE_BOLD,  44)
    fnt_btn     = font(SEGOE_BLACK, 60)
    fnt_sub     = font(SEGOE_BOLD,  34)

    center_y = H // 2 - 80

    # "AutoMail" — huge brand name
    brand = "AutoMail"
    bb_b  = draw.textbbox((0,0), brand, font=fnt_brand)
    bx    = (W - (bb_b[2]-bb_b[0])) // 2
    by    = center_y - (bb_b[3]-bb_b[1]) - 20
    _draw_text_shadow(draw, (bx, by), brand, fnt_brand, offset=6)
    draw.text((bx, by), brand, font=fnt_brand, fill=(*WHITE, 255))

    # Dot accent between brand and tagline
    dot_y = by + (bb_b[3]-bb_b[1]) + 10
    dot_x = W // 2 - 4
    draw.ellipse([(dot_x-4, dot_y), (dot_x+4, dot_y+8)], fill=(*ORANGE, 255))

    # Tagline
    tagline = "Write Less. Connect More. Grow Faster."
    bb_t    = draw.textbbox((0,0), tagline, font=fnt_tagline)
    tx      = (W - (bb_t[2]-bb_t[0])) // 2
    ty      = dot_y + 16
    draw.text((tx, ty), tagline, font=fnt_tagline, fill=(*GRAY, 210))

    # CTA Orange Button — rounded rectangle
    btn_text = "  START FREE TODAY  "
    bb_btn   = draw.textbbox((0,0), btn_text, font=fnt_btn)
    btn_w    = bb_btn[2]-bb_btn[0] + 60
    btn_h    = bb_btn[3]-bb_btn[1] + 32
    btn_x    = (W - btn_w) // 2
    btn_y    = ty + (bb_t[3]-bb_t[1]) + 50
    # Shadow
    draw.rounded_rectangle(
        [(btn_x+6, btn_y+6), (btn_x+btn_w+6, btn_y+btn_h+6)],
        radius=12, fill=(0, 0, 0, 140))
    # Button
    draw.rounded_rectangle(
        [(btn_x, btn_y), (btn_x+btn_w, btn_y+btn_h)],
        radius=12, fill=(*ORANGE, 255))
    # Button text
    btext_x = btn_x + (btn_w - (bb_btn[2]-bb_btn[0])) // 2
    btext_y = btn_y + (btn_h - (bb_btn[3]-bb_btn[1])) // 2
    draw.text((btext_x, btext_y), btn_text, font=fnt_btn, fill=(*WHITE, 255))

    # URL below button
    url_fnt  = font(SEGOE_BOLD, 38)
    url_text = "automail.ai"
    bb_url   = draw.textbbox((0,0), url_text, font=url_fnt)
    ux       = (W - (bb_url[2]-bb_url[0])) // 2
    uy       = btn_y + btn_h + 30
    draw.text((ux, uy), url_text, font=url_fnt, fill=(*GRAY, 200))

    result = Image.alpha_composite(img.convert("RGBA"), canvas)
    return result.convert("RGB")


OVERLAY_FN = {
    "HOOK":     overlay_scene1_hook,
    "SOLUTION": overlay_scene2_solution,
    "BENEFITS": overlay_scene3_benefits,
    "CTA":      overlay_scene4_cta,
}


# ════════════════════════════════════════════════════════════════════
# STEP 4 — PIL frame-by-frame Ken Burns (LANCZOS per frame = zero blur)
# ════════════════════════════════════════════════════════════════════

def _crop_rect(src_w: int, src_h: int, progress: float, effect: str):
    """Return (x, y, w, h) crop region in source image for a given progress."""
    if effect == "zoom_in":
        zoom = 1.0 + 0.18 * progress          # 1.0 → 1.18
    elif effect == "zoom_out":
        zoom = 1.18 - 0.18 * progress         # 1.18 → 1.0
    elif effect == "slow_zoom_in":
        zoom = 1.0 + 0.07 * progress          # 1.0 → 1.07
    else:
        zoom = 1.15                            # constant for pan

    cw = int(src_w / zoom)
    ch = int(src_h / zoom)
    cw = max(cw, OUT_W)   # never crop smaller than output
    ch = max(ch, OUT_H)

    if effect == "pan_right":
        max_x = src_w - cw
        x = int(max_x * progress)
        y = (src_h - ch) // 2
    elif effect == "pan_left":
        max_x = src_w - cw
        x = max_x - int(max_x * progress)
        y = (src_h - ch) // 2
    else:
        x = (src_w - cw) // 2
        y = (src_h - ch) // 2

    return max(0, x), max(0, y), cw, ch


def render_ken_burns_clip(base_img: Image.Image, out_path: Path,
                           duration: int, effect: str) -> bool:
    """
    Render Ken Burns frame by frame using PIL LANCZOS.
    Source image must be >= 1920x1080.
    Includes 0.35s fade-in and 0.35s fade-out.
    """
    total = duration * FPS
    fade  = int(FPS * 0.35)      # frames for each fade
    black = Image.new("RGB", (OUT_W, OUT_H), (0, 0, 0))

    # For pan effects, we need a wider source image; upscale if needed
    src = base_img.copy()
    src_w, src_h = src.size
    if effect in ("pan_right", "pan_left") and src_w < OUT_W * 1.3:
        new_w = int(OUT_W * 1.4)
        new_h = int(new_w * src_h / src_w)
        src = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
        src_w, src_h = src.size

    # For zoom effects, ensure there's enough "zoom room"
    if effect in ("zoom_in", "zoom_out") and min(src_w / OUT_W, src_h / OUT_H) < 1.25:
        new_w = int(OUT_W * 1.30)
        new_h = int(OUT_H * 1.30)
        src = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
        src_w, src_h = src.size

    print(f"   [RENDER] {out_path.name}: {total} frames @ {FPS}fps "
          f"from {src_w}x{src_h} source → {OUT_W}x{OUT_H}")

    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{OUT_W}x{OUT_H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "15",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    try:
        for i in range(total):
            progress = i / (total - 1) if total > 1 else 0
            x, y, cw, ch = _crop_rect(src_w, src_h, progress, effect)
            frame = src.crop((x, y, x + cw, y + ch))
            frame = frame.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)

            # Fade in
            if i < fade:
                frame = Image.blend(black, frame, i / fade)
            # Fade out
            elif i >= total - fade:
                frame = Image.blend(black, frame, (total - i) / fade)

            proc.stdin.write(frame.tobytes())
    finally:
        proc.stdin.close()

    proc.wait()
    if proc.returncode != 0:
        print(f"   [ERR] FFmpeg pipe exited {proc.returncode}")
        return False

    size_mb = out_path.stat().st_size / 1_048_576 if out_path.exists() else 0
    print(f"   [OK]  {out_path.name} ({size_mb:.1f} MB)")
    return True


# ════════════════════════════════════════════════════════════════════
# STEP 5 — Voiceover
# ════════════════════════════════════════════════════════════════════

async def _tts(text: str, voice: str, out: Path):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out))


def generate_voiceover(scenes: list):
    voice = "en-US-AriaNeural"
    files = []
    for i, sc in enumerate(scenes):
        out = VOICE / f"v2_scene_{i+1}.mp3"
        print(f"   [TTS] Scene {i+1}: {sc['voiceover'][:60]}...")
        asyncio.run(_tts(sc["voiceover"], voice, out))
        files.append(out)

    list_f = VOICE / "v2_files.txt"
    with open(list_f, "w") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")

    merged = VOICE / "v2_voiceover.mp3"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c", "copy", str(merged)],
        capture_output=True,
    )
    print(f"   [OK]  {merged.name}")
    return merged


# ════════════════════════════════════════════════════════════════════
# STEP 6 — Assemble (simple concat + audio pad)
# ════════════════════════════════════════════════════════════════════

def assemble(clips: list, audio: Path, output: Path) -> bool:
    # Concat list
    list_f = OUT / "v2_clips.txt"
    with open(list_f, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    merged = OUT / "v2_merged.mp4"
    r = subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "15",
         str(merged)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"   [ERR] concat: {r.stderr[-300:]}")
        return False
    print("   [OK]  Clips concatenated")

    # Get video duration
    rp = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(merged)],
        capture_output=True, text=True,
    )
    vid_dur = float(json.loads(rp.stdout)["format"]["duration"])
    print(f"   [INFO] Video duration: {vid_dur:.3f}s")

    # Mix audio — pad to video length
    with_audio = OUT / "v2_with_audio.mp4"
    r2 = subprocess.run(
        [FFMPEG, "-y",
         "-i", str(merged), "-i", str(audio),
         "-filter_complex", f"[1:a]apad=whole_dur={vid_dur}[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(vid_dur),
         str(with_audio)],
        capture_output=True, text=True,
    )
    if r2.returncode != 0:
        print(f"   [ERR] audio mix: {r2.stderr[-300:]}")
        return False
    print("   [OK]  Audio mixed")

    shutil.copy(str(with_audio), str(output))
    return True


# ════════════════════════════════════════════════════════════════════
# STEP 7 — Export formats
# ════════════════════════════════════════════════════════════════════

def export_formats(src: Path):
    fmts = {"16x9": (1920,1080), "9x16": (1080,1920), "1x1": (1080,1080)}
    for label, (w, h) in fmts.items():
        out = OUT / f"automail_v2_{label}.mp4"
        vf  = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
        )
        subprocess.run(
            [FFMPEG, "-y", "-i", str(src),
             "-vf", vf,
             "-c:v", "libx264", "-crf", "17", "-preset", "medium",
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
    SEP = "=" * 64
    print(SEP)
    print("  AutoMail ULTRA PREMIUM v2  —  30-Second Ad")
    print(SEP)

    scenes = SCRIPT["scenes"]
    clips  = []

    # ── STEP 1–3: Images ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 1/4 — Images: Generate → Grade → Overlay")
    print(SEP)

    for i, (scene, prompt) in enumerate(zip(scenes, PROMPTS)):
        n    = scene["scene_number"]
        lbl  = scene["label"]
        dur  = scene["duration_seconds"]
        fx   = scene["effect"]
        raw  = IMGS / f"v2_raw_{n}.png"
        proc_path = IMGS / f"v2_proc_{n}.png"
        clip = CLIPS / f"v2_clip_{n}.mp4"

        print(f"\n[Scene {n}] {lbl}  ({dur}s)  effect={fx}")

        # Generate
        if not raw.exists():
            ok = generate_image(prompt, raw, n, seed=n * 999 + 42)
            if not ok:
                print(f"[FATAL] Scene {n} image failed"); return
        else:
            print(f"   [SKIP] Raw image cached: {raw.name}")

        # Post-process
        img = Image.open(str(raw)).convert("RGB").resize((1920,1080), Image.Resampling.LANCZOS)
        print(f"   [POST] Color grade + vignette...")
        img = postprocess(img)

        # Apply scene-specific overlay
        print(f"   [TEXT] Applying {lbl} text layout...")
        img = OVERLAY_FN[lbl](img, scene)
        img.save(str(proc_path), "PNG")
        print(f"   [OK]  {proc_path.name}")

        # ── STEP 4: PIL Ken Burns clip ──────────────────────────────
        print(f"   [CLIP] PIL frame-by-frame Ken Burns ({dur}s)...")
        ok = render_ken_burns_clip(img, clip, dur, fx)
        if not ok:
            print(f"[FATAL] Clip {n} failed"); return
        clips.append(clip)

    # ── STEP 5: Voiceover ───────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 2/4 — AriaNeural Voiceover")
    print(SEP)
    audio = generate_voiceover(scenes)

    # ── STEP 6: Assemble ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 3/4 — Assembling Final Video")
    print(SEP)
    final = OUT / "automail_v2_final.mp4"
    ok    = assemble(clips, audio, final)
    if not ok:
        print("[FATAL] Assembly failed"); return

    mb = final.stat().st_size / 1_048_576
    print(f"\n   [MASTER] {final.name}  ({mb:.1f} MB)")

    # ── STEP 7: Formats ─────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 4/4 — Multi-Format Export")
    print(SEP)
    export_formats(final)

    # Demo copy
    demo = DEMO / "automail_v2_premium.mp4"
    shutil.copy(str(final), str(demo))

    print(f"\n{SEP}")
    print("  COMPLETE!")
    print(SEP)
    print(f"""
  Master 16:9  →  output/automail_v2_final.mp4
  Widescreen   →  output/automail_v2_16x9.mp4
  Reels/TikTok →  output/automail_v2_9x16.mp4
  Square Post  →  output/automail_v2_1x1.mp4
  Demo copy    →  demo/automail_v2_premium.mp4
""")


if __name__ == "__main__":
    import json
    main()
