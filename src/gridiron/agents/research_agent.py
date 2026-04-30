"""Research Agent — synthesizes player news and injury intel.

Runs for every player on Travis's rosters. Calls the research model
(Grok if available, else Claude) to produce structured intel summaries.
Writes FF#INTEL#{player_id}#{ts}#ITEM records — no approval needed.

Grounded in: 00-principles.md (always loaded).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import structlog

from gridiron.agents.base import BaseAgent, Decision

log = structlog.get_logger(__name__)

_RESEARCH_PROMPT_TEMPLATE = """{strategy}

---

You are a fantasy football analyst. Synthesize the following player information \
into a concise intel report. Apply the principles above when assessing fantasy \
relevance and confidence.

Player: {name} | Position: {position} | Team: {team} | Age: {age}

Provide:
1. Current injury/health status (1-2 sentences)
2. Role / usage outlook (1-2 sentences)
3. Fantasy relevance for the next 4 weeks (1-2 sentences)
4. A confidence rating: HIGH / MEDIUM / LOW

Be direct and specific. No hedging. Base analysis on what is known about this \
player as of your training data.

Respond as JSON:
{{"health": "...", "role": "...", "fantasy_outlook": "...", "confidence": "HIGH|MEDIUM|LOW"}}"""


class ResearchAgent(BaseAgent):
    name = "research"

    async def run(self, league_id: str) -> list[Decision]:
        """Research all players on Travis's roster for this league."""
        # Load strategy: principles only (no task-specific docs for research)
        strategy = self._load_strategy()

        rosters = self.sleeper.get_rosters(league_id)
        travis_roster = self._find_travis_roster(league_id, rosters)
        if not travis_roster:
            log.warning("research_agent.no_roster_found", league_id=league_id)
            return []

        all_players = self.sleeper.get_all_players()
        player_ids = (
            travis_roster.players
            + travis_roster.reserve
            + travis_roster.taxi
        )

        researched = 0
        for player_id in player_ids:
            player = all_players.get(player_id)
            if not player or not player.full_name:
                continue

            try:
                prompt = _RESEARCH_PROMPT_TEMPLATE.format(
                    strategy=strategy,
                    name=player.full_name,
                    position=player.position or "UNK",
                    team=player.team or "FA",
                    age=player.age or "N/A",
                )
                raw = self.bedrock.research(prompt, max_tokens=512)

                intel: dict[str, Any] = {}
                try:
                    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
                    intel = json.loads(cleaned)
                except Exception:
                    intel = {"raw": raw}

                now = datetime.now(UTC).isoformat()
                pk = f"FF#INTEL#{player_id}#{now}"
                self.dynamo.put_item(
                    pk,
                    "ITEM",
                    {
                        "player_id": player_id,
                        "player_name": player.full_name,
                        "position": player.position,
                        "team": player.team,
                        "league_id": league_id,
                        "intel": json.dumps(intel),
                        "created_at": now,
                        "strategy_docs_loaded": self._current_strategy_versions,
                    },
                )
                researched += 1
                log.info(
                    "research_agent.player_researched",
                    player=player.full_name,
                    confidence=intel.get("confidence", "?"),
                )
            except Exception as exc:
                log.error(
                    "research_agent.player_error",
                    player_id=player_id,
                    error=str(exc),
                )

        log.info("research_agent.done", league_id=league_id, researched=researched)
        return []  # Research produces intel records, not decisions requiring approval

    def _find_travis_roster(self, league_id: str, rosters: list[Any]) -> Any | None:
        """Find Travis's roster by checking DynamoDB league config for his user_id."""
        cfg = self._get_league_config(league_id)
        if not cfg:
            return None
        travis_user_id = cfg.get("travis_user_id")
        if not travis_user_id:
            log.warning("research_agent.travis_user_id_not_in_config", league_id=league_id)
            return rosters[0] if rosters else None
        for r in rosters:
            if r.owner_id == travis_user_id:
                return r
        return None
