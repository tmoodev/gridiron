"""APScheduler job definitions.

Jobs:
  sync_leagues  — hourly: fetch both league configs from Sleeper, upsert DynamoDB
  sync_rosters  — every 30 min during season: snapshot all rosters
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from gridiron.db.dynamo import DynamoClient
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
        "updated_at": datetime.now(timezone.utc).isoformat(),
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
        "snapshotted_at": datetime.now(timezone.utc).isoformat(),
    }


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


def build_scheduler(dynamo: DynamoClient, sleeper: SleeperClient, current_week: int = 1) -> AsyncIOScheduler:
    """Build and return configured AsyncIOScheduler (not yet started)."""
    scheduler = AsyncIOScheduler()

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

    return scheduler
