# 🎬 AI Ad Creation Pipeline

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Groq-Llama%203.3%2070B-purple.svg" alt="Groq">
  <img src="https://img.shields.io/badge/Pexels-Real%20Video%20Clips-green.svg" alt="Pexels">
  <img src="https://img.shields.io/badge/TTS-AriaNeural-red.svg" alt="edge-tts">
  <img src="https://img.shields.io/badge/Pollinations-Flux%20AI%20Images-orange.svg" alt="Pollinations">
  <img src="https://img.shields.io/badge/ZeroScope-T2V%20HuggingFace-yellow.svg" alt="ZeroScope">
</p>

<p align="center">
  <strong>Create professional 30-second video advertisements in minutes using AI + real stock footage</strong><br>
  Free • No credit card required • No video editing skills needed
</p>

---

## 🎥 Demo Videos

### ✅ Latest — AutoMail Ad (Real Pexels Video Clips)

<p align="center">
  <strong>AutoMail 30-Second Premium Ad — Powered by Pexels Real Footage</strong>
</p>

> `demo/automail_pexels_premium.mp4` — Real cinematic video clips, AriaNeural voiceover, premium text overlays

---

### Pipeline Versions

| Version | File | Approach |
|---------|------|----------|
| **v1** | `automail_ultra_premium.py` | AI images (Pollinations Flux) + FFmpeg Ken Burns |
| **v2** | `automail_premium_v2.py` | AI images + PIL frame-by-frame Ken Burns (no blur) |
| **v3 (Current)** | `automail_pexels_video.py` | **Real Pexels 4K video clips** + live frame overlay |
| **v4 (T2V)** | `automail_t2v.py` | **ZeroScope text-to-video** (HuggingFace, free) |

---

## ✨ What's Been Built

### Pipeline Evolution

#### v1 — AI Image Pipeline (`automail_ultra_premium.py`)
- Generated 4 cinematic scenes using **Pollinations Flux AI** image model
- Applied **Ken Burns effects** via FFmpeg `zoompan`
- Added **Pillow text overlays** (brand colors, scene-specific layout)
- AriaNeural voiceover + xfade transitions
- Cinematic FFmpeg color grade (orange/teal split-tone)

#### v2 — PIL Frame-by-Frame Pipeline (`automail_premium_v2.py`)
- **Fixed blurry video**: Replaced FFmpeg zoompan with **PIL LANCZOS per-frame rendering**
- **Fixed overlapping text**: Replaced xfade crossfade with **fade-to-black** transitions
- **Fixed duplicate subtitles**: Removed FFmpeg subtitle burning, text lives in frames only
- **Redesigned 4 unique scene layouts**: HOOK · SOLUTION · BENEFITS · CTA
- Source images upscaled to 1.3× before Ken Burns = zero interpolation blur

#### v4 — ZeroScope Text-to-Video Pipeline (`automail_t2v.py`)
- **True text-to-video**: prompt → AI-generated video clip via **ZeroScope v2** (HuggingFace, FREE)
- Upscales ZeroScope 576×320 output → 1920×1080 via FFmpeg with loop fill
- Same premium PIL text overlays and AriaNeural voiceover as v3
- Uses `hysts/zeroscope-v2` HuggingFace Space with HF token for GPU priority

#### v3 — Pexels Real Video Pipeline (`automail_pexels_video.py`) ✅ Current
- **Real cinematic stock footage** from Pexels API (up to 4K UHD)
- Searches multiple query fallbacks per scene to find best matching clip
- Downloads, trims, and resizes each clip to exact scene duration
- **Burns text overlays frame-by-frame** via FFmpeg→PIL pipe
- **Fade-in / fade-out** on each scene for smooth transitions
- AriaNeural voiceover padded to exact video duration

---

## 🎯 AutoMail Ad — 4-Scene Structure

| Scene | Duration | Label | Key Text |
|-------|----------|-------|----------|
| 1 | 5s | **HOOK** | "But no one's opening your emails." |
| 2 | 9s | **SOLUTION** | "AI emails. Written for you." |
| 3 | 11s | **BENEFITS** | "3x opens. 5hrs saved. Zero effort." |
| 4 | 5s | **CTA** | "START FREE TODAY — automail.ai" |
| **Total** | **30s** | | |

---

## 🚀 Quick Start

### 1. Clone the Repository

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
| **Groq** | 30 req/min | [console.groq.com](https://console.groq.com/keys) |
| **Pexels** | 200 req/hr | [pexels.com/api](https://www.pexels.com/api/) |

> **Pollinations AI** and **edge-tts** work with NO API keys.

### 4. Configure Environment

```env
GROQ_API_KEY=your_groq_key
PEXELS_API_KEY=your_pexels_key
HF_TOKEN=optional
```

### 5. Run the Pipeline

```bash
# Best quality — Real Pexels cinematic footage (recommended)
python automail_pexels_video.py

# True text-to-video — AI-generated clips via ZeroScope (HuggingFace)
python automail_t2v.py

# AI image + Ken Burns — PIL frame-by-frame (no blur)
python automail_premium_v2.py
```

---

## 📁 Project Structure

```
ai-ad-gen/
│
├── automail_pexels_video.py    # v3: Real Pexels video clips pipeline  ✅ Current
├── automail_t2v.py             # v4: ZeroScope text-to-video (HuggingFace free)
├── automail_premium_v2.py      # v2: PIL frame-by-frame Ken Burns (no blur)
├── automail_ultra_premium.py   # v1: AI images + FFmpeg Ken Burns
├── automail_script.json        # AutoMail 30s ad script (4 scenes)
├── automail_seedance.py        # Seedance via Replicate (requires paid API)
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
│   └── automail_pexels_premium.mp4   # Final 30s ad (real footage)
│
├── output/                     # Generated files
│   ├── automail_pexels_final.mp4     # Master 16:9 (28 MB)
│   ├── automail_pexels_16x9.mp4      # YouTube/LinkedIn
│   ├── automail_pexels_9x16.mp4      # Instagram Reels/TikTok
│   ├── automail_pexels_1x1.mp4       # Instagram Feed/Facebook
│   ├── pexels_raw/                   # Downloaded Pexels clips (cached)
│   ├── pexels_proc/                  # Overlaid scene clips
│   └── voice/                        # AriaNeural TTS audio
│
├── requirements.txt
└── README.md
```

---

## 🛠️ How the Pexels Pipeline Works

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

### Scene-Specific Text Layouts

| Scene | Layout Design |
|-------|--------------|
| **HOOK** | Dark overlay · Stark centered headline · Orange underline · Brand strip |
| **SOLUTION** | Tall gradient bar · Huge orange "AI emails." · White sub-text · Logo badge |
| **BENEFITS** | 3-column metrics bar · 3x · 5hrs · Zero in orange · Dividers |
| **CTA** | Full dark overlay · Brand name · Orange CTA button · URL |

---

## 📤 Output Files

After running `automail_pexels_video.py`:

```
output/
├── pexels_raw/
│   ├── pex_raw_1.mp4          # Raw Pexels clip — Scene 1
│   ├── pex_raw_2.mp4          # Raw Pexels clip — Scene 2
│   ├── pex_raw_3.mp4          # Raw Pexels clip — Scene 3
│   └── pex_raw_4.mp4          # Raw Pexels clip — Scene 4
├── pexels_proc/
│   ├── pex_proc_1.mp4         # Trimmed + text overlay — Scene 1
│   ├── pex_proc_2.mp4         # Trimmed + text overlay — Scene 2
│   ├── pex_proc_3.mp4         # Trimmed + text overlay — Scene 3
│   └── pex_proc_4.mp4         # Trimmed + text overlay — Scene 4
├── automail_pexels_final.mp4  # ✅ Master 1920x1080 16:9 (30s)
├── automail_pexels_16x9.mp4   # YouTube / LinkedIn
├── automail_pexels_9x16.mp4   # Instagram Reels / TikTok
└── automail_pexels_1x1.mp4    # Instagram Feed / Facebook
```

---

## 🛠️ Tools & Technologies

| Tool | Purpose | Cost |
|------|---------|------|
| **Groq API** | LLM script generation | Free tier |
| **Pexels API** | Real cinematic stock footage | Free (200 req/hr) |
| **Pollinations AI** | AI image generation (fallback) | Completely free |
| **edge-tts AriaNeural** | Professional neural voiceover | Completely free |
| **FFmpeg** | Video processing, trim, export | Open source |
| **Pillow** | Per-frame text overlays, color grade | Open source |
| **NumPy** | Cinematic color grading curves | Open source |

---

## ⚡ Performance

| Task | Time |
|------|------|
| Pexels search + download (4 clips) | ~1-2 min |
| Frame-by-frame overlay (720 frames) | ~2-3 min |
| Voiceover generation | ~15 sec |
| Assembly + export | ~30 sec |
| **Total** | **~4-5 min** |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Pexels returns no results | Fallback queries auto-tried for each scene |
| FFmpeg not found | `winget install Gyan.FFmpeg` |
| `numpy` missing | `pip install numpy` |
| Video duration mismatch | Audio is padded with silence to match video |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit with descriptive messages
4. Push and open a Pull Request

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Pexels** — Free HD/4K stock footage with generous API
- **Microsoft Edge TTS** — AriaNeural and other premium neural voices
- **Pollinations AI** — Free Flux image generation
- **Groq** — Fast free LLM inference
- **FFmpeg** — Industry-standard video processing

---

<p align="center">
  <strong>Built to understand the full AI video ad creation pipeline — from script to final export</strong>
</p>

<p align="center">
  <a href="https://github.com/sandeepbangaru17/ai-add-gen">⭐ Star this repo</a>
  •
  <a href="https://github.com/sandeepbangaru17/ai-add-gen/issues">Report Bug</a>
  •
  <a href="https://github.com/sandeepbangaru17/ai-add-gen/discussions">Request Feature</a>
</p>
