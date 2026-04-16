<div align="center">

# AI Video Ad Generator

<p>
  <a href="https://ai-add-gen.onrender.com" target="_blank">
    <img src="https://img.shields.io/badge/🚀%20Live%20Demo-ai--add--gen.onrender.com-6366f1?style=for-the-badge" alt="Live Demo">
  </a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/FFmpeg-grey?style=flat-square&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F55036?style=flat-square" alt="Groq">
  <img src="https://img.shields.io/badge/Pexels-4K%20Stock%20Footage-05A081?style=flat-square" alt="Pexels">
  <img src="https://img.shields.io/badge/Edge%20TTS-8%20Voices-0078D4?style=flat-square&logo=microsoft&logoColor=white" alt="TTS">
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License">
</p>

**Generate a broadcast-ready 30-second product ad in minutes.**  
Enter a URL — AI writes the script, finds cinematic footage, adds a professional voiceover, and exports in 3 formats. Automatically.

[**→ Try it live**](https://ai-add-gen.onrender.com)

</div>

---

## What It Does

1. **Scrapes your website** — extracts title, tagline, headings, and product copy
2. **Writes a 4-scene script** — Hook → Solution → Benefits → CTA using Groq LLaMA 3.3 70B
3. **Finds cinematic footage** — searches Pexels for the best matching HD/4K clips per scene
4. **Burns premium overlays** — per-frame text rendering with your brand colors using Pillow
5. **Generates a voiceover** — choose from 8 neural voices (US, UK, AU accents)
6. **Exports 3 formats** — 16:9 (YouTube), 9:16 (Reels/TikTok), 1:1 (Instagram)

---

## Live Demo

**[https://ai-add-gen.onrender.com](https://ai-add-gen.onrender.com)**

| Page | Description |
|------|-------------|
| `/` | Product form — name, URL, brand color, voice |
| `/job/<id>` | Real-time progress → inline video reveal |
| `/videos` | Gallery of all generated ads |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Web framework** | Flask 3 + Gunicorn |
| **Script generation** | Groq API — LLaMA 3.3 70B Versatile |
| **Stock footage** | Pexels API — HD/4K cinematic clips |
| **Video processing** | FFmpeg — trim, concat, mix, export |
| **Text overlays** | Pillow — per-frame compositing pipeline |
| **Voiceover** | Microsoft Edge TTS — 8 neural voices |
| **Website scraping** | BeautifulSoup4 |
| **Real-time progress** | Server-Sent Events (SSE) |
| **Fonts** | Inter (bundled) |
| **Deployment** | Render (static FFmpeg binary via build.sh) |

---

## Quick Start (Local)

### 1. Clone

```bash
git clone https://github.com/sandeepbangaru17/ai-add-gen.git
cd ai-add-gen
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **FFmpeg** must be installed separately:
> - **Windows:** `winget install Gyan.FFmpeg`
> - **Mac:** `brew install ffmpeg`
> - **Linux:** `sudo apt install ffmpeg`

### 3. Set environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_key
PEXELS_API_KEY=your_pexels_key
```

| Service | Free Tier | Link |
|---------|-----------|------|
| **Groq** | 30 req/min, free | [console.groq.com](https://console.groq.com/keys) |
| **Pexels** | 200 req/hr, free | [pexels.com/api](https://www.pexels.com/api/) |

### 4. Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## How the Pipeline Works

```
URL / Product Name
       │
       ▼
┌─────────────────┐
│  Script Writer  │  Groq LLaMA 3.3 → 4-scene JSON script
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pexels Search  │  Scene-specific queries → best HD/4K clip
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Trim & Overlay │  FFmpeg trim → PIL per-frame text burn
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Voiceover     │  Edge TTS → merged MP3
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Assemble     │  Concat clips + mix audio → final.mp4
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Export Formats │  16:9 · 9:16 · 1:1
└─────────────────┘
```

---

## Scene Structure

| Scene | Duration | Purpose | Overlay Style |
|-------|----------|---------|---------------|
| **1 — Hook** | 5s | Grab attention | Dark overlay · centered headline · brand strip |
| **2 — Solution** | 9s | Present the product | Gradient bar · large headline · logo badge |
| **3 — Benefits** | 11s | Show key metrics | 3-column stats with dividers |
| **4 — CTA** | 5s | Drive action | Full dark overlay · CTA button · website URL |

---

## Voice Options

| Voice | Accent | Style |
|-------|--------|-------|
| Aria | 🇺🇸 US | Warm & Conversational |
| Jenny | 🇺🇸 US | Upbeat & Energetic |
| Sara | 🇺🇸 US | Calm & Professional |
| Guy | 🇺🇸 US | Confident & Clear |
| Tony | 🇺🇸 US | Bold & Authoritative |
| Ryan | 🇬🇧 UK | Sophisticated British |
| Sonia | 🇬🇧 UK | Elegant British |
| Natasha | 🇦🇺 AU | Fresh & Approachable |

---

## Project Structure

```
ai-add-gen/
├── app.py                  # Flask app — all routes
├── pipeline_core.py        # Video pipeline — yields SSE progress
├── script_generator.py     # Groq LLM script generation
├── build.sh                # Render build — downloads static FFmpeg
├── nixpacks.toml           # Railway config (alternative deploy)
├── Procfile                # Gunicorn start command
├── requirements.txt
│
├── templates/
│   ├── base.html           # Navbar, theme toggle
│   ├── index.html          # Product form
│   ├── job.html            # Progress + inline video reveal
│   └── videos.html         # Gallery
│
├── static/
│   ├── css/style.css       # Premium design system
│   ├── js/main.js          # Theme toggle
│   └── fonts/              # Bundled Inter font
│
└── jobs/                   # Generated per job (gitignored)
    └── <job_id>/
        ├── meta.json
        ├── script.json
        ├── final.mp4
        ├── <slug>_16x9.mp4
        ├── <slug>_9x16.mp4
        └── <slug>_1x1.mp4
```

---

## Deployment (Render)

1. Fork / clone this repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your repo and set:

| Setting | Value |
|---------|-------|
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300` |

4. Add environment variables:
   - `GROQ_API_KEY`
   - `PEXELS_API_KEY`

5. Deploy — done.

> `build.sh` automatically downloads a static FFmpeg binary — no sudo or system packages needed.

---

## Performance

| Step | Time |
|------|------|
| Script generation | ~5s |
| Pexels search + download (4 clips) | ~1–2 min |
| Frame-by-frame overlay (720 frames) | ~2–3 min |
| Voiceover generation | ~15s |
| Assembly + export (3 formats) | ~30s |
| **Total** | **~4–6 min** |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with Groq · Pexels · Edge TTS · FFmpeg · Flask

[Live Demo](https://ai-add-gen.onrender.com) · [Report Bug](https://github.com/sandeepbangaru17/ai-add-gen/issues) · [Request Feature](https://github.com/sandeepbangaru17/ai-add-gen/discussions)

</div>
