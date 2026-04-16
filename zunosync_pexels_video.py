"""
ZunoSync PREMIUM VIDEO — Pexels Real Video Clips Pipeline
==========================================================
30-second video ad for ZunoSync — AI Social Media Automation platform.
Source: https://www.zunosync.com/

Real product messaging:
  "AI Social Media Automation: Create & Schedule 10x Faster"
  "Generate posts, create videos, and schedule content across all platforms."
  Stats: 10x faster · 50k+ posts generated · 98% user satisfaction · 5+ platforms

Pipeline:
  1. Search & download best Pexels video clip per scene
  2. Trim each clip to exact scene duration
  3. Overlay premium Pillow text per scene (ZunoSync brand)
  4. AriaNeural AI voiceover
  5. Assemble final 30-second video
  6. Export 16:9 · 9:16 · 1:1
==========================================================
"""

import io, json, sys, time, subprocess, shutil, asyncio, requests, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Directories ──────────────────────────────────────────────────────
BASE       = Path(__file__).parent
OUT        = BASE / "output"
RAW_CLIPS  = OUT  / "zuno_raw"
PROC_CLIPS = OUT  / "zuno_proc"
VOICE      = OUT  / "zuno_voice"
DEMO       = BASE / "demo"
for d in [OUT, RAW_CLIPS, PROC_CLIPS, VOICE, DEMO]:
    d.mkdir(parents=True, exist_ok=True)

# ── FFmpeg ───────────────────────────────────────────────────────────
_FF = (
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1-full_build\bin"
)
FFMPEG  = str(Path(_FF) / "ffmpeg.exe")
FFPROBE = str(Path(_FF) / "ffprobe.exe")

# ── Pexels ───────────────────────────────────────────────────────────
PEXELS_KEY     = "Bv2EXlrvW3bVo8ldVRaSAcaG3Bf5aHZrrL7cLcF9ZKKO4kW6Rtsmad13"
PEXELS_HEADERS = {"Authorization": PEXELS_KEY}

# ── ZunoSync Brand Colors ────────────────────────────────────────────
PURPLE    = (124,  58, 237)   # vibrant purple — primary
PINK      = (236,  72, 153)   # electric pink — accent
VIOLET    = ( 88,  28, 135)   # deep violet
DARK      = ( 10,   2,  20)   # near-black
WHITE     = (255, 255, 255)
GRAY      = (196, 181, 253)   # purple-tinted gray
OUT_W, OUT_H = 1920, 1080
FPS = 24

# ── Fonts ────────────────────────────────────────────────────────────
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

SEGOE_BLACK = "C:/Windows/Fonts/seguibl.ttf"
SEGOE_BOLD  = "C:/Windows/Fonts/segoeuib.ttf"
SEGOE_REG   = "C:/Windows/Fonts/segoeui.ttf"

# ════════════════════════════════════════════════════════════════════
# SCRIPT  — 30 seconds
# Based on real zunosync.com content
# ════════════════════════════════════════════════════════════════════
SCRIPT = {
    "product_name": "ZunoSync",
    "tagline": "Create & Schedule 10x Faster",
    "website": "zunosync.com",
    "scenes": [
        {
            "scene_number": 1, "label": "HOOK", "duration_seconds": 5,
            "voiceover": "Writing captions. Designing posts. Scheduling across five platforms. Every single day.",
            "on_screen_text": "Social media is draining you.",
            "pexels_queries": [
                "woman stressed phone laptop multiple screens social media desk",
                "person frustrated overwhelmed smartphone notifications laptop desk",
                "content creator stressed phone tablet laptop desk multiple devices",
                "social media manager overwhelmed phone computer screens notifications",
                "young woman stressed scrolling phone laptop desk office tired",
            ],
        },
        {
            "scene_number": 2, "label": "SOLUTION", "duration_seconds": 9,
            "voiceover": "ZunoSync uses AI to generate posts, create videos, and schedule across all platforms — in one place.",
            "on_screen_text": "AI content. All platforms. One place.",
            "pexels_queries": [
                "woman typing laptop smiling bright modern office window sunlight",
                "young professional woman working laptop creative bright workspace desk",
                "businesswoman happy confident laptop computer modern office daylight",
                "female entrepreneur focused laptop bright office open space",
                "woman working on computer smiling modern clean office sunlight",
            ],
        },
        {
            "scene_number": 3, "label": "BENEFITS", "duration_seconds": 11,
            "voiceover": "Ten times faster content creation. Over fifty thousand posts generated. Ninety-eight percent of users — satisfied.",
            "on_screen_text": "10x Faster. 50k+ Posts. 98% Satisfied.",
            "pexels_queries": [
                "business analytics phone social media growth chart office success",
                "entrepreneur checking phone positive results analytics office growth",
                "young professional smiling phone analytics dashboard results desk",
                "content creator phone laptop analytics metrics positive office",
                "person checking smartphone results growth statistics office success",
            ],
        },
        {
            "scene_number": 4, "label": "CTA", "duration_seconds": 5,
            "voiceover": "Start creating with AI — free today. ZunoSync.",
            "on_screen_text": "Start Free. zunosync.com",
            "pexels_queries": [
                "smartphone dark background glowing screen app studio professional",
                "mobile phone dark studio spotlight advertisement product shot",
                "phone dark background digital app minimal professional premium",
                "smartphone dark minimal desk studio technology product advertisement",
                "mobile phone dark background glow professional studio shot",
            ],
        },
    ],
}

# ════════════════════════════════════════════════════════════════════
# STEP 1 — Pexels Video Search & Download
# ════════════════════════════════════════════════════════════════════

def search_pexels_video(queries: list, min_duration: int) -> dict | None:
    for query in queries:
        print(f"   [SEARCH] '{query}'")
        try:
            r = requests.get(
                "https://api.pexels.com/videos/search",
                headers=PEXELS_HEADERS,
                params={"query": query, "per_page": 15, "orientation": "landscape"},
                timeout=30,
            )
            if r.status_code != 200:
                print(f"   [WARN] HTTP {r.status_code}")
                continue

            videos = r.json().get("videos", [])
            candidates = [v for v in videos if v.get("duration", 0) >= min_duration]
            if not candidates:
                candidates = videos

            for vid in candidates:
                files = vid.get("video_files", [])
                # Prefer HD 1080p — avoids huge UHD files that drop connections
                hd  = [f for f in files if 1280 <= f.get("width", 0) <= 1920 and f.get("file_type") == "video/mp4"]
                uhd = [f for f in files if f.get("width", 0) > 1920 and f.get("file_type") == "video/mp4"]
                pick = sorted(hd if hd else uhd, key=lambda f: f.get("width", 0), reverse=True)
                if pick:
                    return {
                        "url":      pick[0]["link"],
                        "width":    pick[0]["width"],
                        "height":   pick[0]["height"],
                        "duration": vid["duration"],
                        "id":       vid["id"],
                        "query":    query,
                    }
        except Exception as e:
            print(f"   [ERR] {e}")
        time.sleep(0.5)
    return None


def download_video(url: str, out_path: Path) -> bool:
    print(f"   [DOWNLOAD] {url[:70]}...")
    for attempt in range(3):
        try:
            r = requests.get(url, stream=True, timeout=180)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        f.write(chunk)
                mb = out_path.stat().st_size / 1_048_576
                print(f"   [OK]  Downloaded: {out_path.name} ({mb:.1f} MB)")
                return True
            print(f"   [ERR] HTTP {r.status_code}")
        except Exception as e:
            print(f"   [RETRY {attempt+1}/3] {e}")
            if out_path.exists():
                out_path.unlink()
            time.sleep(3)
    return False


# ════════════════════════════════════════════════════════════════════
# STEP 2 — Trim & Resize
# ════════════════════════════════════════════════════════════════════

def get_video_duration(path: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def trim_and_resize(src: Path, out: Path, duration: int) -> bool:
    src_dur = get_video_duration(src)
    if src_dur <= 0:
        return False
    start = min(src_dur * 0.20, max(0, src_dur - duration - 1))
    start = max(0, start)
    fade  = 0.35
    vf = (
        f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H},"
        f"fade=in:st=0:d={fade},"
        f"fade=out:st={duration - fade}:d={fade}"
    )
    cmd = [
        FFMPEG, "-y", "-ss", str(start), "-i", str(src),
        "-t", str(duration), "-vf", vf, "-r", str(FPS),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "15", "-an", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   [ERR] trim: {r.stderr[-400:]}")
        return False
    mb = out.stat().st_size / 1_048_576 if out.exists() else 0
    print(f"   [OK]  Trimmed: {out.name} ({mb:.1f} MB)")
    return True


# ════════════════════════════════════════════════════════════════════
# STEP 3 — Premium Text Overlays (ZunoSync brand — purple/pink)
# ════════════════════════════════════════════════════════════════════

def _shadow(draw, pos, text, fnt, col=(0, 0, 0, 210), offset=4):
    for dx, dy in [(-offset, offset), (offset, offset), (0, offset + 1), (-offset + 1, -offset + 1)]:
        draw.text((pos[0] + dx, pos[1] + dy), text, font=fnt, fill=col)


def _grad_rect(draw, x0, y0, x1, y1, color_top, color_bot, steps=80):
    """Vertical gradient fill."""
    h = y1 - y0
    for i in range(steps):
        t  = i / steps
        r  = int(color_top[0] * (1-t) + color_bot[0] * t)
        g  = int(color_top[1] * (1-t) + color_bot[1] * t)
        b  = int(color_top[2] * (1-t) + color_bot[2] * t)
        a  = int(color_top[3] * (1-t) + color_bot[3] * t)
        yy = y0 + int(i / steps * h)
        draw.rectangle([(x0, yy), (x1, yy + max(1, h // steps))], fill=(r, g, b, a))


def overlay_hook(img):
    """HOOK — dark overlay, sharp pain-point headline, purple accent bar."""
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(cv)

    # Dark vignette
    d.rectangle([(0, 0), (W, H)], fill=(0, 0, 0, 145))
    # Purple top bar
    d.rectangle([(0, 0), (W, 8)], fill=(*PURPLE, 255))
    # Pink accent stripe
    d.rectangle([(0, 8), (W, 14)], fill=(*PINK, 180))
    # Bottom brand strip with gradient
    _grad_rect(d, 0, H - 95, W, H, (*DARK, 240), (*DARK, 220))

    f1 = font(SEGOE_BOLD,  52)
    f2 = font(SEGOE_BLACK, 94)
    f3 = font(SEGOE_BOLD,  33)

    l1 = "Writing captions. Designing posts."
    l2 = "Every. Single. Day."

    bb1 = d.textbbox((0, 0), l1, font=f1)
    x1  = (W - (bb1[2] - bb1[0])) // 2
    y1  = int(H * 0.28)
    _shadow(d, (x1, y1), l1, f1)
    d.text((x1, y1), l1, font=f1, fill=(*GRAY, 220))

    bb2 = d.textbbox((0, 0), l2, font=f2)
    x2  = (W - (bb2[2] - bb2[0])) // 2
    y2  = y1 + (bb1[3] - bb1[1]) + 24
    _shadow(d, (x2, y2), l2, f2, offset=5)
    d.text((x2, y2), l2, font=f2, fill=(*WHITE, 255))

    # Pink underline
    uw = bb2[2] - bb2[0]
    d.rectangle([(x2, y2 + (bb2[3] - bb2[1]) + 14),
                 (x2 + uw, y2 + (bb2[3] - bb2[1]) + 23)],
                fill=(*PINK, 230))

    brand = "ZunoSync  ·  AI Social Media Automation"
    bbb = d.textbbox((0, 0), brand, font=f3)
    bx  = (W - (bbb[2] - bbb[0])) // 2
    by  = H - 95 + (95 - (bbb[3] - bbb[1])) // 2
    d.text((bx, by), brand, font=f3, fill=(*GRAY, 210))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_solution(img):
    """SOLUTION — gradient bottom bar, purple headline, pink accent, logo badge."""
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(cv)

    bar_h = 340
    for y in range(bar_h):
        t     = y / bar_h
        alpha = int(250 * (1 - t) ** 1.25)
        d.rectangle([(0, H - bar_h + y), (W, H - bar_h + y + 1)],
                    fill=(*DARK, alpha))

    # Purple + pink double line separator
    d.rectangle([(0, H - bar_h - 7), (W, H - bar_h - 1)], fill=(*PURPLE, 255))
    d.rectangle([(0, H - bar_h - 1), (W, H - bar_h + 3)], fill=(*PINK, 180))

    f_big  = font(SEGOE_BLACK, 110)
    f_sub  = font(SEGOE_BOLD,  66)
    f_tag  = font(SEGOE_BOLD,  31)
    f_logo = font(SEGOE_BLACK, 42)

    t1, t2 = "AI content.", "All platforms. One place."
    bb1 = d.textbbox((0, 0), t1, font=f_big)
    bb2 = d.textbbox((0, 0), t2, font=f_sub)
    x1, y1 = 80, H - bar_h + 24
    _shadow(d, (x1, y1), t1, f_big, offset=5)
    d.text((x1, y1), t1, font=f_big, fill=(*PURPLE, 255))

    x2 = x1 + (bb1[2] - bb1[0]) + 32
    y2 = y1 + ((bb1[3] - bb1[1]) - (bb2[3] - bb2[1]))
    _shadow(d, (x2, y2), t2, f_sub, offset=4)
    d.text((x2, y2), t2, font=f_sub, fill=(*WHITE, 255))

    tag = "Generate · Create · Schedule — zunosync.com"
    d.text((x1, y1 + (bb1[3] - bb1[1]) + 14), tag, font=f_tag, fill=(*GRAY, 175))

    # Logo badge top-right
    lx, ly = W - 290, 32
    d.rounded_rectangle([(lx - 12, ly - 8), (lx + 256, ly + 54)],
                        radius=10, fill=(*DARK, 175))
    d.text((lx, ly), "ZunoSync", font=f_logo, fill=(*PURPLE, 255))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_benefits(img):
    """BENEFITS — 3 real stats from zunosync.com, purple metrics bar."""
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(cv)

    bar_h = 310
    for y in range(bar_h):
        t     = y / bar_h
        alpha = int(252 * (1 - t) ** 1.2)
        d.rectangle([(0, H - bar_h + y), (W, H - bar_h + y + 1)],
                    fill=(*DARK, alpha))
    d.rectangle([(0, H - bar_h - 7), (W, H - bar_h - 1)], fill=(*PURPLE, 255))
    d.rectangle([(0, H - bar_h - 1), (W, H - bar_h + 3)], fill=(*PINK, 160))

    f_num  = font(SEGOE_BLACK, 106)
    f_lbl  = font(SEGOE_BOLD,  36)
    f_logo = font(SEGOE_BLACK, 40)

    # Real stats from zunosync.com
    METRICS = [
        ("10x",   "Faster Content Creation"),
        ("50k+",  "Posts Generated"),
        ("98%",   "User Satisfaction"),
    ]
    cw = W // 3
    for i, (val, desc) in enumerate(METRICS):
        cx  = i * cw + cw // 2
        bbv = d.textbbox((0, 0), val,  font=f_num)
        bbd = d.textbbox((0, 0), desc, font=f_lbl)
        vw  = bbv[2] - bbv[0]
        dw  = bbd[2] - bbd[0]
        yv  = H - bar_h + 14
        _shadow(d, (cx - vw // 2, yv), val, f_num, offset=5)
        # Alternate purple / pink for visual punch
        col = PURPLE if i % 2 == 0 else PINK
        d.text((cx - vw // 2, yv), val, font=f_num, fill=(*col, 255))
        yd = yv + (bbv[3] - bbv[1]) + 10
        d.text((cx - dw // 2, yd), desc, font=f_lbl, fill=(*WHITE, 215))
        if i < 2:
            dx = (i + 1) * cw
            d.rectangle([(dx - 1, H - bar_h + 14), (dx + 1, H - 18)],
                        fill=(*GRAY, 80))

    lx, ly = W - 272, 34
    d.rounded_rectangle([(lx - 12, ly - 8), (lx + 240, ly + 50)],
                        radius=8, fill=(*DARK, 175))
    d.text((lx, ly), "ZunoSync", font=f_logo, fill=(*PURPLE, 255))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_cta(img):
    """CTA — full dark, ZunoSync brand, purple CTA button, website URL."""
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(cv)

    d.rectangle([(0, 0), (W, H)], fill=(0, 0, 0, 175))
    d.rectangle([(0, 0), (W, 8)],      fill=(*PURPLE, 255))
    d.rectangle([(0, 8), (W, 14)],     fill=(*PINK, 200))
    d.rectangle([(0, H - 8), (W, H)],  fill=(*PURPLE, 255))

    f_brand = font(SEGOE_BLACK, 108)
    f_tag   = font(SEGOE_BOLD,  44)
    f_btn   = font(SEGOE_BLACK, 60)
    f_url   = font(SEGOE_BOLD,  36)

    cy    = H // 2 - 95
    brand = "ZunoSync"
    bb_b  = d.textbbox((0, 0), brand, font=f_brand)
    bx    = (W - (bb_b[2] - bb_b[0])) // 2
    by    = cy - (bb_b[3] - bb_b[1]) - 16
    _shadow(d, (bx, by), brand, f_brand, offset=6)
    d.text((bx, by), brand, font=f_brand, fill=(*WHITE, 255))

    tagline = "AI Social Media Automation: Create & Schedule 10x Faster"
    bbt = d.textbbox((0, 0), tagline, font=f_tag)
    tx  = (W - (bbt[2] - bbt[0])) // 2
    ty  = by + (bb_b[3] - bb_b[1]) + 10
    d.text((tx, ty), tagline, font=f_tag, fill=(*GRAY, 210))

    btn_text = "   START CREATING FREE   "
    bb_btn   = d.textbbox((0, 0), btn_text, font=f_btn)
    bw = bb_btn[2] - bb_btn[0] + 60
    bh = bb_btn[3] - bb_btn[1] + 36
    bx2 = (W - bw) // 2
    by2 = ty + (bbt[3] - bbt[1]) + 52
    # Drop shadow
    d.rounded_rectangle([(bx2 + 7, by2 + 7), (bx2 + bw + 7, by2 + bh + 7)],
                        radius=14, fill=(0, 0, 0, 130))
    # Purple → pink gradient button (approximate with midpoint fill)
    d.rounded_rectangle([(bx2, by2), (bx2 + bw, by2 + bh)],
                        radius=14, fill=(*PURPLE, 255))
    # Pink right half accent
    d.rounded_rectangle([(bx2 + bw // 2, by2), (bx2 + bw, by2 + bh)],
                        radius=14, fill=(*PINK, 200))
    btx = bx2 + (bw - (bb_btn[2] - bb_btn[0])) // 2
    bty = by2 + (bh - (bb_btn[3] - bb_btn[1])) // 2
    d.text((btx, bty), btn_text, font=f_btn, fill=(*WHITE, 255))

    url_text = "zunosync.com"
    bb_url   = d.textbbox((0, 0), url_text, font=f_url)
    ux = (W - (bb_url[2] - bb_url[0])) // 2
    uy = by2 + bh + 28
    d.text((ux, uy), url_text, font=f_url, fill=(*GRAY, 200))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


OVERLAY_FN = {
    "HOOK":     overlay_hook,
    "SOLUTION": overlay_solution,
    "BENEFITS": overlay_benefits,
    "CTA":      overlay_cta,
}


# ════════════════════════════════════════════════════════════════════
# STEP 4 — Burn Overlays frame by frame
# ════════════════════════════════════════════════════════════════════

def burn_overlay_on_clip(src_clip: Path, out_clip: Path, scene: dict) -> bool:
    label        = scene["label"]
    duration     = scene["duration_seconds"]
    total_frames = duration * FPS

    print(f"   [OVERLAY] Burning {label} overlay onto {total_frames} frames...")

    reader_cmd = [
        FFMPEG, "-i", str(src_clip),
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-vframes", str(total_frames), "pipe:1",
    ]
    writer_cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{OUT_W}x{OUT_H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "15", str(out_clip),
    ]

    reader = subprocess.Popen(reader_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    writer = subprocess.Popen(writer_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    frame_size = OUT_W * OUT_H * 3
    frame_idx  = 0
    overlay_fn = OVERLAY_FN[label]

    try:
        while frame_idx < total_frames:
            raw = reader.stdout.read(frame_size)
            if len(raw) < frame_size:
                break
            img = Image.frombytes("RGB", (OUT_W, OUT_H), raw)
            img = overlay_fn(img)
            writer.stdin.write(img.tobytes())
            frame_idx += 1
            if frame_idx % 48 == 0:
                pct = frame_idx / total_frames * 100
                print(f"   [PROGRESS] {pct:.0f}% ({frame_idx}/{total_frames})")
    finally:
        reader.stdout.close()
        reader.terminate()
        writer.stdin.close()
        writer.wait()

    mb = out_clip.stat().st_size / 1_048_576 if out_clip.exists() else 0
    print(f"   [OK]  {out_clip.name} ({mb:.1f} MB)")
    return writer.returncode == 0


# ════════════════════════════════════════════════════════════════════
# STEP 5 — Voiceover (AriaNeural)
# ════════════════════════════════════════════════════════════════════

async def _tts(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out))


def generate_voiceover(scenes):
    voice = "en-US-AriaNeural"
    files = []
    for i, sc in enumerate(scenes):
        out = VOICE / f"zuno_scene_{i + 1}.mp3"
        print(f"   [TTS] Scene {i + 1}: {sc['voiceover'][:60]}...")
        asyncio.run(_tts(sc["voiceover"], voice, out))
        files.append(out)

    list_f = VOICE / "zuno_files.txt"
    with open(list_f, "w") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")

    merged = VOICE / "zuno_voiceover.mp3"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c", "copy", str(merged)],
        capture_output=True,
    )
    print(f"   [OK]  {merged.name}")
    return merged


# ════════════════════════════════════════════════════════════════════
# STEP 6 — Assemble
# ════════════════════════════════════════════════════════════════════

def assemble(clips, audio, output):
    list_f = OUT / "zuno_clips.txt"
    with open(list_f, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    merged = OUT / "zuno_merged.mp4"
    r = subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_f),
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "15", str(merged)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"   [ERR] {r.stderr[-300:]}")
        return False
    print("   [OK]  Clips concatenated")

    rp = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(merged)],
        capture_output=True, text=True,
    )
    vid_dur = float(json.loads(rp.stdout)["format"]["duration"])
    print(f"   [INFO] Video duration: {vid_dur:.2f}s")

    with_audio = OUT / "zuno_with_audio.mp4"
    subprocess.run(
        [FFMPEG, "-y",
         "-i", str(merged), "-i", str(audio),
         "-filter_complex", f"[1:a]apad=whole_dur={vid_dur}[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(vid_dur), str(with_audio)],
        capture_output=True,
    )
    print("   [OK]  Audio mixed")
    shutil.copy(str(with_audio), str(output))
    return True


def export_formats(src):
    fmts = {"16x9": (1920, 1080), "9x16": (1080, 1920), "1x1": (1080, 1080)}
    for label, (w, h) in fmts.items():
        out = OUT / f"zunosync_{label}.mp4"
        vf  = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
        )
        subprocess.run(
            [FFMPEG, "-y", "-i", str(src), "-vf", vf,
             "-c:v", "libx264", "-crf", "17", "-preset", "medium",
             "-c:a", "aac", "-b:a", "192k", str(out)],
            capture_output=True,
        )
        mb = out.stat().st_size / 1_048_576 if out.exists() else 0
        print(f"   [OK]  {label}: {out.name} ({mb:.1f} MB)")


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

def main():
    SEP = "=" * 64
    print(SEP)
    print("  ZunoSync PREMIUM  —  AI Social Media Automation Ad")
    print(SEP)

    scenes      = SCRIPT["scenes"]
    final_clips = []

    print(f"\n{SEP}")
    print("  STEP 1/4 — Fetch Pexels Clips + Burn Overlays")
    print(SEP)

    for scene in scenes:
        n   = scene["scene_number"]
        lbl = scene["label"]
        dur = scene["duration_seconds"]

        raw_path  = RAW_CLIPS  / f"zuno_raw_{n}.mp4"
        trim_path = RAW_CLIPS  / f"zuno_trim_{n}.mp4"
        proc_path = PROC_CLIPS / f"zuno_proc_{n}.mp4"

        print(f"\n[Scene {n}] {lbl}  ({dur}s)")

        if not raw_path.exists():
            info = search_pexels_video(scene["pexels_queries"], dur)
            if not info:
                print(f"   [FATAL] No clip found for scene {n}"); return
            print(f"   [FOUND] {info['width']}x{info['height']}  {info['duration']}s  id={info['id']}")
            if not download_video(info["url"], raw_path):
                print("   [FATAL] Download failed"); return
        else:
            print(f"   [SKIP] Cached: {raw_path.name}")

        if not trim_path.exists():
            if not trim_and_resize(raw_path, trim_path, dur):
                print("   [FATAL] Trim failed"); return
        else:
            print(f"   [SKIP] Cached: {trim_path.name}")

        if not burn_overlay_on_clip(trim_path, proc_path, scene):
            print("   [FATAL] Overlay failed"); return

        final_clips.append(proc_path)

    print(f"\n{SEP}")
    print("  STEP 2/4 — AriaNeural Voiceover")
    print(SEP)
    audio = generate_voiceover(scenes)

    print(f"\n{SEP}")
    print("  STEP 3/4 — Assembling Final Video")
    print(SEP)
    final = OUT / "zunosync_final.mp4"
    if not assemble(final_clips, audio, final):
        print("[FATAL] Assembly failed"); return

    mb = final.stat().st_size / 1_048_576
    print(f"\n   [MASTER] {final.name}  ({mb:.1f} MB)")

    print(f"\n{SEP}")
    print("  STEP 4/4 — Multi-Format Export")
    print(SEP)
    export_formats(final)

    # Clean up temp files
    for f in [OUT / "zuno_clips.txt", OUT / "zuno_merged.mp4", OUT / "zuno_with_audio.mp4"]:
        f.unlink(missing_ok=True)
    shutil.rmtree(RAW_CLIPS,  ignore_errors=True)
    shutil.rmtree(PROC_CLIPS, ignore_errors=True)
    shutil.rmtree(VOICE,      ignore_errors=True)

    demo = DEMO / "zunosync_premium.mp4"
    shutil.copy(str(final), str(demo))

    print(f"\n{SEP}")
    print("  ZUNOSYNC PREMIUM VIDEO COMPLETE!")
    print(SEP)
    print(f"""
  Master 16:9  →  output/zunosync_final.mp4
  Widescreen   →  output/zunosync_16x9.mp4
  Reels/TikTok →  output/zunosync_9x16.mp4
  Square Post  →  output/zunosync_1x1.mp4
  Demo copy    →  demo/zunosync_premium.mp4
""")


if __name__ == "__main__":
    main()
