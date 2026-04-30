"""Valuation Agent — compute league-adjusted player values.

Sources:
  - KeepTradeCut: dynasty 1QB + SuperFlex values
  - Sleeper projections: weekly/redraft scores
  - Claude (reasoning): keeper-cost-adjusted values, IDP-specific values

Writes FF#PLAYER#{player_id}#META with all three valuation views.
No approval needed — purely informational.

Grounded in:
  - 00-principles.md (always)
  - 01-valuation-philosophy.md (both leagues)
  - 06-dynasty-rookie-draft.md (dynasty only)
  - 07-keeper-selection.md (keeper/home league only)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import structlog

from gridiron.agents.base import BaseAgent, Decision
from gridiron.scrapers.ktc import KTCScraper

log = structlog.get_logger(__name__)

_KEEPER_LEAGUE_ID = "1183557197018804224"
_DYNASTY_LEAGUE_ID = "1331779473430810624"

_VALUATION_PROMPT_TEMPLATE = """{strategy}

---

You are a fantasy football valuation expert. Apply the valuation philosophy \
above when computing scores. Given the following player data, compute:

1. **keeper_value** (0-100): Value in a 12-team half-PPR IDP keeper league with 3 keepers.
   Weight: current NFL role (40%), age/trajectory (30%), IDP eligibility if applicable (20%), keeper scarcity (10%).
2. **dynasty_value** (0-100): Value in a 12-team SUPER_FLEX, full-PPR, TE-premium dynasty league.
   Weight: age/trajectory (40%), current role (30%), SUPER_FLEX QB premium for QBs (20%), TE premium bonus (10%).
3. **redraft_value** (0-100): Standard redraft value for the upcoming season.

Player data:
{player_json}

Respond as JSON only:
{{"keeper_value": <int>, "dynasty_value": <int>, "redraft_value": <int>, "reasoning": "<2 sentences>"}}"""

_IDP_PROMPT_TEMPLATE = """{strategy}

---

You are an IDP (Individual Defensive Player) fantasy expert. Apply the principles \
above when evaluating defensive players. Compute the IDP value for:

Player: {name} | Position: {position} | Team: {team} | Age: {age}

Scoring system:
- Solo tackle: 1pt | Assist tackle: 0.5pt | Sack: 2pt | INT: 4pt
- FF: 3pt | Safety: 2pt | Pass deflection: 1pt

Estimate:
1. **weekly_floor** (pts): Conservative weekly output
2. **weekly_ceiling** (pts): Upside weekly output
3. **idp_tier**: 1 (elite) to 5 (bench/waiver)

Respond as JSON:
{{"weekly_floor": <float>, "weekly_ceiling": <float>, "idp_tier": <int>, "notes": "<1 sentence>"}}"""


class ValuationAgent(BaseAgent):
    name = "valuation"

    async def run(self, league_id: str) -> list[Decision]:
        """Recompute valuations for all relevant players."""
        # Load strategy docs based on league format
        is_dynasty = (league_id == _DYNASTY_LEAGUE_ID)
        is_keeper = (league_id == _KEEPER_LEAGUE_ID)

        if is_dynasty:
            strategy = self._load_strategy("01-valuation-philosophy", "06-dynasty-rookie-draft")
        elif is_keeper:
            strategy = self._load_strategy("01-valuation-philosophy", "07-keeper-selection")
        else:
            strategy = self._load_strategy("01-valuation-philosophy")

        # Scrape KTC data
        with KTCScraper() as ktc:
            ktc_players = ktc.scrape()

        log.info("valuation_agent.ktc_loaded", count=len(ktc_players))

        ktc_by_name = {p.name.lower().strip(): p for p in ktc_players}
        all_players = self.sleeper.get_all_players()

        is_idp = is_keeper

        processed = 0
        for player_id, player in all_players.items():
            if not player.full_name or player.position not in (
                "QB", "RB", "WR", "TE", "K", "DL", "LB", "DB"
            ):
                continue

            if not is_idp and player.position in ("DL", "LB", "DB"):
                continue

            try:
                ktc = ktc_by_name.get((player.full_name or "").lower().strip())

                player_json = json.dumps({
                    "name": player.full_name,
                    "position": player.position,
                    "team": player.team or "FA",
                    "age": player.age,
                    "years_exp": player.years_exp,
                    "status": player.status,
                    "ktc_value_1qb": ktc.value_1qb if ktc else None,
                    "ktc_value_sf": ktc.value_sf if ktc else None,
                    "ktc_trend_1qb": ktc.trend_1qb if ktc else None,
                })

                prompt = _VALUATION_PROMPT_TEMPLATE.format(
                    strategy=strategy, player_json=player_json
                )
                raw = self.bedrock.reason(prompt, max_tokens=256)

                vals: dict[str, Any] = {}
                try:
                    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
                    vals = json.loads(cleaned)
                except Exception:
                    vals = {"raw": raw}

                idp_vals: dict[str, Any] = {}
                if is_idp and player.position in ("DL", "LB", "DB"):
                    idp_raw = self.bedrock.reason(
                        _IDP_PROMPT_TEMPLATE.format(
                            strategy=strategy,
                            name=player.full_name,
                            position=player.position,
                            team=player.team or "FA",
                            age=player.age or "N/A",
                        ),
                        max_tokens=256,
                    )
                    try:
                        cleaned = idp_raw.strip().removeprefix("```json").removesuffix("```").strip()
                        idp_vals = json.loads(cleaned)
                    except Exception:
                        idp_vals = {"raw": idp_raw}

                dynamo_item: dict[str, Any] = {
                    "player_id": player_id,
                    "player_name": player.full_name,
                    "position": player.position,
                    "team": player.team,
                    "age": player.age,
                    "years_exp": player.years_exp,
                    "updated_at": datetime.now(UTC).isoformat(),
                    "valuations": json.dumps({
                        "keeper": vals.get("keeper_value"),
                        "dynasty": vals.get("dynasty_value"),
                        "redraft": vals.get("redraft_value"),
                        "reasoning": vals.get("reasoning"),
                        "idp": idp_vals if idp_vals else None,
                    }),
                    "strategy_docs_loaded": list(self._current_strategy_versions.keys()),
                    "strategy_doc_versions": json.dumps(self._current_strategy_versions),
                }

                if ktc:
                    dynamo_item.update(ktc.to_dynamo())

                self.dynamo.put_item(
                    f"FF#PLAYER#{player_id}",
                    "META",
                    dynamo_item,
                )
                processed += 1

            except Exception as exc:
                log.error(
                    "valuation_agent.player_error",
                    player_id=player_id,
                    error=str(exc),
                )

        log.info("valuation_agent.done", league_id=league_id, processed=processed)
        return []
