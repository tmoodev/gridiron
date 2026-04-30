"""Tests verifying agents load strategy docs and log them in decision records."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from gridiron.agents.base import BaseAgent, Decision

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LEAGUE_ID = "1183557197018804224"


def mock_dynamo(league_cfg: dict | None = None) -> MagicMock:
    dynamo = MagicMock()
    dynamo.get_item.return_value = league_cfg or {
        "travis_user_id": "user_123",
        "format": "keeper_idp",
        "scoring": "half_ppr",
        "roster_slots": "{}",
        "faab_budget": 80,
        "faab_remaining_2025": 74,
    }
    dynamo.query_prefix.return_value = []
    return dynamo


def mock_sleeper() -> MagicMock:
    sleeper = MagicMock()
    roster = MagicMock()
    roster.owner_id = "user_123"
    roster.roster_id = 1
    roster.players = []
    roster.reserve = []
    roster.taxi = []
    sleeper.get_rosters.return_value = [roster]
    sleeper.get_all_players.return_value = {}
    return sleeper


def mock_bedrock() -> MagicMock:
    bedrock = MagicMock()
    bedrock.reason.return_value = '{"starters": {}, "reasoning": "test", "confidence": "LOW", "sit_start_highlights": []}'
    bedrock.research.return_value = '{"health": "ok", "role": "ok", "fantasy_outlook": "ok", "confidence": "LOW"}'
    return bedrock


# ---------------------------------------------------------------------------
# BaseAgent._load_strategy
# ---------------------------------------------------------------------------


def test_load_strategy_populates_versions() -> None:
    agent = BaseAgent(
        dynamo=mock_dynamo(),
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )
    with patch("gridiron.agents.base._strategy_loader") as mock_loader:
        mock_loader.load.return_value = "strategy content"
        mock_loader.load_metadata.return_value = {
            "00-principles": "1.0",
            "03-waiver-strategy": "1.0",
        }
        content = agent._load_strategy("03-waiver-strategy")

    assert content == "strategy content"
    assert agent._current_strategy_versions == {
        "00-principles": "1.0",
        "03-waiver-strategy": "1.0",
    }


def test_save_decision_records_strategy_metadata() -> None:
    dynamo = mock_dynamo()
    agent = BaseAgent(
        dynamo=dynamo,
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )
    agent._current_strategy_versions = {
        "00-principles": "1.0",
        "03-waiver-strategy": "1.0",
    }

    decision = Decision(
        league_id=LEAGUE_ID,
        type="lineup",
        summary="test",
        reasoning="test",
    )
    agent._save_decision(decision)

    assert decision.strategy_docs_loaded == ["00-principles", "03-waiver-strategy"]
    assert decision.strategy_doc_versions == {
        "00-principles": "1.0",
        "03-waiver-strategy": "1.0",
    }

    # Verify DynamoDB put_item was called with the strategy metadata
    call_args = dynamo.put_item.call_args
    item_data = call_args[0][2]  # third positional arg is the item dict
    assert item_data["strategy_docs_loaded"] == ["00-principles", "03-waiver-strategy"]
    assert item_data["strategy_doc_versions"] == {
        "00-principles": "1.0",
        "03-waiver-strategy": "1.0",
    }


def test_save_decision_with_no_strategy_loaded() -> None:
    """Decision saved before any strategy loaded has empty strategy fields."""
    dynamo = mock_dynamo()
    agent = BaseAgent(
        dynamo=dynamo,
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )
    decision = Decision(
        league_id=LEAGUE_ID,
        type="lineup",
        summary="test",
        reasoning="test",
    )
    agent._save_decision(decision)

    assert decision.strategy_docs_loaded == []
    assert decision.strategy_doc_versions == {}


# ---------------------------------------------------------------------------
# LineupWaiverAgent — verify strategy is loaded and logged
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_lineup_waiver_agent_loads_strategy() -> None:
    from gridiron.agents.lineup_waiver_agent import LineupWaiverAgent

    dynamo = mock_dynamo()
    agent = LineupWaiverAgent(
        dynamo=dynamo,
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )

    with patch("gridiron.agents.base._strategy_loader") as mock_loader:
        mock_loader.load.return_value = "principles + lineup strategy"
        mock_loader.load_metadata.return_value = {
            "00-principles": "1.0",
            "02-roster-construction": "1.0",
            "03-waiver-strategy": "1.0",
            "05-lineup-strategy": "1.0",
            "08-in-season-management": "1.0",
        }
        await agent.run(LEAGUE_ID, week=1)

    # loader.load should have been called with the correct docs
    mock_loader.load.assert_called_once_with(
        "02-roster-construction",
        "03-waiver-strategy",
        "05-lineup-strategy",
        "08-in-season-management",
    )


# ---------------------------------------------------------------------------
# TradeAgent — verify league-specific doc selection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_trade_agent_loads_dynasty_docs() -> None:
    from gridiron.agents.trade_agent import TradeAgent

    dynasty_id = "1331779473430810624"
    dynamo = mock_dynamo({"travis_user_id": "user_123", "format": "dynasty", "scoring": "full_ppr"})
    agent = TradeAgent(
        dynamo=dynamo,
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )

    with patch("gridiron.agents.base._strategy_loader") as mock_loader:
        mock_loader.load.return_value = "dynasty strategy"
        mock_loader.load_metadata.return_value = {"00-principles": "1.0"}
        await agent.run(dynasty_id)

    call_args = mock_loader.load.call_args[0]
    assert "06-dynasty-rookie-draft" in call_args
    assert "07-keeper-selection" not in call_args


@pytest.mark.asyncio
async def test_trade_agent_loads_keeper_docs() -> None:
    from gridiron.agents.trade_agent import TradeAgent

    dynamo = mock_dynamo({"travis_user_id": "user_123", "format": "keeper_idp", "scoring": "half_ppr"})
    agent = TradeAgent(
        dynamo=dynamo,
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )

    with patch("gridiron.agents.base._strategy_loader") as mock_loader:
        mock_loader.load.return_value = "keeper strategy"
        mock_loader.load_metadata.return_value = {"00-principles": "1.0"}
        await agent.run(LEAGUE_ID)

    call_args = mock_loader.load.call_args[0]
    assert "07-keeper-selection" in call_args
    assert "06-dynasty-rookie-draft" not in call_args


# ---------------------------------------------------------------------------
# ValuationAgent — doc selection by league
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_valuation_agent_loads_dynasty_docs() -> None:
    from gridiron.agents.valuation_agent import ValuationAgent

    dynasty_id = "1331779473430810624"
    dynamo = mock_dynamo()
    agent = ValuationAgent(
        dynamo=dynamo,
        sleeper=mock_sleeper(),
        bedrock=mock_bedrock(),
    )

    with patch("gridiron.agents.base._strategy_loader") as mock_loader, \
         patch("gridiron.agents.valuation_agent.KTCScraper") as mock_ktc:
        mock_loader.load.return_value = "dynasty strategy"
        mock_loader.load_metadata.return_value = {"00-principles": "1.0"}
        mock_ktc.return_value.__enter__ = MagicMock(return_value=MagicMock(scrape=MagicMock(return_value=[])))
        mock_ktc.return_value.__exit__ = MagicMock(return_value=False)
        await agent.run(dynasty_id)

    call_args = mock_loader.load.call_args[0]
    assert "01-valuation-philosophy" in call_args
    assert "06-dynasty-rookie-draft" in call_args
    assert "07-keeper-selection" not in call_args
