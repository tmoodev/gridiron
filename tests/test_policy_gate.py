"""Tests for PolicyGate."""

from __future__ import annotations

from unittest.mock import MagicMock

from gridiron.policy.gate import PolicyGate

_YAML_CONFIG = {
    "policy": {
        "lineup_set": "propose",
        "waiver_claim_low_faab": "propose",
        "waiver_claim_high_faab": "propose",
        "player_drop_low_value": "propose",
        "player_drop_high_value": "propose",
        "trade_respond": "propose",
        "trade_send": "propose",
    },
    "thresholds": {
        "faab_high_pct": 15,
        "drop_value_high": 5,
    },
}


def make_gate(dynamo_item: dict | None = None) -> PolicyGate:
    dynamo = MagicMock()
    dynamo.get_item.return_value = dynamo_item
    return PolicyGate(dynamo=dynamo)


# ---------------------------------------------------------------------------
# Basic routing
# ---------------------------------------------------------------------------


def test_lineup_set_requires_approval() -> None:
    gate = make_gate(_YAML_CONFIG)
    d = gate.check("lineup_set")
    assert d.requires_approval is True
    assert d.mode == "propose"


def test_trade_respond_requires_approval() -> None:
    gate = make_gate(_YAML_CONFIG)
    d = gate.check("trade_respond")
    assert d.requires_approval is True


def test_trade_send_requires_approval() -> None:
    gate = make_gate(_YAML_CONFIG)
    d = gate.check("trade_send")
    assert d.requires_approval is True


# ---------------------------------------------------------------------------
# Waiver threshold routing
# ---------------------------------------------------------------------------


def test_waiver_claim_low_faab() -> None:
    gate = make_gate(_YAML_CONFIG)
    # $5 bid on $80 remaining = 6.25% < 15% threshold → low
    d = gate.check("waiver_claim", bid_amount=5, faab_remaining=80)
    assert d.action_type == "waiver_claim_low_faab"


def test_waiver_claim_high_faab() -> None:
    gate = make_gate(_YAML_CONFIG)
    # $15 bid on $80 remaining = 18.75% > 15% threshold → high
    d = gate.check("waiver_claim", bid_amount=15, faab_remaining=80)
    assert d.action_type == "waiver_claim_high_faab"


def test_waiver_claim_exactly_at_threshold_is_high() -> None:
    gate = make_gate(_YAML_CONFIG)
    # $12 bid on $80 remaining = 15.0% == threshold → high
    d = gate.check("waiver_claim", bid_amount=12, faab_remaining=80)
    assert d.action_type == "waiver_claim_high_faab"


def test_waiver_claim_zero_faab_remaining_is_low() -> None:
    gate = make_gate(_YAML_CONFIG)
    # faab_remaining=0 → division guard → low
    d = gate.check("waiver_claim", bid_amount=5, faab_remaining=0)
    assert d.action_type == "waiver_claim_low_faab"


# ---------------------------------------------------------------------------
# Drop threshold routing
# ---------------------------------------------------------------------------


def test_player_drop_low_value() -> None:
    gate = make_gate(_YAML_CONFIG)
    d = gate.check("player_drop", player_value=3)
    assert d.action_type == "player_drop_low_value"


def test_player_drop_high_value() -> None:
    gate = make_gate(_YAML_CONFIG)
    d = gate.check("player_drop", player_value=6)
    assert d.action_type == "player_drop_high_value"


# ---------------------------------------------------------------------------
# DynamoDB fallback to YAML
# ---------------------------------------------------------------------------


def test_dynamo_miss_falls_back_to_yaml() -> None:
    dynamo = MagicMock()
    dynamo.get_item.return_value = None  # DynamoDB miss
    gate = PolicyGate(dynamo=dynamo)
    d = gate.check("lineup_set")
    assert d.requires_approval is True


def test_no_dynamo_falls_back_to_yaml() -> None:
    gate = PolicyGate(dynamo=None)
    d = gate.check("lineup_set")
    assert d.requires_approval is True


def test_dynamo_exception_falls_back_to_yaml() -> None:
    dynamo = MagicMock()
    dynamo.get_item.side_effect = RuntimeError("DynamoDB unavailable")
    gate = PolicyGate(dynamo=dynamo)
    d = gate.check("lineup_set")
    assert d.requires_approval is True


# ---------------------------------------------------------------------------
# Unknown mode defaults to propose
# ---------------------------------------------------------------------------


def test_unknown_mode_defaults_to_propose() -> None:
    gate = make_gate({
        "policy": {"lineup_set": "totally_unknown_mode"},
        "thresholds": {},
    })
    d = gate.check("lineup_set")
    assert d.mode == "propose"
    assert d.requires_approval is True


# ---------------------------------------------------------------------------
# auto_email / auto_silent
# ---------------------------------------------------------------------------


def test_auto_email_does_not_require_approval() -> None:
    gate = make_gate({
        "policy": {"waiver_claim_low_faab": "auto_email"},
        "thresholds": {"faab_high_pct": 15, "drop_value_high": 5},
    })
    d = gate.check("waiver_claim", bid_amount=5, faab_remaining=80)
    assert d.requires_approval is False
    assert d.mode == "auto_email"


def test_auto_silent_does_not_require_approval() -> None:
    gate = make_gate({
        "policy": {"lineup_set": "auto_silent"},
        "thresholds": {},
    })
    d = gate.check("lineup_set")
    assert d.requires_approval is False
    assert d.mode == "auto_silent"
