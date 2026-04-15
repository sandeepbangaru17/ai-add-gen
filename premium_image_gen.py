"""
Premium Image Generator - High Quality AI Images
"""
import io
import json
import time
import requests
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

# Windows encoding fix
import sys
if sys.platform == "win32":
    import io as io_module
    sys.stdout = io_module.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUTPUT_DIR = Path("output/scene_images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Premium prompts with quality modifiers
PREMIUM_PROMPTS = {
    1: "professional photograph of tired business owner working late at night, messy desk with papers and coffee, multiple glowing laptop screens showing social media apps, stressed expression, moody dark office lighting with warm desk lamp, cinematic portrait, ultra realistic, 8k resolution, sharp focus, commercial photography",
    2: "professional photograph of happy young entrepreneur smiling at modern laptop showing clean dashboard interface, bright spacious office with large windows, natural sunlight, green plants, sleek furniture, clean minimalist design, ultra realistic, 8k, sharp focus, lifestyle commercial",
    3: "professional photograph of confident business owner looking at laptop with rising graphs and charts, modern standing desk, city skyline visible through window, golden hour sunlight, analytics dashboard on screen, coffee cup, ultra realistic, 8k, sharp focus, corporate lifestyle",
    4: "professional product photograph of modern laptop screen with large colorful Get Started button, clean white desk, celebratory atmosphere, diverse happy team in background smiling, confetti, bright inviting office, ultra realistic, 8k, sharp focus, premium product shot"
}

def enhance_image(img):
    """Enhance image for premium quality"""
    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    # Increase contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    
    # Slight color enhancement
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.05)
    
    return img

def upscale_image(img, target_size=(1920, 1080)):
    """Upscale image using high-quality resampling"""
    # First upscale with LANCZOS
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Apply subtle unsharp mask for crispness
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    
    return img

def generate_premium_image(scene_num, prompt, seed=42):
    """Generate premium quality image"""
    print(f"\n[SCENE {scene_num}] Generating premium image...")
    
    # Add quality modifiers to prompt
    quality_prompt = f"{prompt}, masterpiece, best quality, highly detailed, ultra sharp, professional lighting, studio grade"
    
    for attempt in range(5):
        try:
            print(f"   Attempt {attempt+1}/5...")
            
            # Try different seeds for variety
            current_seed = seed + attempt * 100
            
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(quality_prompt)}?width=1024&height=576&seed={current_seed}&model=flux&nologo=true"
            
            response = requests.get(url, timeout=180)
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                
                # Enhance and upscale
                img = upscale_image(img, (1920, 1080))
                img = enhance_image(img)
                
                # Save
                output_path = OUTPUT_DIR / f"scene_{scene_num}_premium.png"
                img.save(str(output_path), "PNG", quality=95)
                
                print(f"   [OK] Saved: {output_path.name}")
                return output_path
            
            print(f"   Status: {response.status_code}, retrying...")
            time.sleep(5)
            
        except Exception as e:
            print(f"   Error: {e}")
            time.sleep(5)
    
    return None

def main():
    print("=" * 60)
    print(" PREMIUM IMAGE GENERATION")
    print("=" * 60)
    
    for scene_num, prompt in PREMIUM_PROMPTS.items():
        result = generate_premium_image(scene_num, prompt)
        if result:
            print(f"   Done: {result}")
        else:
            print(f"   Failed!")
    
    print("\n" + "=" * 60)
    print(" PREMIUM IMAGES COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
