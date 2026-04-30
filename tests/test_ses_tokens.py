"""Unit tests for SES HMAC token generation and verification."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from gridiron.email.ses import generate_token, verify_token


_FAKE_KEY = "deadbeefdeadbeefdeadbeefdeadbeef"


def _mock_get_key(monkeypatch: object) -> None:
    """Patch _get_hmac_key to return a fixed test key."""
    with patch("gridiron.email.ses._get_hmac_key", return_value=_FAKE_KEY.encode()):
        pass


@patch("gridiron.email.ses._get_hmac_key", return_value=_FAKE_KEY.encode())
def test_generate_and_verify(mock_key: MagicMock) -> None:
    token = generate_token("decision-abc", "approve")
    result = verify_token(token)
    assert result is not None
    decision_id, action = result
    assert decision_id == "decision-abc"
    assert action == "approve"


@patch("gridiron.email.ses._get_hmac_key", return_value=_FAKE_KEY.encode())
def test_reject_action(mock_key: MagicMock) -> None:
    token = generate_token("decision-xyz", "reject")
    result = verify_token(token)
    assert result is not None
    _, action = result
    assert action == "reject"


@patch("gridiron.email.ses._get_hmac_key", return_value=_FAKE_KEY.encode())
def test_tampered_token_rejected(mock_key: MagicMock) -> None:
    token = generate_token("decision-123", "approve")
    # Tamper with the signature
    parts = token.rsplit(":", 1)
    tampered = parts[0] + ":deadbeef"
    assert verify_token(tampered) is None


@patch("gridiron.email.ses._get_hmac_key", return_value=_FAKE_KEY.encode())
@patch("gridiron.email.ses.time")
def test_expired_token_rejected(mock_time: MagicMock, mock_key: MagicMock) -> None:
    # Generate token "in the past" by setting time.time() to past value
    mock_time.time.return_value = time.time() - (73 * 3600)  # 73 hours ago
    token = generate_token("decision-old", "approve")
    # Now restore real time for verification
    mock_time.time.return_value = time.time()
    result = verify_token(token)
    assert result is None


@patch("gridiron.email.ses._get_hmac_key", return_value=_FAKE_KEY.encode())
def test_malformed_token_rejected(mock_key: MagicMock) -> None:
    assert verify_token("not-a-valid-token") is None
    assert verify_token("a:b:c") is None  # too few parts
    assert verify_token("") is None
