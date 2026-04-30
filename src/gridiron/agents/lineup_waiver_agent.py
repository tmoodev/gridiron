"""Lineup & Waiver Agent — optimize lineup and propose FAAB bids.

Proposes:
  1. Optimal lineup for the current week (starter slots)
  2. Waiver/FAAB additions worth bidding on

Both proposals land as FF#DECISION# records with status="pending".
An approval email is sent for each. Travis approves/rejects; Phase 3
actuator executes approved decisions via Playwright.

Grounded in:
  - 00-principles.md (always)
  - 02-roster-construction.md
  - 03-waiver-strategy.md
  - 05-lineup-strategy.md
  - 08-in-season-management.md
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from gridiron.agents.base import BaseAgent, Decision

log = structlog.get_logger(__name__)

_LINEUP_PROMPT_TEMPLATE = """{strategy}

---

You are an expert fantasy football lineup optimizer. Apply the lineup strategy \
and principles above when selecting starters.

League format: {format}
Scoring: {scoring}
Roster positions: {positions}
Week: {week}

My current roster (player_id → name, position, team, projected_points):
{roster_json}

Propose the optimal starting lineup. For each slot, pick the best available player.
Consider: matchups, injury status, bye weeks, and projected points.

Respond as JSON:
{{
  "starters": {{"QB": "<player_id>", "RB1": "<player_id>", ...}},
  "reasoning": "<2-3 sentences explaining key decisions>",
  "confidence": "HIGH|MEDIUM|LOW",
  "sit_start_highlights": ["<player>: start because...", "<player>: sit because..."]
}}"""

_WAIVER_PROMPT_TEMPLATE = """{strategy}

---

You are an expert fantasy football waiver wire analyst. Apply the waiver strategy \
and principles above when evaluating targets and structuring bids.

League: {format} | Scoring: {scoring} | FAAB remaining: ${faab_remaining}
Week: {week}

My roster:
{roster_json}

Available free agents (top targets by position, with projected points):
{free_agents_json}

Propose up to 3 FAAB bids. For each: player to add, bid amount, player to drop \
(if needed), and reasoning. Prioritize by need and value relative to cost. \
Be aggressive for high-upside players but respect the FAAB principles above.

Respond as JSON:
{{
  "bids": [
    {{
      "add_player_id": "<id>",
      "add_player_name": "<name>",
      "drop_player_id": "<id or null>",
      "drop_player_name": "<name or null>",
      "bid_amount": <int>,
      "reasoning": "<1 sentence>"
    }}
  ],
  "total_faab_used": <int>,
  "reasoning": "<overall 1-2 sentence strategy>"
}}"""


class LineupWaiverAgent(BaseAgent):
    name = "lineup_waiver"

    async def run(self, league_id: str, week: int = 1) -> list[Decision]:
        decisions: list[Decision] = []

        # Load strategy docs for lineup/waiver decisions
        strategy = self._load_strategy(
            "02-roster-construction",
            "03-waiver-strategy",
            "05-lineup-strategy",
            "08-in-season-management",
        )

        cfg = self._get_league_config(league_id)
        if not cfg:
            log.warning("lineup_waiver_agent.no_config", league_id=league_id)
            return []

        rosters = self.sleeper.get_rosters(league_id)
        travis_user_id = cfg.get("travis_user_id")
        travis_roster = next(
            (r for r in rosters if r.owner_id == travis_user_id),
            rosters[0] if rosters else None,
        )
        if not travis_roster:
            return []

        all_players = self.sleeper.get_all_players()

        roster_data = self._build_roster_context(travis_roster.players, all_players)

        league_format = cfg.get("format", "unknown")
        scoring = cfg.get("scoring", "half_ppr")
        positions = json.loads(cfg.get("roster_slots", "{}"))
        faab_remaining = cfg.get("faab_remaining_2025", cfg.get("faab_budget", 80))

        # --- Lineup proposal ---
        try:
            prompt = _LINEUP_PROMPT_TEMPLATE.format(
                strategy=strategy,
                format=league_format,
                scoring=scoring,
                positions=json.dumps(positions),
                week=week,
                roster_json=json.dumps(roster_data, indent=2),
            )
            raw = self.bedrock.reason(prompt, max_tokens=1024)
            lineup_proposal = self._parse_json(raw)

            decision = Decision(
                league_id=league_id,
                type="lineup",
                summary=f"Week {week} lineup proposal — {lineup_proposal.get('confidence', '?')} confidence",
                reasoning=lineup_proposal.get("reasoning", raw[:500]),
                proposed_action={
                    "week": week,
                    "starters": lineup_proposal.get("starters", {}),
                    "highlights": lineup_proposal.get("sit_start_highlights", []),
                },
            )
            self._save_decision(decision)
            decisions.append(decision)
            log.info("lineup_waiver_agent.lineup_proposed", league_id=league_id, week=week)
        except Exception as exc:
            log.error("lineup_waiver_agent.lineup_error", league_id=league_id, error=str(exc))

        # --- Waiver proposal ---
        try:
            all_rostered = {p for r in rosters for p in r.players + r.reserve + r.taxi}
            free_agents = [
                p for pid, p in all_players.items()
                if pid not in all_rostered
                and p.position in ("QB", "RB", "WR", "TE", "K", "DL", "LB", "DB")
                and p.full_name
            ]
            free_agents.sort(key=lambda p: p.search_rank or 9999)
            fa_data = [
                {
                    "player_id": p.player_id,
                    "name": p.full_name,
                    "position": p.position,
                    "team": p.team,
                    "status": p.status,
                }
                for p in free_agents[:30]
            ]

            prompt = _WAIVER_PROMPT_TEMPLATE.format(
                strategy=strategy,
                format=league_format,
                scoring=scoring,
                faab_remaining=faab_remaining,
                week=week,
                roster_json=json.dumps(roster_data, indent=2),
                free_agents_json=json.dumps(fa_data, indent=2),
            )
            raw = self.bedrock.reason(prompt, max_tokens=1024)
            waiver_proposal = self._parse_json(raw)

            bids = waiver_proposal.get("bids", [])
            if bids:
                decision = Decision(
                    league_id=league_id,
                    type="waiver",
                    summary=f"Week {week} waiver proposals — {len(bids)} bid(s), ${waiver_proposal.get('total_faab_used', 0)} FAAB",
                    reasoning=waiver_proposal.get("reasoning", raw[:500]),
                    proposed_action={
                        "week": week,
                        "bids": bids,
                        "total_faab_used": waiver_proposal.get("total_faab_used", 0),
                    },
                )
                self._save_decision(decision)
                decisions.append(decision)
                log.info(
                    "lineup_waiver_agent.waiver_proposed",
                    league_id=league_id,
                    week=week,
                    bids=len(bids),
                )
        except Exception as exc:
            log.error("lineup_waiver_agent.waiver_error", league_id=league_id, error=str(exc))

        return decisions

    def _build_roster_context(
        self, player_ids: list[str], all_players: dict[str, Any]
    ) -> list[dict[str, Any]]:
        result = []
        for pid in player_ids:
            p = all_players.get(pid)
            if p:
                result.append({
                    "player_id": pid,
                    "name": p.full_name,
                    "position": p.position,
                    "team": p.team,
                    "injury_status": p.injury_status,
                    "status": p.status,
                })
        return result

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        try:
            cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
            result: dict[str, Any] = json.loads(cleaned)
            return result
        except Exception:
            return {"raw": raw}
