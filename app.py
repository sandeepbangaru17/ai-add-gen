"""
app.py — Flask web application for AI Video Ad Generator.
Run: python app.py  |  Open: http://localhost:5000
"""

import os, uuid, json, queue, threading
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

BRAND_PRESETS = {
    "purple": {"label": "Purple & Pink",   "primary": [124,58,237],  "secondary": [236,72,153],  "preview": ["#7C3AED","#EC4899"]},
    "blue":   {"label": "Blue & Cyan",     "primary": [0,122,255],   "secondary": [0,210,255],   "preview": ["#007AFF","#00D2FF"]},
    "orange": {"label": "Orange & Red",    "primary": [255,107,53],  "secondary": [239,68,68],   "preview": ["#FF6B35","#EF4444"]},
    "green":  {"label": "Green & Teal",    "primary": [16,185,129],  "secondary": [6,182,212],   "preview": ["#10B981","#06B6D4"]},
    "gold":   {"label": "Gold & Amber",    "primary": [245,158,11],  "secondary": [251,191,36],  "preview": ["#F59E0B","#FBBF24"]},
}


# ── Routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", presets=BRAND_PRESETS)


@app.route("/generate", methods=["POST"])
def generate():
    product_name    = request.form.get("product_name", "").strip()
    tagline         = request.form.get("tagline", "").strip()
    website_url     = request.form.get("website_url", "").strip()
    brand_preset    = request.form.get("brand_preset", "purple")
    website_display = request.form.get("website_display", "").strip()

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
        "primary":   tuple(preset["primary"]),
        "secondary": tuple(preset["secondary"]),
        "preset":    brand_preset,
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
        "status":    "processing",
    }
    with open(job_dir / "meta.json", "w") as f:
        json.dump(meta, f)

    q = queue.Queue()
    _jobs[job_id] = {"status": "processing", "queue": q, "brand": brand, "meta": meta}

    def worker():
        try:
            q.put("Analysing product and generating script...")
            script = generate_script(product_name, tagline, website_url)
            with open(job_dir / "script.json", "w") as f:
                json.dump(script, f, indent=2)
            q.put("Script ready. Starting video pipeline...")
            for msg in run_pipeline(job_dir, script, brand):
                q.put(msg)
            # Mark done in meta
            meta["status"] = "done"
            with open(job_dir / "meta.json", "w") as f:
                json.dump(meta, f)
        except Exception as e:
            q.put(f"ERROR|{e}")

    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/job/<job_id>")
def job_page(job_id):
    """Single page: shows progress then reveals video inline when done."""
    job_dir = JOBS_DIR / job_id
    meta = {}
    if (job_dir / "meta.json").exists():
        with open(job_dir / "meta.json") as f:
            meta = json.load(f)
    job   = _jobs.get(job_id, {})
    brand = job.get("brand", {
        "name":    meta.get("product", ""),
        "tagline": meta.get("tagline", ""),
        "website": meta.get("website", ""),
        "preset":  meta.get("preset", "purple"),
    })
    return render_template("job.html", job_id=job_id, brand=brand, meta=meta)


@app.route("/progress/<job_id>")
def progress_stream(job_id):
    if job_id not in _jobs:
        # Job may have finished — send DONE immediately
        job_dir = JOBS_DIR / job_id
        if (job_dir / "meta.json").exists():
            with open(job_dir / "meta.json") as f:
                meta = json.load(f)
            if meta.get("status") == "done":
                slug = meta.get("product","video").lower().replace(" ","_")
                formats = {
                    lbl: f"{slug}_{lbl}.mp4"
                    for lbl in ["16x9","9x16","1x1"]
                    if (job_dir / f"{slug}_{lbl}.mp4").exists()
                }
                def _done():
                    yield f"data: DONE|{json.dumps(formats)}\n\n"
                return Response(_done(), mimetype="text/event-stream",
                                headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})
        abort(404)

    def stream():
        q = _jobs[job_id]["queue"]
        while True:
            try:
                msg = q.get(timeout=300)
                yield f"data: {msg}\n\n"
                if msg.startswith("DONE|") or msg.startswith("ERROR"):
                    break
            except queue.Empty:
                yield "data: [TIMEOUT]\n\n"
                break

    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


@app.route("/videos")
def videos():
    jobs = []
    for d in sorted(JOBS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        meta_path = d / "meta.json"
        if not meta_path.exists():
            continue
        with open(meta_path) as f:
            meta = json.load(f)
        # Check if final video exists
        final = d / "final.mp4"
        meta["has_video"] = final.exists()
        meta["size_mb"]   = round(final.stat().st_size / 1_048_576, 1) if final.exists() else 0
        jobs.append(meta)
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


if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000)
