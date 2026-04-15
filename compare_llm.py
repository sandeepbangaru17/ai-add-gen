"""
Compare NVIDIA vs Groq for script generation
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import NVIDIA_API_KEY, GROQ_API_KEY


def test_nvidia_script():
    """Generate script using NVIDIA Nemotron"""
    from openai import OpenAI

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY
    )

    prompt = """Create a 30-second ad script for "ZunoSync" - an AI tool that helps small businesses manage social media from one dashboard.

Target: Small business owners and startups
Tone: Professional and slightly emotional
Platforms: Instagram, YouTube

Create 4 scenes with:
- scene_id, duration_seconds, voiceover, on_screen_text, visual_description

Return ONLY valid JSON in this format:
{
  "total_duration_seconds": 30,
  "scenes": [...]
}

Make the script compelling and emotional."""

    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
    )

    return response.choices[0].message.content


def test_groq_script():
    """Generate script using Groq Llama"""
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)

    prompt = """Create a 30-second ad script for "ZunoSync" - an AI tool that helps small businesses manage social media from one dashboard.

Target: Small business owners and startups
Tone: Professional and slightly emotional
Platforms: Instagram, YouTube

Create 4 scenes with:
- scene_id, duration_seconds, voiceover, on_screen_text, visual_description

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content


print("=" * 60)
print("NVIDIA Nemotron Script:")
print("=" * 60)
try:
    nvidia_result = test_nvidia_script()
    print(nvidia_result)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Groq Llama Script:")
print("=" * 60)
try:
    groq_result = test_groq_script()
    print(groq_result)
except Exception as e:
    print(f"Error: {e}")
