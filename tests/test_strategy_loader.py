"""Tests for strategy corpus loader."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gridiron.strategy.loader import StrategyLoader, _parse_version

LOCAL_DIR = Path(__file__).parent.parent / "docs" / "strategy"


# ---------------------------------------------------------------------------
# _parse_version
# ---------------------------------------------------------------------------


def test_parse_version_standard() -> None:
    content = "# 00 — Gridiron Principles\n\n**Version:** 1.0\n\nSome content."
    assert _parse_version(content) == "1.0"


def test_parse_version_missing() -> None:
    assert _parse_version("# No version here\n\nContent.") == "unknown"


# ---------------------------------------------------------------------------
# Local fallback
# ---------------------------------------------------------------------------


class LocalLoader(StrategyLoader):
    """Loader subclass that always falls back to local (no S3 calls)."""

    def _fetch_s3(self, doc_id: str) -> str:
        raise RuntimeError("S3 unavailable")


def test_local_fallback_loads_file() -> None:
    loader = LocalLoader()
    content = loader.load()  # just 00-principles
    assert "Gridiron Principles" in content or len(content) > 100


def test_load_always_prepends_principles() -> None:
    loader = LocalLoader()
    content = loader.load("03-waiver-strategy")
    # Should have principles first
    assert content.index("00 —") < content.index("03 —")


def test_load_deduplicates_principles() -> None:
    loader = LocalLoader()
    content = loader.load("00-principles", "03-waiver-strategy")
    # 00-principles should appear only once
    assert content.count("# 00 —") == 1


def test_load_metadata_includes_principles() -> None:
    loader = LocalLoader()
    meta = loader.load_metadata("03-waiver-strategy")
    assert "00-principles" in meta
    assert "03-waiver-strategy" in meta
    assert meta["00-principles"] == "1.0"


def test_load_metadata_empty_args_returns_just_principles() -> None:
    loader = LocalLoader()
    meta = loader.load_metadata()
    assert list(meta.keys()) == ["00-principles"]


# ---------------------------------------------------------------------------
# TTL cache
# ---------------------------------------------------------------------------


def test_cache_hit() -> None:
    loader = LocalLoader()
    loader._cache["00-principles"] = ("cached content", time.time() + 3600)
    content = loader.load()
    assert "cached content" in content


def test_cache_miss_on_expiry() -> None:
    loader = LocalLoader()
    loader._cache["00-principles"] = ("stale content", time.time() - 1)
    content = loader.load()
    # Should re-fetch from local; "stale content" should not be present
    assert "stale content" not in content


def test_invalidate_single() -> None:
    loader = LocalLoader()
    loader._cache["00-principles"] = ("cached", time.time() + 3600)
    loader.invalidate("00-principles")
    assert "00-principles" not in loader._cache


def test_invalidate_all() -> None:
    loader = LocalLoader()
    loader._cache["00-principles"] = ("a", time.time() + 3600)
    loader._cache["03-waiver-strategy"] = ("b", time.time() + 3600)
    loader.invalidate()
    assert loader._cache == {}


# ---------------------------------------------------------------------------
# S3 path
# ---------------------------------------------------------------------------


def test_s3_fetch_uses_correct_key() -> None:
    loader = StrategyLoader()
    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"**Version:** 2.0\n\ncontent")
    }

    with patch("gridiron.strategy.loader.boto3") as mock_boto3:
        mock_boto3.client.return_value = mock_s3
        content = loader._fetch_s3("03-waiver-strategy")

    mock_s3.get_object.assert_called_once_with(
        Bucket="gridiron-strategy-docs",
        Key="strategy/03-waiver-strategy.md",
    )
    assert "Version" in content


# ---------------------------------------------------------------------------
# All 10 docs present locally
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("doc_id", [
    "00-principles",
    "01-valuation-philosophy",
    "02-roster-construction",
    "03-waiver-strategy",
    "04-trade-strategy",
    "05-lineup-strategy",
    "06-dynasty-rookie-draft",
    "07-keeper-selection",
    "08-in-season-management",
    "09-league-specific-notes",
])
def test_local_doc_exists_and_has_version(doc_id: str) -> None:
    path = LOCAL_DIR / f"{doc_id}.md"
    assert path.exists(), f"Missing: {path}"
    content = path.read_text()
    assert _parse_version(content) != "unknown", f"No **Version:** header in {doc_id}"
