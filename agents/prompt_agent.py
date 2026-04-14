"""
Stage 4 — Scene Prompt Creation Agent
Uses Groq (free LLM) to convert script scenes into cinematic visual prompts.
Outputs: output/scene_prompts.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    OUTPUT_DIR,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_FALLBACK_MODEL,
    ensure_dirs,
)

try:
    from groq import Groq
except ImportError:
    print("❌ Please install groq: pip install groq")
    sys.exit(1)


PROMPT_TEMPLATE = """You are a creative director creating visual prompts for AI image generators.

The goal is to create a COMPELLING ADVERTISEMENT that looks professional and sells the product.

Script scenes:
{scenes_json}

Product: {product_name}
Brand Colors: {brand_colors}

IMPORTANT RULES:
1. Create CLEAR, SPECIFIC prompts that describe EXACTLY what should appear
2. Use simple, direct language - AI generators understand "a person at desk with multiple screens" better than "synergy optimization"
3. Describe REAL scenes - people, objects, settings, not abstract concepts
4. Include style: "commercial photography, professional, high quality, bright lighting"
5. Describe backgrounds and settings clearly
6. Use brand colors in the scene descriptions

Return ONLY valid JSON:
{{
  "scenes": [
    {{
      "scene_id": <number>,
      "video_prompt": "<clear visual description for AI image generator>",
      "on_screen_text": "<short text to show on screen>",
      "duration_seconds": <number>
    }}
  ]
}}

Examples of GOOD prompts:
- "stressed business owner at cluttered desk with four screens showing Instagram Facebook Twitter LinkedIn, dark moody lighting, professional commercial photography"
- "happy entrepreneur at clean desk with laptop showing simple dashboard, bright natural window light, professional photo"
- "diverse small business owners smiling at phones and laptops in modern co-working space, bright warm lighting, authentic commercial style"
- "clean modern laptop screen with big button that says Get Started, minimalist white desk, soft gradient background in blue and white, professional product photography"
"""


def generate_prompts(script: dict, brief: dict, max_retries: int = 3) -> dict:
    """Generate scene prompts using Groq LLM."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env file")

    client = Groq(api_key=GROQ_API_KEY)

    prompt = PROMPT_TEMPLATE.format(
        scenes_json=json.dumps(script["scenes"], indent=2),
        product_name=brief.get("product_name", ""),
        brand_colors=", ".join(brief.get("brand_colors", [])),
    )

    model = GROQ_MODEL
    for attempt in range(max_retries):
        try:
            print(f"   🤖 Creating visual prompts using {model}...")

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            result = json.loads(raw)

            if "scenes" in result and len(result["scenes"]) > 0:
                return result

            print("   ⚠️  Response missing 'scenes' array")

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Invalid JSON: {e}")
            if attempt == 1:
                model = GROQ_FALLBACK_MODEL
        except Exception as e:
            print(f"   ⚠️  API error: {e}")
            if attempt == 1:
                model = GROQ_FALLBACK_MODEL

    raise RuntimeError("Failed to generate scene prompts after all retries")


def run(script: dict = None, brief: dict = None) -> dict:
    """Run the Prompt Agent."""
    ensure_dirs()

    # Load script if not provided
    if script is None:
        script_path = OUTPUT_DIR / "script.json"
        if not script_path.exists():
            raise FileNotFoundError(
                f"Script not found at {script_path}. Run Stage 2 first."
            )
        with open(script_path, "r", encoding="utf-8") as f:
            script = json.load(f)

    # Load brief if not provided
    if brief is None:
        brief_path = OUTPUT_DIR / "brief.json"
        if not brief_path.exists():
            raise FileNotFoundError(
                f"Brief not found at {brief_path}. Run Stage 1 first."
            )
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)

    print("\n" + "=" * 60)
    print("  🎨  Stage 4 — Scene Prompt Creation (Groq LLM)")
    print("=" * 60)

    prompts = generate_prompts(script, brief)

    # Save
    output_path = OUTPUT_DIR / "scene_prompts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2)

    print(f"\n✅ Scene prompts generated: {output_path}")
    for s in prompts["scenes"]:
        print(f"   Scene {s['scene_id']}: {s.get('video_prompt', 'N/A')[:70]}...")

    return prompts


if __name__ == "__main__":
    run()
