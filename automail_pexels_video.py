"""
AutoMail PREMIUM VIDEO — Pexels Real Video Clips Pipeline
==========================================================
Uses REAL cinematic stock footage from Pexels instead of static images.
Pipeline:
  1. Search & download best Pexels video clip per scene
  2. Trim each clip to exact scene duration
  3. Overlay premium Pillow text per scene (unique layout per scene)
  4. AriaNeural AI voiceover
  5. Assemble final 30-second video
  6. Export 16:9 · 9:16 · 1:1
==========================================================
"""

import io, json, sys, time, subprocess, shutil, asyncio, requests, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Directories ──────────────────────────────────────────────────────
BASE      = Path(__file__).parent
OUT       = BASE / "output"
RAW_CLIPS = OUT  / "pexels_raw"
PROC_CLIPS= OUT  / "pexels_proc"
VOICE     = OUT  / "voice"
DEMO      = BASE / "demo"
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
PEXELS_KEY = "Bv2EXlrvW3bVo8ldVRaSAcaG3Bf5aHZrrL7cLcF9ZKKO4kW6Rtsmad13"
PEXELS_HEADERS = {"Authorization": PEXELS_KEY}

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

SEGOE_BLACK = "C:/Windows/Fonts/seguibl.ttf"
SEGOE_BOLD  = "C:/Windows/Fonts/segoeuib.ttf"
SEGOE_REG   = "C:/Windows/Fonts/segoeui.ttf"

# ════════════════════════════════════════════════════════════════════
# SCRIPT  (30 seconds total)
# ════════════════════════════════════════════════════════════════════
SCRIPT = {
    "product_name": "AutoMail",
    "tagline": "Write Less. Connect More. Grow Faster.",
    "scenes": [
        {
            "scene_number": 1, "label": "HOOK", "duration_seconds": 5,
            "voiceover": "You built something great. But no one's opening your emails.",
            "on_screen_text": "Your emails go unread.",
            "pexels_queries": [
                "stressed entrepreneur working late night laptop",
                "tired business person desk night",
                "frustrated woman computer office night",
            ],
        },
        {
            "scene_number": 2, "label": "SOLUTION", "duration_seconds": 9,
            "voiceover": "AutoMail uses AI to write personalized campaigns that actually get read — in minutes.",
            "on_screen_text": "AI emails. Written for you.",
            "pexels_queries": [
                "entrepreneur smiling laptop modern office",
                "businesswoman happy computer office sunlight",
                "person excited laptop working bright office",
            ],
        },
        {
            "scene_number": 3, "label": "BENEFITS", "duration_seconds": 11,
            "voiceover": "Three times higher open rates. Five hours saved every week. Real results — zero writing skills needed.",
            "on_screen_text": "3x opens. 5hrs saved. Zero effort.",
            "pexels_queries": [
                "business team celebrating office success",
                "team happy achievement office celebration",
                "diverse business people success city office",
            ],
        },
        {
            "scene_number": 4, "label": "CTA", "duration_seconds": 5,
            "voiceover": "Start free today. Your next campaign writes itself.",
            "on_screen_text": "Start Free. AutoMail.ai",
            "pexels_queries": [
                "laptop dark background glowing screen studio",
                "modern laptop on desk dark background",
                "laptop computer dark minimalist professional",
            ],
        },
    ],
}

# ════════════════════════════════════════════════════════════════════
# STEP 1 — Pexels Video Search & Download
# ════════════════════════════════════════════════════════════════════

def search_pexels_video(queries: list, min_duration: int) -> dict | None:
    """Try each query, return best matching video file info."""
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
            # Filter: duration >= min_duration, prefer HD
            candidates = [v for v in videos if v.get("duration", 0) >= min_duration]
            if not candidates:
                candidates = videos  # relax filter

            for vid in candidates:
                # Pick best quality file (prefer HD 1920x1080)
                files = vid.get("video_files", [])
                # Sort by width descending
                files_sorted = sorted(files, key=lambda f: f.get("width", 0), reverse=True)
                for f in files_sorted:
                    if f.get("width", 0) >= 1280 and f.get("file_type") == "video/mp4":
                        return {
                            "url": f["link"],
                            "width": f["width"],
                            "height": f["height"],
                            "duration": vid["duration"],
                            "id": vid["id"],
                            "query": query,
                        }
        except Exception as e:
            print(f"   [ERR] {e}")
        time.sleep(0.5)
    return None


def download_video(url: str, out_path: Path) -> bool:
    print(f"   [DOWNLOAD] {url[:70]}...")
    try:
        r = requests.get(url, stream=True, timeout=120)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            size_mb = out_path.stat().st_size / 1_048_576
            print(f"   [OK]  Downloaded: {out_path.name} ({size_mb:.1f} MB)")
            return True
        print(f"   [ERR] HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERR] {e}")
    return False


# ════════════════════════════════════════════════════════════════════
# STEP 2 — Trim & Resize Clip to exact scene duration
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
    """
    Trim clip to `duration` seconds from a good starting point,
    scale to 1920x1080, add subtle fade-in and fade-out.
    """
    src_dur = get_video_duration(src)
    if src_dur <= 0:
        return False

    # Start at 20% in to skip slow intros, but ensure enough duration remains
    start = min(src_dur * 0.20, max(0, src_dur - duration - 1))
    start = max(0, start)

    fade = 0.35
    vf = (
        f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H},"
        f"fade=in:st=0:d={fade},"
        f"fade=out:st={duration - fade}:d={fade}"
    )

    cmd = [
        FFMPEG, "-y",
        "-ss", str(start),
        "-i", str(src),
        "-t", str(duration),
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "15",
        "-an",   # remove original audio
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   [ERR] trim: {r.stderr[-400:]}")
        return False
    size_mb = out.stat().st_size / 1_048_576 if out.exists() else 0
    print(f"   [OK]  Trimmed: {out.name} ({size_mb:.1f} MB)")
    return True


# ════════════════════════════════════════════════════════════════════
# STEP 3 — Premium Text Overlays (scene-specific)
# ════════════════════════════════════════════════════════════════════

def _shadow(draw, pos, text, fnt, col=(0,0,0,190), offset=4):
    for dx, dy in [(-offset,offset),(offset,offset),(0,offset+1),(-offset+1,-offset+1)]:
        draw.text((pos[0]+dx, pos[1]+dy), text, font=fnt, fill=col)


def overlay_hook(img):
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0,0,0,0))
    d  = ImageDraw.Draw(cv)
    # Dark full overlay
    d.rectangle([(0,0),(W,H)], fill=(0,0,0,120))
    # Top orange bar
    d.rectangle([(0,0),(W,6)], fill=(*ORANGE,255))
    # Bottom brand strip
    d.rectangle([(0,H-80),(W,H)], fill=(0,0,0,200))

    f1 = font(SEGOE_BOLD, 52)
    f2 = font(SEGOE_BLACK, 96)
    f3 = font(SEGOE_BOLD, 34)

    l1 = "You built something great."
    l2 = "But no one's opening your emails."

    bb1 = d.textbbox((0,0), l1, font=f1)
    x1  = (W-(bb1[2]-bb1[0]))//2
    y1  = int(H*0.33)
    _shadow(d,(x1,y1),l1,f1)
    d.text((x1,y1), l1, font=f1, fill=(*GRAY,220))

    bb2 = d.textbbox((0,0), l2, font=f2)
    x2  = (W-(bb2[2]-bb2[0]))//2
    y2  = y1+(bb1[3]-bb1[1])+28
    _shadow(d,(x2,y2),l2,f2,offset=5)
    d.text((x2,y2), l2, font=f2, fill=(*WHITE,255))
    # Underline
    uw = bb2[2]-bb2[0]
    d.rectangle([(x2, y2+(bb2[3]-bb2[1])+12),(x2+uw, y2+(bb2[3]-bb2[1])+20)],
                fill=(*ORANGE,230))

    brand = "AutoMail  ·  Write Less. Connect More. Grow Faster."
    bbb = d.textbbox((0,0), brand, font=f3)
    bx  = (W-(bbb[2]-bbb[0]))//2
    by  = H-80+(80-(bbb[3]-bbb[1]))//2
    d.text((bx,by), brand, font=f3, fill=(*ORANGE,200))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_solution(img):
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0,0,0,0))
    d  = ImageDraw.Draw(cv)
    bar_h = 320
    for y in range(bar_h):
        t = y/bar_h
        d.rectangle([(0,H-bar_h+y),(W,H-bar_h+y+1)], fill=(8,10,20,int(235*(1-t)**1.3)))
    d.rectangle([(0,H-bar_h-5),(W,H-bar_h)], fill=(*ORANGE,255))

    f_big  = font(SEGOE_BLACK,112)
    f_sub  = font(SEGOE_BOLD, 70)
    f_tag  = font(SEGOE_BOLD, 32)
    f_logo = font(SEGOE_BLACK,42)

    t1,t2 = "AI emails.", "Written for you."
    bb1 = d.textbbox((0,0),t1,font=f_big)
    bb2 = d.textbbox((0,0),t2,font=f_sub)
    x1,y1 = 80, H-bar_h+28
    _shadow(d,(x1,y1),t1,f_big,offset=5)
    d.text((x1,y1),t1,font=f_big,fill=(*ORANGE,255))

    x2 = x1+(bb1[2]-bb1[0])+36
    y2 = y1+((bb1[3]-bb1[1])-(bb2[3]-bb2[1]))
    _shadow(d,(x2,y2),t2,f_sub,offset=4)
    d.text((x2,y2),t2,font=f_sub,fill=(*WHITE,255))

    tag = "Powered by AutoMail AI  ·  automail.ai"
    bbt = d.textbbox((0,0),tag,font=f_tag)
    d.text((x1, y1+(bb1[3]-bb1[1])+16), tag, font=f_tag, fill=(*GRAY,175))

    # Logo badge top-right
    lx,ly = W-260,34
    d.rounded_rectangle([(lx-12,ly-8),(lx+220,ly+52)],radius=8,fill=(0,0,0,150))
    d.text((lx,ly),"AutoMail",font=f_logo,fill=(*ORANGE,255))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_benefits(img):
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0,0,0,0))
    d  = ImageDraw.Draw(cv)
    bar_h = 290
    for y in range(bar_h):
        t = y/bar_h
        d.rectangle([(0,H-bar_h+y),(W,H-bar_h+y+1)], fill=(5,7,15,int(245*(1-t)**1.2)))
    d.rectangle([(0,H-bar_h-6),(W,H-bar_h)], fill=(*ORANGE,255))

    f_num  = font(SEGOE_BLACK,105)
    f_lbl  = font(SEGOE_BOLD, 36)
    f_logo = font(SEGOE_BLACK,40)

    METRICS = [("3x","Higher Open Rates"),("5hrs","Saved Every Week"),("Zero","Writing Skills Needed")]
    cw = W//3
    for i,(val,desc) in enumerate(METRICS):
        cx  = i*cw+cw//2
        bbv = d.textbbox((0,0),val,font=f_num)
        vw  = bbv[2]-bbv[0]
        yv  = H-bar_h+18
        _shadow(d,(cx-vw//2,yv),val,f_num,offset=5)
        d.text((cx-vw//2,yv),val,font=f_num,fill=(*ORANGE,255))
        bbd = d.textbbox((0,0),desc,font=f_lbl)
        dw  = bbd[2]-bbd[0]
        yd  = yv+(bbv[3]-bbv[1])+10
        d.text((cx-dw//2,yd),desc,font=f_lbl,fill=(*WHITE,215))
        if i<2:
            dx = (i+1)*cw
            d.rectangle([(dx-1,H-bar_h+14),(dx+1,H-18)],fill=(*ORANGE,90))

    lx,ly = W-252,34
    d.rounded_rectangle([(lx-12,ly-8),(lx+212,ly+50)],radius=8,fill=(0,0,0,150))
    d.text((lx,ly),"AutoMail",font=f_logo,fill=(*ORANGE,255))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_cta(img):
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0,0,0,0))
    d  = ImageDraw.Draw(cv)
    d.rectangle([(0,0),(W,H)], fill=(0,0,0,165))
    d.rectangle([(0,0),(W,6)], fill=(*ORANGE,255))
    d.rectangle([(0,H-6),(W,H)], fill=(*ORANGE,255))

    f_brand = font(SEGOE_BLACK,108)
    f_tag   = font(SEGOE_BOLD, 46)
    f_btn   = font(SEGOE_BLACK, 62)
    f_url   = font(SEGOE_BOLD, 38)

    cy = H//2 - 90
    brand = "AutoMail"
    bb_b  = d.textbbox((0,0),brand,font=f_brand)
    bx    = (W-(bb_b[2]-bb_b[0]))//2
    by    = cy-(bb_b[3]-bb_b[1])-18
    _shadow(d,(bx,by),brand,f_brand,offset=6)
    d.text((bx,by),brand,font=f_brand,fill=(*WHITE,255))

    tagline = "Write Less. Connect More. Grow Faster."
    bbt = d.textbbox((0,0),tagline,font=f_tag)
    tx  = (W-(bbt[2]-bbt[0]))//2
    ty  = by+(bb_b[3]-bb_b[1])+10
    d.text((tx,ty),tagline,font=f_tag,fill=(*GRAY,205))

    btn_text = "   START FREE TODAY   "
    bb_btn   = d.textbbox((0,0),btn_text,font=f_btn)
    bw = bb_btn[2]-bb_btn[0]+60
    bh = bb_btn[3]-bb_btn[1]+34
    bx2 = (W-bw)//2
    by2 = ty+(bbt[3]-bbt[1])+50
    d.rounded_rectangle([(bx2+6,by2+6),(bx2+bw+6,by2+bh+6)],radius=12,fill=(0,0,0,140))
    d.rounded_rectangle([(bx2,by2),(bx2+bw,by2+bh)],radius=12,fill=(*ORANGE,255))
    btx = bx2+(bw-(bb_btn[2]-bb_btn[0]))//2
    bty = by2+(bh-(bb_btn[3]-bb_btn[1]))//2
    d.text((btx,bty),btn_text,font=f_btn,fill=(*WHITE,255))

    url_text = "automail.ai"
    bb_url   = d.textbbox((0,0),url_text,font=f_url)
    ux = (W-(bb_url[2]-bb_url[0]))//2
    uy = by2+bh+28
    d.text((ux,uy),url_text,font=f_url,fill=(*GRAY,195))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


OVERLAY_FN = {
    "HOOK":     overlay_hook,
    "SOLUTION": overlay_solution,
    "BENEFITS": overlay_benefits,
    "CTA":      overlay_cta,
}


# ════════════════════════════════════════════════════════════════════
# STEP 4 — Burn Text Overlay onto Video Clip (frame by frame via pipe)
# ════════════════════════════════════════════════════════════════════

def burn_overlay_on_clip(src_clip: Path, out_clip: Path,
                          scene: dict) -> bool:
    """
    Read each frame from the trimmed Pexels clip,
    apply PIL text overlay, pipe back to FFmpeg.
    """
    label   = scene["label"]
    duration= scene["duration_seconds"]
    total_frames = duration * FPS

    print(f"   [OVERLAY] Burning {label} overlay onto {total_frames} frames...")

    # Reader process
    reader_cmd = [
        FFMPEG, "-i", str(src_clip),
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-vframes", str(total_frames),
        "pipe:1",
    ]
    # Writer process
    writer_cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{OUT_W}x{OUT_H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "15",
        str(out_clip),
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
            img   = Image.frombytes("RGB", (OUT_W, OUT_H), raw)
            img   = overlay_fn(img)
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

    print(f"   [OK]  {out_clip.name} ({out_clip.stat().st_size/1_048_576:.1f} MB)")
    return writer.returncode == 0


# ════════════════════════════════════════════════════════════════════
# STEP 5 — Voiceover
# ════════════════════════════════════════════════════════════════════

async def _tts(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out))


def generate_voiceover(scenes):
    voice = "en-US-AriaNeural"
    files = []
    for i, sc in enumerate(scenes):
        out = VOICE / f"pex_scene_{i+1}.mp3"
        print(f"   [TTS] Scene {i+1}: {sc['voiceover'][:55]}...")
        asyncio.run(_tts(sc["voiceover"], voice, out))
        files.append(out)

    list_f = VOICE / "pex_files.txt"
    with open(list_f, "w") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")

    merged = VOICE / "pex_voiceover.mp3"
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
    list_f = OUT / "pex_clips.txt"
    with open(list_f, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    merged = OUT / "pex_merged.mp4"
    r = subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f),
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "15",
         str(merged)],
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
    print(f"   [INFO] Video: {vid_dur:.2f}s")

    with_audio = OUT / "pex_with_audio.mp4"
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
    fmts = {"16x9":(1920,1080), "9x16":(1080,1920), "1x1":(1080,1080)}
    for label,(w,h) in fmts.items():
        out = OUT / f"automail_pexels_{label}.mp4"
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
    print("  AutoMail PREMIUM  —  Pexels Real Video Pipeline")
    print(SEP)

    scenes       = SCRIPT["scenes"]
    final_clips  = []

    # ── STEP 1–4: Per scene ─────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 1/4 — Fetch Pexels Clips + Burn Overlays")
    print(SEP)

    for scene in scenes:
        n   = scene["scene_number"]
        lbl = scene["label"]
        dur = scene["duration_seconds"]

        raw_path  = RAW_CLIPS  / f"pex_raw_{n}.mp4"
        trim_path = RAW_CLIPS  / f"pex_trim_{n}.mp4"
        proc_path = PROC_CLIPS / f"pex_proc_{n}.mp4"

        print(f"\n[Scene {n}] {lbl}  ({dur}s)")

        # 1a. Find & download Pexels clip
        if not raw_path.exists():
            info = search_pexels_video(scene["pexels_queries"], dur)
            if not info:
                print(f"   [FATAL] No Pexels clip found for scene {n}")
                return
            print(f"   [FOUND] {info['width']}x{info['height']}  {info['duration']}s  id={info['id']}")
            ok = download_video(info["url"], raw_path)
            if not ok:
                print(f"   [FATAL] Download failed"); return
        else:
            print(f"   [SKIP] Raw clip cached: {raw_path.name}")

        # 1b. Trim & resize to exact duration
        if not trim_path.exists():
            ok = trim_and_resize(raw_path, trim_path, dur)
            if not ok:
                print(f"   [FATAL] Trim failed"); return
        else:
            print(f"   [SKIP] Trimmed clip cached: {trim_path.name}")

        # 1c. Burn text overlay frame by frame
        ok = burn_overlay_on_clip(trim_path, proc_path, scene)
        if not ok:
            print(f"   [FATAL] Overlay failed"); return

        final_clips.append(proc_path)

    # ── STEP 5: Voiceover ───────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 2/4 — AriaNeural Voiceover")
    print(SEP)
    audio = generate_voiceover(scenes)

    # ── STEP 6: Assemble ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 3/4 — Assembling Final Video")
    print(SEP)
    final = OUT / "automail_pexels_final.mp4"
    ok    = assemble(final_clips, audio, final)
    if not ok:
        print("[FATAL] Assembly failed"); return

    mb = final.stat().st_size / 1_048_576
    print(f"\n   [MASTER] {final.name}  ({mb:.1f} MB)")

    # ── STEP 7: Formats ─────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 4/4 — Multi-Format Export")
    print(SEP)
    export_formats(final)

    demo = DEMO / "automail_pexels_premium.mp4"
    shutil.copy(str(final), str(demo))

    print(f"\n{SEP}")
    print("  PEXELS PREMIUM VIDEO COMPLETE!")
    print(SEP)
    print(f"""
  Master 16:9  →  output/automail_pexels_final.mp4
  Widescreen   →  output/automail_pexels_16x9.mp4
  Reels/TikTok →  output/automail_pexels_9x16.mp4
  Square Post  →  output/automail_pexels_1x1.mp4
  Demo copy    →  demo/automail_pexels_premium.mp4
""")


if __name__ == "__main__":
    main()
