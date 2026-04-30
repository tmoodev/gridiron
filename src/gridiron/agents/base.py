"""Base agent class and shared Decision model."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import structlog
from pydantic import BaseModel, Field

from gridiron.db.dynamo import DynamoClient
from gridiron.llm.bedrock_client import BedrockClient
from gridiron.sleeper.client import SleeperClient

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
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    expires_at: str = Field(
        default_factory=lambda: (
            datetime.now(timezone.utc) + timedelta(hours=72)
        ).isoformat()
    )

    def pk(self) -> str:
        return f"FF#DECISION#{self.league_id}#{self.created_at}"

    def sk(self) -> str:
        return f"LOG#{self.decision_id}"

    def to_dynamo(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dynamo(cls, item: dict[str, Any]) -> "Decision":
        return cls.model_validate(item)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > datetime.fromisoformat(self.expires_at)


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

    def _save_decision(self, decision: Decision) -> None:
        self.dynamo.put_item(decision.pk(), decision.sk(), decision.to_dynamo())
        log.info(
            "agent.decision_saved",
            agent=self.name,
            type=decision.type,
            league_id=decision.league_id,
            decision_id=decision.decision_id,
            status=decision.status,
        )

    def _get_league_config(self, league_id: str) -> dict[str, Any] | None:
        return self.dynamo.get_item(f"FF#LEAGUE#{league_id}", "CONFIG")

    async def run(self, league_id: str) -> list[Decision]:
        raise NotImplementedError
