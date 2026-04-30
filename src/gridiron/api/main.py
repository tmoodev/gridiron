"""FastAPI application — Gridiron API."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import structlog
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gridiron.agents.base import Decision
from gridiron.db.dynamo import DynamoClient
from gridiron.email.ses import verify_token
from gridiron.llm.bedrock_client import BedrockClient
from gridiron.scheduler.jobs import LEAGUE_IDS, build_scheduler, sync_leagues, sync_rosters
from gridiron.sleeper.client import SleeperClient

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

_dynamo: DynamoClient | None = None
_sleeper: SleeperClient | None = None
_bedrock: BedrockClient | None = None


def get_dynamo() -> DynamoClient:
    assert _dynamo is not None, "DynamoClient not initialized"
    return _dynamo


def get_sleeper() -> SleeperClient:
    assert _sleeper is not None, "SleeperClient not initialized"
    return _sleeper


def get_bedrock() -> BedrockClient:
    assert _bedrock is not None, "BedrockClient not initialized"
    return _bedrock


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _dynamo, _sleeper, _bedrock
    _dynamo = DynamoClient()
    _sleeper = SleeperClient()
    _bedrock = BedrockClient()

    # Run initial sync on startup
    await sync_leagues(_dynamo, _sleeper)
    await sync_rosters(_dynamo, _sleeper, week=1)

    scheduler = build_scheduler(_dynamo, _sleeper, _bedrock)
    scheduler.start()
    log.info("gridiron.started")

    yield

    scheduler.shutdown(wait=False)
    _sleeper.close()
    log.info("gridiron.shutdown")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Gridiron", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gridiron.datatrav.net"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Cloudflare Access middleware
# CF Access validates the JWT at the infrastructure layer (Cloudflare Tunnel).
# We check header presence here as a secondary guard.
# /api/action is token-gated via HMAC and exempt from CF Access.
# ---------------------------------------------------------------------------

CF_ACCESS_HEADER = "CF-Access-Jwt-Assertion"
_CF_EXEMPT_PREFIXES = ("/api/action", "/api/health")


@app.middleware("http")
async def cloudflare_access(request: Request, call_next: Any) -> Response:
    path = request.url.path
    if any(path.startswith(p) for p in _CF_EXEMPT_PREFIXES):
        return await call_next(request)  # type: ignore[return-value]
    if CF_ACCESS_HEADER not in request.headers:
        log.warning("cf_access.missing_header", path=path)
        return Response(status_code=401, content="Unauthorized")
    return await call_next(request)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.2.0")


# ---------------------------------------------------------------------------
# Leagues
# ---------------------------------------------------------------------------


class LeagueSummary(BaseModel):
    league_id: str
    league_name: str | None
    season: str | None
    status: str | None
    format: str | None
    total_rosters: int | None
    faab_budget: int | None
    faab_remaining: int | None


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
                    faab_budget=int(item["faab_budget"]) if "faab_budget" in item else None,
                    faab_remaining=int(item["faab_remaining_2025"]) if "faab_remaining_2025" in item else None,
                )
            )
    return summaries


# ---------------------------------------------------------------------------
# Roster
# ---------------------------------------------------------------------------


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
                "reserve": json.loads(item["reserve"]) if "reserve" in item else [],
                "taxi": json.loads(item["taxi"]) if "taxi" in item else [],
            }
        )
    return RosterResponse(league_id=league_id, week=week, rosters=rosters)


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------


class DecisionSummary(BaseModel):
    decision_id: str
    league_id: str
    type: str
    summary: str
    status: str
    created_at: str
    expires_at: str


class DecisionDetail(DecisionSummary):
    reasoning: str
    proposed_action: dict[str, Any]


@app.get("/api/decisions", response_model=list[DecisionSummary])
async def list_decisions(
    league_id: str | None = Query(None),
    status: str = Query("pending"),
) -> list[DecisionSummary]:
    dynamo = get_dynamo()
    results = []
    leagues = [league_id] if league_id else LEAGUE_IDS
    for lid in leagues:
        # Scan recent decision PKs
        items = dynamo.query_prefix(f"FF#DECISION#{lid}")
        for item in items:
            if item.get("status") == status:
                results.append(
                    DecisionSummary(
                        decision_id=item.get("decision_id", ""),
                        league_id=item.get("league_id", lid),
                        type=item.get("type", ""),
                        summary=item.get("summary", ""),
                        status=item.get("status", ""),
                        created_at=item.get("created_at", ""),
                        expires_at=item.get("expires_at", ""),
                    )
                )
    results.sort(key=lambda d: d.created_at, reverse=True)
    return results


@app.get("/api/decisions/{decision_id}", response_model=DecisionDetail)
async def get_decision(decision_id: str, league_id: str = Query(...)) -> DecisionDetail:
    dynamo = get_dynamo()
    items = dynamo.query_prefix(f"FF#DECISION#{league_id}", sk_prefix=f"LOG#{decision_id}")
    if not items:
        raise HTTPException(status_code=404, detail="Decision not found")
    item = items[0]
    return DecisionDetail(
        decision_id=item.get("decision_id", ""),
        league_id=item.get("league_id", league_id),
        type=item.get("type", ""),
        summary=item.get("summary", ""),
        reasoning=item.get("reasoning", ""),
        status=item.get("status", ""),
        created_at=item.get("created_at", ""),
        expires_at=item.get("expires_at", ""),
        proposed_action=item.get("proposed_action", {}),
    )


@app.post("/api/decisions/{decision_id}/approve")
async def approve_decision_dashboard(decision_id: str, league_id: str = Query(...)) -> dict[str, str]:
    """Approve a decision from the dashboard (CF Access protected)."""
    return await _update_decision_status(decision_id, league_id, "approved")


@app.post("/api/decisions/{decision_id}/reject")
async def reject_decision_dashboard(decision_id: str, league_id: str = Query(...)) -> dict[str, str]:
    """Reject a decision from the dashboard (CF Access protected)."""
    return await _update_decision_status(decision_id, league_id, "rejected")


# ---------------------------------------------------------------------------
# Token-gated approve/reject (email links, no CF Access required)
# ---------------------------------------------------------------------------


@app.get("/api/action")
async def action_via_token(token: str = Query(...)) -> Response:
    """Handle approve/reject from email link. Token-gated, no CF Access needed.

    Replay protection: token hash is recorded in DynamoDB on first use.
    Subsequent requests with the same token are rejected as already-used.
    """
    result = verify_token(token)
    if not result:
        return Response(
            content="<html><body><h2>Link expired or invalid.</h2></body></html>",
            media_type="text/html",
            status_code=400,
        )
    decision_id, action = result
    dynamo = get_dynamo()

    # Rate limiting: max 10 /api/action attempts per hour globally (brute-force guard)
    import hashlib
    now_hour = datetime.now(timezone.utc).strftime("%Y%m%dT%H")
    rate_item = dynamo.get_item("FF#RATELIMIT#ACTION", now_hour)
    attempt_count = int(rate_item.get("count", 0)) if rate_item else 0
    if attempt_count >= 10:
        log.warning("api.action_via_token.rate_limited")
        return Response(
            content="<html><body><h2>Too many requests. Try again later.</h2></body></html>",
            media_type="text/html",
            status_code=429,
        )
    dynamo.update_item("FF#RATELIMIT#ACTION", now_hour, {"count": attempt_count + 1})

    # Replay protection: check if this token has been used before
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
    used_item = dynamo.get_item("FF#TOKEN#USED", token_hash)
    if used_item:
        log.warning("api.action_via_token.replay_attempt", token_hash=token_hash, decision_id=decision_id)
        return Response(
            content="<html><body><h2>This link has already been used.</h2></body></html>",
            media_type="text/html",
            status_code=409,
        )

    # Find the decision across all leagues
    updated = False
    for lid in LEAGUE_IDS:
        items = dynamo.query_prefix(f"FF#DECISION#{lid}", sk_prefix=f"LOG#{decision_id}")
        if items:
            item = items[0]
            if item.get("status") != "pending":
                return Response(
                    content="<html><body><h2>Decision already actioned.</h2></body></html>",
                    media_type="text/html",
                    status_code=409,
                )
            new_status = "approved" if action == "approve" else "rejected"
            # Mark token as used before updating decision (prevents TOCTOU replay)
            dynamo.put_item(
                "FF#TOKEN#USED",
                token_hash,
                {"decision_id": decision_id, "action": action, "used_at": datetime.now(timezone.utc).isoformat()},
            )
            dynamo.update_item(
                f"FF#DECISION#{lid}#{item['created_at']}",
                f"LOG#{decision_id}",
                {"status": new_status, "actioned_at": datetime.now(timezone.utc).isoformat()},
            )
            log.info("api.action_via_token", decision_id=decision_id, action=action, status=new_status)
            updated = True
            break

    if not updated:
        return Response(
            content="<html><body><h2>Decision not found.</h2></body></html>",
            media_type="text/html",
            status_code=404,
        )

    verb = "Approved" if action == "approve" else "Rejected"
    return Response(
        content=f"""<html><body style="font-family:sans-serif;text-align:center;padding:60px">
<h2 style="color:{'#16a34a' if action=='approve' else '#dc2626'}">{verb}</h2>
<p>Decision <code>{decision_id[:8]}...</code> has been {verb.lower()}.</p>
<p><a href="https://gridiron.datatrav.net/decisions">Back to dashboard</a></p>
</body></html>""",
        media_type="text/html",
    )


# ---------------------------------------------------------------------------
# Intel
# ---------------------------------------------------------------------------


@app.get("/api/intel/{player_id}")
async def get_player_intel(player_id: str, limit: int = 5) -> list[dict[str, Any]]:
    dynamo = get_dynamo()
    items = dynamo.query_prefix(f"FF#INTEL#{player_id}", limit=limit)
    return [
        {
            "player_id": item.get("player_id"),
            "player_name": item.get("player_name"),
            "intel": json.loads(item["intel"]) if "intel" in item else {},
            "created_at": item.get("created_at"),
        }
        for item in items
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _update_decision_status(
    decision_id: str,
    league_id: str,
    new_status: str,
) -> dict[str, str]:
    dynamo = get_dynamo()
    items = dynamo.query_prefix(f"FF#DECISION#{league_id}", sk_prefix=f"LOG#{decision_id}")
    if not items:
        raise HTTPException(status_code=404, detail="Decision not found")
    item = items[0]
    if item.get("status") != "pending":
        raise HTTPException(status_code=409, detail=f"Decision already {item.get('status')}")
    dynamo.update_item(
        f"FF#DECISION#{league_id}#{item['created_at']}",
        f"LOG#{decision_id}",
        {"status": new_status, "actioned_at": datetime.now(timezone.utc).isoformat()},
    )
    log.info("api.decision_updated", decision_id=decision_id, status=new_status)
    return {"decision_id": decision_id, "status": new_status}
