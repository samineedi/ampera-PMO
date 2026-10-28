# PMO Automation (Trello): dashboard, weekly report, planning, closure

A Flask JSON API with a React (Vite) frontend, plus LangGraph agents that read a Trello board and give a PMO team the visibility it normally
builds by hand for software projects: how complete the project is, weekly status and risks, and project planning/closure.

## Run it
```
pip install -e "backend[dev]"      # installs the `pmo` package + pytest/ruff
cp .env.example .env        # add your Trello keys (and optionally GOOGLE_API_KEY)
cd frontend && npm install && npm run build && cd ..   # build the React app once
python -m pmo               # http://localhost:5000
```
Frontend development with hot reload: run `python -m pmo` (or `powershell -File scripts/dev.ps1` to start both) and, in another terminal, `cd frontend && npm run dev`
(http://localhost:5173, `/api` is proxied to Flask). Needs Node 18+.
Login: the app asks for a username and password. Set `APP_USERNAME`, `APP_PASSWORD_HASH` and `SECRET_KEY` in `.env` (commands are in `.env.example`); the app will not start without them. For local development only, `AUTH_DISABLED=true` turns the login off. When deployed over HTTPS set `COOKIE_SECURE=true`, and `TRUST_PROXY=true` behind a proxy.
Live Trello data only: the app will not start without the three Trello settings in `.env`.

## Pages
| Page | Purpose |
|---|---|
| Dashboard | Project selector, completion of each project, tasks done / in progress / blocked / overdue, pipeline Backlog > Development > Testing > Done, planned vs actual dates |
| Weekly Report | KPIs, risk radar, reminders, editable report draft (Gemini wording optional) |
| Planning | Brief + team -> tasks, assignments, due dates -> create Trello cards |
| Closure | Completion check, closure report, archive board |

A floating chat bubble (bottom-right, every page) answers questions about the board through a read-only Gemini tool-calling agent (`backend/src/pmo/agents/chat_agent.py`); it needs `GOOGLE_API_KEY`.

Pages read cached data, so opening them never calls Trello. The cache refreshes every 30 minutes
and with the Refresh button.

## Use your real Trello board
1. Get an API key and token (see below) and put them in `.env`.
2. Set `TRELLO_BOARD_ID=...` in `.env`, then start the app.

Get credentials: https://trello.com/power-ups/admin -> New -> generate an API key -> click the Token link (authorize, read+write).
Board ID: open the board, add `.json` to its URL, copy the top-level `id`.

## Tag your cards (the dashboards read these)
`Project: Project 1`, `Release: v1.4`, `Team: Backend`, `Phase: QA` as labels (phases such as Design, Dev, QA, UAT); a `Blocked` label plus a comment for the reason;
Lists are the status (To Do / Doing / In Review / Done).
Names are configurable in `backend/src/pmo/config.py`. Cards without a Release or Phase label appear under "Unassigned" / "No phase".

## Automatic runs (email/Slack)
```
python -m pmo.jobs.run_scheduled reminders      # saves reminders to data/reports (nothing is sent)
python -m pmo.jobs.run_scheduled weekly
python -m pmo.jobs.scheduler                            # keeps running: weekly report + weekday reminders (see .env)
```
Safe by default: output is saved to `data/reports`. Add `--send` (or `SCHEDULE_SEND=true`) to really email or post.
Jobs refuse to run without Trello credentials. A GitHub Actions option is in `.github/workflows/`.

## Project layout
```
backend/
  pyproject.toml          dependencies, pytest and ruff config (pip install -e "backend[dev]")
  src/pmo/
    main.py               create_app() factory (python -m pmo, or gunicorn "pmo.main:create_app()")
    config.py             board conventions + settings; loads the repo-root .env
    api/                  Flask blueprints: dashboard, digest, planning, closure, chat, system (health + React shell); auth
    domain/               pure rules, no I/O: normalize, classify, kpi, risk, dashboard
    services/             cache (JSON files), notifier, closure (check, report, archive)
    agents/               LangGraph workflow + LLM wording: graph, drafter, planner, chat_agent
    integrations/         Trello client, email/Slack sender
    jobs/                 scheduler and run_scheduled (python -m pmo.jobs.scheduler)
  tests/                  mirrors src/pmo (api, agents, domain, integrations)
frontend/src/             pages/, components/, hooks/, api/ (fetch client), styles/
docs/                     ARCHITECTURE.md, specs/, plans/
scripts/                  dev.ps1 (start both servers), set_password.py
data/                     runtime output (cache/, reports/), git-ignored
.github/workflows/        ci.yml (ruff + pytest + frontend build), weekly-report.yml
```
Dependencies point one way: `api` / `jobs` -> `agents` / `services` -> `domain` + `integrations`. Run the checks with `cd backend && ruff check . && pytest`.

## How it is built
`backend/src/pmo/` holds the logic (plain Python rules for numbers; the LLM only writes wording), `pmo/api/` is the JSON API (and serves
`frontend/dist`), and `frontend/` is the React app (`src/pages/` has one component per page). See `docs/ARCHITECTURE.md` for the workflow diagram, models, tools and API keys.
Health checks: `/ping`, `/api/trello-health`.

## Run with Docker (and host on Azure)
```
docker build -t pmo-automation .
docker run --rm -p 5000:5000 --env-file .env -v pmo-data:/app/data pmo-automation     # http://localhost:5000
```
Settings come from the environment (`--env-file .env`), never from the image; `.env` is excluded by `.dockerignore`. `data/` (cache and reports) is a volume.
On Azure (App Service for Containers or Container Apps) push the image to Azure Container Registry, set the same variables as app settings, and add
`COOKIE_SECURE=true` and `TRUST_PROXY=true` (HTTPS behind Azure's proxy). The app listens on `PORT` (default 5000); on App Service also set `WEBSITES_PORT=5000`.
The container's filesystem is not persistent on Azure: the board cache is rebuilt from Trello on start, but saved reports need a mounted Azure Files share on `/app/data`.
