"""
LLM Client - Supports NVIDIA Nemotron and Groq Llama
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import NVIDIA_API_KEY, GROQ_API_KEY, LLM_PROVIDER


def get_llm_client():
    """Get the configured LLM client"""
    if LLM_PROVIDER == "nvidia" and NVIDIA_API_KEY:
        from openai import OpenAI

        return OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY
        ), "nvidia/nemotron-3-super-120b-a12b"
    else:
        from groq import Groq

        return Groq(api_key=GROQ_API_KEY), "llama-3.3-70b-versatile"


def generate_with_llm(
    prompt: str, max_tokens: int = 2048, temperature: float = 0.7
) -> str:
    """Generate text using configured LLM"""
    client, model = get_llm_client()

    if "nemotron" in model:
        # NVIDIA
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    else:
        # Groq
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
