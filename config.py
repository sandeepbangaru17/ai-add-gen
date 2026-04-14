"""
Configuration module for the AI Ad Creation Pipeline.
Loads environment variables and defines paths, model settings, and defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ─── Load .env ───────────────────────────────────────────────────────
load_dotenv()

# ─── API Keys ────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# ─── Paths ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
SCHEMAS_DIR = BASE_DIR / "schemas"
FINAL_OUTPUT_DIR = BASE_DIR / "final_output"

# Sub-directories under output/
VOICE_DIR = OUTPUT_DIR / "voice"
SCENE_IMAGES_DIR = OUTPUT_DIR / "scene_images"
SCENE_CLIPS_DIR = OUTPUT_DIR / "scene_clips"
RAW_CLIPS_DIR = OUTPUT_DIR / "raw_clips"
METADATA_DIR = FINAL_OUTPUT_DIR / "metadata"
SOCIAL_DIR = FINAL_OUTPUT_DIR / "social"
MASTER_DIR = FINAL_OUTPUT_DIR / "master"
ASSETS_OUT_DIR = FINAL_OUTPUT_DIR / "assets"

# Music
MUSIC_DIR = ASSETS_DIR / "music"

# ─── Model Settings ──────────────────────────────────────────────────
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_FALLBACK_MODEL = "llama-3.1-8b-instant"
HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

# ─── Voice Settings ──────────────────────────────────────────────────
VOICE_MAP = {
    "professional": "en-US-GuyNeural",
    "energetic": "en-US-TonyNeural",
    "emotional": "en-US-AriaNeural",
    "urgent": "en-US-DavisNeural",
    "warm": "en-US-JennyNeural",
    "default": "en-US-GuyNeural",
}

# ─── Video Settings ──────────────────────────────────────────────────
VIDEO_FPS = 24
VIDEO_RESOLUTION = (1920, 1080)  # 16:9 master
VERTICAL_RESOLUTION = (1080, 1920)  # 9:16
SQUARE_RESOLUTION = (1080, 1080)  # 1:1

# ─── FFmpeg ──────────────────────────────────────────────────────────
_FFMPEG_DIR = Path(
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
)
FFMPEG_BIN = str(_FFMPEG_DIR / "ffmpeg.exe")
FFPROBE_BIN = str(_FFMPEG_DIR / "ffprobe.exe")


# ─── Ensure directories exist ────────────────────────────────────────
def ensure_dirs():
    """Create all required output directories."""
    dirs = [
        OUTPUT_DIR,
        VOICE_DIR,
        SCENE_IMAGES_DIR,
        SCENE_CLIPS_DIR,
        RAW_CLIPS_DIR,
        FINAL_OUTPUT_DIR,
        METADATA_DIR,
        SOCIAL_DIR,
        MASTER_DIR,
        ASSETS_OUT_DIR,
        ASSETS_DIR,
        MUSIC_DIR,
        SCHEMAS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
