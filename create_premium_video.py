"""Create Premium Final Video"""
import subprocess
import shutil
from pathlib import Path
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FFMPEG = r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

OUTPUT = Path("output")
SCENE_DIR = OUTPUT / "scene_images"
VOICE_DIR = OUTPUT / "voice"

def create_clip(img_path, clip_path, duration, effect="zoom_in"):
    """Create video clip with Ken Burns effect"""
    if effect == "zoom_in":
        vf = "scale=1920:1080,zoompan=z='min(zoom+0.004,1.3)':d=25:s=1920x1080:fps=24"
    elif effect == "zoom_out":
        vf = "scale=1920:1080,zoompan=z='max(zoom-0.003,1.0)':d=25:s=1920x1080:fps=24"
    elif effect == "pan_right":
        vf = "scale=1920:1080,crop=1920:1080:(iw-1920)*t/60:0"
    else:
        vf = "scale=1920:1080,crop=1920:1080:(iw-1920)*(1-t/60):0"
    
    cmd = [FFMPEG, "-y", "-loop", "1", "-i", str(img_path), "-vf", vf, "-t", str(duration), "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", str(clip_path)]
    subprocess.run(cmd, capture_output=True)

def main():
    print("=" * 60)
    print(" CREATING PREMIUM FINAL VIDEO")
    print("=" * 60)
    
    scenes = [
        ("scene_1_premium.png", 5, "zoom_in"),
        ("scene_2_premium.png", 7, "zoom_out"),
        ("scene_3_premium.png", 10, "pan_right"),
        ("scene_4_premium.png", 8, "zoom_in"),
    ]
    
    clips = []
    for i, (img, duration, effect) in enumerate(scenes):
        img_path = SCENE_DIR / img
        clip_path = OUTPUT / f"clip_{i+1}.mp4"
        print(f"\nScene {i+1}: Creating clip...")
        create_clip(img_path, clip_path, duration, effect)
        clips.append(clip_path)
        print(f"   Done: {clip_path.name}")
    
    # Create clips list
    list_file = OUTPUT / "clips.txt"
    with open(list_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")
    
    # Merge clips
    merged = OUTPUT / "merged_premium.mp4"
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(merged)]
    subprocess.run(cmd, capture_output=True)
    print(f"\n[MERGED] {merged.name}")
    
    # Add audio
    audio = VOICE_DIR / "voiceover.mp3"
    with_audio = OUTPUT / "with_audio_premium.mp4"
    cmd = [FFMPEG, "-y", "-i", str(merged), "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-shortest", str(with_audio)]
    subprocess.run(cmd, capture_output=True)
    print(f"[AUDIO] Added")
    
    # Burn subtitles
    srt = VOICE_DIR / "subtitles.srt"
    shutil.copy(str(srt), str(OUTPUT / "subtitles.srt"))
    final = OUTPUT / "premium_final.mp4"
    cmd = [FFMPEG, "-y", "-i", str(with_audio), "-vf", f"subtitles={str(OUTPUT / 'subtitles.srt')}", "-c:v", "libx264", "-crf", "18", "-c:a", "copy", str(final)]
    subprocess.run(cmd, capture_output=True)
    print(f"[FINAL] {final.name}")
    
    # Pad to 30 seconds
    padded = OUTPUT / "premium_final_30s.mp4"
    cmd = [FFMPEG, "-y", "-i", str(final), "-i", str(audio), "-filter_complex", "[1:a]apad=whole_dur=30[aout]", "-map", "0:v", "-map", "[aout]", "-t", "30", "-c:v", "copy", "-c:a", "aac", str(padded)]
    subprocess.run(cmd, capture_output=True)
    print(f"[30S VERSION] {padded.name}")
    
    # Copy to demo
    shutil.copy(str(padded), "demo/premium_final_30s.mp4")
    print(f"\n[DEMO] demo/premium_final_30s.mp4")
    
    print("\n" + "=" * 60)
    print(" PREMIUM VIDEO COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
