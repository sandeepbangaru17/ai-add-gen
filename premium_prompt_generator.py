"""
Premium Scene Prompt Generator
Creates cinematic, professional prompts for AI image generation
"""

import json
import sys
from pathlib import Path

# Windows encoding fix
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from config import NVIDIA_API_KEY, LLM_PROVIDER

try:
    from openai import OpenAI
    from groq import Groq
except ImportError:
    print("❌ Please install: pip install openai groq")
    sys.exit(1)


PREMIUM_PROMPT_TEMPLATE = """You are a professional cinematographer creating prompts for AI image generation.

Create CLEAR, DETAILED prompts for a premium 30-second advertisement.

Script:
{scenes_json}

Product: {product_name}
Brand Colors: {brand_colors}

RULES:
1. Each prompt MUST include: subject, setting/background, lighting, camera style
2. Use: "professional photography, 4K, sharp focus, commercial quality"
3. Describe REAL people with real emotions - not abstract
4. Lighting: mention "warm golden light" or "natural daylight" or "cinematic lighting"
5. Camera: mention "shallow depth of field" or "close-up" or "medium shot"
6. Background: describe specific setting, not vague
7. Brand colors should be present but subtle

Output JSON format:
{{
  "scenes": [
    {{
      "scene_id": 1,
      "video_prompt": "<clear cinematic description for AI image generator>",
      "on_screen_text": "<short bold text>",
      "duration_seconds": <number>
    }}
  ]
}}

BAD Examples (too vague):
- "business person working"
- "social media dashboard"
- "happy team"

GOOD Examples (clear and detailed):
- "tired entrepreneur at midnight desk with glowing phone screens showing Instagram Facebook Twitter apps, multiple devices charging, scattered business papers, moody dark office lighting with blue screen glow, shallow depth of field, professional portrait photography, 4K sharp focus"
- "clean modern laptop displaying elegant ZunoSync dashboard interface with colorful social media icons, content calendar visible, young smiling entrepreneur in background soft focus, bright sunlit office with green plants, professional commercial photography, warm natural lighting"
- "business owner at modern standing desk checking rising engagement graphs on laptop screen, analytics dashboard with upward trending purple and white charts, confident smile, minimalist white office, golden hour sunlight streaming through window, lifestyle product photography"
"""


def generate_premium_prompts(script_path: str, output_path: str = None):
    """Generate premium visual prompts using NVIDIA."""
    with open(script_path, "r") as f:
        script = json.load(f)

    # Get client
    if LLM_PROVIDER == "nvidia" and NVIDIA_API_KEY:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY
        )
        model = "nvidia/nemotron-3-super-120b-a12b"
    else:
        client = Groq(api_key="")
        model = "llama-3.3-70b-versatile"

    prompt = PREMIUM_PROMPT_TEMPLATE.format(
        scenes_json=json.dumps(script["scenes"], indent=2),
        product_name=script.get("product_name", ""),
        brand_colors=", ".join(script.get("brand_colors", [])),
    )

    print("[PROMPT] Generating premium visual prompts...")

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=2048,
            )

            raw = response.choices[0].message.content.strip()

            # Try to fix JSON if needed
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            result = json.loads(raw)
            break
        except json.JSONDecodeError as e:
            print(f"[RETRY] Attempt {attempt + 1}: JSON error - {e}")
            if attempt == 2:
                # Fallback: create prompts from script
                result = {"scenes": []}
                for scene in script["scenes"]:
                    result["scenes"].append(
                        {
                            "scene_id": scene["scene_id"],
                            "video_prompt": scene["visual_description"],
                            "on_screen_text": scene["on_screen_text"],
                            "duration_seconds": scene["duration_seconds"],
                        }
                    )

    # Save
    if output_path is None:
        output_path = script_path.replace(".json", "_prompts.json")

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[OK] Premium prompts saved to: {output_path}")
    return result


if __name__ == "__main__":
    script = "premium_script.json"
    if len(sys.argv) > 1:
        script = sys.argv[1]
    generate_premium_prompts(script)
