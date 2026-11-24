# gridiron

> Scaffolded 2026-11-23 by the KB sleep cycle (`scripts/sleep/agents_scaffold.py`) from the knowledge base, the repo's manifests and its previous CLAUDE.md. Sections are only as good as those sources; correct State and Gotchas on first real use and the next `/kb-update` makes it yours.

## Overview

Gridiron is an autonomous fantasy football agent system that manages two Sleeper leagues for a single operator (Travis Moore). It provides a 3-column dark-themed dashboard (`gridiron.datatrav.net`) for human oversight, featuring roster analytics, player valuations, trade recommendations, and an intel feed. The system integrates with Sleeper’s API for read operations and uses Playwright to automate write actions (lineup changes, trades, waivers). Four specialized agents—Research, Valuation, Lineup/Waiver, and Trade—operate hourly, grounding decisions in a 10-document strategy corpus and policy rules stored in DynamoDB. All actions are logged with reasoning chains and strategy document versions for auditability. The system is designed for dynasty and IDP formats with keeper rules, supporting both in-season management and off-season preparation.

## Stack

- **Backend**: Python 3.11 (FastAPI 0.115.0), APScheduler 3.10.0, Playwright 1.48.0
- **Frontend**: TypeScript 5.6.3, React 18.3.1, Recharts 3.8.1, Vite 5.4.10, Tailwind CSS 3.4.14
- **LLM**: AWS Bedrock (Claude Sonnet for reasoning, Grok for research)
- **Database**: DynamoDB (`datatrav-ops` table with `FF#` prefix keys)
- **Infrastructure**: Docker (Python 3.11-slim, Node 20-slim), Cloudflare Tunnel (Zero Trust Access), SES for email
- **CI/CD**: GitHub Actions (SSH deploy via `appleboy/ssh-action`)
- **Host**: `datatrav-mdc-prod` (bare-metal instance, no elastic IP)
- **Networking**: Cloudflare Tunnel routes `gridiron.datatrav.net` to frontend container port 3000; backend exposes port 8000 internally

## Architecture

- **Services**: 
  - `gridiron-backend`: FastAPI service (port 8000) hosting agents, API routes, and scheduler. Runs Playwright for Sleeper UI automation.
  - `gridiron-frontend`: React SPA (port 3000) with 3-column layout (Roster | Analytics | Recommendations) and slide-in PlayerDrawer.
  - `cloudflared`: Cloudflare Tunnel container routing `gridiron.datatrav.net` to frontend via Secrets Manager token (`digitalmoore/gridiron/cf-tunnel-token`).
- **Data Flow**:
  - Agents pull league/player data from Sleeper API and DynamoDB hourly, then call Bedrock for reasoning.
  - Decisions are logged to DynamoDB with strategy document versions and reasoning chains.
  - Playwright executes approved actions (e.g., trades, lineup changes) via Sleeper UI.
  - SES emails (`gridiron@datatrav.com`) notify the operator of pending decisions requiring approval.
- **Deployment**: All services run as Docker containers on `datatrav-mdc-prod` in `/opt/gridiron/`, connected via `datatrav-net` network.

## Deploy

Merge to `main` triggers a GitHub Actions workflow (`appleboy/ssh-action`) that deploys to `datatrav-mdc-prod` via SSH. The workflow:
1. SSHes into the target host (IP resolved from EC2 instance, not hardcoded).
2. Pulls the latest `main` branch to `/opt/gridiron/`.
3. Runs `docker compose up -d --build` to rebuild and restart containers.
4. Verifies backend health via `curl -f http://localhost:8000/api/health`.

**Rule**: `github_actions` deploy method; merge to `main` auto-deploys. No manual deploy steps are required, but the SSH transport requires the instance’s public IP to be resolvable (KB audit B-21 notes this as a risk if the IP changes).

## Environments / URLs

| Environment | URL | Host | Ports | Notes |
|-------------|-----|------|-------|-------|
| Production | `https://gridiron.datatrav.net` | `datatrav-mdc-prod` | 3000 (frontend), 8000 (backend) | Cloudflare Tunnel + Access; backend not publicly exposed |
| Local (dev) | `http://localhost:3000` (frontend), `http://localhost:8000` (backend) | localhost | 3000, 8000 | Docker Compose; requires AWS credentials for DynamoDB/Bedrock |

## State

As of 2026-11-23 (scaffolded from the KB; verify):
- **Live**: 
  - Dashboard (`gridiron.datatrav.net`) with 3-column layout (Roster | Analytics | Recommendations) and new pages: DecisionLogPage, PolicyPanelPage, IntelFeedPage, SystemHealthPage.
  - Backend API v0.3.0 (`main.py`) with routes for roster analytics, proposals, player intel, and recommendations.
  - All 4 agents (Research, Valuation, Lineup/Waiver, Trade) grounded in 10-document strategy corpus.
  - DynamoDB `FF#` keys for league/player/decision data.
  - SES email notifications for pending decisions.
- **Not Running**:
  - Obsolete frontend pages: DecisionsPage.tsx, LeaguePage.tsx (removed in PR 4, merged 2026-04-30).
- **In Flight**:
  - Degeneration X league (`1331779473430810624`) in pre-draft 2026 phase (no active waivers/trades).
  - Fantasy Football Season 9 (`1183557197018804224`) completed 2025; 2026 prep underway.

## History

- **2026-04-30**: Operator Dark Dashboard Rebuild merged (PR 4). Frontend rebuilt as 3-column grid with navy/teal theme, PlayerDrawer, and new pages (DecisionLogPage, PolicyPanelPage, IntelFeedPage, SystemHealthPage). Backend API v0.3.0 added routes for roster analytics, proposals, player intel, and recommendations.
- **2026-04-30 (previously)**: Strategy Corpus and Agent Overhaul (PR 3). Added 10 strategy docs, StrategyLoader with S3/local fallback, PolicyGate with DynamoDB config, and grounded all agents in strategy corpus with version stamping.

## Gotchas

- **SSH Deploy IP Rot**: The GitHub Actions workflow hardcodes the `datatrav-mdc-prod` public IP in its `EC2_HOST` secret. The instance has no elastic IP, so this value rots if the IP changes (KB audit B-21 / TODO #14a). Resolve the current IP from the instance metadata instead.
- **Cloudflare Tunnel Token**: The `cloudflared` container requires `CLOUDFLARE_TUNNEL_TOKEN` from Secrets Manager (`digitalmoore/gridiron/cf-tunnel-token`). The tunnel must be created via Cloudflare dashboard (Zero Trust → Tunnels → gridiron) before deployment.
- **DynamoDB Key Prefix**: All keys use the `FF#` prefix on the shared `datatrav-ops` table. Schema is documented in `README.md`; do not alter without migrating data.
- **Agent Grounding**: All agent decisions are stamped with `strategy_docs_loaded` and `strategy_doc_versions`. Changes to strategy docs (`docs/strategy/`) require agent restart to take effect (1hr TTL cache).
- **Sleeper UI Automation**: Playwright interacts with Sleeper’s UI for write operations (e.g., trades, lineups). Changes to Sleeper’s DOM may break selectors; test locally before deploying.
- **Merge Deploy Only**: Deployments are triggered by merges to `main`. Do not manually run deploy commands unless debugging (documented in `CLAUDE.md`).

## KB pointer

`kb/products/gridiron.md` and `deploy/gridiron.md` in `datatrav-ops-kb` (`~/code/datatrav-ops-kb` on the workstation). Read the session brief `briefings/gridiron.md` first; open the KB files when the brief cites them. After a commit, push or deploy, run `/kb-update`.

Cloud/mobile sessions: attach `tmoodev/datatrav-ops-kb` with `add_repo`, then read its `cloud/global-rules.md` and `AGENTS.md`.
