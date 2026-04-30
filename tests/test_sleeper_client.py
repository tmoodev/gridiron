"""Unit tests for SleeperClient — all HTTP calls are mocked."""

from __future__ import annotations

import pytest
import httpx
import respx

from gridiron.sleeper.client import SleeperClient, SleeperLeague, SleeperRoster, SleeperUser

SLEEPER_BASE = "https://api.sleeper.app/v1"


@respx.mock
def test_get_user() -> None:
    respx.get(f"{SLEEPER_BASE}/user/Travy2Chains").mock(
        return_value=httpx.Response(
            200,
            json={
                "user_id": "123",
                "username": "Travy2Chains",
                "display_name": "Travis Moore",
                "avatar": None,
            },
        )
    )
    with SleeperClient() as client:
        user = client.get_user("Travy2Chains")
    assert isinstance(user, SleeperUser)
    assert user.user_id == "123"
    assert user.username == "Travy2Chains"


@respx.mock
def test_get_league() -> None:
    league_id = "1183557197018804224"
    respx.get(f"{SLEEPER_BASE}/league/{league_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "league_id": league_id,
                "name": "Fantasy Football Season 9",
                "season": "2026",
                "status": "pre_draft",
                "sport": "nfl",
                "total_rosters": 12,
                "roster_positions": ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "K"],
                "scoring_settings": {"rec": 0.5},
                "settings": {},
                "metadata": {},
                "draft_id": "abc123",
                "previous_league_id": None,
            },
        )
    )
    with SleeperClient() as client:
        league = client.get_league(league_id)
    assert isinstance(league, SleeperLeague)
    assert league.league_id == league_id
    assert league.name == "Fantasy Football Season 9"
    assert league.scoring_settings["rec"] == 0.5
    assert league.total_rosters == 12


@respx.mock
def test_get_rosters() -> None:
    league_id = "1331779473430810624"
    respx.get(f"{SLEEPER_BASE}/league/{league_id}/rosters").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "roster_id": 1,
                    "owner_id": "user001",
                    "league_id": league_id,
                    "players": ["1234", "5678"],
                    "starters": ["1234"],
                    "reserve": [],
                    "taxi": ["5678"],
                    "settings": {},
                    "metadata": {},
                }
            ],
        )
    )
    with SleeperClient() as client:
        rosters = client.get_rosters(league_id)
    assert len(rosters) == 1
    roster = rosters[0]
    assert isinstance(roster, SleeperRoster)
    assert roster.roster_id == 1
    assert roster.owner_id == "user001"
    assert "1234" in roster.players
    assert "5678" in roster.taxi


@respx.mock
def test_get_traded_picks_empty() -> None:
    league_id = "1183557197018804224"
    respx.get(f"{SLEEPER_BASE}/league/{league_id}/traded_picks").mock(
        return_value=httpx.Response(200, json=[])
    )
    with SleeperClient() as client:
        picks = client.get_traded_picks(league_id)
    assert picks == []
