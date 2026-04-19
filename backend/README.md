# Backend README

This folder contains the **Syndi backend**: a FastAPI application with a custom matching engine.

## Entry point

- Main application: `main.py`
- ASGI object: `app`
- Used in Uvicorn / systemd as: `uvicorn main:app --host 0.0.0.0 --port 8081`

## Local development

From the repository root:

```bash
cd backend
1) Create and activate virtualenv

python3 -m venv .venv
source .venv/bin/activate
2) Install dependencies

pip install --upgrade pip
pip install -r requirements.txt
3) Initialize database (if required)

python init_db.py
4) Run the server locally

uvicorn main:app --host 127.0.0.1 --port 8081 --reload

text

Then open:

- `http://127.0.0.1:8081/` – root endpoint
- `http://127.0.0.1:8081/health` – health check
- `http://127.0.0.1:8081/docs` – Swagger UI

## Layout overview

```text
Dockerfile          # Containerization (not used by systemd deployment yet)
Makefile            # Optional helper tasks
init_db.py          # DB initialization / seeding
main.py             # FastAPI app (used in production)
requirements.txt    # Python dependencies
system_prompt.txt   # System prompt for AI components

agents/             # Agent implementations (Kristina, base agents, etc.)
api/                # Legacy / alternate API entry (not used by systemd)
core/               # Matching, AI, mystic, quantum modules
  ai/
  matching/
  mystic/
  quantum/
  agents/

database/           # Async engine, session, CRUD implementation
db/                 # Legacy duplication (to be unified with database/)
models/             # Pydantic / domain models (user, big five, bot, etc.)
services/           # LLM + matching orchestration
tests/              # Unit tests for agents, big five, matching
```

## Production services

On the production host, systemd units look conceptually like this:

- `syndi-api.service`
  - `WorkingDirectory=/opt/syndi-ai/backend`
  - `ExecStart=/opt/syndi-ai/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8081`
  - `Restart=always`

- `syndi-bot.service`
  - Separate worker / bot process (runs background logic, not HTTP).

Typical commands:

```bash
Status

systemctl status syndi-api.service
systemctl status syndi-bot.service
Restart API after code changes

systemctl restart syndi-api.service

