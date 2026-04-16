"""
script_generator.py — Uses Groq LLM to generate a 4-scene video ad script
from scraped website content. Falls back gracefully if scrape or LLM fails.
"""

import os, json, re, requests
from groq import Groq
from bs4 import BeautifulSoup

GROQ_CLIENT = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


def scrape_website(url: str) -> str:
    """Fetch and extract readable text from a URL."""
    try:
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "iframe"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ", strip=True).split())
        return text[:4000]
    except Exception as e:
        return ""


def generate_script(product_name: str, tagline: str, website_url: str = "") -> dict:
    """
    Returns a script dict compatible with pipeline_core.run_pipeline().
    """
    context = ""
    if website_url:
        context = scrape_website(website_url)

    prompt = f"""
You are a professional video ad scriptwriter. Write a 30-second, 4-scene video ad script for:

Product: {product_name}
Tagline: {tagline}
Website content: {context[:2000] if context else "Not available"}

Return ONLY valid JSON (no markdown, no explanation) in this exact format:
{{
  "scenes": [
    {{
      "scene_number": 1,
      "label": "HOOK",
      "duration_seconds": 5,
      "voiceover": "short punchy voiceover line highlighting the pain point",
      "on_screen_text": "Short pain statement|Bold Impact Line",
      "metrics": "",
      "cta_button": "",
      "pexels_queries": [
        "specific scene-matching query 1",
        "specific scene-matching query 2",
        "specific scene-matching query 3",
        "specific scene-matching query 4",
        "specific scene-matching query 5"
      ]
    }},
    {{
      "scene_number": 2,
      "label": "SOLUTION",
      "duration_seconds": 9,
      "voiceover": "voiceover introducing the product solution clearly",
      "on_screen_text": "Short headline. Supporting line.",
      "metrics": "",
      "cta_button": "",
      "pexels_queries": [
        "specific scene-matching query 1",
        "specific scene-matching query 2",
        "specific scene-matching query 3",
        "specific scene-matching query 4",
        "specific scene-matching query 5"
      ]
    }},
    {{
      "scene_number": 3,
      "label": "BENEFITS",
      "duration_seconds": 11,
      "voiceover": "voiceover listing 3 specific benefits or stats",
      "on_screen_text": "Metric1 Label1 · Metric2 Label2 · Metric3 Label3",
      "metrics": "Metric1 Label1 · Metric2 Label2 · Metric3 Label3",
      "cta_button": "",
      "pexels_queries": [
        "specific scene-matching query 1",
        "specific scene-matching query 2",
        "specific scene-matching query 3",
        "specific scene-matching query 4",
        "specific scene-matching query 5"
      ]
    }},
    {{
      "scene_number": 4,
      "label": "CTA",
      "duration_seconds": 5,
      "voiceover": "short CTA voiceover — free, today, action",
      "on_screen_text": "Start Free. website.com",
      "metrics": "",
      "cta_button": "   GET STARTED FREE   ",
      "pexels_queries": [
        "specific scene-matching query 1",
        "specific scene-matching query 2",
        "specific scene-matching query 3",
        "specific scene-matching query 4",
        "specific scene-matching query 5"
      ]
    }}
  ]
}}

Rules:
- HOOK pexels_queries: show the pain/problem visually (stressed person, chaos, frustration)
- SOLUTION pexels_queries: show someone happily using a computer/phone, bright modern workspace
- BENEFITS pexels_queries: show business results, analytics, growth, success
- CTA pexels_queries: clean product shot — laptop or phone on dark/minimal background
- Keep all text SHORT and punchy
- metrics field for BENEFITS: format as "10x Faster · 50k+ Users · 98% Satisfaction"
- Pexels queries must be realistic stock footage descriptions, not abstract concepts
"""

    try:
        resp = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        # Fallback minimal script
        return _fallback_script(product_name, tagline, website_url)


def _fallback_script(product_name, tagline, website_url):
    domain = website_url.replace("https://", "").replace("http://", "").rstrip("/") if website_url else f"{product_name.lower().replace(' ','')}.com"
    return {
        "scenes": [
            {
                "scene_number": 1, "label": "HOOK", "duration_seconds": 5,
                "voiceover": f"Still doing everything the hard way?",
                "on_screen_text": f"There's a better way.|Stop wasting time.",
                "metrics": "", "cta_button": "",
                "pexels_queries": [
                    "person stressed working laptop office desk",
                    "business person frustrated computer deadline",
                    "entrepreneur overwhelmed work desk multiple screens",
                    "woman stressed phone laptop office notifications",
                    "professional frustrated desk work overload",
                ],
            },
            {
                "scene_number": 2, "label": "SOLUTION", "duration_seconds": 9,
                "voiceover": f"{product_name} gives you everything you need — in one place.",
                "on_screen_text": f"Meet {product_name}. Everything in one place.",
                "metrics": "", "cta_button": "",
                "pexels_queries": [
                    "woman smiling laptop modern bright office sunlight",
                    "professional happy working computer clean workspace",
                    "business person excited laptop results office",
                    "entrepreneur confident laptop desk bright office window",
                    "person working laptop smiling creative workspace",
                ],
            },
            {
                "scene_number": 3, "label": "BENEFITS", "duration_seconds": 11,
                "voiceover": "Save time, boost results, and grow faster than ever.",
                "on_screen_text": "10x Faster · Save Hours · Grow Faster",
                "metrics": "10x Faster · Save Hours · Grow Faster",
                "cta_button": "",
                "pexels_queries": [
                    "business team reviewing results analytics office success",
                    "professional checking analytics growth chart laptop",
                    "entrepreneur positive results phone laptop office",
                    "business growth statistics chart office meeting",
                    "team success results office laptop screens",
                ],
            },
            {
                "scene_number": 4, "label": "CTA", "duration_seconds": 5,
                "voiceover": f"Start free today. {domain}",
                "on_screen_text": f"Start Free. {domain}",
                "metrics": "", "cta_button": "   GET STARTED FREE   ",
                "pexels_queries": [
                    "laptop dark background glowing screen studio professional",
                    "smartphone dark background app interface minimal studio",
                    "laptop dark minimal desk studio spotlight product",
                    "mobile phone dark background glow professional advertisement",
                    "technology device dark studio premium product shot",
                ],
            },
        ]
    }
