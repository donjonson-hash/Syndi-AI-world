# Syndi Backend (FastAPI + Matching Engine)

This directory contains the **backend API** for the Syndi project.  
It powers the matching engine used by the mobile app and bots.

## Tech stack

- Python 3.12
- FastAPI (ASGI framework)
- Uvicorn (ASGI server)
- SQLAlchemy Async + SQLite (for now)
- Custom matching engine (skills + personality + enneagram) in `core/ai/matching_engine.py`

Backend code lives under:

- `backend/main.py` – main FastAPI application (`app`).
- `backend/database/` – async DB session, CRUD helpers.
- `backend/core/` – matching logic, AI utilities, mystic / quantum modules.
- `backend/services/` – LLM and matching orchestration services.
- `backend/tests/` – unit tests for agents, big five, matching.

---

## Project structure (backend)

```text
backend/
  Dockerfile
  Makefile
  main.py
  init_db.py
  requirements.txt
  system_prompt.txt

  agents/
  api/
  core/
    ai/
    matching/
    mystic/
    quantum/
    agents/
  database/
  db/
  models/
  services/
  tests/
```

Note: `database/` and `db/` currently coexist – this is legacy from earlier iterations and can be refactored later.

---

## Running backend locally (dev mode)

Requirements:

- Python 3.12
- A virtual environment

Steps:

```bash
cd backend
1) Create venv

python3 -m venv .venv
source .venv/bin/activate
2) Install dependencies

pip install -r requirements.txt
3) Initialize the database (if needed)

python init_db.py
4) Run FastAPI with Uvicorn (dev defaults)

uvicorn main:app --host 127.0.0.1 --port 8081 --reload

You can then access:

- Health check: `http://127.0.0.1:8081/health`
- Root: `http://127.0.0.1:8081/`
- Swagger UI: `http://127.0.0.1:8081/docs`

---

## Systemd services on production server

On the production server, the backend is managed by **systemd** and runs via `uvicorn main:app` in the `backend` directory.

Two key services:

1. `syndi-api.service` – **HTTP API** (FastAPI + Uvicorn)
   - Working directory: `/opt/syndi-ai/backend`
   - Entry point: `main:app`
   - Port: `8081` (`0.0.0.0:8081`)
   - Health endpoint: `/health` (returns `{"status": "healthy"}`)

2. `syndi-bot.service` – **bot / background worker** (separate process)

Basic systemd commands (run as root):

```bash
Check status

systemctl status syndi-api.service
systemctl status syndi-bot.service
Start / stop / restart

systemctl start syndi-api.service
systemctl restart syndi-api.service
systemctl stop syndi-api.service
Enable on boot

systemctl enable syndi-api.service
systemctl enable syndi-bot.service

On the current server, a healthy state looks like:

- `curl http://localhost:8081/health` → `{"status": "healthy"}`
- `systemctl is-active syndi-api.service syndi-bot.service` → `active active`

---

## Notes

- The backend code in `backend/` is a direct import of the working code from `/opt/syndi-ai/backend` on the production server (minus virtual environments).
- Future work:
  - unify `database/` and `db/` modules,
  - clean up legacy folders (`api/main.py.backup` etc.),
  - add migrations tool (Alembic) if/when we move beyond simple SQLite.

