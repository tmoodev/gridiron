# Gridiron

Autonomous fantasy football agent managing two Sleeper leagues for Travis Moore (`Travy2Chains`).

## Architecture

```mermaid
graph TD
    subgraph Sleeper
        SL[Sleeper API - Read]
        SW[Sleeper UI - Write via Playwright]
    end

    subgraph Gridiron - datatrav-mdc-prod
        API[FastAPI :8000]
        SCH[APScheduler]
        AGT[Agents<br/>Research / Valuation / Lineup / Trade]
        ACT[Actuator<br/>Playwright]
        EMAIL[SES Email<br/>gridiron@datatrav.com]
    end

    subgraph AWS
        BED[Bedrock<br/>Claude Sonnet - reasoning<br/>Grok - research]
        DDB[(DynamoDB<br/>datatrav-ops FF# keys)]
    end

    subgraph User
        TRV[Travis<br/>travis@datatrav.com]
        DASH[gridiron.datatrav.net<br/>Cloudflare Access]
    end

    SCH -->|hourly| SL
    SCH -->|sync| DDB
    AGT --> BED
    AGT --> DDB
    ACT --> SW
    EMAIL --> TRV
    TRV -->|approve/reject| API
    API --> DASH
    API --> DDB
```

## Leagues

| League | Format | Status |
|--------|--------|--------|
| Fantasy Football Season 9 (`1183557197018804224`) | 12-team keeper IDP, half-PPR | 2025 complete; 2026 prep |
| Degeneration X (`1331779473430810624`) | 12-team dynasty, SUPER_FLEX, TE premium, full PPR | Pre-draft 2026 |

See `docs/leagues.md` for full discovery report.

## Local Development

```bash
# Clone and install
git clone https://github.com/tmoodev/gridiron.git
cd gridiron
pip install -e ".[dev]"

# Run API
uvicorn gridiron.api.main:app --reload

# Or via Docker
docker compose up
```

Requires AWS credentials with access to `datatrav-ops` DynamoDB table and Bedrock.

## Testing

```bash
pytest tests/ -v
mypy --strict src/gridiron/
ruff check src/ tests/
black --check src/ tests/
```

## Deployment

Merge to `main` triggers GitHub Actions, which deploys to `datatrav-mdc-prod` at `/opt/gridiron/`.

Docker service: `gridiron-backend`
Frontend: `https://gridiron.datatrav.net` (Cloudflare Tunnel + Access)

## DynamoDB Key Schema

All keys use prefix `FF#` on the shared `datatrav-ops` table.

| pk | sk | Purpose |
|----|----|---------|
| `FF#LEAGUE#{league_id}` | `CONFIG` | League rules from Sleeper API |
| `FF#PLAYER#{player_id}` | `META` | Player metadata + valuations |
| `FF#ROSTER#{league_id}#{week}` | `SNAPSHOT#{roster_id}` | Weekly roster snapshots |
| `FF#MATCHUP#{league_id}#{week}` | `DATA` | Matchup results/projections |
| `FF#DECISION#{league_id}#{ts}` | `LOG` | Actions with reasoning chain |
| `FF#WAIVER#{league_id}#{week}` | `DATA` | Waiver claims |
| `FF#TRADE#{league_id}#{trade_id}` | `DATA` | Trade proposals + analysis |
| `FF#INTEL#{player_id}#{ts}` | `ITEM` | Research findings, injury news |
| `FF#PICK#{league_id}#{year}#{round}#{slot}` | `META` | Draft pick assets |
| `FF#JOB#{job_id}` | `STATUS` | Scheduled job run status |
