"""
Stage 1 — Ad Brief Input Agent
Collects and validates the campaign brief from the user.
Outputs: output/brief.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, ensure_dirs


# ─── Validation Rules (from spec) ────────────────────────────────────
VALID_DURATIONS = [15, 30, 60]
MAX_CTA_LENGTH = 60


def validate_brief(brief: dict) -> list[str]:
    """Validate brief against spec rules. Returns list of errors."""
    errors = []

    required = ["product_name", "target_audience", "ad_duration_seconds",
                 "tone", "platform", "cta"]
    for field in required:
        if field not in brief or not brief[field]:
            errors.append(f"Missing required field: {field}")

    if brief.get("ad_duration_seconds") not in VALID_DURATIONS:
        errors.append(f"ad_duration_seconds must be one of {VALID_DURATIONS}")

    if not isinstance(brief.get("platform"), list) or len(brief.get("platform", [])) == 0:
        errors.append("platform must be a non-empty array")

    if len(brief.get("cta", "")) > MAX_CTA_LENGTH:
        errors.append(f"cta must not exceed {MAX_CTA_LENGTH} characters")

    return errors


def collect_brief_interactive() -> dict:
    """Collect brief from user via interactive CLI prompts."""
    print("\n" + "=" * 60)
    print("  🎬  AI AD CREATION PIPELINE — Campaign Brief")
    print("=" * 60 + "\n")

    brief = {}
    brief["product_name"] = input("Product Name: ").strip() or "ZunoSync"
    brief["tagline"] = input("Tagline (optional): ").strip() or ""
    brief["target_audience"] = input("Target Audience: ").strip() or "Small business owners"

    while True:
        dur = input("Ad Duration (15, 30, or 60 seconds) [30]: ").strip() or "30"
        if int(dur) in VALID_DURATIONS:
            brief["ad_duration_seconds"] = int(dur)
            break
        print(f"  ❌ Must be one of {VALID_DURATIONS}")

    brief["tone"] = input("Tone (e.g., professional, energetic): ").strip() or "professional, energetic"

    platforms = input("Platforms (comma-separated, e.g., Instagram Reel, YouTube Ad): ").strip()
    brief["platform"] = [p.strip() for p in platforms.split(",")] if platforms else ["Instagram Reel", "YouTube Ad"]

    brief["cta"] = input("Call to Action (max 60 chars): ").strip() or "Try free for 14 days"

    colors = input("Brand Colors (comma-separated hex, e.g., #1A1AFF, #FFFFFF): ").strip()
    brief["brand_colors"] = [c.strip() for c in colors.split(",")] if colors else ["#1A1AFF", "#FFFFFF"]

    brief["logo_url"] = input("Logo URL (optional): ").strip() or ""

    return brief


def load_brief_from_file(filepath: str) -> dict:
    """Load an existing brief from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_default_brief() -> dict:
    """Return the ZunoSync test brief from the spec."""
    return {
        "product_name": "ZunoSync",
        "tagline": "Your AI marketing team in one click",
        "target_audience": "Small business owners",
        "ad_duration_seconds": 30,
        "tone": "professional, energetic",
        "platform": ["Instagram Reel", "YouTube Ad"],
        "cta": "Try ZunoSync free for 14 days",
        "brand_colors": ["#1A1AFF", "#FFFFFF"],
        "logo_url": "https://cdn.example.com/zunosync-logo.png"
    }


def run(brief_path: str = None, use_default: bool = False) -> dict:
    """
    Run the Brief Agent.
    - If brief_path is provided, load from file
    - If use_default is True, use the ZunoSync test brief
    - Otherwise, collect interactively
    """
    ensure_dirs()

    if brief_path:
        print(f"📄 Loading brief from: {brief_path}")
        brief = load_brief_from_file(brief_path)
    elif use_default:
        print("📄 Using default ZunoSync test brief")
        brief = get_default_brief()
    else:
        brief = collect_brief_interactive()

    # Validate
    errors = validate_brief(brief)
    if errors:
        print("\n❌ Brief validation failed:")
        for e in errors:
            print(f"   • {e}")
        raise ValueError("Brief validation failed")

    # Save
    output_path = OUTPUT_DIR / "brief.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(brief, f, indent=2)

    print(f"\n✅ Brief saved to: {output_path}")
    print(f"   Product: {brief['product_name']}")
    print(f"   Duration: {brief['ad_duration_seconds']}s")
    print(f"   Platforms: {', '.join(brief['platform'])}")

    return brief


if __name__ == "__main__":
    run(use_default=True)
