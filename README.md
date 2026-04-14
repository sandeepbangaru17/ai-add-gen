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
  Free • No credit card required • No video editing skills needed
</p>

---

## 🎥 See It In Action

<p align="center">
  <strong>30-Second ZunoSync Advertisement - Generated with AI</strong>
</p>

<div align="center">

https://github.com/user-attachments/assets/video-placeholder

</div>

<p align="center">
  <em>This entire video was created using the AI Ad Creation Pipeline — from script to final export</em>
</p>

<details>
<summary><strong>📋 View the Generated Script</strong></summary>

```json
{
  "product_name": "ZunoSync",
  "target_audience": "Small business owners and startups",
  "total_duration_seconds": 30,
  "scenes": [
    {
      "scene_id": 1,
      "duration_seconds": 8,
      "voiceover": "Managing social media for your business shouldn't feel like a second job...",
      "on_screen_text": "Social Media Overload?",
      "visual_description": "A stressed small business owner with multiple devices showing different social media apps"
    },
    {
      "scene_id": 2,
      "duration_seconds": 8,
      "voiceover": "What if you could manage all your accounts from one simple dashboard?",
      "on_screen_text": "One Dashboard. All Platforms.",
      "visual_description": "Clean desk with ZunoSync dashboard in brand colors"
    },
    {
      "scene_id": 3,
      "duration_seconds": 8,
      "voiceover": "Thousands of small businesses already save hours every week with ZunoSync...",
      "on_screen_text": "Trusted by 10,000+ Businesses",
      "visual_description": "Diverse business owners using ZunoSync with engagement metrics"
    },
    {
      "scene_id": 4,
      "duration_seconds": 6,
      "voiceover": "Start your free trial today at zunosync.com...",
      "on_screen_text": "Start Free Trial at zunosync.com",
      "visual_description": "Clean Get Started button with brand colors"
    }
  ]
}
```

</details>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Script Generation** | Create compelling ad scripts with Groq's Llama 3.3 |
| 🎙️ **Natural Voiceover** | Professional neural voices using Microsoft Edge TTS |
| 🎨 **AI Image Generation** | Stunning visuals with Pollinations Flux (free, no API key) |
| 🎬 **Ken Burns Effect** | Cinematic motion on static images |
| 📱 **Multi-Platform Export** | Optimized for Instagram, YouTube, TikTok, Facebook |
| 💾 **Complete Deliverables** | Master video, social cuts, subtitles, metadata |

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

**Interactive Mode:**
```bash
python pipeline.py
```

**Demo Mode (ZunoSync ad):**
```bash
python pipeline.py --default
```

**Custom Brief:**
```bash
python pipeline.py --brief my_brief.json
```

---

## 📁 Project Structure

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
│   ├── stitch_agent.py         # Video assembly (FFmpeg)
│   ├── post_agent.py          # Platform exports
│   └── export_agent.py        # Final packaging
├── 📁 schemas/                 # JSON validation schemas
├── 📄 zunosync_ad_script.json  # Production example script
├── 📄 requirements.txt         # Python dependencies
├── 📄 spec.md                 # Technical specification
└── 📄 README.md               # This file
```

---

## 🎯 How It Works

The pipeline consists of **8 stages** that transform a campaign brief into professional video advertisements:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE OVERVIEW                               │
├──────────────┬──────────────┬──────────────┬────────────────────────────┤
│  Stage       │  Agent       │  Tool        │  Output                   │
├──────────────┼──────────────┼──────────────┼────────────────────────────┤
│ 1. Brief     │ Brief Agent  │ CLI Input    │ brief.json                │
│ 2. Script    │ Script Agent │ Groq LLM     │ script.json               │
│ 3. Voice     │ Voice Agent  │ edge-tts     │ voiceover.mp3 + SRT       │
│ 4. Prompts   │ Prompt Agent │ Groq LLM     │ scene_prompts.json        │
│ 5. Video     │ Video Agent  │ Pollinations │ scene_clips/              │
│ 6. Stitch    │ Stitch Agent │ FFmpeg       │ ad_draft.mp4              │
│ 7. Post      │ Post Agent   │ FFmpeg       │ 4 format variations       │
│ 8. Export    │ Export Agent │ FFmpeg       │ final_output/             │
└──────────────┴──────────────┴──────────────┴────────────────────────────┘
```

### Stage Details

| Stage | Description | Output |
|-------|-------------|--------|
| **1. Brief** | Enter campaign details | `brief.json` |
| **2. Script** | AI generates 4-scene script with voiceovers | `script.json` |
| **3. Voice** | Neural TTS creates professional voiceover | `voiceover.mp3` |
| **4. Prompts** | AI generates visual prompts for each scene | `scene_prompts.json` |
| **5. Video** | AI generates images + Ken Burns effect | `scene_clips/*.mp4` |
| **6. Stitch** | Combines clips, adds audio, burns subtitles | `ad_draft.mp4` |
| **7. Post** | Exports to 9:16, 1:1, 16:9 formats | `zunosync_*.mp4` |
| **8. Export** | Packages in organized folder structure | `final_output/` |

---

## 📂 Output Structure

After running the pipeline:

```
final_output/
├── 📁 master/
│   └── zunosync_ad_master_HD.mp4      # High quality (1920x1080)
│
├── 📁 social/
│   ├── zunosync_ad_9x16_reels.mp4     # Instagram Reels / TikTok
│   ├── zunosync_ad_1x1_feed.mp4       # Instagram Feed / Facebook
│   └── zunosync_ad_16x9_youtube.mp4   # YouTube / LinkedIn
│
├── 📁 assets/
│   ├── subtitles.srt                  # Subtitles file
│   └── thumbnail.png                  # Video thumbnail
│
└── 📁 metadata/
    ├── brief.json                     # Original brief
    ├── script.json                    # Generated script
    ├── scene_prompts.json             # Visual prompts
    └── production_log.json           # Execution log
```

---

## 🎨 Example Campaign Brief

Create a `my_brief.json`:

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

**Validation Rules:**
- `ad_duration_seconds`: Must be 15, 30, or 60
- `platform`: At least one platform required
- `cta`: Maximum 60 characters

---

## 🛠️ Tools & Technologies

### All Free — No Credit Card Required

| Tool | Purpose | Cost |
|------|---------|------|
| **Groq API** | LLM for script & prompts | Free tier (30 req/min) |
| **edge-tts** | Neural text-to-speech | Completely free |
| **Pollinations AI** | AI image generation | Completely free |
| **FFmpeg** | Video processing | Open source |

### Why These Tools?

- **Groq**: Fastest LLM inference, generous free tier
- **edge-tts**: High-quality Microsoft neural voices
- **Pollinations**: No API key needed, excellent image quality
- **FFmpeg**: Industry-standard video processing

---

## ⏱️ Performance

| Metric | Time |
|--------|------|
| **Total Pipeline** | ~2-3 minutes |
| **Script Generation** | ~3 seconds |
| **Voice Generation** | ~10-25 seconds |
| **Prompt Generation** | ~2 seconds |
| **Image Generation** | ~5-10 seconds per scene |
| **Video Assembly** | ~30 seconds |

---

## 🔧 Configuration

### Command Line Options

```bash
python pipeline.py [options]

Options:
  --default              Use built-in ZunoSync test brief
  --brief <path>         Use custom brief JSON file
  --start-from <stage>   Resume from stage 1-8
```

### Resume from Any Stage

```bash
# Resume from voice generation
python pipeline.py --start-from 3

# Resume from video generation
python pipeline.py --start-from 5
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "GROQ_API_KEY not set" | Add API key to `.env` file |
| FFmpeg not found | Install FFmpeg and add to PATH |
| Fontconfig error | Normal on Windows, subtitles still work |
| Images look blurry | Using Pollinations Flux (default) |

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

## 📊 Example: 30-Second ZunoSync Ad

### Script Structure

| Scene | Duration | Purpose | Key Message |
|-------|----------|---------|-------------|
| 1 | 8s | **Problem** | Social media overwhelm |
| 2 | 8s | **Solution** | One dashboard for all |
| 3 | 8s | **Proof** | 10,000+ businesses trust it |
| 4 | 6s | **CTA** | Start free trial |

### The Ad Flow

```
Scene 1: Problem
┌─────────────────────────────────────┐
│  😰 Multiple devices, different      │
│  platforms, overwhelming           │
│                                     │
│  "Social Media Overload?"           │
└─────────────────────────────────────┘

Scene 2: Solution
┌─────────────────────────────────────┐
│  😊 Clean desk, single dashboard    │
│  showing ZunoSync                   │
│                                     │
│  "One Dashboard. All Platforms."    │
└─────────────────────────────────────┘

Scene 3: Social Proof
┌─────────────────────────────────────┐
│  👥 Diverse businesses succeeding   │
│  with growing engagement metrics    │
│                                     │
│  "Trusted by 10,000+ Businesses"    │
└─────────────────────────────────────┘

Scene 4: Call to Action
┌─────────────────────────────────────┐
│  🖱️ "Get Started" button           │
│  with brand colors                  │
│                                     │
│  "Start Free Trial → zunosync.com" │
└─────────────────────────────────────┘
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit with detailed messages
4. Push and open a Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** - Fast and free LLM inference
- **Microsoft** - Edge-tts neural voices
- **Pollinations** - Free AI image generation
- **FFmpeg** - Industry-standard video processing

---

<p align="center">
  <strong>Made with ❤️ for creators who want professional ads without the complexity</strong>
</p>

<p align="center">
  <a href="https://github.com/sandeepbangaru17/ai-add-gen">⭐ Star this repo</a>
  •
  <a href="https://github.com/sandeepbangaru17/ai-add-gen/issues">Report Bug</a>
  •
  <a href="https://github.com/sandeepbangaru17/ai-add-gen/discussions">Request Feature</a>
</p>
