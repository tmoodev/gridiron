"""KeepTradeCut scraper.

Fetches the `playersArray` JS variable from the KTC page — no auth required.
Returns rich player valuation data: 1QB value, SuperFlex value, 30-day trend.

Upserts FF#PLAYER#{player_id}#META in DynamoDB keyed by KTC player name
cross-referenced against Sleeper player IDs.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog

log = structlog.get_logger(__name__)

KTC_URL = "https://keeptradecut.com/dynasty-rankings"
KTC_SUPERFLEX_URL = "https://keeptradecut.com/dynasty-rankings?format=2"

_PLAYERS_ARRAY_RE = re.compile(r"var playersArray\s*=\s*(\[.*?\]);", re.DOTALL)


class KTCPlayer:
    __slots__ = (
        "ktc_id",
        "name",
        "position",
        "team",
        "age",
        "value_1qb",
        "value_sf",
        "trend_1qb",
        "trend_sf",
        "scraped_at",
    )

    def __init__(
        self,
        ktc_id: str,
        name: str,
        position: str,
        team: str,
        age: int | None,
        value_1qb: int,
        value_sf: int,
        trend_1qb: int,
        trend_sf: int,
        scraped_at: str,
    ) -> None:
        self.ktc_id = ktc_id
        self.name = name
        self.position = position
        self.team = team
        self.age = age
        self.value_1qb = value_1qb
        self.value_sf = value_sf
        self.trend_1qb = trend_1qb
        self.trend_sf = trend_sf
        self.scraped_at = scraped_at

    def to_dynamo(self) -> dict[str, Any]:
        return {
            "ktc_id": self.ktc_id,
            "name": self.name,
            "position": self.position,
            "team": self.team,
            "age": self.age,
            "ktc_value_1qb": self.value_1qb,
            "ktc_value_sf": self.value_sf,
            "ktc_trend_1qb": self.trend_1qb,
            "ktc_trend_sf": self.trend_sf,
            "ktc_scraped_at": self.scraped_at,
        }


def _parse_players(html: str, is_sf: bool) -> dict[str, dict[str, Any]]:
    """Parse playersArray from KTC HTML. Returns {name_key: {...}} dict."""
    match = _PLAYERS_ARRAY_RE.search(html)
    if not match:
        log.warning("ktc.parse.no_players_array_found")
        return {}

    try:
        raw: list[dict[str, Any]] = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        log.error("ktc.parse.json_error", error=str(exc))
        return {}

    result: dict[str, dict[str, Any]] = {}
    for player in raw:
        name = player.get("playerName", "")
        if not name:
            continue
        key = name.lower().strip()
        value = player.get("value", 0) or 0
        trend = player.get("trend30Day", 0) or 0
        if is_sf:
            result.setdefault(key, {})["value_sf"] = value
            result.setdefault(key, {})["trend_sf"] = trend
        else:
            result.setdefault(key, {}).update(
                {
                    "ktc_id": str(player.get("playerID", "")),
                    "name": name,
                    "position": player.get("position", ""),
                    "team": player.get("team", ""),
                    "age": player.get("age"),
                    "value_1qb": value,
                    "trend_1qb": trend,
                }
            )

    return result


class KTCScraper:
    def __init__(self, timeout: float = 30.0) -> None:
        self._http = httpx.Client(
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                )
            },
            follow_redirects=True,
        )

    def scrape(self) -> list[KTCPlayer]:
        """Fetch both 1QB and SuperFlex rankings and merge into a single list."""
        now = datetime.now(timezone.utc).isoformat()

        log.info("ktc.scrape.start")
        resp_1qb = self._http.get(KTC_URL)
        resp_1qb.raise_for_status()
        players_1qb = _parse_players(resp_1qb.text, is_sf=False)
        log.info("ktc.scrape.1qb_done", count=len(players_1qb))

        resp_sf = self._http.get(KTC_SUPERFLEX_URL)
        resp_sf.raise_for_status()
        players_sf = _parse_players(resp_sf.text, is_sf=True)
        log.info("ktc.scrape.sf_done", count=len(players_sf))

        results: list[KTCPlayer] = []
        for key, data in players_1qb.items():
            sf_data = players_sf.get(key, {})
            results.append(
                KTCPlayer(
                    ktc_id=data.get("ktc_id", ""),
                    name=data.get("name", ""),
                    position=data.get("position", ""),
                    team=data.get("team", ""),
                    age=data.get("age"),
                    value_1qb=data.get("value_1qb", 0),
                    value_sf=sf_data.get("value_sf", data.get("value_1qb", 0)),
                    trend_1qb=data.get("trend_1qb", 0),
                    trend_sf=sf_data.get("trend_sf", data.get("trend_1qb", 0)),
                    scraped_at=now,
                )
            )

        log.info("ktc.scrape.done", total=len(results))
        return results

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> KTCScraper:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
