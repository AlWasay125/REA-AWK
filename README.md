# ReVerseAI

A minimal but working foundation for the ReVerseAI milestone described in the project specification.

This repository intentionally implements the first end-to-end slice: user preferences, case/artifact creation, static analysis of supported files, and a frontend settings screen connected to a real FastAPI backend.

Important: the project is designed to run without external services by default. Ghidra is integrated as an optional path; if it is not installed, the backend uses deterministic static analysis on PE/ELF files and exposes a clear status/error instead of claiming unsupported analysis. This is consistent with the specification's requirement to avoid fake functionality.

## Quick start

1. Copy `.env.example` to `.env` and adjust values.
2. Create the virtual environment and install Python dependencies:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev -- --host 0.0.0.0 --port 5173
   ```
5. Open the frontend and use the Settings page.

## Included milestone work

- FastAPI backend with auth stub and preference APIs
- SQLite-ready SQLAlchemy models and migrations
- Case and artifact upload flow with SHA-256
- Static evidence extraction for PE and ELF files
- Simple job lifecycle and progress tracking
- Settings page connected to backend preferences API
- Alembic migration scaffolding
- Testing scaffold for preference scenarios

## Status

This repository is intentionally a practical foundation, not a complete end-to-end production system. The next milestones would add real Ghidra orchestration, richer worker isolation, larger frontend views, and deeper multi-agent analysis.
