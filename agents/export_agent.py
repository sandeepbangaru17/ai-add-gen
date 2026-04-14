"""
Stage 8 — Final Export & Distribution Agent
Packages all deliverables into the spec-defined output directory structure.
Outputs: final_output/ directory with master, social, assets, metadata
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    OUTPUT_DIR, FINAL_OUTPUT_DIR, MASTER_DIR, SOCIAL_DIR,
    ASSETS_OUT_DIR, METADATA_DIR, VOICE_DIR, FFMPEG_BIN, ensure_dirs,
)


def generate_thumbnail(video_path: Path, output_path: Path) -> bool:
    """Extract a thumbnail from the video at the 3-second mark."""
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(video_path),
        "-ss", "3",
        "-vframes", "1",
        "-q:v", "2",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0


def create_production_log(stages_status: dict = None) -> dict:
    """Create a production log with timestamps and pipeline status."""
    log = {
        "pipeline_version": "1.0",
        "created_at": datetime.now().isoformat(),
        "tool_stack": {
            "llm": "Groq (Llama 3.3 70B) — Free Tier",
            "tts": "edge-tts (Microsoft Edge Neural Voices) — Free",
            "image_gen": "Hugging Face Inference API (SDXL) — Free",
            "video_effects": "FFmpeg Ken Burns — Open Source",
            "video_processing": "FFmpeg — Open Source",
        },
        "stages": stages_status or {
            "stage_1_brief": "completed",
            "stage_2_script": "completed",
            "stage_3_voice": "completed",
            "stage_4_prompts": "completed",
            "stage_5_video": "completed",
            "stage_6_stitch": "completed",
            "stage_7_post": "completed",
            "stage_8_export": "completed",
        },
    }
    return log


def run(exports: dict = None) -> dict:
    """Run the Export Agent."""
    ensure_dirs()

    print("\n" + "=" * 60)
    print("  📦  Stage 8 — Final Export & Distribution")
    print("=" * 60)

    # Load brief for naming
    product_name = "ad"
    brief_path = OUTPUT_DIR / "brief.json"
    if brief_path.exists():
        with open(brief_path, "r") as f:
            brief = json.load(f)
            product_name = brief.get("product_name", "ad").lower().replace(" ", "")

    # ── Copy master ──
    print("\n   📁 Organizing master copy...")
    master_src = OUTPUT_DIR / f"{product_name}_master_HD.mp4"
    if master_src.exists():
        master_dst = MASTER_DIR / f"{product_name}_ad_master_HD.mp4"
        shutil.copy2(str(master_src), str(master_dst))
        print(f"   ✅ {master_dst}")

    # ── Copy social exports ──
    print("\n   📁 Organizing social exports...")
    social_files = {
        f"{product_name}_9x16_reels.mp4": f"{product_name}_ad_9x16_reels.mp4",
        f"{product_name}_1x1_feed.mp4": f"{product_name}_ad_1x1_feed.mp4",
        f"{product_name}_16x9_youtube.mp4": f"{product_name}_ad_16x9_youtube.mp4",
    }
    for src_name, dst_name in social_files.items():
        src = OUTPUT_DIR / src_name
        if src.exists():
            dst = SOCIAL_DIR / dst_name
            shutil.copy2(str(src), str(dst))
            print(f"   ✅ {dst}")

    # ── Copy assets (thumbnail + subtitles) ──
    print("\n   📁 Organizing assets...")

    # Generate thumbnail
    thumb_path = ASSETS_OUT_DIR / "thumbnail.png"
    draft_path = OUTPUT_DIR / "ad_draft.mp4"
    if draft_path.exists():
        if generate_thumbnail(draft_path, thumb_path):
            print(f"   ✅ Thumbnail: {thumb_path}")

    # Copy subtitles
    srt_src = VOICE_DIR / "subtitles.srt"
    if srt_src.exists():
        srt_dst = ASSETS_OUT_DIR / "subtitles.srt"
        shutil.copy2(str(srt_src), str(srt_dst))
        print(f"   ✅ Subtitles: {srt_dst}")

    # ── Copy metadata ──
    print("\n   📁 Organizing metadata...")
    metadata_files = ["brief.json", "script.json", "scene_prompts.json"]
    for mf in metadata_files:
        src = OUTPUT_DIR / mf
        if src.exists():
            dst = METADATA_DIR / mf
            shutil.copy2(str(src), str(dst))
            print(f"   ✅ {dst}")

    # Production log
    prod_log = create_production_log()
    log_path = METADATA_DIR / "production_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(prod_log, f, indent=2)
    print(f"   ✅ Production log: {log_path}")

    # ── Summary ──
    result = {
        "final_output_dir": str(FINAL_OUTPUT_DIR),
        "production_log": str(log_path),
    }

    print(f"\n{'=' * 60}")
    print(f"  🎉  PIPELINE COMPLETE!")
    print(f"{'=' * 60}")
    print(f"\n   📂 All deliverables in: {FINAL_OUTPUT_DIR}")
    print(f"\n   Directory structure:")

    # Print tree
    for p in sorted(FINAL_OUTPUT_DIR.rglob("*")):
        rel = p.relative_to(FINAL_OUTPUT_DIR)
        indent = "   " * (len(rel.parts))
        if p.is_file():
            size_kb = p.stat().st_size / 1024
            print(f"      {indent}📄 {p.name} ({size_kb:.0f} KB)")
        else:
            print(f"      {indent}📁 {p.name}/")

    return result


if __name__ == "__main__":
    run()
