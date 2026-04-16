"""
AutoMail PREMIUM — Wan2.1 Local Assembly Pipeline
===================================================
Run AFTER downloading clips from Kaggle notebook.

Steps:
  1. Place Kaggle-generated clips in:  output/wan21_raw/
       scene_1_hook.mp4
       scene_2_solution.mp4
       scene_3_benefits.mp4
       scene_4_cta.mp4
  2. Run:  python automail_wan21_local.py
  3. Pipeline trims, overlays, adds voiceover, exports.
===================================================
"""

import io, json, sys, time, subprocess, shutil, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Directories ───────────────────────────────────────────────────────
BASE      = Path(__file__).parent
OUT       = BASE / "output"
WAN_RAW   = OUT  / "wan21_raw"
WAN_PROC  = OUT  / "wan21_proc"
VOICE     = OUT  / "voice"
DEMO      = BASE / "demo"
for d in [OUT, WAN_RAW, WAN_PROC, VOICE, DEMO]:
    d.mkdir(parents=True, exist_ok=True)

# ── FFmpeg ────────────────────────────────────────────────────────────
_FF = (
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1-full_build\bin"
)
FFMPEG  = str(Path(_FF) / "ffmpeg.exe")
FFPROBE = str(Path(_FF) / "ffprobe.exe")

# ── Brand ─────────────────────────────────────────────────────────────
ORANGE = (255, 107,  53)
WHITE  = (255, 255, 255)
GRAY   = (180, 180, 180)
OUT_W, OUT_H = 1920, 1080
FPS = 24

# ── Fonts ─────────────────────────────────────────────────────────────
def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

SEGOE_BLACK = "C:/Windows/Fonts/seguibl.ttf"
SEGOE_BOLD  = "C:/Windows/Fonts/segoeuib.ttf"

# ── Script ────────────────────────────────────────────────────────────
SCRIPT = [
    {
        "scene_number": 1, "label": "HOOK",     "duration_seconds": 5,
        "raw_file": "scene_1_hook.mp4",
        "voiceover": "You built something great. But no one's opening your emails.",
    },
    {
        "scene_number": 2, "label": "SOLUTION", "duration_seconds": 9,
        "raw_file": "scene_2_solution.mp4",
        "voiceover": "AutoMail uses AI to write personalized campaigns that actually get read — in minutes.",
    },
    {
        "scene_number": 3, "label": "BENEFITS", "duration_seconds": 11,
        "raw_file": "scene_3_benefits.mp4",
        "voiceover": "Three times higher open rates. Five hours saved every week. Real results — zero writing skills needed.",
    },
    {
        "scene_number": 4, "label": "CTA",      "duration_seconds": 5,
        "raw_file": "scene_4_cta.mp4",
        "voiceover": "Start free today. Your next campaign writes itself.",
    },
]


# ════════════════════════════════════════════════════════════════════
# Trim + Resize to exact duration at 1920x1080
# ════════════════════════════════════════════════════════════════════

def get_duration(path):
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except:
        return 0.0


def trim_and_resize(src, out, target_dur):
    src_dur = get_duration(src)
    if src_dur <= 0:
        print(f"   [ERR] Cannot read duration of {src}")
        return False

    fade  = 0.35
    loops = max(1, int(target_dur / src_dur) + 2) if src_dur < target_dur else 1

    vf = (
        f"loop={loops}:size=9999:start=0,"
        f"trim=duration={target_dur},"
        f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H},"
        f"setsar=1,"
        f"fade=in:st=0:d={fade},"
        f"fade=out:st={target_dur - fade}:d={fade}"
    )
    cmd = [
        FFMPEG, "-y", "-i", str(src),
        "-vf", vf, "-t", str(target_dur),
        "-r", str(FPS), "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "15",
        "-an", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   [ERR] {r.stderr[-300:]}")
        return False
    mb = out.stat().st_size / 1_048_576
    print(f"   [OK]  Resized: {out.name} ({mb:.1f} MB)")
    return True


# ════════════════════════════════════════════════════════════════════
# Premium Text Overlays
# ════════════════════════════════════════════════════════════════════

def _shadow(draw, pos, text, fnt, col=(0, 0, 0, 190), offset=4):
    for dx, dy in [(-offset, offset), (offset, offset), (0, offset + 1)]:
        draw.text((pos[0]+dx, pos[1]+dy), text, font=fnt, fill=col)


def overlay_hook(img):
    W, H = img.size
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(cv)
    d.rectangle([(0,0),(W,H)],    fill=(0,0,0,120))
    d.rectangle([(0,0),(W,6)],    fill=(*ORANGE,255))
    d.rectangle([(0,H-80),(W,H)], fill=(0,0,0,200))
    f1 = font(SEGOE_BOLD,  52)
    f2 = font(SEGOE_BLACK, 96)
    f3 = font(SEGOE_BOLD,  34)
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
    uw  = bb2[2]-bb2[0]
    d.rectangle([(x2,y2+(bb2[3]-bb2[1])+12),(x2+uw,y2+(bb2[3]-bb2[1])+20)], fill=(*ORANGE,230))
    brand = "AutoMail  ·  Write Less. Connect More. Grow Faster."
    bbb   = d.textbbox((0,0), brand, font=f3)
    bx    = (W-(bbb[2]-bbb[0]))//2
    by    = H-80+(80-(bbb[3]-bbb[1]))//2
    d.text((bx,by), brand, font=f3, fill=(*ORANGE,200))
    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_solution(img):
    W, H = img.size
    cv = Image.new("RGBA",(W,H),(0,0,0,0))
    d  = ImageDraw.Draw(cv)
    bar_h = 320
    for y in range(bar_h):
        t = y/bar_h
        d.rectangle([(0,H-bar_h+y),(W,H-bar_h+y+1)], fill=(8,10,20,int(235*(1-t)**1.3)))
    d.rectangle([(0,H-bar_h-5),(W,H-bar_h)], fill=(*ORANGE,255))
    f_big  = font(SEGOE_BLACK, 112)
    f_sub  = font(SEGOE_BOLD,   70)
    f_tag  = font(SEGOE_BOLD,   32)
    f_logo = font(SEGOE_BLACK,  42)
    t1,t2  = "AI emails.", "Written for you."
    bb1    = d.textbbox((0,0), t1, font=f_big)
    bb2    = d.textbbox((0,0), t2, font=f_sub)
    x1,y1  = 80, H-bar_h+28
    _shadow(d,(x1,y1),t1,f_big,offset=5)
    d.text((x1,y1), t1, font=f_big, fill=(*ORANGE,255))
    x2 = x1+(bb1[2]-bb1[0])+36
    y2 = y1+((bb1[3]-bb1[1])-(bb2[3]-bb2[1]))
    _shadow(d,(x2,y2),t2,f_sub,offset=4)
    d.text((x2,y2), t2, font=f_sub, fill=(*WHITE,255))
    d.text((x1,y1+(bb1[3]-bb1[1])+16), "Powered by AutoMail AI  ·  automail.ai", font=f_tag, fill=(*GRAY,175))
    lx,ly = W-260,34
    d.rounded_rectangle([(lx-12,ly-8),(lx+220,ly+52)], radius=8, fill=(0,0,0,150))
    d.text((lx,ly), "AutoMail", font=f_logo, fill=(*ORANGE,255))
    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_benefits(img):
    W, H = img.size
    cv = Image.new("RGBA",(W,H),(0,0,0,0))
    d  = ImageDraw.Draw(cv)
    bar_h = 290
    for y in range(bar_h):
        t = y/bar_h
        d.rectangle([(0,H-bar_h+y),(W,H-bar_h+y+1)], fill=(5,7,15,int(245*(1-t)**1.2)))
    d.rectangle([(0,H-bar_h-6),(W,H-bar_h)], fill=(*ORANGE,255))
    f_num  = font(SEGOE_BLACK, 105)
    f_lbl  = font(SEGOE_BOLD,   36)
    f_logo = font(SEGOE_BLACK,  40)
    METRICS = [("3x","Higher Open Rates"),("5hrs","Saved Every Week"),("Zero","Writing Skills Needed")]
    cw = W//3
    for i,(val,desc) in enumerate(METRICS):
        cx  = i*cw+cw//2
        bbv = d.textbbox((0,0), val,  font=f_num)
        bbd = d.textbbox((0,0), desc, font=f_lbl)
        vw,dw = bbv[2]-bbv[0], bbd[2]-bbd[0]
        yv = H-bar_h+18
        yd = yv+(bbv[3]-bbv[1])+10
        _shadow(d,(cx-vw//2,yv),val,f_num,offset=5)
        d.text((cx-vw//2,yv), val,  font=f_num, fill=(*ORANGE,255))
        d.text((cx-dw//2,yd), desc, font=f_lbl, fill=(*WHITE,215))
        if i<2:
            dx=(i+1)*cw
            d.rectangle([(dx-1,H-bar_h+14),(dx+1,H-18)], fill=(*ORANGE,90))
    lx,ly = W-252,34
    d.rounded_rectangle([(lx-12,ly-8),(lx+212,ly+50)], radius=8, fill=(0,0,0,150))
    d.text((lx,ly), "AutoMail", font=f_logo, fill=(*ORANGE,255))
    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


def overlay_cta(img):
    W, H = img.size
    cv = Image.new("RGBA",(W,H),(0,0,0,0))
    d  = ImageDraw.Draw(cv)
    d.rectangle([(0,0),(W,H)],  fill=(0,0,0,165))
    d.rectangle([(0,0),(W,6)],  fill=(*ORANGE,255))
    d.rectangle([(0,H-6),(W,H)],fill=(*ORANGE,255))
    f_brand = font(SEGOE_BLACK,108)
    f_tag   = font(SEGOE_BOLD,  46)
    f_btn   = font(SEGOE_BLACK, 62)
    f_url   = font(SEGOE_BOLD,  38)
    cy    = H//2-90
    brand = "AutoMail"
    bb_b  = d.textbbox((0,0), brand, font=f_brand)
    bx    = (W-(bb_b[2]-bb_b[0]))//2
    by    = cy-(bb_b[3]-bb_b[1])-18
    _shadow(d,(bx,by),brand,f_brand,offset=6)
    d.text((bx,by), brand, font=f_brand, fill=(*WHITE,255))
    tagline = "Write Less. Connect More. Grow Faster."
    bbt = d.textbbox((0,0), tagline, font=f_tag)
    tx  = (W-(bbt[2]-bbt[0]))//2
    ty  = by+(bb_b[3]-bb_b[1])+10
    d.text((tx,ty), tagline, font=f_tag, fill=(*GRAY,205))
    btn_text = "   START FREE TODAY   "
    bb_btn   = d.textbbox((0,0), btn_text, font=f_btn)
    bw  = bb_btn[2]-bb_btn[0]+60
    bh  = bb_btn[3]-bb_btn[1]+34
    bx2 = (W-bw)//2
    by2 = ty+(bbt[3]-bbt[1])+50
    d.rounded_rectangle([(bx2+6,by2+6),(bx2+bw+6,by2+bh+6)], radius=12, fill=(0,0,0,140))
    d.rounded_rectangle([(bx2,by2),(bx2+bw,by2+bh)],         radius=12, fill=(*ORANGE,255))
    btx = bx2+(bw-(bb_btn[2]-bb_btn[0]))//2
    bty = by2+(bh-(bb_btn[3]-bb_btn[1]))//2
    d.text((btx,bty), btn_text, font=f_btn, fill=(*WHITE,255))
    ux = (W-(d.textbbox((0,0),"automail.ai",font=f_url)[2]-d.textbbox((0,0),"automail.ai",font=f_url)[0]))//2
    d.text((ux,by2+bh+28), "automail.ai", font=f_url, fill=(*GRAY,195))
    return Image.alpha_composite(img.convert("RGBA"), cv).convert("RGB")


OVERLAY_FN = {
    "HOOK": overlay_hook, "SOLUTION": overlay_solution,
    "BENEFITS": overlay_benefits, "CTA": overlay_cta,
}


def burn_overlay(src, out, scene):
    label        = scene["label"]
    duration     = scene["duration_seconds"]
    total_frames = duration * FPS
    print(f"   [OVERLAY] Burning {label} — {total_frames} frames...")

    reader = subprocess.Popen(
        [FFMPEG, "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-vframes", str(total_frames), "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    writer = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
         "-s", f"{OUT_W}x{OUT_H}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "pipe:0",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "15",
         str(out)],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    frame_size = OUT_W * OUT_H * 3
    fn         = OVERLAY_FN[label]
    idx        = 0
    try:
        while idx < total_frames:
            raw = reader.stdout.read(frame_size)
            if len(raw) < frame_size:
                break
            img = Image.frombytes("RGB", (OUT_W, OUT_H), raw)
            writer.stdin.write(fn(img).tobytes())
            idx += 1
            if idx % 48 == 0:
                print(f"   [PROGRESS] {idx/total_frames*100:.0f}%")
    finally:
        reader.stdout.close(); reader.terminate()
        writer.stdin.close();  writer.wait()

    mb = out.stat().st_size / 1_048_576 if out.exists() else 0
    print(f"   [OK]  {out.name} ({mb:.1f} MB)")
    return writer.returncode == 0


# ════════════════════════════════════════════════════════════════════
# Voiceover
# ════════════════════════════════════════════════════════════════════

async def _tts(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out))


def generate_voiceover(scenes):
    voice = "en-US-AriaNeural"
    files = []
    for i, sc in enumerate(scenes):
        out = VOICE / f"wan21_scene_{i+1}.mp3"
        print(f"   [TTS] Scene {i+1}: {sc['voiceover'][:55]}...")
        asyncio.run(_tts(sc["voiceover"], voice, out))
        files.append(out)
    list_f = VOICE / "wan21_files.txt"
    merged = VOICE / "wan21_voiceover.mp3"
    with open(list_f, "w") as f:
        for p in files:
            f.write(f"file '{p.resolve()}'\n")
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_f), "-c", "copy", str(merged)],
        capture_output=True,
    )
    print(f"   [OK]  {merged.name}")
    return merged


# ════════════════════════════════════════════════════════════════════
# Assemble + Export
# ════════════════════════════════════════════════════════════════════

def assemble(clips, audio, output):
    list_f = OUT / "wan21_clips.txt"
    with open(list_f, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")
    merged = OUT / "wan21_merged.mp4"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_f),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "15",
         str(merged)], capture_output=True,
    )
    rp = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(merged)],
        capture_output=True, text=True,
    )
    vid_dur = float(json.loads(rp.stdout)["format"]["duration"])
    print(f"   [INFO] Video: {vid_dur:.2f}s")
    with_audio = OUT / "wan21_with_audio.mp4"
    subprocess.run(
        [FFMPEG, "-y", "-i", str(merged), "-i", str(audio),
         "-filter_complex", f"[1:a]apad=whole_dur={vid_dur}[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(vid_dur), str(with_audio)], capture_output=True,
    )
    shutil.copy(str(with_audio), str(output))
    return True


def export_formats(src):
    for label, (w, h) in {"16x9":(1920,1080), "9x16":(1080,1920), "1x1":(1080,1080)}.items():
        out = OUT / f"automail_wan21_{label}.mp4"
        vf  = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1")
        subprocess.run(
            [FFMPEG, "-y", "-i", str(src), "-vf", vf,
             "-c:v", "libx264", "-crf", "17", "-preset", "medium",
             "-c:a", "aac", "-b:a", "192k", str(out)], capture_output=True,
        )
        mb = out.stat().st_size / 1_048_576 if out.exists() else 0
        print(f"   [OK]  {label}: {out.name} ({mb:.1f} MB)")


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

def main():
    SEP = "=" * 64
    print(SEP)
    print("  AutoMail PREMIUM  —  Wan2.1 Local Assembly")
    print(SEP)

    # Check all raw clips exist
    missing = []
    for sc in SCRIPT:
        p = WAN_RAW / sc["raw_file"]
        if not p.exists():
            missing.append(sc["raw_file"])

    if missing:
        print("\n[ERROR] Missing Kaggle-generated clips in output/wan21_raw/:")
        for m in missing:
            print(f"  ✗ {m}")
        print("\nSteps:")
        print("  1. Open automail_wan21_kaggle.ipynb on Kaggle (GPU T4)")
        print("  2. Run all cells — takes ~15-20 min")
        print("  3. Download automail_wan21_clips.zip from Kaggle Output")
        print("  4. Extract the 4 .mp4 files into:  output/wan21_raw/")
        print("  5. Run this script again")
        return

    final_clips = []

    print(f"\n{SEP}")
    print("  STEP 1/4 — Trim + Resize Wan2.1 Clips to 1920x1080")
    print(SEP)

    for sc in SCRIPT:
        n         = sc["scene_number"]
        lbl       = sc["label"]
        raw_path  = WAN_RAW  / sc["raw_file"]
        trim_path = WAN_RAW  / f"wan21_trim_{n}.mp4"
        proc_path = WAN_PROC / f"wan21_proc_{n}.mp4"

        print(f"\n[Scene {n}] {lbl}  ({sc['duration_seconds']}s)")

        if not trim_path.exists():
            ok = trim_and_resize(raw_path, trim_path, sc["duration_seconds"])
            if not ok:
                print(f"   [FATAL] Trim failed for scene {n}"); return
        else:
            print(f"   [SKIP] Trimmed cached: {trim_path.name}")

        ok = burn_overlay(trim_path, proc_path, sc)
        if not ok:
            print(f"   [FATAL] Overlay failed"); return
        final_clips.append(proc_path)

    print(f"\n{SEP}")
    print("  STEP 2/4 — AriaNeural Voiceover")
    print(SEP)
    audio = generate_voiceover(SCRIPT)

    print(f"\n{SEP}")
    print("  STEP 3/4 — Assembling Final Video")
    print(SEP)
    final = OUT / "automail_wan21_final.mp4"
    assemble(final_clips, audio, final)
    mb = final.stat().st_size / 1_048_576
    print(f"\n   [MASTER] {final.name}  ({mb:.1f} MB)")

    print(f"\n{SEP}")
    print("  STEP 4/4 — Multi-Format Export")
    print(SEP)
    export_formats(final)

    demo = DEMO / "automail_wan21_premium.mp4"
    shutil.copy(str(final), str(demo))

    print(f"\n{SEP}")
    print("  WAN2.1 PIPELINE COMPLETE!")
    print(SEP)
    print(f"""
  Master 16:9  →  output/automail_wan21_final.mp4
  Widescreen   →  output/automail_wan21_16x9.mp4
  Reels/TikTok →  output/automail_wan21_9x16.mp4
  Square Post  →  output/automail_wan21_1x1.mp4
  Demo copy    →  demo/automail_wan21_premium.mp4
""")


if __name__ == "__main__":
    main()
