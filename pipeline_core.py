"""
pipeline_core.py — Abstract video generation pipeline.
Accepts any product script dict and yields progress strings via a queue.
"""

import os, json, time, shutil, subprocess, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests

# ── FFmpeg ───────────────────────────────────────────────────────────
def _find_ff(name):
    """Locate ffmpeg/ffprobe: env var → shutil.which → Windows WinGet path."""
    env_key = "FFMPEG_PATH" if name == "ffmpeg" else "FFPROBE_PATH"
    if os.environ.get(env_key):
        return os.environ[env_key]
    found = shutil.which(name)
    if found:
        return found
    # Fallback: Windows WinGet install path
    _win = (
        r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages"
        r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
        r"\ffmpeg-8.1-full_build\bin"
    )
    return str(Path(_win) / f"{name}.exe")

FFMPEG  = _find_ff("ffmpeg")
FFPROBE = _find_ff("ffprobe")

PEXELS_KEY     = os.environ.get("PEXELS_API_KEY", "")
PEXELS_HEADERS = {"Authorization": PEXELS_KEY}

OUT_W, OUT_H = 1920, 1080
FPS = 24

# ── Fonts ─────────────────────────────────────────────────────────────
_FONTS_DIR = Path(__file__).parent / "static" / "fonts"
SEGOE_BLACK = str(_FONTS_DIR / "Inter-Black.ttf")
SEGOE_BOLD  = str(_FONTS_DIR / "Inter-Bold.ttf")
SEGOE_REG   = str(_FONTS_DIR / "Inter-Regular.ttf")

WHITE = (255, 255, 255)
GRAY  = (200, 200, 210)
BLACK = (0, 0, 0)


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _shadow(draw, pos, text, fnt, col=(0, 0, 0, 200), offset=4):
    for dx, dy in [(-offset, offset), (offset, offset), (0, offset+1)]:
        draw.text((pos[0]+dx, pos[1]+dy), text, font=fnt, fill=col)


# ── Pexels ───────────────────────────────────────────────────────────

def search_pexels(queries, min_duration):
    for query in queries:
        try:
            r = requests.get(
                "https://api.pexels.com/videos/search",
                headers=PEXELS_HEADERS,
                params={"query": query, "per_page": 15, "orientation": "landscape"},
                timeout=30,
            )
            if r.status_code != 200:
                continue
            videos = r.json().get("videos", [])
            candidates = [v for v in videos if v.get("duration", 0) >= min_duration] or videos
            for vid in candidates:
                files = vid.get("video_files", [])
                hd  = [f for f in files if 1280 <= f.get("width", 0) <= 1920 and f.get("file_type") == "video/mp4"]
                uhd = [f for f in files if f.get("width", 0) > 1920 and f.get("file_type") == "video/mp4"]
                pick = sorted(hd if hd else uhd, key=lambda f: f.get("width", 0), reverse=True)
                if pick:
                    return {"url": pick[0]["link"], "width": pick[0]["width"],
                            "height": pick[0]["height"], "duration": vid["duration"],
                            "id": vid["id"], "query": query}
        except Exception:
            pass
        time.sleep(0.4)
    return None


def download_video(url, path):
    for attempt in range(3):
        try:
            r = requests.get(url, stream=True, timeout=180)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
                return True
        except Exception:
            if path.exists():
                path.unlink()
            time.sleep(3)
    return False


def get_duration(path):
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def trim_clip(src, out, duration):
    src_dur = get_duration(src)
    if src_dur <= 0:
        return False
    start = min(src_dur * 0.20, max(0, src_dur - duration - 1))
    fade  = 0.35
    vf = (f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
          f"crop={OUT_W}:{OUT_H},"
          f"fade=in:st=0:d={fade},fade=out:st={duration-fade}:d={fade}")
    r = subprocess.run(
        [FFMPEG, "-y", "-ss", str(start), "-i", str(src),
         "-t", str(duration), "-vf", vf, "-r", str(FPS),
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "15", "-an", str(out)],
        capture_output=True,
    )
    return r.returncode == 0


# ── Overlay builder ───────────────────────────────────────────────────

def build_overlay(img, scene, brand):
    """
    Universal overlay: bottom gradient bar with headline + brand name.
    Brand dict: { primary: (r,g,b), secondary: (r,g,b), name: str, tagline: str }
    """
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(cv)

    primary   = brand["primary"]
    secondary = brand["secondary"]
    dark_bg   = (8, 8, 18)
    label     = scene["label"]

    if label == "HOOK":
        # Dark overlay + full-screen impact text
        d.rectangle([(0, 0), (W, H)], fill=(0, 0, 0, 140))
        d.rectangle([(0, 0), (W, 8)], fill=(*primary, 255))
        d.rectangle([(0, 8), (W, 14)], fill=(*secondary, 160))
        d.rectangle([(0, H-90), (W, H)], fill=(*dark_bg, 235))

        f1 = font(SEGOE_BOLD, 54)
        f2 = font(SEGOE_BLACK, 92)
        f3 = font(SEGOE_BOLD, 32)

        lines = scene["on_screen_text"].split("|") if "|" in scene["on_screen_text"] else [scene["on_screen_text"]]
        y = int(H * 0.30)
        for i, line in enumerate(lines):
            fnt = f1 if i == 0 and len(lines) > 1 else f2
            col = (*GRAY, 210) if i == 0 and len(lines) > 1 else (*WHITE, 255)
            bb  = d.textbbox((0, 0), line, font=fnt)
            x   = (W - (bb[2]-bb[0])) // 2
            _shadow(d, (x, y), line, fnt)
            d.text((x, y), line, font=fnt, fill=col)
            if i == len(lines)-1:
                uw = bb[2]-bb[0]
                d.rectangle([(x, y+(bb[3]-bb[1])+12), (x+uw, y+(bb[3]-bb[1])+21)],
                            fill=(*secondary, 220))
            y += (bb[3]-bb[1]) + 22

        brand_str = f"{brand['name']}  ·  {brand['tagline']}"
        fb = font(SEGOE_BOLD, 32)
        bbb = d.textbbox((0, 0), brand_str, font=fb)
        bx  = (W - (bbb[2]-bbb[0])) // 2
        by  = H - 90 + (90-(bbb[3]-bbb[1])) // 2
        d.text((bx, by), brand_str, font=fb, fill=(*primary, 200))

    elif label == "SOLUTION":
        # Bottom gradient bar
        bar_h = 330
        for y in range(bar_h):
            t = y / bar_h
            a = int(248 * (1-t)**1.25)
            d.rectangle([(0, H-bar_h+y), (W, H-bar_h+y+1)], fill=(*dark_bg, a))
        d.rectangle([(0, H-bar_h-7), (W, H-bar_h-1)], fill=(*primary, 255))
        d.rectangle([(0, H-bar_h-1), (W, H-bar_h+3)], fill=(*secondary, 160))

        parts = scene["on_screen_text"].split("|") if "|" in scene["on_screen_text"] else scene["on_screen_text"].split(". ", 1)
        t1 = parts[0].strip()
        t2 = parts[1].strip() if len(parts) > 1 else ""

        f_big = font(SEGOE_BLACK, 108)
        f_sub = font(SEGOE_BOLD, 66)
        f_tag = font(SEGOE_BOLD, 30)
        f_logo= font(SEGOE_BLACK, 42)

        bb1 = d.textbbox((0, 0), t1, font=f_big)
        x1, y1 = 80, H-bar_h+22
        _shadow(d, (x1, y1), t1, f_big, offset=5)
        d.text((x1, y1), t1, font=f_big, fill=(*primary, 255))

        if t2:
            bb2 = d.textbbox((0, 0), t2, font=f_sub)
            x2  = x1 + (bb1[2]-bb1[0]) + 30
            y2  = y1 + ((bb1[3]-bb1[1])-(bb2[3]-bb2[1]))
            _shadow(d, (x2, y2), t2, f_sub, offset=4)
            d.text((x2, y2), t2, font=f_sub, fill=(*WHITE, 255))

        d.text((x1, y1+(bb1[3]-bb1[1])+12), brand["website"], font=f_tag, fill=(*GRAY, 170))

        lx, ly = W-285, 32
        d.rounded_rectangle([(lx-12, ly-8), (lx+252, ly+54)], radius=10, fill=(0,0,0,165))
        d.text((lx, ly), brand["name"], font=f_logo, fill=(*primary, 255))

    elif label == "BENEFITS":
        # 3-column metrics bar
        bar_h = 305
        for y in range(bar_h):
            t = y / bar_h
            a = int(252 * (1-t)**1.2)
            d.rectangle([(0, H-bar_h+y), (W, H-bar_h+y+1)], fill=(*dark_bg, a))
        d.rectangle([(0, H-bar_h-7), (W, H-bar_h-1)], fill=(*primary, 255))
        d.rectangle([(0, H-bar_h-1), (W, H-bar_h+3)], fill=(*secondary, 150))

        metrics_str = scene.get("metrics", scene["on_screen_text"])
        raw = [m.strip() for m in metrics_str.split("·") if m.strip()]
        metrics = []
        for item in raw[:3]:
            parts = item.split(" ", 1)
            metrics.append((parts[0], parts[1] if len(parts) > 1 else ""))

        f_num  = font(SEGOE_BLACK, 102)
        f_lbl  = font(SEGOE_BOLD, 35)
        f_logo = font(SEGOE_BLACK, 40)
        cw = W // 3
        for i, (val, desc) in enumerate(metrics):
            cx  = i*cw + cw//2
            bbv = d.textbbox((0, 0), val,  font=f_num)
            bbd = d.textbbox((0, 0), desc, font=f_lbl)
            vw, dw = bbv[2]-bbv[0], bbd[2]-bbd[0]
            yv = H-bar_h+14
            _shadow(d, (cx-vw//2, yv), val, f_num, offset=5)
            col = primary if i % 2 == 0 else secondary
            d.text((cx-vw//2, yv), val, font=f_num, fill=(*col, 255))
            yd = yv + (bbv[3]-bbv[1]) + 9
            d.text((cx-dw//2, yd), desc, font=f_lbl, fill=(*WHITE, 215))
            if i < 2:
                dx = (i+1)*cw
                d.rectangle([(dx-1, H-bar_h+14), (dx+1, H-16)], fill=(*GRAY, 70))

        lx, ly = W-272, 34
        d.rounded_rectangle([(lx-12, ly-8), (lx+240, ly+50)], radius=8, fill=(0,0,0,165))
        d.text((lx, ly), brand["name"], font=f_logo, fill=(*primary, 255))

    elif label == "CTA":
        # Full dark overlay, centered brand + CTA button
        d.rectangle([(0, 0), (W, H)], fill=(0, 0, 0, 175))
        d.rectangle([(0, 0), (W, 8)],     fill=(*primary, 255))
        d.rectangle([(0, 8), (W, 14)],    fill=(*secondary, 190))
        d.rectangle([(0, H-8), (W, H)],   fill=(*primary, 255))

        f_brand = font(SEGOE_BLACK, 108)
        f_tag   = font(SEGOE_BOLD, 44)
        f_btn   = font(SEGOE_BLACK, 60)
        f_url   = font(SEGOE_BOLD, 36)

        cy = H//2 - 95
        bb_b = d.textbbox((0, 0), brand["name"], font=f_brand)
        bx   = (W-(bb_b[2]-bb_b[0]))//2
        by   = cy-(bb_b[3]-bb_b[1])-16
        _shadow(d, (bx, by), brand["name"], f_brand, offset=6)
        d.text((bx, by), brand["name"], font=f_brand, fill=(*WHITE, 255))

        bbt = d.textbbox((0, 0), brand["tagline"], font=f_tag)
        tx  = (W-(bbt[2]-bbt[0]))//2
        ty  = by+(bb_b[3]-bb_b[1])+10
        d.text((tx, ty), brand["tagline"], font=f_tag, fill=(*GRAY, 205))

        cta_text = scene.get("cta_button", "   GET STARTED FREE   ")
        bb_btn   = d.textbbox((0, 0), cta_text, font=f_btn)
        bw = bb_btn[2]-bb_btn[0]+60
        bh = bb_btn[3]-bb_btn[1]+36
        bx2 = (W-bw)//2
        by2 = ty+(bbt[3]-bbt[1])+52
        d.rounded_rectangle([(bx2+7, by2+7), (bx2+bw+7, by2+bh+7)], radius=14, fill=(0,0,0,130))
        d.rounded_rectangle([(bx2, by2), (bx2+bw//2, by2+bh)], radius=14, fill=(*primary, 255))
        d.rounded_rectangle([(bx2+bw//2, by2), (bx2+bw, by2+bh)], radius=14, fill=(*secondary, 255))
        btx = bx2+(bw-(bb_btn[2]-bb_btn[0]))//2
        bty = by2+(bh-(bb_btn[3]-bb_btn[1]))//2
        d.text((btx, bty), cta_text, font=f_btn, fill=(*WHITE, 255))

        bb_url = d.textbbox((0, 0), brand["website"], font=f_url)
        ux = (W-(bb_url[2]-bb_url[0]))//2
        d.text((ux, by2+bh+28), brand["website"], font=f_url, fill=(*GRAY, 200))

    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


# ── Frame burner ─────────────────────────────────────────────────────

def burn_overlay(src, out, scene, brand):
    total = scene["duration_seconds"] * FPS
    reader = subprocess.Popen(
        [FFMPEG, "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-vframes", str(total), "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    writer = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
         "-s", f"{OUT_W}x{OUT_H}", "-pix_fmt", "rgb24",
         "-r", str(FPS), "-i", "pipe:0",
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "15", str(out)],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    frame_size = OUT_W * OUT_H * 3
    idx = 0
    try:
        while idx < total:
            raw = reader.stdout.read(frame_size)
            if len(raw) < frame_size:
                break
            img = Image.frombytes("RGB", (OUT_W, OUT_H), raw)
            img = build_overlay(img, scene, brand)
            writer.stdin.write(img.tobytes())
            idx += 1
    finally:
        reader.stdout.close()
        reader.terminate()
        writer.stdin.close()
        writer.wait()
    return writer.returncode == 0


# ── TTS ──────────────────────────────────────────────────────────────

async def _tts(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out))


def generate_voiceover(scenes, voice_dir, voice="en-US-AriaNeural"):
    files = []
    for i, sc in enumerate(scenes):
        out = voice_dir / f"scene_{i+1}.mp3"
        asyncio.run(_tts(sc["voiceover"], voice, out))
        files.append(out)
    list_f = voice_dir / "files.txt"
    with open(list_f, "w") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")
    merged = voice_dir / "voiceover.mp3"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_f), "-c", "copy", str(merged)],
                   capture_output=True)
    return merged


# ── Assemble ─────────────────────────────────────────────────────────

def assemble(clips, audio, output, tmp_dir):
    list_f = tmp_dir / "clips.txt"
    with open(list_f, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")
    merged = tmp_dir / "merged.mp4"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_f),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "medium", "-crf", "15", str(merged)],
                   capture_output=True)
    rp = subprocess.run([FFPROBE, "-v", "quiet", "-print_format", "json",
                         "-show_format", str(merged)],
                        capture_output=True, text=True)
    vid_dur = float(json.loads(rp.stdout)["format"]["duration"])
    with_audio = tmp_dir / "with_audio.mp4"
    subprocess.run([FFMPEG, "-y", "-i", str(merged), "-i", str(audio),
                    "-filter_complex", f"[1:a]apad=whole_dur={vid_dur}[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", str(vid_dur), str(with_audio)],
                   capture_output=True)
    shutil.copy(str(with_audio), str(output))
    return vid_dur


def export_formats(src, out_dir, slug):
    results = {}
    fmts = {"16x9": (1920,1080), "9x16": (1080,1920), "1x1": (1080,1080)}
    for label, (w, h) in fmts.items():
        out = out_dir / f"{slug}_{label}.mp4"
        vf  = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1")
        subprocess.run([FFMPEG, "-y", "-i", str(src), "-vf", vf,
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                        "-c:a", "aac", "-b:a", "192k", str(out)],
                       capture_output=True)
        results[label] = out.name
    return results


# ── Main runner (yields progress strings) ────────────────────────────

def run_pipeline(job_dir: Path, script: dict, brand: dict):
    """
    Yields progress strings. Saves final video to job_dir/final.mp4
    and format variants to job_dir/*.mp4
    """
    scenes   = script["scenes"]
    raw_dir  = job_dir / "raw"
    proc_dir = job_dir / "proc"
    voice_dir= job_dir / "voice"
    for d in [raw_dir, proc_dir, voice_dir]:
        d.mkdir(parents=True, exist_ok=True)

    final_clips = []

    for scene in scenes:
        n   = scene["scene_number"]
        lbl = scene["label"]
        dur = scene["duration_seconds"]

        yield f"[{n}/4] Searching clip for {lbl} scene..."

        raw  = raw_dir  / f"raw_{n}.mp4"
        trim = raw_dir  / f"trim_{n}.mp4"
        proc = proc_dir / f"proc_{n}.mp4"

        info = search_pexels(scene["pexels_queries"], dur)
        if not info:
            yield f"[ERROR] No clip found for scene {n}"; return
        yield f"[{n}/4] Found clip id={info['id']} ({info['width']}x{info['height']})  Downloading..."

        if not download_video(info["url"], raw):
            yield f"[ERROR] Download failed for scene {n}"; return
        yield f"[{n}/4] Trimming to {dur}s..."

        if not trim_clip(raw, trim, dur):
            yield f"[ERROR] Trim failed for scene {n}"; return
        yield f"[{n}/4] Burning {lbl} overlay..."

        if not burn_overlay(trim, proc, scene, brand):
            yield f"[ERROR] Overlay failed for scene {n}"; return
        yield f"[{n}/4] Scene {lbl} done."

        final_clips.append(proc)

    yield "[5/6] Generating voiceover..."
    audio = generate_voiceover(scenes, voice_dir, brand.get("voice_id", "en-US-AriaNeural"))

    yield "[6/6] Assembling final video..."
    final = job_dir / "final.mp4"
    assemble(final_clips, audio, final, job_dir)

    yield "[6/6] Exporting formats..."
    slug = brand["name"].lower().replace(" ", "_")
    formats = export_formats(final, job_dir, slug)

    # Clean up temp files — keep only finals
    for tmp in [job_dir / "clips.txt", job_dir / "merged.mp4", job_dir / "with_audio.mp4"]:
        tmp.unlink(missing_ok=True)
    shutil.rmtree(raw_dir,   ignore_errors=True)
    shutil.rmtree(proc_dir,  ignore_errors=True)
    shutil.rmtree(voice_dir, ignore_errors=True)

    yield f"DONE|{json.dumps(formats)}"
