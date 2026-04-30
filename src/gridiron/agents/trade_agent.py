"""Trade Agent — analyze incoming trades and propose outgoing offers.

For each pending trade on Sleeper:
  - Evaluate the offer using valuations + Claude reasoning
  - Write FF#TRADE# + FF#DECISION# records
  - Send approval email (Phase 4) for accept/reject

Also proposes outgoing trades based on roster gaps.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import structlog

from gridiron.agents.base import BaseAgent, Decision

log = structlog.get_logger(__name__)

_TRADE_EVAL_PROMPT = """You are an expert dynasty/keeper fantasy football trade analyst.

League: {format} | Scoring: {scoring}

Incoming trade offer:
  Giving up: {giving_up}
  Receiving: {receiving}

Player valuations (keeper_value / dynasty_value / redraft_value out of 100):
{valuations_json}

Analyze this trade:
1. Net value delta (positive = you win, negative = you lose)
2. Age/trajectory angle — does this trade help now vs. the future?
3. Positional need adjustment — does this fill a hole?
4. Verdict: ACCEPT / REJECT / COUNTER

Respond as JSON:
{{
  "net_value_delta": <int, positive favors accept>,
  "verdict": "ACCEPT|REJECT|COUNTER",
  "counter_suggestion": "<what to ask for instead, or null>",
  "reasoning": "<2-3 sentences>",
  "confidence": "HIGH|MEDIUM|LOW"
}}"""

_OUTGOING_TRADE_PROMPT = """You are an expert dynasty/keeper fantasy football trade strategist.

League: {format} | Scoring: {scoring}

My roster (player valuations included):
{my_roster_json}

League roster overview (all teams, summarized):
{league_overview_json}

Identify 1-2 trade proposals that would improve my team:
- Look for positional surpluses I can trade from
- Look for positions where I'm weak
- Target players on other rosters who might be available

Respond as JSON:
{{
  "proposals": [
    {{
      "offer_player_ids": ["<id>"],
      "offer_player_names": ["<name>"],
      "target_player_ids": ["<id>"],
      "target_player_names": ["<name>"],
      "target_team_roster_id": <int>,
      "reasoning": "<1-2 sentences>",
      "confidence": "HIGH|MEDIUM|LOW"
    }}
  ]
}}"""


class TradeAgent(BaseAgent):
    name = "trade"

    async def run(self, league_id: str) -> list[Decision]:
        decisions: list[Decision] = []

        cfg = self._get_league_config(league_id)
        if not cfg:
            return []

        travis_user_id = cfg.get("travis_user_id")
        league_format = cfg.get("format", "unknown")
        scoring = cfg.get("scoring", "half_ppr")
        all_players = self.sleeper.get_all_players()
        rosters = self.sleeper.get_rosters(league_id)

        travis_roster = next(
            (r for r in rosters if r.owner_id == travis_user_id),
            rosters[0] if rosters else None,
        )
        if not travis_roster:
            return []

        # --- Evaluate incoming trades ---
        try:
            incoming = self._get_pending_trades(league_id, travis_roster.roster_id)
            for trade in incoming:
                d = await self._evaluate_incoming_trade(
                    trade, league_id, league_format, scoring, all_players
                )
                if d:
                    self._save_decision(d)
                    decisions.append(d)
        except Exception as exc:
            log.error("trade_agent.incoming_error", league_id=league_id, error=str(exc))

        # --- Propose outgoing trades ---
        try:
            outgoing_decisions = await self._propose_outgoing_trades(
                league_id, league_format, scoring, travis_roster, rosters, all_players
            )
            for d in outgoing_decisions:
                self._save_decision(d)
                decisions.append(d)
        except Exception as exc:
            log.error("trade_agent.outgoing_error", league_id=league_id, error=str(exc))

        log.info("trade_agent.done", league_id=league_id, decisions=len(decisions))
        return decisions

    def _get_pending_trades(self, league_id: str, roster_id: int) -> list[dict[str, Any]]:
        """Query DynamoDB for pending trade records involving Travis's roster."""
        items = self.dynamo.query_prefix(
            f"FF#TRADE#{league_id}",
            sk_prefix="DATA",
        )
        return [
            item for item in items
            if item.get("status") == "pending"
            and (
                roster_id in item.get("roster_ids", [])
                or str(roster_id) in str(item.get("roster_ids", []))
            )
        ]

    async def _evaluate_incoming_trade(
        self,
        trade: dict[str, Any],
        league_id: str,
        league_format: str,
        scoring: str,
        all_players: dict[str, Any],
    ) -> Decision | None:
        giving_up = trade.get("gives", [])
        receiving = trade.get("receives", [])

        def describe_players(ids: list[str]) -> list[str]:
            return [
                f"{all_players[pid].full_name} ({all_players[pid].position})"
                for pid in ids
                if pid in all_players and all_players[pid].full_name
            ]

        # Fetch valuations from DynamoDB
        valuations: dict[str, Any] = {}
        all_ids = giving_up + receiving
        for pid in all_ids:
            item = self.dynamo.get_item(f"FF#PLAYER#{pid}", "META")
            if item and "valuations" in item:
                try:
                    valuations[pid] = json.loads(item["valuations"])
                except Exception:
                    pass

        prompt = _TRADE_EVAL_PROMPT.format(
            format=league_format,
            scoring=scoring,
            giving_up=", ".join(describe_players(giving_up)) or "nothing",
            receiving=", ".join(describe_players(receiving)) or "nothing",
            valuations_json=json.dumps(valuations, indent=2),
        )

        raw = self.bedrock.reason(prompt, max_tokens=512)
        analysis: dict[str, Any] = {}
        try:
            cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
            analysis = json.loads(cleaned)
        except Exception:
            analysis = {"raw": raw}

        verdict = analysis.get("verdict", "REJECT")
        return Decision(
            league_id=league_id,
            type="trade_response",
            summary=f"Trade offer: {verdict} — {analysis.get('reasoning', '')[:100]}",
            reasoning=analysis.get("reasoning", raw[:500]),
            proposed_action={
                "trade_id": trade.get("trade_id", "unknown"),
                "verdict": verdict,
                "net_value_delta": analysis.get("net_value_delta", 0),
                "counter_suggestion": analysis.get("counter_suggestion"),
                "giving_up": giving_up,
                "receiving": receiving,
            },
        )

    async def _propose_outgoing_trades(
        self,
        league_id: str,
        league_format: str,
        scoring: str,
        travis_roster: Any,
        all_rosters: list[Any],
        all_players: dict[str, Any],
    ) -> list[Decision]:
        def roster_summary(roster: Any) -> list[dict[str, Any]]:
            return [
                {"player_id": pid, "name": all_players[pid].full_name, "position": all_players[pid].position}
                for pid in roster.players
                if pid in all_players and all_players[pid].full_name
            ]

        my_roster_data = []
        for pid in travis_roster.players:
            p = all_players.get(pid)
            if not p or not p.full_name:
                continue
            val_item = self.dynamo.get_item(f"FF#PLAYER#{pid}", "META")
            vals = {}
            if val_item and "valuations" in val_item:
                try:
                    vals = json.loads(val_item["valuations"])
                except Exception:
                    pass
            my_roster_data.append({
                "player_id": pid,
                "name": p.full_name,
                "position": p.position,
                "team": p.team,
                "valuations": vals,
            })

        league_overview = [
            {"roster_id": r.roster_id, "players": roster_summary(r)}
            for r in all_rosters
            if r.roster_id != travis_roster.roster_id
        ]

        prompt = _OUTGOING_TRADE_PROMPT.format(
            format=league_format,
            scoring=scoring,
            my_roster_json=json.dumps(my_roster_data, indent=2),
            league_overview_json=json.dumps(league_overview, indent=2),
        )

        raw = self.bedrock.reason(prompt, max_tokens=1024)
        proposals_data: dict[str, Any] = {}
        try:
            cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
            proposals_data = json.loads(cleaned)
        except Exception:
            proposals_data = {}

        decisions = []
        for proposal in proposals_data.get("proposals", []):
            d = Decision(
                league_id=league_id,
                type="trade_proposal",
                summary=(
                    f"Propose trading {', '.join(proposal.get('offer_player_names', []))} "
                    f"for {', '.join(proposal.get('target_player_names', []))}"
                ),
                reasoning=proposal.get("reasoning", ""),
                proposed_action=proposal,
            )
            decisions.append(d)

        return decisions
