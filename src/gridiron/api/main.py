"""FastAPI application — Gridiron API."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gridiron.db.dynamo import DynamoClient
from gridiron.scheduler.jobs import LEAGUE_IDS, build_scheduler, sync_leagues, sync_rosters
from gridiron.sleeper.client import SleeperClient

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

_dynamo: DynamoClient | None = None
_sleeper: SleeperClient | None = None


def get_dynamo() -> DynamoClient:
    assert _dynamo is not None, "DynamoClient not initialized"
    return _dynamo


def get_sleeper() -> SleeperClient:
    assert _sleeper is not None, "SleeperClient not initialized"
    return _sleeper


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _dynamo, _sleeper
    _dynamo = DynamoClient()
    _sleeper = SleeperClient()

    # Run initial sync on startup
    await sync_leagues(_dynamo, _sleeper)
    await sync_rosters(_dynamo, _sleeper, week=1)

    scheduler = build_scheduler(_dynamo, _sleeper)
    scheduler.start()
    log.info("gridiron.started")

    yield

    scheduler.shutdown(wait=False)
    _sleeper.close()
    log.info("gridiron.shutdown")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Gridiron", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gridiron.datatrav.net"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Cloudflare Access middleware
# ---------------------------------------------------------------------------

CF_ACCESS_HEADER = "CF-Access-Jwt-Assertion"
# Token-gated endpoints (approve/reject) skip CF Access — they use HMAC tokens.
_CF_EXEMPT_PREFIXES = ("/api/approve", "/api/reject", "/api/health")


@app.middleware("http")
async def cloudflare_access(request: Request, call_next: Any) -> Response:
    path = request.url.path
    if any(path.startswith(p) for p in _CF_EXEMPT_PREFIXES):
        return await call_next(request)  # type: ignore[return-value]
    # In production, Cloudflare Access validates the JWT before requests reach
    # the container, so we only check for presence here.
    if CF_ACCESS_HEADER not in request.headers:
        log.warning("cf_access.missing_header", path=path)
        return Response(status_code=401, content="Unauthorized")
    return await call_next(request)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


class LeagueSummary(BaseModel):
    league_id: str
    league_name: str | None
    season: str | None
    status: str | None
    format: str | None
    total_rosters: int | None


@app.get("/api/leagues", response_model=list[LeagueSummary])
async def list_leagues() -> list[LeagueSummary]:
    dynamo = get_dynamo()
    summaries = []
    for league_id in LEAGUE_IDS:
        item = dynamo.get_item(f"FF#LEAGUE#{league_id}", "CONFIG")
        if item:
            summaries.append(
                LeagueSummary(
                    league_id=league_id,
                    league_name=item.get("league_name"),
                    season=item.get("season"),
                    status=item.get("status"),
                    format=item.get("format"),
                    total_rosters=int(item["total_rosters"]) if "total_rosters" in item else None,
                )
            )
    return summaries


class RosterResponse(BaseModel):
    league_id: str
    week: int
    rosters: list[dict[str, Any]]


@app.get("/api/leagues/{league_id}/roster", response_model=RosterResponse)
async def get_roster(league_id: str, week: int = 1) -> RosterResponse:
    if league_id not in LEAGUE_IDS:
        raise HTTPException(status_code=404, detail="League not found")
    dynamo = get_dynamo()
    items = dynamo.query_prefix(f"FF#ROSTER#{league_id}#{week}", sk_prefix="SNAPSHOT#")
    rosters = []
    for item in items:
        rosters.append(
            {
                "roster_id": item.get("roster_id"),
                "owner_id": item.get("owner_id"),
                "players": json.loads(item["players"]) if "players" in item else [],
                "starters": json.loads(item["starters"]) if "starters" in item else [],
            }
        )
    return RosterResponse(league_id=league_id, week=week, rosters=rosters)
