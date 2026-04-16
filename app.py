"""
app.py — Flask web application for AI Video Ad Generator.
Run: python app.py
Open: http://localhost:5000
"""

import os, uuid, json, queue, threading
from pathlib import Path
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

# In-memory job registry  { job_id: { status, queue, script, brand } }
_jobs: dict = {}

# Brand color presets
BRAND_PRESETS = {
    "purple": {
        "label":     "Purple & Pink",
        "primary":   [124,  58, 237],
        "secondary": [236,  72, 153],
        "preview":   ["#7C3AED", "#EC4899"],
    },
    "blue": {
        "label":     "Blue & Cyan",
        "primary":   [  0, 122, 255],
        "secondary": [  0, 210, 255],
        "preview":   ["#007AFF", "#00D2FF"],
    },
    "orange": {
        "label":     "Orange & Red",
        "primary":   [255, 107,  53],
        "secondary": [239,  68,  68],
        "preview":   ["#FF6B35", "#EF4444"],
    },
    "green": {
        "label":     "Green & Teal",
        "primary":   [ 16, 185, 129],
        "secondary": [  6, 182, 212],
        "preview":   ["#10B981", "#06B6D4"],
    },
    "gold": {
        "label":     "Gold & Amber",
        "primary":   [245, 158,  11],
        "secondary": [251, 191,  36],
        "preview":   ["#F59E0B", "#FBBF24"],
    },
}


# ── Routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", presets=BRAND_PRESETS)


@app.route("/generate", methods=["POST"])
def generate():
    product_name = request.form.get("product_name", "").strip()
    tagline      = request.form.get("tagline", "").strip()
    website_url  = request.form.get("website_url", "").strip()
    brand_preset = request.form.get("brand_preset", "purple")
    website_display = request.form.get("website_display", "").strip()

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    preset = BRAND_PRESETS.get(brand_preset, BRAND_PRESETS["purple"])
    brand  = {
        "name":      product_name,
        "tagline":   tagline or "The smarter way to work.",
        "website":   website_display or (website_url.replace("https://","").replace("http://","").rstrip("/") if website_url else f"{product_name.lower().replace(' ','')}.com"),
        "primary":   tuple(preset["primary"]),
        "secondary": tuple(preset["secondary"]),
    }

    job_id  = str(uuid.uuid4())[:8]
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    q = queue.Queue()
    _jobs[job_id] = {"status": "starting", "queue": q, "brand": brand}

    def worker():
        try:
            q.put("Analysing product and generating script...")
            script = generate_script(product_name, tagline, website_url)
            # Save script for reference
            with open(job_dir / "script.json", "w") as f:
                json.dump(script, f, indent=2)
            _jobs[job_id]["script"] = script
            q.put("Script ready. Starting video pipeline...")
            for msg in run_pipeline(job_dir, script, brand):
                q.put(msg)
        except Exception as e:
            q.put(f"ERROR|{e}")

    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
def progress(job_id):
    if job_id not in _jobs:
        abort(404)

    def stream():
        q = _jobs[job_id]["queue"]
        while True:
            try:
                msg = q.get(timeout=120)
                yield f"data: {msg}\n\n"
                if msg.startswith("DONE|") or msg.startswith("ERROR"):
                    break
            except queue.Empty:
                yield "data: [TIMEOUT]\n\n"
                break

    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/result/<job_id>")
def result(job_id):
    job_dir = JOBS_DIR / job_id
    if not job_dir.exists():
        abort(404)
    final = job_dir / "final.mp4"
    if not final.exists():
        abort(404)

    job   = _jobs.get(job_id, {})
    brand = job.get("brand", {})

    # Collect format files
    formats = {}
    for label in ["16x9", "9x16", "1x1"]:
        slug = brand.get("name", "video").lower().replace(" ", "_")
        f = job_dir / f"{slug}_{label}.mp4"
        if f.exists():
            formats[label] = f.name

    return render_template("result.html",
                           job_id=job_id,
                           brand=brand,
                           formats=formats,
                           final_name=final.name)


@app.route("/download/<job_id>/<filename>")
def download(job_id, filename):
    job_dir = JOBS_DIR / job_id
    file_path = job_dir / filename
    if not file_path.exists() or not file_path.suffix == ".mp4":
        abort(404)
    return send_file(str(file_path), as_attachment=True,
                     download_name=filename)


@app.route("/watch/<job_id>/<filename>")
def watch(job_id, filename):
    """Stream video for in-browser playback."""
    job_dir   = JOBS_DIR / job_id
    file_path = job_dir / filename
    if not file_path.exists():
        abort(404)
    return send_file(str(file_path), mimetype="video/mp4")


if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000)
