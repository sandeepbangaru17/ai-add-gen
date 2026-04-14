# Web App Development - TODO List

## Status: Saved - Continue Tomorrow

---

## Summary of What We Built Today

### AI Ad Creation Pipeline (COMPLETED ✅)
- 8-stage pipeline for generating video ads
- Tools: Groq (LLM), edge-tts (voice), Pollinations (images), FFmpeg (video)
- Free tier - no credit card required
- Output: 16:9, 9:16, 1:1 video formats

### Repository
- **GitHub:** https://github.com/sandeepbangaru17/ai-add-gen
- **Demo:** ZunoSync 30-second ad video included

---

## Tomorrow: Web Application

### Step 1: Project Setup
- [ ] Create new folder: `web-app/`
- [ ] Initialize frontend: React + Vite
- [ ] Initialize backend: FastAPI
- [ ] Setup project structure

### Step 2: Backend API (FastAPI)
- [ ] `/api/campaigns` - GET list, POST create
- [ ] `/api/campaign/{id}` - GET details
- [ ] `/api/generate/{id}` - POST start pipeline
- [ ] `/api/status/{id}` - GET progress (SSE)
- [ ] `/api/download/{id}/{format}` - GET video file
- [ ] `/api/delete/{id}` - DELETE campaign

### Step 3: Frontend (React)
- [ ] Landing page with hero section
- [ ] Campaign creation form
- [ ] Progress tracker (real-time)
- [ ] Video preview page
- [ ] Dashboard with campaign list

### Step 4: Integration
- [ ] Connect frontend to backend
- [ ] Real-time progress updates
- [ ] Video streaming/download

### Step 5: Deployment
- [ ] Create Dockerfile
- [ ] Deploy to Railway/Render
- [ ] Test production

---

## Quick Start Commands for Tomorrow

```bash
# 1. Open project
cd ai-add-gen

# 2. Create web app folder
mkdir web-app && cd web-app

# 3. Initialize frontend
npm create vite@latest frontend -- --template react
cd frontend && npm install
cd ..

# 4. Initialize backend
mkdir backend
cd backend
python -m venv venv
# Activate: source venv/bin/activate (Mac/Linux) or venv\Scripts\activate (Windows)
pip install fastapi uvicorn python-multipart aiofiles

# 5. Run locally
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## File Structure to Create

```
ai-add-gen/
├── pipeline.py              # (existing)
├── web-app/                 # NEW
│   ├── backend/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # Pydantic models
│   │   ├── routes/
│   │   │   ├── campaigns.py
│   │   │   └── generate.py
│   │   ├── services/
│   │   │   └── pipeline.py  # Wrapper for pipeline.py
│   │   └── requirements.txt
│   │
│   └── frontend/
│       ├── src/
│       │   ├── App.jsx
│       │   ├── pages/
│       │   │   ├── Home.jsx
│       │   │   ├── Dashboard.jsx
│       │   │   ├── Create.jsx
│       │   │   └── Preview.jsx
│       │   └── components/
│       │       ├── Navbar.jsx
│       │       ├── BriefForm.jsx
│       │       └── ProgressBar.jsx
│       └── package.json
│
│   └── Dockerfile           # NEW
```

---

## Notes for Tomorrow

- Keep the existing pipeline.py working as-is
- Create a wrapper service that calls pipeline
- Use Server-Sent Events (SSE) for progress updates
- Store videos in `static/videos/` folder
- Use SQLite for simple campaign storage

---

## Questions to Answer Tomorrow

1. Do you want user authentication (login/signup)?
2. Should campaigns be public or private by default?
3. Do you want to charge for API usage?
4. Which hosting platform do you prefer?

---

*Last updated: 2024*
