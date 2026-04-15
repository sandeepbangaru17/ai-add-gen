"""
Test NVIDIA API for script/prompt generation
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import NVIDIA_API_KEY, GROQ_API_KEY, LLM_PROVIDER

# Test NVIDIA API
print("Testing NVIDIA API...")
print(f"Provider: {LLM_PROVIDER}")

if LLM_PROVIDER == "nvidia":
    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY
        )

        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'NVIDIA API is working!' in one sentence.",
                }
            ],
            temperature=0.5,
            max_tokens=100,
        )
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"NVIDIA Error: {e}")
else:
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Groq API is working!' in one sentence.",
                }
            ],
            max_tokens=100,
        )
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Groq Error: {e}")
