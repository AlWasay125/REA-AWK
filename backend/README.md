# ReVerseAI Backend

This backend provides a small but complete foundation for the first milestone of ReVerseAI.

## Getting started

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

- Authentication is intentionally minimal for local development and uses the `X-User-Id` header.
- SQLite is the default database for local development. PostgreSQL is fully compatible via the env-backed `DATABASE_URL`.
- Ghidra is optional. The analysis service checks whether it is available; otherwise it performs a deterministic static-analysis fallback on supported PE/ELF files.
