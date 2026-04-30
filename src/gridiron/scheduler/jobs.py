"""APScheduler job definitions.

Jobs:
  sync_leagues        — hourly: fetch both league configs from Sleeper, upsert DynamoDB
  sync_rosters        — every 30 min during season: snapshot all rosters
  sync_strategy_docs  — nightly 2am CT: upload local docs/strategy/ to S3
  run_research        — daily at 7am ET: research all rostered players
  run_valuation       — weekly (Monday 6am ET): recompute all player valuations
  run_lineup_waiver   — weekly (Wednesday 8am ET): propose lineup + waiver bids
  run_trades          — daily at 9am ET: check for incoming trades + propose outgoing
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import boto3
import structlog
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from gridiron.agents.lineup_waiver_agent import LineupWaiverAgent
from gridiron.agents.research_agent import ResearchAgent
from gridiron.agents.trade_agent import TradeAgent
from gridiron.agents.valuation_agent import ValuationAgent
from gridiron.db.dynamo import DynamoClient
from gridiron.email.ses import send_decision_email
from gridiron.llm.bedrock_client import BedrockClient
from gridiron.sleeper.client import SleeperClient, SleeperLeague, SleeperRoster

log = structlog.get_logger(__name__)

KEEPER_LEAGUE_ID = "1183557197018804224"
DYNASTY_LEAGUE_ID = "1331779473430810624"
LEAGUE_IDS = [KEEPER_LEAGUE_ID, DYNASTY_LEAGUE_ID]


def _league_to_dynamo(league: SleeperLeague) -> dict[str, object]:
    return {
        "league_name": league.name,
        "season": league.season,
        "status": league.status,
        "roster_positions": json.dumps(league.roster_positions),
        "scoring_settings": json.dumps(league.scoring_settings),
        "settings": json.dumps(league.settings),
        "total_rosters": league.total_rosters,
        "draft_id": league.draft_id,
        "updated_at": datetime.now(UTC).isoformat(),
    }


def _roster_to_dynamo(roster: SleeperRoster, week: int) -> dict[str, object]:
    return {
        "roster_id": roster.roster_id,
        "owner_id": roster.owner_id,
        "players": json.dumps(roster.players),
        "starters": json.dumps(roster.starters),
        "reserve": json.dumps(roster.reserve),
        "taxi": json.dumps(roster.taxi),
        "settings": json.dumps(roster.settings),
        "week": week,
        "snapshotted_at": datetime.now(UTC).isoformat(),
    }


# ---------------------------------------------------------------------------
# Sync jobs (data pipeline)
# ---------------------------------------------------------------------------


async def sync_leagues(dynamo: DynamoClient, sleeper: SleeperClient) -> None:
    """Fetch both leagues from Sleeper and upsert CONFIG records in DynamoDB."""
    log.info("jobs.sync_leagues.start")
    for league_id in LEAGUE_IDS:
        try:
            league = sleeper.get_league(league_id)
            pk = f"FF#LEAGUE#{league_id}"
            dynamo.put_item(pk, "CONFIG", _league_to_dynamo(league))
            log.info("jobs.sync_leagues.synced", league_id=league_id, name=league.name)
        except Exception as exc:
            log.error("jobs.sync_leagues.error", league_id=league_id, error=str(exc))
    log.info("jobs.sync_leagues.done")


async def sync_rosters(dynamo: DynamoClient, sleeper: SleeperClient, week: int) -> None:
    """Snapshot all rosters for both leagues at the given week."""
    log.info("jobs.sync_rosters.start", week=week)
    for league_id in LEAGUE_IDS:
        try:
            rosters = sleeper.get_rosters(league_id)
            for roster in rosters:
                pk = f"FF#ROSTER#{league_id}#{week}"
                sk = f"SNAPSHOT#{roster.roster_id}"
                dynamo.put_item(pk, sk, _roster_to_dynamo(roster, week))
            log.info(
                "jobs.sync_rosters.synced",
                league_id=league_id,
                week=week,
                count=len(rosters),
            )
        except Exception as exc:
            log.error("jobs.sync_rosters.error", league_id=league_id, week=week, error=str(exc))
    log.info("jobs.sync_rosters.done", week=week)


_MODELS_YAML = Path(__file__).parent.parent.parent.parent / "config" / "models.yaml"
_STRATEGY_LOCAL = Path(__file__).parent.parent.parent.parent / "docs" / "strategy"


async def sync_strategy_docs() -> None:
    """Nightly 2am CT: upload docs/strategy/*.md to S3 gridiron-strategy-docs."""
    log.info("jobs.sync_strategy_docs.start")
    try:
        cfg: dict[str, object] = {}
        try:
            with open(_MODELS_YAML) as f:
                cfg = yaml.safe_load(f) or {}
        except Exception:
            pass

        bucket = str(cfg.get("strategy_bucket", "gridiron-strategy-docs"))
        prefix = str(cfg.get("strategy_prefix", "strategy/"))
        s3 = boto3.client("s3")

        uploaded = 0
        for md_file in sorted(_STRATEGY_LOCAL.glob("*.md")):
            key = f"{prefix}{md_file.name}"
            s3.upload_file(str(md_file), bucket, key)
            uploaded += 1
            log.info("jobs.sync_strategy_docs.uploaded", file=md_file.name, key=key)

        log.info("jobs.sync_strategy_docs.done", uploaded=uploaded)
    except Exception as exc:
        log.error("jobs.sync_strategy_docs.error", error=str(exc))


# ---------------------------------------------------------------------------
# Agent jobs (propose-then-approve)
# ---------------------------------------------------------------------------


async def run_research(
    dynamo: DynamoClient,
    sleeper: SleeperClient,
    bedrock: BedrockClient,
) -> None:
    """Research all rostered players across both leagues."""
    agent = ResearchAgent(dynamo, sleeper, bedrock)
    for league_id in LEAGUE_IDS:
        try:
            await agent.run(league_id)
        except Exception as exc:
            log.error("jobs.research.error", league_id=league_id, error=str(exc))


async def run_valuation(
    dynamo: DynamoClient,
    sleeper: SleeperClient,
    bedrock: BedrockClient,
) -> None:
    """Recompute player valuations (all positions, both scoring formats)."""
    agent = ValuationAgent(dynamo, sleeper, bedrock)
    # Valuation runs once — dynasty mode covers all offensive positions
    # Keeper mode adds IDP on second pass
    for league_id in LEAGUE_IDS:
        try:
            await agent.run(league_id)
        except Exception as exc:
            log.error("jobs.valuation.error", league_id=league_id, error=str(exc))


async def run_lineup_waiver(
    dynamo: DynamoClient,
    sleeper: SleeperClient,
    bedrock: BedrockClient,
    week: int,
) -> None:
    """Propose lineup and waiver bids for both leagues; email decisions to Travis."""
    agent = LineupWaiverAgent(dynamo, sleeper, bedrock)
    for league_id in LEAGUE_IDS:
        try:
            decisions = await agent.run(league_id, week=week)
            for decision in decisions:
                try:
                    send_decision_email(decision)
                except Exception as email_exc:
                    log.error(
                        "jobs.lineup_waiver.email_error",
                        decision_id=decision.decision_id,
                        error=str(email_exc),
                    )
        except Exception as exc:
            log.error("jobs.lineup_waiver.error", league_id=league_id, error=str(exc))


async def run_trades(
    dynamo: DynamoClient,
    sleeper: SleeperClient,
    bedrock: BedrockClient,
) -> None:
    """Check for incoming trades and propose outgoing; email decisions to Travis."""
    agent = TradeAgent(dynamo, sleeper, bedrock)
    for league_id in LEAGUE_IDS:
        try:
            decisions = await agent.run(league_id)
            for decision in decisions:
                try:
                    send_decision_email(decision)
                except Exception as email_exc:
                    log.error(
                        "jobs.trades.email_error",
                        decision_id=decision.decision_id,
                        error=str(email_exc),
                    )
        except Exception as exc:
            log.error("jobs.trades.error", league_id=league_id, error=str(exc))


# ---------------------------------------------------------------------------
# Scheduler factory
# ---------------------------------------------------------------------------


def build_scheduler(
    dynamo: DynamoClient,
    sleeper: SleeperClient,
    bedrock: BedrockClient,
    current_week: int = 1,
) -> AsyncIOScheduler:
    """Build and return configured AsyncIOScheduler (not yet started)."""
    scheduler = AsyncIOScheduler(timezone="America/New_York")

    # Data pipeline
    scheduler.add_job(
        sync_strategy_docs,
        trigger=CronTrigger(hour=2, minute=0),  # 2am CT nightly
        id="sync_strategy_docs",
        replace_existing=True,
        misfire_grace_time=600,
    )
    scheduler.add_job(
        sync_leagues,
        trigger=IntervalTrigger(hours=1),
        args=[dynamo, sleeper],
        id="sync_leagues",
        replace_existing=True,
        misfire_grace_time=300,
    )
    scheduler.add_job(
        sync_rosters,
        trigger=IntervalTrigger(minutes=30),
        args=[dynamo, sleeper, current_week],
        id="sync_rosters",
        replace_existing=True,
        misfire_grace_time=120,
    )

    # Agent jobs
    scheduler.add_job(
        run_research,
        trigger=CronTrigger(hour=7, minute=0),  # 7am ET daily
        args=[dynamo, sleeper, bedrock],
        id="run_research",
        replace_existing=True,
        misfire_grace_time=600,
    )
    scheduler.add_job(
        run_valuation,
        trigger=CronTrigger(day_of_week="mon", hour=6, minute=0),  # Monday 6am ET
        args=[dynamo, sleeper, bedrock],
        id="run_valuation",
        replace_existing=True,
        misfire_grace_time=1800,
    )
    scheduler.add_job(
        run_lineup_waiver,
        trigger=CronTrigger(day_of_week="wed", hour=8, minute=0),  # Wednesday 8am ET
        args=[dynamo, sleeper, bedrock, current_week],
        id="run_lineup_waiver",
        replace_existing=True,
        misfire_grace_time=600,
    )
    scheduler.add_job(
        run_trades,
        trigger=CronTrigger(hour=9, minute=0),  # 9am ET daily
        args=[dynamo, sleeper, bedrock],
        id="run_trades",
        replace_existing=True,
        misfire_grace_time=600,
    )

    return scheduler
