# 🎬 AI Ad Creation Pipeline

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Groq-Llama%203.3%2070B-purple.svg" alt="Groq">
  <img src="https://img.shields.io/badge/AI-Pollinations%20Flux-orange.svg" alt="Pollinations">
  <img src="https://img.shields.io/badge/TTS-edge--tts-red.svg" alt="edge-tts">
</p>

<p align="center">
  <strong>Create professional video advertisements in minutes using AI</strong><br>
  Free • No credit card • No video editing skills required
</p>

---

## ✨ Features

- **🤖 AI-Powered Script Generation** - Create compelling ad scripts with Groq's Llama 3.3
- **🎙️ Natural Voiceover** - Professional neural voices using Microsoft Edge TTS
- **🎨 AI Image Generation** - Stunning visuals with Pollinations Flux (free, no API key)
- **🎬 Ken Burns Effect** - Cinematic motion on static images
- **📱 Multi-Platform Export** - Optimized for Instagram, YouTube, TikTok, Facebook
- **💾 Complete Deliverables** - Master video, social cuts, subtitles, metadata

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
```

### 3. Get Free API Keys

| Service | Free Tier | Sign Up |
|---------|-----------|---------|
| **Groq** | 30 requests/min | [console.groq.com](https://console.groq.com/keys) |
| **HuggingFace** | Optional fallback | [huggingface.co](https://huggingface.co/settings/tokens) |

> **Note:** Pollinations AI and edge-tts work WITHOUT any API keys!

### 4. Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here   # Optional
```

### 5. Run the Pipeline

**Interactive Mode (recommended for new topics):**
```bash
python pipeline.py
```

**Test Mode (ZunoSync demo):**
```bash
python pipeline.py --default
```

**Custom Brief:**
```bash
python pipeline.py --brief my_brief.json
```

---

## 📋 Project Structure

```
ai-add-gen/
├── 📄 pipeline.py              # Main orchestrator
├── ⚙️ config.py               # Configuration & paths
├── 📁 agents/                  # AI agents for each stage
│   ├── brief_agent.py         # Campaign brief collection
│   ├── script_agent.py        # Script generation (LLM)
│   ├── voice_agent.py         # Voiceover (edge-tts)
│   ├── prompt_agent.py        # Visual prompts (LLM)
│   ├── video_agent.py         # AI images + Ken Burns
│   ├── stitch_agent.py        # Video assembly (FFmpeg)
│   ├── post_agent.py          # Platform exports
│   └── export_agent.py        # Final packaging
├── 📁 schemas/                 # JSON validation schemas
├── 📄 requirements.txt         # Python dependencies
├── 📄 spec.md                 # Technical specification
└── 📄 README.md               # This file
```

---

## 🎯 How It Works

The pipeline consists of **8 stages** that transform a campaign brief into professional video advertisements:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                                │
├──────────────┬──────────────┬──────────────┬──────────────────────────┤
│  Stage       │  Agent       │  Tool        │  Output                  │
├──────────────┼──────────────┼──────────────┼──────────────────────────┤
│ 1. Brief     │ Brief Agent  │ CLI Input    │ brief.json               │
│ 2. Script    │ Script Agent │ Groq LLM     │ script.json              │
│ 3. Voice     │ Voice Agent  │ edge-tts     │ voiceover.mp3 + SRT      │
│ 4. Prompts   │ Prompt Agent │ Groq LLM     │ scene_prompts.json       │
│ 5. Video     │ Video Agent  │ Pollinations │ scene_clips/             │
│ 6. Stitch    │ Stitch Agent │ FFmpeg       │ ad_draft.mp4             │
│ 7. Post      │ Post Agent   │ FFmpeg       │ 4 format variations       │
│ 8. Export    │ Export Agent │ FFmpeg       │ final_output/            │
└──────────────┴──────────────┴──────────────┴──────────────────────────┘
```

### Stage Details

| Stage | Description |
|-------|-------------|
| **1. Brief** | Enter campaign details: product name, audience, duration, tone, platforms, CTA |
| **2. Script** | AI generates a compelling 5-scene script with voiceovers and on-screen text |
| **3. Voice** | Neural text-to-speech creates professional voiceover audio |
| **4. Prompts** | AI generates detailed visual prompts for each scene |
| **5. Video** | AI generates images + Ken Burns effect creates animated clips |
| **6. Stitch** | FFmpeg combines clips, adds audio, burns subtitles |
| **7. Post** | Exports to 9:16 (Reels), 1:1 (Feed), 16:9 (YouTube) |
| **8. Export** | Packages everything in organized folder structure |

---

## 📁 Output Structure

After running the pipeline, you'll find your deliverables in `final_output/`:

```
final_output/
├── 📁 master/
│   └── zunosync_ad_master_HD.mp4      # High quality master (1920x1080)
│
├── 📁 social/
│   ├── zunosync_ad_9x16_reels.mp4     # Instagram Reels / TikTok / YouTube Shorts
│   ├── zunosync_ad_1x1_feed.mp4       # Instagram Feed / Facebook
│   └── zunosync_ad_16x9_youtube.mp4   # YouTube / LinkedIn
│
├── 📁 assets/
│   ├── subtitles.srt                  # Subtitles file (burned into video)
│   └── thumbnail.png                  # Video thumbnail
│
└── 📁 metadata/
    ├── brief.json                     # Original campaign brief
    ├── script.json                    # Generated ad script
    ├── scene_prompts.json             # Visual prompts used
    └── production_log.json           # Pipeline execution log
```

---

## 🎨 Example Campaign Brief

Create a `my_brief.json` file:

```json
{
  "product_name": "Your Amazing Product",
  "tagline": "Transform Your Business Today",
  "target_audience": "Small business owners aged 25-45",
  "ad_duration_seconds": 30,
  "tone": "professional, energetic",
  "platform": ["Instagram Reel", "YouTube Ad"],
  "cta": "Start Your Free Trial",
  "brand_colors": ["#FF5500", "#FFFFFF"],
  "logo_url": ""
}
```

**Brief Validation Rules:**
- `ad_duration_seconds` must be 15, 30, or 60
- `platform` must have at least one platform
- `cta` maximum 60 characters

---

## 🛠️ Tools & Technologies

### Free Tools Used (No Credit Card Required)

| Tool | Purpose | Cost |
|------|---------|------|
| **Groq API** | LLM for script & prompts | Free tier: 30 req/min |
| **edge-tts** | Neural text-to-speech | Completely free |
| **Pollinations AI** | AI image generation | Completely free |
| **FFmpeg** | Video processing | Open source |

### Why These Tools?

- **Groq**: Fastest LLM inference, generous free tier
- **edge-tts**: High-quality Microsoft neural voices
- **Pollinations**: No API key needed, good image quality
- **FFmpeg**: Industry-standard video processing

---

## ⏱️ Performance

| Metric | Value |
|--------|-------|
| **Total Time** | ~2-3 minutes |
| **Script Generation** | ~3 seconds |
| **Voice Generation** | ~10-25 seconds |
| **Prompt Generation** | ~2 seconds |
| **Image Generation** | ~20-30 seconds per scene |
| **Video Assembly** | ~30 seconds |

---

## 🔧 Configuration

### Command Line Options

```bash
python pipeline.py [options]

Options:
  --default              Use built-in ZunoSync test brief
  --brief <path>         Use custom brief JSON file
  --start-from <stage>   Resume from specific stage (1-8)
```

### Environment Variables

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
HF_TOKEN=your_huggingface_token_here   # For HuggingFace fallback
PEXELS_API_KEY=your_pexels_key_here     # For stock image fallback
```

### Customizing Voice

Edit `config.py` to change the TTS voice:

```python
VOICE_MAP = {
    "professional": "en-US-GuyNeural",  # Male, calm, clear
    "energetic": "en-US-TonyNeural",    # Male, upbeat
    "emotional": "en-US-AriaNeural",    # Female, warm
    "urgent": "en-US-DavisNeural",       # Male, direct
    "warm": "en-US-JennyNeural",         # Female, soft
}
```

---

## 🔄 Pipeline Resume

If the pipeline fails, you can resume from any stage:

```bash
# Resume from Stage 3 (Voice Generation)
python pipeline.py --start-from 3

# Resume from Stage 5 (Video Generation)
python pipeline.py --start-from 5
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "GROQ_API_KEY not set" | Add your API key to `.env` file |
| FFmpeg not found | Install FFmpeg and add to PATH |
| Fontconfig error on Windows | This is normal, subtitles still work |
| Images look blurry | Use Pollinations Flux model (already default) |

### FFmpeg Installation

**Windows:**
```bash
winget install Gyan.FFmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

---

## 📊 Pipeline Results

After completion, check `output/pipeline_results.json`:

```json
{
  "success": true,
  "stages_completed": 8,
  "total_time_seconds": 156.2,
  "outputs": {
    "master_video": "final_output/master/zunosync_ad_master_HD.mp4",
    "social_exports": ["9x16", "1x1", "16x9"]
  }
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes with detailed commit messages
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** - For providing fast and free LLM inference
- **Microsoft** - For edge-tts neural voices
- **Pollinations** - For free AI image generation
- **FFmpeg** - For industry-standard video processing
- **HuggingFace** - For AI model hosting

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/sandeepbangaru17/ai-add-gen/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sandeepbangaru17/ai-add-gen/discussions)

---

<p align="center">
  <strong>Made with ❤️ for creators who want professional ads without the complexity</strong>
</p>

<p align="center">
  ⭐ Star this repo if you found it useful!
</p>
