"""
Stage 2 — Script Generation Agent
Uses Groq (free LLM) to generate a structured ad script from the brief.
Outputs: output/script.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, GROQ_API_KEY, GROQ_MODEL, GROQ_FALLBACK_MODEL, ensure_dirs

try:
    from groq import Groq
except ImportError:
    print("❌ Please install groq: pip install groq")
    sys.exit(1)


PROMPT_TEMPLATE = """You are a professional ad copywriter. Given the following campaign brief, generate a structured {duration}-second video ad script.

Brief:
{brief_json}

Return ONLY valid JSON matching this exact schema (no markdown, no explanation):
{{
  "total_duration_seconds": {duration},
  "scenes": [
    {{
      "scene_id": 1,
      "duration_seconds": <number>,
      "voiceover": "<narration text, under 20 words>",
      "on_screen_text": "<short text shown on screen>",
      "visual_description": "<what the viewer sees>"
    }}
  ]
}}

Requirements:
- Hook the viewer in the first 3 seconds
- Keep each scene voiceover under 20 words
- End with a clear CTA matching: {cta}
- Tone: {tone}
- Scene durations MUST add up to exactly {duration} seconds
- Generate 4-6 scenes depending on duration
- Each visual_description should be detailed enough for AI image generation
"""


def validate_script(script: dict, expected_duration: int) -> list[str]:
    """Validate the generated script."""
    errors = []

    if "scenes" not in script or not script["scenes"]:
        errors.append("Script must contain 'scenes' array")
        return errors

    total = sum(s.get("duration_seconds", 0) for s in script["scenes"])
    if abs(total - expected_duration) > 2:  # Allow 2s tolerance
        errors.append(f"Scene durations sum to {total}s, expected {expected_duration}s")

    for i, scene in enumerate(script["scenes"]):
        required = ["scene_id", "duration_seconds", "voiceover", "on_screen_text", "visual_description"]
        for field in required:
            if field not in scene:
                errors.append(f"Scene {i+1} missing field: {field}")

        vo = scene.get("voiceover", "")
        if len(vo.split()) > 25:
            errors.append(f"Scene {i+1} voiceover too long ({len(vo.split())} words)")

    return errors


def generate_script(brief: dict, max_retries: int = 3) -> dict:
    """Generate script using Groq LLM."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env file")

    client = Groq(api_key=GROQ_API_KEY)
    duration = brief["ad_duration_seconds"]

    prompt = PROMPT_TEMPLATE.format(
        duration=duration,
        brief_json=json.dumps(brief, indent=2),
        cta=brief.get("cta", ""),
        tone=brief.get("tone", "professional"),
    )

    model = GROQ_MODEL
    for attempt in range(max_retries):
        try:
            print(f"   🤖 Attempt {attempt+1}/{max_retries} using {model}...")

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            script = json.loads(raw)

            # Validate
            errors = validate_script(script, duration)
            if not errors:
                return script

            print(f"   ⚠️  Validation issues: {errors}")
            if attempt < max_retries - 1:
                prompt += "\n\nIMPORTANT: Fix these issues: " + "; ".join(errors)

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Invalid JSON response: {e}")
            if attempt == 1:
                model = GROQ_FALLBACK_MODEL
                print(f"   🔄 Switching to fallback model: {model}")
        except Exception as e:
            print(f"   ⚠️  API error: {e}")
            if attempt == 1:
                model = GROQ_FALLBACK_MODEL

    raise RuntimeError("Failed to generate valid script after all retries")


def run(brief: dict = None) -> dict:
    """Run the Script Agent."""
    ensure_dirs()

    # Load brief if not provided
    if brief is None:
        brief_path = OUTPUT_DIR / "brief.json"
        if not brief_path.exists():
            raise FileNotFoundError(f"Brief not found at {brief_path}. Run Stage 1 first.")
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)

    print("\n" + "=" * 60)
    print("  ✍️  Stage 2 — Generating Ad Script (Groq LLM)")
    print("=" * 60)
    print(f"   Product: {brief['product_name']}")
    print(f"   Duration: {brief['ad_duration_seconds']}s")
    print(f"   Tone: {brief['tone']}")

    script = generate_script(brief)

    # Save
    output_path = OUTPUT_DIR / "script.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2)

    print(f"\n✅ Script generated: {output_path}")
    print(f"   Scenes: {len(script['scenes'])}")
    for s in script["scenes"]:
        print(f"   Scene {s['scene_id']} ({s['duration_seconds']}s): {s['voiceover'][:50]}...")

    return script


if __name__ == "__main__":
    run()
