"""
Stage 7 — Post-Processing Agent
Resizes video for all target platforms using FFmpeg.
Outputs: Platform-specific video files
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, FFMPEG_BIN, ensure_dirs


# Platform export specs from the spec document
EXPORT_FORMATS = {
    "vertical": {
        "resolution": "1080:1920",
        "aspect": "9:16",
        "suffix": "9x16_reels",
        "platforms": "Instagram Reels, TikTok, YouTube Shorts",
    },
    "square": {
        "resolution": "1080:1080",
        "aspect": "1:1",
        "suffix": "1x1_feed",
        "platforms": "Instagram Feed, Facebook",
    },
    "landscape": {
        "resolution": "1920:1080",
        "aspect": "16:9",
        "suffix": "16x9_youtube",
        "platforms": "YouTube, LinkedIn",
    },
}


def resize_video(input_path: Path, output_path: Path, resolution: str) -> bool:
    """Resize video to target resolution with padding."""
    w, h = resolution.split(":")

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(input_path),
        "-vf", (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1"
        ),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        print(f"   ⚠️  Resize error: {result.stderr[:300]}")
        return False
    return True


def create_master_copy(input_path: Path, output_path: Path) -> bool:
    """Create high-quality master copy."""
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "256k",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return result.returncode == 0


def run(draft_path: Path = None) -> dict:
    """Run the Post Agent."""
    ensure_dirs()

    draft_path = draft_path or OUTPUT_DIR / "ad_draft.mp4"
    if not draft_path.exists():
        raise FileNotFoundError(f"Draft video not found at {draft_path}. Run Stage 6 first.")

    print("\n" + "=" * 60)
    print("  🎨  Stage 7 — Post-Processing & Platform Exports")
    print("=" * 60)

    # Load brief for product name
    product_name = "ad"
    brief_path = OUTPUT_DIR / "brief.json"
    if brief_path.exists():
        import json
        with open(brief_path, "r") as f:
            brief = json.load(f)
            product_name = brief.get("product_name", "ad").lower().replace(" ", "")

    exports = {}

    # Generate platform-specific versions
    for format_name, spec in EXPORT_FORMATS.items():
        output_path = OUTPUT_DIR / f"{product_name}_{spec['suffix']}.mp4"
        print(f"\n   📐 {format_name.upper()} ({spec['resolution']}) → {spec['platforms']}")

        if resize_video(draft_path, output_path, spec["resolution"]):
            exports[format_name] = str(output_path)
            print(f"   ✅ Exported: {output_path}")
        else:
            print(f"   ❌ Failed to export {format_name}")

    # Master copy
    master_path = OUTPUT_DIR / f"{product_name}_master_HD.mp4"
    print(f"\n   🏆 MASTER (1920x1080, high quality)")
    if create_master_copy(draft_path, master_path):
        exports["master"] = str(master_path)
        print(f"   ✅ Master: {master_path}")

    result = {
        "exports": exports,
        "product_name": product_name,
    }

    print(f"\n✅ Post-processing complete: {len(exports)} versions exported")
    return result


if __name__ == "__main__":
    run()
