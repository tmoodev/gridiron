"""Base agent class and shared Decision model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import structlog
from pydantic import BaseModel, Field

from gridiron.db.dynamo import DynamoClient
from gridiron.llm.bedrock_client import BedrockClient
from gridiron.sleeper.client import SleeperClient
from gridiron.strategy import loader as _strategy_loader

log = structlog.get_logger(__name__)

DecisionType = Literal["lineup", "waiver", "trade_response", "trade_proposal", "research"]
DecisionStatus = Literal["pending", "approved", "rejected", "executed", "expired"]


class Decision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    league_id: str
    type: DecisionType
    summary: str
    reasoning: str
    proposed_action: dict[str, Any] = Field(default_factory=dict)
    status: DecisionStatus = "pending"
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    expires_at: str = Field(
        default_factory=lambda: (
            datetime.now(UTC) + timedelta(hours=72)
        ).isoformat()
    )
    strategy_docs_loaded: list[str] = Field(default_factory=list)
    strategy_doc_versions: dict[str, str] = Field(default_factory=dict)

    def pk(self) -> str:
        return f"FF#DECISION#{self.league_id}#{self.created_at}"

    def sk(self) -> str:
        return f"LOG#{self.decision_id}"

    def to_dynamo(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dynamo(cls, item: dict[str, Any]) -> Decision:
        return cls.model_validate(item)

    def is_expired(self) -> bool:
        return datetime.now(UTC) > datetime.fromisoformat(self.expires_at)


class BaseAgent:
    name: str = "base"

    def __init__(
        self,
        dynamo: DynamoClient,
        sleeper: SleeperClient,
        bedrock: BedrockClient,
    ) -> None:
        self.dynamo = dynamo
        self.sleeper = sleeper
        self.bedrock = bedrock
        self._current_strategy_versions: dict[str, str] = {}

    def _load_strategy(self, *doc_ids: str) -> str:
        """Load strategy docs (always prepends 00-principles). Returns concatenated content.

        Stores doc versions in self._current_strategy_versions for decision logging.
        """
        content = _strategy_loader.load(*doc_ids)
        self._current_strategy_versions = _strategy_loader.load_metadata(*doc_ids)
        log.debug(
            "agent.strategy_loaded",
            agent=self.name,
            docs=list(self._current_strategy_versions.keys()),
        )
        return content

    def _save_decision(self, decision: Decision) -> None:
        decision.strategy_docs_loaded = list(self._current_strategy_versions.keys())
        decision.strategy_doc_versions = dict(self._current_strategy_versions)
        self.dynamo.put_item(decision.pk(), decision.sk(), decision.to_dynamo())
        log.info(
            "agent.decision_saved",
            agent=self.name,
            type=decision.type,
            league_id=decision.league_id,
            decision_id=decision.decision_id,
            status=decision.status,
            strategy_docs=decision.strategy_docs_loaded,
        )

    def _get_league_config(self, league_id: str) -> dict[str, Any] | None:
        return self.dynamo.get_item(f"FF#LEAGUE#{league_id}", "CONFIG")

    async def run(self, league_id: str) -> list[Decision]:
        raise NotImplementedError
