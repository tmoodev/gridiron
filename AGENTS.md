# Gridiron — Agent Guide

## Overview

Autonomous fantasy football agent managing two Sleeper leagues (owner: `Travy2Chains`). Four LLM-driven agents (Research / Valuation / Lineup / Trade) grounded in a strategy corpus propose moves; approved actions are executed against the Sleeper UI via a Playwright actuator. Email notifications go out via SES; a React dashboard fronts the API for review/approval.

Leagues:

| League | Format | Status |
|--------|--------|--------|
| Fantasy Football Season 9 (`1183557197018804224`) | 12-team keeper IDP, half-PPR | 2025 complete; 2026 prep |
| Degeneration X (`1331779473430810624`) | 12-team dynasty, SUPER_FLEX, TE premium, full PPR | Pre-draft 2026 |

See `docs/leagues.md` for the full discovery report.

## Stack

- **Backend:** Python 3.11, FastAPI + uvicorn (`:8000`), APScheduler, Pydantic v2, structlog, httpx
- **LLM:** AWS Bedrock (Claude Sonnet for reasoning, Grok for research)
- **Data:** DynamoDB (shared `datatrav-ops` table, all keys prefixed `FF#`), S3 for strategy docs (local fallback)
- **Actuator:** Playwright (writes to Sleeper UI; Sleeper API is read-only)
- **Frontend:** React + Vite + TypeScript + Tailwind, Recharts, served by nginx (`:3000`)
- **Infra:** Docker Compose (`gridiron-backend`, `gridiron-frontend`, `cloudflared`), Cloudflare Tunnel + Access
- **Quality gates:** ruff, black, `mypy --strict`, pytest (moto/respx for AWS/HTTP mocking)

## Architecture

- `src/gridiron/api/` — FastAPI app (`main.py`, v0.3.0): leagues, roster, analytics, proposals, players, recommendations, policy, job-trigger routes. Health at `/api/health`.
- `src/gridiron/agents/` — Research / Valuation / Lineup / Trade agents, all grounded in the strategy corpus (5-section prompt structure); decision records stamped with `strategy_docs_loaded` + `strategy_doc_versions`.
- `src/gridiron/strategy/` — StrategyLoader: S3 primary, local `docs/strategy/` fallback, 1-hour TTL cache.
- `src/gridiron/policy/` — PolicyGate: DynamoDB config with yaml fallback; `GET/POST /api/policy`.
- `src/gridiron/scheduler/` — APScheduler jobs (hourly Sleeper sync etc.); manual trigger via `POST /api/jobs/trigger/{job_name}` (allowlisted jobs only).
- `src/gridiron/actuator/` — Playwright automation for Sleeper UI writes.
- `src/gridiron/sleeper/`, `src/gridiron/scrapers/` — Sleeper API client (read), KTC scraper.
- `src/gridiron/db/` — DynamoDB layer. Key schema (all on the shared `datatrav-ops` table, `FF#` prefix) is documented in `README.md`. Notably `FF#LEAGUE#{league_id}` / `CONFIG` holds league rules seeded from Sleeper (Phase 0 discovery) and is read at runtime by `agents/base.py`, `api/main.py`, and `scheduler/jobs.py` — scoring/roster adjustments are automatic from these records, never hardcoded.
- `src/gridiron/email/` — SES email (gridiron@datatrav.com → owner approval loop).
- `frontend/` — dashboard (Operator Dark theme), 3-column grid: Roster | Analytics tabs | Recommendations sidebar; PlayerDrawer, DecisionLog/Policy/IntelFeed/SystemHealth pages.
- `docs/strategy/` — 10 strategy docs (the corpus).

## Deploy

- **deploy_method:** `ssh` (automated — merge to `main` triggers it; do NOT deploy manually)
- **Pipeline:** `.github/workflows/ci.yml` — lint/test + frontend build on PRs and pushes; on push to `main`, the `deploy` job SSHes into the prod host via `appleboy/ssh-action` (secrets `EC2_HOST` / `EC2_KEY`), then on the box: `git reset --hard origin/main` in `/opt/gridiron`, fetch Cloudflare tunnel token from Secrets Manager (`digitalmoore/gridiron/cf-tunnel-token`), `docker compose up -d --build`, health-check `:8000/api/health` and `:3000` with 5 retries, and auto-rollback to the previous commit on persistent failure.
- **deploy_path:** `/opt/gridiron/`
- **docker_service:** `gridiron-backend` (plus `gridiron-frontend`, `gridiron-cloudflared`)
- **target_host:** `datatrav-mdc-prod`

## Environments / URLs

- **Production dashboard:** https://gridiron.datatrav.net (Cloudflare Tunnel + Cloudflare Access)
- **On-host:** backend `localhost:8000`, frontend `localhost:3000`, docker network `datatrav-net` (external)
- **Local dev:** `pip install -e ".[dev]"` then `uvicorn gridiron.api.main:app --reload`, or `docker compose up`. Requires AWS credentials with access to the `datatrav-ops` DynamoDB table and Bedrock.
- **Tests:** `pytest tests/ -v`, `mypy --strict src/gridiron/`, `ruff check src/ tests/`, `black --check src/ tests/`

## State

- API at v0.3.0; single production environment, no staging.
- Season context: 2025 season complete in the keeper league; both leagues in 2026 prep/pre-draft mode.
- League config, valuations, decisions, intel, and job status all live under `FF#*` keys in the shared `datatrav-ops` DynamoDB table (see schema table in `README.md`).

## History

- **2026-07-12** — Adopted AGENTS.md convention; CLAUDE.md is now a one-line `@AGENTS.md` shim.
- **2026-06-09/10** — PR #5: added CLAUDE.md deploy config (superseded by this file).
- **2026-04-30** — PR #4: Operator Dark dashboard rebuild (3-column grid, PlayerDrawer, DecisionLog/Policy/IntelFeed/SystemHealth pages, Recharts) + all missing API routes (my-roster, analytics, proposals approve/reject/modify, players/intel, recommendations promote, job trigger); API bumped to v0.3.0.
- **2026-04-30** — PR #3: strategy corpus (10 docs in `docs/strategy/`), StrategyLoader (S3 + local fallback + 1h TTL), PolicyGate (DynamoDB config + yaml fallback), all 4 agents grounded in corpus, `GET/POST /api/policy`.
- **2026-04-30** — PR #2: Phase 2 — agents, KTC scraper, React dashboard, deploy pipeline.
- **2026-04-30** — PR #1: Phase 1 foundation — API, Sleeper client, DynamoDB layer, scheduler, CI. Phase 0 league discovery report in `docs/leagues.md`.

## Gotchas

- **EC2_HOST secret rots.** The deploy workflow's `EC2_HOST` GitHub secret holds the prod host's public IP; the instance has no Elastic IP, so if the IP changes the secret must be updated or deploys silently fail at the SSH step. Resolve the current IP from the instance — never hardcode it in files.
- **Deploy method is SSH, not SSM.** Despite other services in the fleet using SSM, this pipeline is `appleboy/ssh-action`. Merge deploys automatically — do not also deploy manually.
- **Shared DynamoDB table.** Gridiron does not own `datatrav-ops`; only touch items with the `FF#` key prefix.
- **Sleeper writes go through Playwright.** The Sleeper API is read-only for this app; all mutations are UI automation via the actuator, which is inherently fragile to Sleeper UI changes.
- **Scoring rules are data, not code.** Agents read `scoring_settings`/`roster_positions` from `FF#LEAGUE#{id}` records at runtime; do not hardcode league-format assumptions.
- **Version drift:** `pyproject.toml` still says `0.2.0` while the API reports `0.3.0`.
- **Health-check rollback:** a failed deploy auto-rolls-back on the host; check the Actions log before re-triggering.
- **No secrets in this repo.** Runtime secrets come from AWS Secrets Manager (e.g. `digitalmoore/gridiron/cf-tunnel-token`); deploy credentials are GitHub Actions secrets.

## KB pointer

Internal operational docs live in the private `datatrav-ops-kb` repo: `kb/products/gridiron.md` (change log) and `deploy/gridiron.md` (authoritative deploy config). Update both after any deploy or infra change.
