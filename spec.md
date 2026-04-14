# AI Ad Creation Pipeline — Technical Specification

**Project:** End-to-End AI-Generated Advertisement Pipeline  
**Version:** 1.0  
**Status:** Draft  
**Author:** [Your Name]  
**Date:** April 2026

---

## 1. Overview

This document defines the technical architecture, agent responsibilities, data contracts, and delivery requirements for an automated AI ad creation pipeline. The system accepts a campaign brief as input and outputs a fully produced video advertisement with voiceover, subtitles, and platform-optimised exports.

### 1.1 Goal

Build a multi-agent pipeline where each stage is handled by a specialised AI tool, with structured data flowing between stages and minimal manual intervention required.

### 1.2 Reference Use Case

> "Create a 30-second ad for ZunoSync targeting small business owners, highlighting AI-powered social media automation."

This serves as the test case for validating every stage of the pipeline.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Stage       │  Agent       │  Tool        │  Output            │
├──────────────┼──────────────┼──────────────┼────────────────────┤
│ 1. Brief     │ Brief Agent  │ Input Form   │ brief.json         │
│ 2. Script    │ Script Agent │ Groq LLM     │ script.json        │
│              │              │ (Llama 3.3)  │                    │
│ 3. Voice     │ Voice Agent  │ edge-tts     │ voiceover.mp3      │
│              │              │ (Microsoft)  │                    │
│ 4. Prompts   │ Prompt Agent │ Groq LLM     │ scene_prompts.json │
│ 5. Video     │ Video Agent  │ HuggingFace  │ scene_clips/       │
│              │              │ (SDXL) +     │                    │
│              │              │ Ken Burns    │                    │
│ 6. Stitch    │ Stitch Agent │ FFmpeg       │ ad_draft.mp4       │
│ 7. Post      │ Post Agent   │ FFmpeg       │ ad_final.mp4       │
│ 8. Export    │ Export Agent │ FFmpeg       │ exports/           │
└──────────────┴──────────────┴──────────────┴────────────────────┘

NOTE: All tools used are FREE tier — no credit card required.
```

---

## 3. Stage-by-Stage Specification

---

### Stage 1 — Ad Brief Input

**Responsibility:** Collect and validate the campaign brief from the user.

**Input:** User-provided form or JSON payload

**Output:** `brief.json`

```json
{
  "product_name": "ZunoSync",
  "tagline": "Your AI marketing team in one click",
  "target_audience": "Small business owners",
  "ad_duration_seconds": 30,
  "tone": "professional, energetic",
  "platform": ["Instagram Reel", "YouTube Ad"],
  "cta": "Try ZunoSync free for 14 days",
  "brand_colors": ["#1A1AFF", "#FFFFFF"],
  "logo_url": "https://cdn.example.com/zunosync-logo.png"
}
```

**Validation Rules:**
- `ad_duration_seconds` must be 15, 30, or 60
- `platform` must be a non-empty array
- `cta` must not exceed 60 characters

---

### Stage 2 — Script Generation

**Responsibility:** Generate a structured scene-by-scene script with voiceover narration and on-screen text.

**Tool:** Groq LLM (Llama 3.3 70B — Free tier)

**Input:** `brief.json`

**Output:** `script.json`

```json
{
  "total_duration_seconds": 30,
  "scenes": [
    {
      "scene_id": 1,
      "duration_seconds": 6,
      "voiceover": "Managing social media shouldn't take over your day.",
      "on_screen_text": "Sound familiar?",
      "visual_description": "Stressed entrepreneur at desk, multiple browser tabs open"
    },
    {
      "scene_id": 2,
      "duration_seconds": 8,
      "voiceover": "Meet ZunoSync — your AI marketing team in one click.",
      "on_screen_text": "ZunoSync",
      "visual_description": "Clean dashboard UI appears, notifications popping up"
    },
    {
      "scene_id": 3,
      "duration_seconds": 8,
      "voiceover": "Schedule posts, generate captions, and analyse performance — all automatically.",
      "on_screen_text": "Auto-schedule. Auto-caption. Auto-grow.",
      "visual_description": "Screen recording of ZunoSync features, smooth animations"
    },
    {
      "scene_id": 4,
      "duration_seconds": 8,
      "voiceover": "Join thousands of business owners who have reclaimed their time.",
      "on_screen_text": "Try free for 14 days →",
      "visual_description": "Happy business owner on phone, brand logo on screen"
    }
  ]
}
```

**LLM Prompt Template:**

```
You are a professional ad copywriter. Given the following campaign brief, 
generate a structured {duration}-second video ad script.

Brief: {brief_json}

Return ONLY valid JSON matching this schema: {schema}

Requirements:
- Hook the viewer in the first 3 seconds
- Keep each scene voiceover under 20 words
- End with a clear CTA
- Tone: {tone}
```

---

### Stage 3 — Voice Generation

**Responsibility:** Convert the voiceover narration into a realistic audio track.

**Tool:** Microsoft edge-tts (Free, no API key required)

**Input:** Array of `voiceover` strings from `script.json`

**Output:** `voiceover.mp3` (merged), individual `scene_{n}_voice.mp3` files

**Voice Selection (edge-tts):**

| Tone        | Recommended Voice Style          |
|-------------|----------------------------------|
| Professional| en-US-GuyNeural (Male, calm)    |
| Energetic   | en-US-TonyNeural (Male, upbeat)  |
| Emotional   | en-US-AriaNeural (Female, warm)  |
| Urgent      | en-US-DavisNeural (Male, direct) |
| Warm        | en-US-JennyNeural (Female, soft) |

*edge-tts uses Microsoft Edge neural voices, no API key required.*

**A/B Testing:** Generate 2 voice variants per ad for testing.

---

### Stage 4 — Scene Prompt Creation

**Responsibility:** Convert each script scene into a cinematic visual prompt for the video generation tool.

**Tool:** Groq LLM (same as Stage 2)

**Input:** `script.json`

**Output:** `scene_prompts.json`

```json
{
  "scenes": [
    {
      "scene_id": 1,
      "video_prompt": "A stressed young entrepreneur sitting at a cluttered wooden desk, multiple browser tabs visible on laptop screen, natural window lighting, shallow depth of field, cinematic commercial style, 4K, warm tones",
      "duration_seconds": 6,
      "camera": "medium shot, slight push-in",
      "mood": "relatable frustration"
    }
  ]
}
```

**Prompt Structure Template:**

```
{subject description}, {environment}, {lighting}, {camera angle}, 
{motion instruction}, {visual style}, {brand mood}
```

---

### Stage 5 — AI Video Generation

**Responsibility:** Generate short video clips for each scene.

**Tool:** Pollinations AI Flux model (free, no API key) + FFmpeg Ken Burns effect

*Pollinations Flux provides high-quality AI image generation. Falls back to Pillow-generated placeholder images if unavailable.*

**Input:** `scene_prompts.json`

**Output:** `scene_clips/scene_{n}.mp4`

**Clip Specifications:**

| Property      | Value                  |
|---------------|------------------------|
| Duration      | 3–6 seconds per clip   |
| Resolution    | 1080p minimum          |
| Frame rate    | 24fps                  |
| Aspect ratio  | 9:16 (Reels), 16:9 (YouTube) |
| Style         | Consistent across all scenes |

**Notes:**
- Generate 2 variants per scene and select the best
- Maintain consistent character appearance across scenes if a person is shown
- Store raw outputs in `/raw_clips/` before selection

---

### Stage 6 — Asset Stitching & Video Assembly

**Responsibility:** Combine all scene clips, voiceover audio, background music, transitions, and text overlays into a single draft video.

**Tool:** FFmpeg

**Input:**
- `scene_clips/scene_{n}.mp4`
- `voiceover.mp3`
- `music/background.mp3`
- `assets/logo.png`
- `script.json` (for subtitle timing)

**Output:** `ad_draft.mp4`

**FFmpeg Assembly Command:**

```bash
# Concatenate scene clips
ffmpeg -f concat -safe 0 -i clips_list.txt -c copy merged_clips.mp4

# Mix voiceover + background music (music at -20dB)
ffmpeg -i merged_clips.mp4 -i voiceover.mp3 -i background.mp3 \
  -filter_complex "[1:a]volume=1.0[vo]; [2:a]volume=0.2[bg]; [vo][bg]amix=inputs=2[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac ad_with_audio.mp4

# Add subtitles
ffmpeg -i ad_with_audio.mp4 -vf "subtitles=subtitles.srt" ad_draft.mp4
```

**Subtitle Generation:**
- Auto-generate `.srt` file from `script.json` voiceover timings
- Font: Bold sans-serif, white with black outline
- Position: Lower third

---

### Stage 7 — Post-Processing

**Responsibility:** Apply final enhancements and resize for all target platforms.

**Tool:** FFmpeg / CapCut API

**Input:** `ad_draft.mp4`

**Output:** Platform-specific versions

**Export Formats:**

| Format    | Resolution  | Aspect Ratio | Platform              |
|-----------|-------------|--------------|----------------------|
| Vertical  | 1080×1920   | 9:16         | Instagram Reels, TikTok, YouTube Shorts |
| Square    | 1080×1080   | 1:1          | Instagram Feed, Facebook |
| Landscape | 1920×1080   | 16:9         | YouTube, LinkedIn     |
| Master    | 1920×1080   | 16:9         | Archive / TV          |

**FFmpeg Resize Commands:**

```bash
# 9:16 vertical
ffmpeg -i ad_draft.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" vertical.mp4

# 1:1 square
ffmpeg -i ad_draft.mp4 -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2" square.mp4
```

**Optional Enhancements:**
- Sound effects (whoosh, notification ping) at key moments
- Colour grade / LUT for brand consistency
- Lip-sync avatar overlay if spokesperson is AI-generated

---

### Stage 8 — Final Export & Distribution

**Responsibility:** Package all deliverables and prepare for upload/distribution.

**Output Directory Structure:**

```
final_output/
├── master/
│   └── zunosync_ad_master_HD.mp4
├── social/
│   ├── zunosync_ad_9x16_reels.mp4
│   ├── zunosync_ad_1x1_feed.mp4
│   └── zunosync_ad_16x9_youtube.mp4
├── assets/
│   ├── thumbnail.png
│   └── subtitles.srt
└── metadata/
    ├── brief.json
    ├── script.json
    └── production_log.json
```

---

## 4. Data Flow Summary

```
brief.json
    └──► script.json
              ├──► voiceover.mp3      (ElevenLabs)
              └──► scene_prompts.json
                        └──► scene_clips/*.mp4  (Seedance/Runway)
                                  └──► ad_draft.mp4  (FFmpeg)
                                            └──► exports/  (FFmpeg resize)
```

---

## 5. API Keys & Environment Variables

```env
GROQ_API_KEY=          # Free: https://console.groq.com/keys
HF_TOKEN=              # Optional (for HF fallback): https://huggingface.co/settings/tokens
PEXELS_API_KEY=        # Optional: https://www.pexels.com/api/
```

> **Note:** 
> - edge-tts and Pollinations AI require no API keys
> - FFmpeg must be installed locally
> - Groq provides free LLM access with generous rate limits

---

## 6. Error Handling

| Stage | Failure Scenario              | Fallback Action                              |
|-------|-------------------------------|---------------------------------------------|
| 2     | LLM returns invalid JSON      | Retry with stricter prompt, use fallback model |
| 3     | edge-tts fails                | Retry 3 times, skip audio if persistent    |
| 5     | Pollinations AI fails         | Try HuggingFace API, then Pillow fallback    |
| 6     | FFmpeg merge fails            | Check codec compatibility, re-encode clips   |
| 6     | FFmpeg subtitles fails        | Copy video without subtitles as fallback      |

---

## 7. Timeline Estimate

| Stage | Task                        | Estimated Time |
|-------|-----------------------------|----------------|
| 1–2   | Brief + Script generation   | 1–2 hours      |
| 3     | Voice generation            | 30 minutes     |
| 4–5   | Scene prompts + Video gen   | 2–4 hours      |
| 6–7   | Stitching + Post-processing | 1–2 hours      |
| 8     | Export + QA                 | 30 minutes     |
| **Total** |                         | **~1 working day** |

---

## 8. Open Questions for Lead

1. Is FFmpeg installed locally? (Required for video processing)
2. Do you have a Groq API key? (Free at console.groq.com)
3. Do you have a HuggingFace token? (Free at huggingface.co/settings/tokens)
4. What is the priority platform for the first deliverable (Instagram or YouTube)?
5. Should the pipeline be fully automated or semi-manual for the first version?

---

## 9. Glossary

| Term        | Meaning                                        |
|-------------|------------------------------------------------|
| Brief       | Campaign input defining product, audience, CTA |
| Storyboard  | Scene-by-scene breakdown of the ad             |
| TTS         | Text-to-Speech (voice generation)             |
| FFmpeg      | Open-source tool for video/audio processing   |
| Ken Burns   | Slow pan/zoom effect on still images          |
| Groq        | Free LLM API provider using Meta Llama models  |
| edge-tts    | Microsoft Edge browser's free TTS service      |
| Pollinations| Free AI image generation service (no API key) |

---

*This spec is a living document. Update after each stage is validated.*
