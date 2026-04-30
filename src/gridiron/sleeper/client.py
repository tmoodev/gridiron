"""Typed Pydantic v2 client for the Sleeper public API.

All endpoints are read-only; no authentication required.
Base URL: https://api.sleeper.app/v1
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog
from pydantic import BaseModel, Field

log = structlog.get_logger(__name__)

SLEEPER_BASE = "https://api.sleeper.app/v1"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class SleeperUser(BaseModel):
    user_id: str
    username: str
    display_name: str
    avatar: str | None = None


class SleeperLeague(BaseModel):
    league_id: str
    name: str
    season: str
    status: str  # "pre_draft", "drafting", "in_season", "complete"
    sport: str
    total_rosters: int
    roster_positions: list[str]
    scoring_settings: dict[str, float] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    draft_id: str | None = None
    previous_league_id: str | None = None


class SleeperRoster(BaseModel):
    roster_id: int
    owner_id: str | None = None
    league_id: str
    players: list[str] = Field(default_factory=list)
    starters: list[str] = Field(default_factory=list)
    reserve: list[str] = Field(default_factory=list)
    taxi: list[str] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SleeperMatchup(BaseModel):
    roster_id: int
    matchup_id: int
    week: int
    points: float = 0.0
    custom_points: float | None = None
    players: list[str] = Field(default_factory=list)
    starters: list[str] = Field(default_factory=list)
    players_points: dict[str, float] = Field(default_factory=dict)


class SleeperPlayer(BaseModel):
    player_id: str
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None
    team: str | None = None
    age: int | None = None
    years_exp: int | None = None
    status: str | None = None  # "Active", "Injured_Reserve", etc.
    injury_status: str | None = None
    fantasy_positions: list[str] = Field(default_factory=list)
    depth_chart_position: int | None = None
    search_rank: int | None = None


class SleeperPick(BaseModel):
    """A traded draft pick asset."""
    season: str
    round: int
    roster_id: int  # original owner
    owner_id: str   # current owner (user_id)
    previous_owner_id: str | None = None


class SleeperDraft(BaseModel):
    draft_id: str
    league_id: str
    season: str
    status: str  # "pre_draft", "drafting", "complete"
    type: str    # "snake", "linear", etc.
    settings: dict[str, Any] = Field(default_factory=dict)
    draft_order: dict[str, int] | None = None  # user_id -> pick slot
    slot_to_roster_id: dict[str, int] | None = None


class SleeperDraftPick(BaseModel):
    """An actual pick made during a draft."""
    round: int
    draft_slot: int
    pick_no: int
    player_id: str
    picked_by: str
    roster_id: int
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class SleeperClient:
    def __init__(self, timeout: float = 10.0) -> None:
        self._http = httpx.Client(
            base_url=SLEEPER_BASE,
            timeout=timeout,
            headers={"User-Agent": "gridiron/0.1 (travis@datatrav.com)"},
        )

    def _get(self, path: str) -> Any:
        resp = self._http.get(path)
        resp.raise_for_status()
        log.debug("sleeper.get", path=path, status=resp.status_code)
        return resp.json()

    # -----------------------------------------------------------------------
    # User
    # -----------------------------------------------------------------------

    def get_user(self, username: str) -> SleeperUser:
        data = self._get(f"/user/{username}")
        return SleeperUser.model_validate(data)

    # -----------------------------------------------------------------------
    # League
    # -----------------------------------------------------------------------

    def get_league(self, league_id: str) -> SleeperLeague:
        data = self._get(f"/league/{league_id}")
        return SleeperLeague.model_validate(data)

    def get_user_leagues(self, user_id: str, season: str, sport: str = "nfl") -> list[SleeperLeague]:
        data = self._get(f"/user/{user_id}/leagues/{sport}/{season}")
        return [SleeperLeague.model_validate(item) for item in (data or [])]

    # -----------------------------------------------------------------------
    # Rosters
    # -----------------------------------------------------------------------

    def get_rosters(self, league_id: str) -> list[SleeperRoster]:
        data = self._get(f"/league/{league_id}/rosters")
        return [SleeperRoster.model_validate(item) for item in (data or [])]

    # -----------------------------------------------------------------------
    # Matchups
    # -----------------------------------------------------------------------

    def get_matchups(self, league_id: str, week: int) -> list[SleeperMatchup]:
        data = self._get(f"/league/{league_id}/matchups/{week}")
        return [SleeperMatchup.model_validate({**item, "week": week}) for item in (data or [])]

    # -----------------------------------------------------------------------
    # Players
    # -----------------------------------------------------------------------

    def get_all_players(self, sport: str = "nfl") -> dict[str, SleeperPlayer]:
        """Returns full player DB (~5MB). Cache aggressively — updates once daily."""
        data = self._get(f"/players/{sport}")
        players: dict[str, SleeperPlayer] = {}
        for player_id, pdata in (data or {}).items():
            try:
                players[player_id] = SleeperPlayer.model_validate(
                    {"player_id": player_id, **pdata}
                )
            except Exception:
                log.warning("sleeper.player_parse_error", player_id=player_id)
        log.info("sleeper.players_loaded", count=len(players))
        return players

    # -----------------------------------------------------------------------
    # Traded picks
    # -----------------------------------------------------------------------

    def get_traded_picks(self, league_id: str) -> list[SleeperPick]:
        data = self._get(f"/league/{league_id}/traded_picks")
        return [SleeperPick.model_validate(item) for item in (data or [])]

    # -----------------------------------------------------------------------
    # Draft
    # -----------------------------------------------------------------------

    def get_drafts(self, league_id: str) -> list[SleeperDraft]:
        data = self._get(f"/league/{league_id}/drafts")
        return [SleeperDraft.model_validate(item) for item in (data or [])]

    def get_draft(self, draft_id: str) -> SleeperDraft:
        data = self._get(f"/draft/{draft_id}")
        return SleeperDraft.model_validate(data)

    def get_draft_picks(self, draft_id: str) -> list[SleeperDraftPick]:
        data = self._get(f"/draft/{draft_id}/picks")
        return [SleeperDraftPick.model_validate(item) for item in (data or [])]

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SleeperClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
