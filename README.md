# AI Ad Creation Pipeline

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Pexels-Real%20Video%20Clips-green.svg" alt="Pexels">
  <img src="https://img.shields.io/badge/TTS-AriaNeural-red.svg" alt="edge-tts">
  <img src="https://img.shields.io/badge/Pollinations-Flux%20AI%20Images-orange.svg" alt="Pollinations">
  <img src="https://img.shields.io/badge/Kaggle-Free%20T4%20GPU-20BEFF.svg" alt="Kaggle">
</p>

<p align="center">
  <strong>Create professional 30-second video advertisements in minutes using AI + real stock footage</strong><br>
  Free · No credit card required · No video editing skills needed
</p>

---

## Demo Video

### Lead — AutoMail Ad (Real Pexels Video Clips)

> `demo/automail_pexels_premium.mp4` — Real cinematic 4K footage, AriaNeural voiceover, premium text overlays

**4 scenes · 30 seconds · Multi-format export (16:9, 9:16, 1:1)**

---

## Pipeline Versions

| Version | Script | Approach |
|---------|--------|----------|
| **v1** | `automail_ultra_premium.py` | AI images (Pollinations Flux) + FFmpeg Ken Burns |
| **v2** | `automail_premium_v2.py` | AI images + PIL frame-by-frame Ken Burns (no blur) |
| **v3 (Lead)** | `automail_pexels_video.py` | **Real Pexels 4K video clips** + live frame overlay |
| **v4 (Free GPU)** | `automail_wan21_kaggle.ipynb` | **Stable Video Diffusion** on Kaggle free T4 GPU |

---

## AutoMail Ad — 4-Scene Structure

| Scene | Duration | Label | Clip | Key Text |
|-------|----------|-------|------|----------|
| 1 | 5s | **HOOK** | Businesswoman stressed at laptop, dark room | "Your emails go unread." |
| 2 | 9s | **SOLUTION** | Woman smiling at laptop, sunny office | "AI emails. Written for you." |
| 3 | 11s | **BENEFITS** | Team reviewing growth charts, modern office | "3x opens. 5hrs saved. Zero effort." |
| 4 | 5s | **CTA** | Laptop glowing, dark studio spotlight | "Start Free. AutoMail.ai" |
| **Total** | **30s** | | | |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/sandeepbangaru17/ai-add-gen.git
cd ai-add-gen
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install numpy
```

### 3. Get Free API Keys

| Service | Free Tier | Sign Up |
|---------|-----------|---------|
| **Pexels** | 200 req/hr | [pexels.com/api](https://www.pexels.com/api/) |
| **Groq** | 30 req/min | [console.groq.com](https://console.groq.com/keys) |

> **Pollinations AI** and **edge-tts** require no API keys.

### 4. Configure Environment

```env
PEXELS_API_KEY=your_pexels_key
GROQ_API_KEY=your_groq_key
```

### 5. Run

```bash
# Lead pipeline — Real Pexels cinematic footage (recommended)
python automail_pexels_video.py

# AI image + Ken Burns — PIL frame-by-frame (no blur)
python automail_premium_v2.py
```

---

## How the Pexels Pipeline Works

```
┌─────────────────────────────────────────────────────────────────┐
│              PEXELS REAL VIDEO PIPELINE (v3)                    │
├──────────────┬─────────────────────────────────────────────────┤
│  Step        │  What happens                                   │
├──────────────┼─────────────────────────────────────────────────┤
│ 1. Search    │ Query Pexels API with scene-specific keywords   │
│ 2. Download  │ Fetch best HD/4K clip for each scene           │
│ 3. Trim      │ Cut clip to exact scene duration (FFmpeg)       │
│ 4. Overlay   │ Burn premium text frame-by-frame via PIL pipe   │
│ 5. Voiceover │ AriaNeural TTS for all 4 scenes                │
│ 6. Assemble  │ Concatenate clips + mix padded audio            │
│ 7. Export    │ Output 16:9 · 9:16 · 1:1 formats               │
└──────────────┴─────────────────────────────────────────────────┘
```

### Scene Text Layouts

| Scene | Layout |
|-------|--------|
| **HOOK** | Dark overlay · Centered headline · Orange underline · Brand strip |
| **SOLUTION** | Gradient bar · Large orange headline · White sub-text · Logo badge |
| **BENEFITS** | 3-column metrics (3x · 5hrs · Zero) in orange with dividers |
| **CTA** | Full dark overlay · Brand name · Orange CTA button · URL |

---

## Kaggle Free GPU Pipeline (v4)

For true AI text-to-video (no stock footage), use the Kaggle notebook on a free T4 GPU:

1. Open `automail_wan21_kaggle.ipynb` on [Kaggle](https://www.kaggle.com)
2. Set **Settings → Accelerator → GPU T4 x1**
3. Run all cells — generates 4 AI video clips via Pollinations Flux + Stable Video Diffusion
4. Download `automail_clips.zip` from the Output panel
5. Extract to `output/wan21_raw/` and run `python automail_wan21_local.py`

---

## Project Structure

```
ai-ad-gen/
│
├── automail_pexels_video.py    # v3: Pexels real footage pipeline (lead)
├── automail_premium_v2.py      # v2: PIL Ken Burns, AI images
├── automail_ultra_premium.py   # v1: FFmpeg Ken Burns, AI images
├── automail_wan21_kaggle.ipynb # v4: Kaggle T4 GPU — Flux + SVD text-to-video
├── automail_wan21_local.py     # v4 local assembly for Kaggle-generated clips
├── automail_seedance.py        # Seedance 2 via kie.ai API
├── automail_t2v.py             # ZeroScope T2V via HuggingFace
├── automail_script.json        # AutoMail 30s ad script (4 scenes)
│
├── pipeline.py                 # Original modular pipeline
├── config.py                   # Configuration & API keys
├── llm_client.py               # Groq LLM client
│
├── agents/                     # Modular AI agents
│   ├── brief_agent.py
│   ├── script_agent.py
│   ├── voice_agent.py
│   ├── prompt_agent.py
│   ├── video_agent.py
│   ├── stitch_agent.py
│   ├── post_agent.py
│   └── export_agent.py
│
├── schemas/                    # JSON validation schemas
│
├── demo/
│   └── automail_pexels_premium.mp4   # Lead 30s ad
│
├── output/                     # Generated on run
│   ├── automail_pexels_final.mp4     # Master 16:9
│   ├── automail_pexels_16x9.mp4      # YouTube / LinkedIn
│   ├── automail_pexels_9x16.mp4      # Instagram Reels / TikTok
│   └── automail_pexels_1x1.mp4       # Instagram Feed / Facebook
│
├── requirements.txt
└── README.md
```

---

## Output Files

```
output/
├── automail_pexels_final.mp4   # Master 1920x1080 16:9 (30s)
├── automail_pexels_16x9.mp4    # YouTube / LinkedIn
├── automail_pexels_9x16.mp4    # Instagram Reels / TikTok
└── automail_pexels_1x1.mp4     # Instagram Feed / Facebook
```

---

## Tools & Technologies

| Tool | Purpose | Cost |
|------|---------|------|
| **Pexels API** | Real cinematic stock footage | Free (200 req/hr) |
| **Pollinations AI** | AI image generation | Completely free |
| **edge-tts AriaNeural** | Neural voiceover | Completely free |
| **Stable Video Diffusion** | Image-to-video on Kaggle T4 | Free GPU |
| **FFmpeg** | Video processing, trim, export | Open source |
| **Pillow** | Per-frame text overlays | Open source |
| **Groq API** | LLM script generation | Free tier |

---

## Performance

| Task | Time |
|------|------|
| Pexels search + download (4 clips) | ~1-2 min |
| Frame-by-frame overlay (720 frames) | ~2-3 min |
| Voiceover generation | ~15 sec |
| Assembly + export | ~30 sec |
| **Total** | **~4-5 min** |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pexels returns no results | Fallback queries auto-tried for each scene |
| FFmpeg not found | `winget install Gyan.FFmpeg` |
| `numpy` missing | `pip install numpy` |
| Video duration mismatch | Audio is padded with silence to match video |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **Pexels** — Free HD/4K stock footage with generous API
- **Microsoft Edge TTS** — AriaNeural neural voice
- **Pollinations AI** — Free Flux image generation
- **Stability AI** — Stable Video Diffusion
- **Groq** — Fast free LLM inference
- **FFmpeg** — Industry-standard video processing

---

<p align="center">
  <strong>Built to understand the full AI video ad creation pipeline — from script to final export</strong>
</p>

<p align="center">
  <a href="https://github.com/sandeepbangaru17/ai-add-gen">Star this repo</a>
  ·
  <a href="https://github.com/sandeepbangaru17/ai-add-gen/issues">Report Bug</a>
  ·
  <a href="https://github.com/sandeepbangaru17/ai-add-gen/discussions">Request Feature</a>
</p>
