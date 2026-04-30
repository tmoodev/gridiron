"""Policy gate — determines approval mode for each action type.

Reads live config from DynamoDB (FF#CONFIG#POLICY); falls back to
config/policy.yaml on cold start or DynamoDB miss.

Usage:
    gate = PolicyGate(dynamo=dynamo_client)
    decision = gate.check("waiver_claim_low_faab", bid_amount=5, faab_remaining=80)
    if decision.requires_approval:
        # propose to Travis before acting
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
import yaml

if TYPE_CHECKING:
    from gridiron.db.dynamo import DynamoClient

log = structlog.get_logger(__name__)

_POLICY_YAML = Path(__file__).parent.parent.parent.parent / "config" / "policy.yaml"

_VALID_MODES = frozenset({"propose", "auto_email", "auto_silent"})

PolicyMode = str  # "propose" | "auto_email" | "auto_silent"


@dataclass
class PolicyDecision:
    action_type: str
    mode: PolicyMode
    requires_approval: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class PolicyGate:
    """Checks an action type against the active policy config."""

    def __init__(self, dynamo: DynamoClient | None = None) -> None:
        self._dynamo = dynamo

    def check(self, action_type: str, **kwargs: Any) -> PolicyDecision:
        """Return a PolicyDecision for the given action_type and context."""
        config = self._get_config()
        policy = config.get("policy", {})
        thresholds = config.get("thresholds", {})

        # Resolve the bucket (e.g. waiver_claim_low_faab vs high_faab)
        resolved_type = self._resolve_type(action_type, thresholds, kwargs)
        mode = policy.get(resolved_type, "propose")
        if mode not in _VALID_MODES:
            log.warning("policy_gate.unknown_mode", mode=mode, action_type=resolved_type)
            mode = "propose"

        return PolicyDecision(
            action_type=resolved_type,
            mode=mode,
            requires_approval=(mode == "propose"),
            metadata={"thresholds": thresholds, "kwargs": kwargs},
        )

    def get_config(self) -> dict[str, Any]:
        return self._get_config()

    def set_config(self, patch: dict[str, Any]) -> None:
        """Persist a policy patch to DynamoDB."""
        if not self._dynamo:
            raise RuntimeError("DynamoDB not configured; cannot persist policy changes")
        self._dynamo.put_item("FF#CONFIG#POLICY", "CONFIG", patch)
        log.info("policy_gate.config_updated", patch=json.dumps(patch)[:200])

    # ------------------------------------------------------------------

    def _get_config(self) -> dict[str, Any]:
        if self._dynamo:
            try:
                item = self._dynamo.get_item("FF#CONFIG#POLICY", "CONFIG")
                if item:
                    return item
            except Exception as exc:
                log.warning("policy_gate.dynamo_miss", error=str(exc))
        return self._load_yaml()

    @staticmethod
    def _load_yaml() -> dict[str, Any]:
        try:
            with open(_POLICY_YAML) as f:
                return yaml.safe_load(f) or {}
        except Exception as exc:
            log.error("policy_gate.yaml_load_error", error=str(exc))
            return {}

    @staticmethod
    def _resolve_type(
        action_type: str,
        thresholds: dict[str, Any],
        kwargs: dict[str, Any],
    ) -> str:
        """Map generic action types to bucketed keys using threshold context."""
        if action_type == "waiver_claim":
            faab_high_pct = float(thresholds.get("faab_high_pct", 15))
            bid_amount = float(kwargs.get("bid_amount", 0))
            faab_remaining = float(kwargs.get("faab_remaining", 80))
            if faab_remaining > 0 and (bid_amount / faab_remaining * 100) >= faab_high_pct:
                return "waiver_claim_high_faab"
            return "waiver_claim_low_faab"

        if action_type == "player_drop":
            drop_value_high = float(thresholds.get("drop_value_high", 5))
            player_value = float(kwargs.get("player_value", 0))
            if player_value >= drop_value_high:
                return "player_drop_high_value"
            return "player_drop_low_value"

        return action_type
