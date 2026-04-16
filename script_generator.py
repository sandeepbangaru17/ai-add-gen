"""
script_generator.py — Premium AI script generation using Groq LLM.
Scrapes website → extracts real product info → writes cinematic 4-scene script.
"""

import os, json, re, requests
from groq import Groq
from bs4 import BeautifulSoup

GROQ_CLIENT = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


def scrape_website(url: str) -> dict:
    """Fetch website and extract structured product signals."""
    try:
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract title and meta description first — highest signal
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        for m in soup.find_all("meta"):
            if m.get("name") in ("description", "og:description") or m.get("property") == "og:description":
                meta_desc = m.get("content", "")
                break

        # Pull hero / h1 / h2 text (first 8) — highest quality copy
        headings = []
        for tag in soup.find_all(["h1", "h2"])[:8]:
            t = tag.get_text(" ", strip=True)
            if t:
                headings.append(t)

        # Remove noise tags
        for tag in soup(["script", "style", "nav", "footer", "iframe", "header"]):
            tag.decompose()

        body_text = " ".join(soup.get_text(" ", strip=True).split())

        return {
            "title":       title,
            "description": meta_desc,
            "headings":    headings,
            "body":        body_text[:2500],
        }
    except Exception:
        return {"title": "", "description": "", "headings": [], "body": ""}


def generate_script(product_name: str, tagline: str, website_url: str = "") -> dict:
    """Returns a script dict compatible with pipeline_core.run_pipeline()."""
    site = {}
    if website_url:
        site = scrape_website(website_url)

    # Build rich context string from structured scrape
    context_parts = []
    if site.get("title"):
        context_parts.append(f"Page title: {site['title']}")
    if site.get("description"):
        context_parts.append(f"Meta description: {site['description']}")
    if site.get("headings"):
        context_parts.append("Key headlines:\n" + "\n".join(f"  • {h}" for h in site["headings"]))
    if site.get("body"):
        context_parts.append(f"Body copy (first 2500 chars):\n{site['body']}")
    context = "\n\n".join(context_parts) if context_parts else "No website content available."

    prompt = f"""You are an award-winning video ad director and copywriter. Your scripts have sold millions in products. Write a high-converting 30-second video ad script for the product below.

━━━ PRODUCT INFO ━━━
Name: {product_name}
Tagline: {tagline if tagline else "Not provided — infer from website content"}
Website content:
{context}

━━━ STRUCTURE ━━━
Scene 1 — HOOK (5 seconds)
  Goal: Grab attention in the first 2 seconds. Show a REAL, SPECIFIC pain your audience feels every day.
  Voiceover: 1–2 punchy sentences. Short. Rhythmic. Emotionally resonant. No fluff.
  On-screen text: Two lines separated by | — first line is relatable pain, second is the sharp twist.
  Pexels clips: Real footage of someone experiencing this exact pain (stressed, overwhelmed, frustrated).

Scene 2 — SOLUTION (9 seconds)
  Goal: Introduce the product as the elegant answer. Show relief, confidence, ease.
  Voiceover: Clearly name the product and what it does in plain English. Confident tone. 2–3 sentences max.
  On-screen text: Short product claim. Supporting benefit.
  Pexels clips: Someone looking happy, confident, productive — at a clean modern desk or workspace.

Scene 3 — BENEFITS (11 seconds)
  Goal: Prove it works with 3 specific, real numbers or outcomes. Make it undeniable.
  Voiceover: Speak the 3 metrics dramatically. Pause between each. Let them land.
  On-screen text: 3 metrics in format: "Value Label · Value Label · Value Label"
  Pexels clips: Business growth, analytics, team success, results — energy and momentum.

Scene 4 — CTA (5 seconds)
  Goal: Drive action NOW. Urgency. Simplicity. One clear next step.
  Voiceover: Ultra short — 1 sentence max. Action word. Free or easy entry point.
  On-screen text: "Start Free. domain.com"
  Pexels clips: Clean product or tech shot on dark/minimal background.

━━━ COPYWRITING RULES ━━━
- Voiceover must sound natural when spoken aloud — no corporate buzzwords
- HOOK must name a pain the audience whispers to themselves ("I hate this")
- SOLUTION must say the product name clearly in the first sentence
- BENEFITS must use real numbers from the website (or realistic estimates if not available)
- CTA must be a single, irresistible sentence — short enough to fit on a billboard
- Every line must earn its place — cut anything vague or generic

━━━ PEXELS QUERY RULES ━━━
- Each query = a specific visual scene description a filmmaker would search for
- Must be realistic stock footage that EXISTS on Pexels
- Include visual details: lighting, setting, emotion, action, demographics
- Examples of GOOD queries:
    "tired young businesswoman late at night blue laptop screen dark home office"
    "smiling woman typing on macbook bright modern cafe sunlight"
    "business team celebrating results high five open plan office"
    "sleek laptop on white marble desk dark background studio lighting"
- Examples of BAD queries (too abstract, won't find good footage):
    "success", "technology innovation", "business growth concept"

━━━ OUTPUT ━━━
Return ONLY valid JSON. No markdown. No explanation. No code fences. Exactly this structure:

{{
  "scenes": [
    {{
      "scene_number": 1,
      "label": "HOOK",
      "duration_seconds": 5,
      "voiceover": "...",
      "on_screen_text": "Pain line here|Bold impact twist here",
      "metrics": "",
      "cta_button": "",
      "pexels_queries": ["query1","query2","query3","query4","query5"]
    }},
    {{
      "scene_number": 2,
      "label": "SOLUTION",
      "duration_seconds": 9,
      "voiceover": "...",
      "on_screen_text": "Short headline. Supporting line.",
      "metrics": "",
      "cta_button": "",
      "pexels_queries": ["query1","query2","query3","query4","query5"]
    }},
    {{
      "scene_number": 3,
      "label": "BENEFITS",
      "duration_seconds": 11,
      "voiceover": "...",
      "on_screen_text": "Value1 Label1 · Value2 Label2 · Value3 Label3",
      "metrics": "Value1 Label1 · Value2 Label2 · Value3 Label3",
      "cta_button": "",
      "pexels_queries": ["query1","query2","query3","query4","query5"]
    }},
    {{
      "scene_number": 4,
      "label": "CTA",
      "duration_seconds": 5,
      "voiceover": "...",
      "on_screen_text": "Start Free. domain.com",
      "metrics": "",
      "cta_button": "   GET STARTED FREE   ",
      "pexels_queries": ["query1","query2","query3","query4","query5"]
    }}
  ]
}}"""

    try:
        resp = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.75,
            max_tokens=2500,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```\s*$", "", raw)
        return json.loads(raw)
    except Exception:
        return _fallback_script(product_name, tagline, website_url)


def _fallback_script(product_name, tagline, website_url):
    domain = (website_url.replace("https://","").replace("http://","").rstrip("/")
              if website_url else f"{product_name.lower().replace(' ','')}.com")
    return {
        "scenes": [
            {
                "scene_number": 1, "label": "HOOK", "duration_seconds": 5,
                "voiceover": "You're working harder than ever. But the results aren't showing up.",
                "on_screen_text": "Working hard. Getting nowhere.|There's a smarter way.",
                "metrics": "", "cta_button": "",
                "pexels_queries": [
                    "tired businesswoman working late night laptop dark office blue screen glow",
                    "frustrated professional staring at computer screen deadline stress office",
                    "overwhelmed entrepreneur multiple screens phone laptop notifications desk",
                    "stressed person head in hands desk computer work pressure",
                    "business person exhausted overworked laptop dark home office night",
                ],
            },
            {
                "scene_number": 2, "label": "SOLUTION", "duration_seconds": 9,
                "voiceover": f"{product_name} changes everything. Built to save you time, cut the chaos, and get results — fast.",
                "on_screen_text": f"Meet {product_name}.|Built for results.",
                "metrics": "", "cta_button": "",
                "pexels_queries": [
                    "confident smiling woman working laptop bright modern office large windows sunlight",
                    "happy professional typing computer clean minimal workspace natural light",
                    "young entrepreneur excited laptop positive results bright creative office",
                    "businesswoman focused laptop smiling modern glass office building",
                    "person working laptop coffee shop smiling relaxed productive",
                ],
            },
            {
                "scene_number": 3, "label": "BENEFITS", "duration_seconds": 11,
                "voiceover": "Ten times faster. Hours back every week. Results you can actually measure.",
                "on_screen_text": "10x Faster · Hours Saved · Real Results",
                "metrics": "10x Faster · Hours Saved · Real Results",
                "cta_button": "",
                "pexels_queries": [
                    "business team reviewing analytics dashboard laptop modern office success",
                    "professional checking growth chart phone positive results office",
                    "diverse team celebrating project success high five bright office",
                    "entrepreneur looking at laptop screen positive metrics results desk",
                    "business growth statistics presentation meeting room success",
                ],
            },
            {
                "scene_number": 4, "label": "CTA", "duration_seconds": 5,
                "voiceover": f"Start free today. {domain}",
                "on_screen_text": f"Start Free. {domain}",
                "metrics": "", "cta_button": "   GET STARTED FREE   ",
                "pexels_queries": [
                    "sleek laptop white marble desk dark studio background professional spotlight",
                    "smartphone glowing screen dark minimal background studio advertisement",
                    "macbook dark background dramatic spotlight product shot premium",
                    "laptop dark minimal desk blue screen glow professional studio",
                    "technology device dark background cinematic product advertisement",
                ],
            },
        ]
    }
