"""
app.py — Flask web application for AI Video Ad Generator.
Run: python app.py  |  Open: http://localhost:5000
"""

import os, uuid, json, threading
from pathlib import Path
from datetime import datetime
from flask import (Flask, render_template, request,
                   Response, jsonify, send_file, abort)
from dotenv import load_dotenv

load_dotenv()

from script_generator import generate_script
from pipeline_core import run_pipeline

app = Flask(__name__)
app.secret_key = os.urandom(24)

JOBS_DIR = Path(__file__).parent / "jobs"
JOBS_DIR.mkdir(exist_ok=True)

# In-memory job registry  { job_id: { status, queue, brand } }
_jobs: dict = {}

VOICES = {
    "aria":   {"name": "Aria",    "id": "en-US-AriaNeural",    "flag": "🇺🇸", "gender": "♀", "style": "Warm & Conversational",    "desc": "Natural, friendly — great for lifestyle & SaaS"},
    "jenny":  {"name": "Jenny",   "id": "en-US-JennyNeural",   "flag": "🇺🇸", "gender": "♀", "style": "Upbeat & Energetic",        "desc": "Bright and optimistic — perfect for consumer apps"},
    "sara":   {"name": "Sara",    "id": "en-US-SaraNeural",    "flag": "🇺🇸", "gender": "♀", "style": "Calm & Professional",       "desc": "Clear and polished — ideal for B2B products"},
    "guy":    {"name": "Guy",     "id": "en-US-GuyNeural",     "flag": "🇺🇸", "gender": "♂", "style": "Confident & Clear",         "desc": "Trustworthy and direct — works for anything"},
    "tony":   {"name": "Tony",    "id": "en-US-TonyNeural",    "flag": "🇺🇸", "gender": "♂", "style": "Bold & Authoritative",      "desc": "Strong presence — great for high-impact ads"},
    "ryan":   {"name": "Ryan",    "id": "en-GB-RyanNeural",    "flag": "🇬🇧", "gender": "♂", "style": "Sophisticated British",     "desc": "Premium feel — elevates luxury & tech brands"},
    "sonia":  {"name": "Sonia",   "id": "en-GB-SoniaNeural",   "flag": "🇬🇧", "gender": "♀", "style": "Elegant British",           "desc": "Refined and articulate — premium brand voice"},
    "natasha":{"name": "Natasha", "id": "en-AU-NatashaNeural", "flag": "🇦🇺", "gender": "♀", "style": "Fresh & Approachable",      "desc": "Relaxed yet professional — great for startups"},
}

BRAND_PRESETS = {
    "purple": {"label": "Purple & Pink",   "primary": [124,58,237],  "secondary": [236,72,153],  "preview": ["#7C3AED","#EC4899"]},
    "blue":   {"label": "Blue & Cyan",     "primary": [0,122,255],   "secondary": [0,210,255],   "preview": ["#007AFF","#00D2FF"]},
    "orange": {"label": "Orange & Red",    "primary": [255,107,53],  "secondary": [239,68,68],   "preview": ["#FF6B35","#EF4444"]},
    "green":  {"label": "Green & Teal",    "primary": [16,185,129],  "secondary": [6,182,212],   "preview": ["#10B981","#06B6D4"]},
    "gold":   {"label": "Gold & Amber",    "primary": [245,158,11],  "secondary": [251,191,36],  "preview": ["#F59E0B","#FBBF24"]},
}


# ── Helpers ──────────────────────────────────────────────────────────

def _load_meta(job_id: str) -> dict:
    """Load meta.json for a job, backfilling from script.json for old jobs."""
    job_dir  = JOBS_DIR / job_id
    meta_path = job_dir / "meta.json"

    if meta_path.exists():
        with open(meta_path) as f:
            return json.load(f)

    # Backfill meta for old jobs that pre-date meta.json
    meta = {
        "job_id":     job_id,
        "product":    "",
        "tagline":    "",
        "website":    "",
        "preset":     "purple",
        "preview":    ["#7C3AED", "#EC4899"],
        "created_at": datetime.fromtimestamp((job_dir).stat().st_mtime).strftime("%b %d, %Y · %H:%M"),
        "status":     "done" if (job_dir / "final.mp4").exists() else "processing",
    }
    script_path = job_dir / "script.json"
    if script_path.exists():
        with open(script_path) as f:
            script = json.load(f)
        # Try to extract product name from CTA scene voiceover or on_screen_text
        for sc in script.get("scenes", []):
            if sc.get("label") == "CTA":
                text = sc.get("on_screen_text", "")
                parts = text.split(".")
                meta["website"] = parts[-1].strip() if parts else ""
                meta["product"] = parts[0].strip() if parts else job_id
                break

    # Save for next time
    with open(meta_path, "w") as f:
        json.dump(meta, f)
    return meta


# ── Routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", presets=BRAND_PRESETS, voices=VOICES)


@app.route("/generate", methods=["POST"])
def generate():
    product_name    = request.form.get("product_name", "").strip()
    tagline         = request.form.get("tagline", "").strip()
    website_url     = request.form.get("website_url", "").strip()
    brand_preset    = request.form.get("brand_preset", "purple")
    website_display = request.form.get("website_display", "").strip()
    voice_key       = request.form.get("voice", "aria")

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    preset = BRAND_PRESETS.get(brand_preset, BRAND_PRESETS["purple"])
    brand  = {
        "name":      product_name,
        "tagline":   tagline or "The smarter way to work.",
        "website":   website_display or (
            website_url.replace("https://","").replace("http://","").rstrip("/")
            if website_url else f"{product_name.lower().replace(' ','')}.com"
        ),
        "primary":    tuple(preset["primary"]),
        "secondary":  tuple(preset["secondary"]),
        "preset":     brand_preset,
        "voice_id":   VOICES.get(voice_key, VOICES["aria"])["id"],
        "voice_name": VOICES.get(voice_key, VOICES["aria"])["name"],
    }

    job_id  = str(uuid.uuid4())[:8]
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata immediately so /videos can list it
    meta = {
        "job_id":    job_id,
        "product":   product_name,
        "tagline":   brand["tagline"],
        "website":   brand["website"],
        "preset":    brand_preset,
        "preview":   preset["preview"],
        "created_at": datetime.now().strftime("%b %d, %Y · %H:%M"),
        "status":     "processing",
        "voice_name": brand["voice_name"],
    }
    with open(job_dir / "meta.json", "w") as f:
        json.dump(meta, f)

    _jobs[job_id] = {"status": "processing", "log": [], "brand": brand, "meta": meta}

    def worker():
        job = _jobs[job_id]
        def push(msg):
            job["log"].append(msg)

        try:
            push("Analysing product and generating script...")
            script = generate_script(product_name, tagline, website_url)
            with open(job_dir / "script.json", "w") as f:
                json.dump(script, f, indent=2)
            push("Script ready. Starting video pipeline...")
            for msg in run_pipeline(job_dir, script, brand):
                push(msg)
                if msg.startswith("DONE|"):
                    job["status"] = "done"
                    meta["status"] = "done"
                    with open(job_dir / "meta.json", "w") as f:
                        json.dump(meta, f)
                    return
            meta["status"] = "done"
            with open(job_dir / "meta.json", "w") as f:
                json.dump(meta, f)
        except Exception as e:
            push(f"ERROR|{e}")
            job["status"] = "error"

    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/job/<job_id>")
def job_page(job_id):
    """Single page: shows progress then reveals video inline when done."""
    job_dir = JOBS_DIR / job_id
    if not job_dir.exists():
        abort(404)
    meta = _load_meta(job_id)
    job  = _jobs.get(job_id, {})
    brand = job.get("brand", {
        "name":    meta.get("product", ""),
        "tagline": meta.get("tagline", ""),
        "website": meta.get("website", ""),
        "preset":  meta.get("preset", "purple"),
    })
    return render_template("job.html", job_id=job_id, brand=brand, meta=meta)


@app.route("/progress/<job_id>")
def progress_stream(job_id):
    """Polling endpoint — returns new log messages since `since` index."""
    since = int(request.args.get("since", 0))

    if job_id not in _jobs:
        # Job not in memory — check if already done on disk
        job_dir = JOBS_DIR / job_id
        if (job_dir / "meta.json").exists():
            with open(job_dir / "meta.json") as f:
                meta = json.load(f)
            if meta.get("status") == "done":
                slug = meta.get("product", "video").lower().replace(" ", "_")
                formats = {
                    lbl: f"{slug}_{lbl}.mp4"
                    for lbl in ["16x9", "9x16", "1x1"]
                    if (job_dir / f"{slug}_{lbl}.mp4").exists()
                }
                return jsonify({
                    "status": "done",
                    "messages": [f"DONE|{json.dumps(formats)}"],
                    "next": 1,
                })
        abort(404)

    job  = _jobs[job_id]
    log  = job["log"]
    new  = log[since:]
    return jsonify({
        "status":   job["status"],
        "messages": new,
        "next":     since + len(new),
    })


@app.route("/videos")
def videos():
    jobs = []
    for d in sorted(JOBS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not d.is_dir():
            continue
        try:
            meta = _load_meta(d.name)
            final = d / "final.mp4"
            meta["has_video"] = final.exists()
            meta["size_mb"]   = round(final.stat().st_size / 1_048_576, 1) if final.exists() else 0
            jobs.append(meta)
        except Exception:
            continue
    return render_template("videos.html", jobs=jobs)


@app.route("/watch/<job_id>/<filename>")
def watch(job_id, filename):
    job_dir   = JOBS_DIR / job_id
    file_path = job_dir / filename
    if not file_path.exists() or file_path.suffix != ".mp4":
        abort(404)
    return send_file(str(file_path), mimetype="video/mp4")


@app.route("/download/<job_id>/<filename>")
def download(job_id, filename):
    job_dir   = JOBS_DIR / job_id
    file_path = job_dir / filename
    if not file_path.exists() or file_path.suffix != ".mp4":
        abort(404)
    return send_file(str(file_path), as_attachment=True, download_name=filename)


# ── Error handlers ────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, threaded=True, host="0.0.0.0", port=port)
