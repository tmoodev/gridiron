"""Strategy corpus loader with S3 sync and in-memory TTL cache.

Usage:
    from gridiron.strategy import loader

    content = loader.load("03-waiver-strategy", "09-league-specific-notes")
    # → 00-principles content + 03 content + 09 content (always prepends 00)

    meta = loader.load_metadata("03-waiver-strategy")
    # → {"00-principles": "1.0", "03-waiver-strategy": "1.0"}
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

import boto3
import structlog
import yaml

log = structlog.get_logger(__name__)

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "models.yaml"
_LOCAL_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "strategy"

_TTL = 3600  # 1 hour


def _load_yaml_config() -> dict[str, Any]:
    try:
        with open(_CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


_CONFIG = _load_yaml_config()
_BUCKET: str = _CONFIG.get("strategy_bucket", "gridiron-strategy-docs")
_PREFIX: str = _CONFIG.get("strategy_prefix", "strategy/")


class StrategyLoader:
    """Loads strategy docs from S3 with 1-hour TTL per doc; falls back to local."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[str, float]] = {}

    def load(self, *doc_ids: str) -> str:
        """Return concatenated strategy content, always prepending 00-principles."""
        all_ids = _dedup_with_principles(doc_ids)
        parts = [self._load_doc(doc_id) for doc_id in all_ids]
        return "\n\n".join(parts)

    def load_metadata(self, *doc_ids: str) -> dict[str, str]:
        """Return {doc_id: version_string} for all docs that would be loaded."""
        all_ids = _dedup_with_principles(doc_ids)
        return {doc_id: _parse_version(self._load_doc(doc_id)) for doc_id in all_ids}

    def _load_doc(self, doc_id: str) -> str:
        cached_content, expires = self._cache.get(doc_id, ("", 0.0))
        if cached_content and time.time() < expires:
            return cached_content

        content = self._fetch(doc_id)
        self._cache[doc_id] = (content, time.time() + _TTL)
        return content

    def _fetch(self, doc_id: str) -> str:
        try:
            return self._fetch_s3(doc_id)
        except Exception as exc:
            log.warning("strategy_loader.s3_miss", doc_id=doc_id, error=str(exc))
            return self._fetch_local(doc_id)

    def _fetch_s3(self, doc_id: str) -> str:
        s3 = boto3.client("s3")
        key = f"{_PREFIX}{doc_id}.md"
        resp = s3.get_object(Bucket=_BUCKET, Key=key)
        content: str = resp["Body"].read().decode("utf-8")
        log.debug("strategy_loader.s3_hit", doc_id=doc_id)
        return content

    def _fetch_local(self, doc_id: str) -> str:
        path = _LOCAL_DIR / f"{doc_id}.md"
        log.info("strategy_loader.local_fallback", doc_id=doc_id, path=str(path))
        return path.read_text(encoding="utf-8")

    def invalidate(self, doc_id: str | None = None) -> None:
        """Clear one or all cached docs (useful for testing)."""
        if doc_id:
            self._cache.pop(doc_id, None)
        else:
            self._cache.clear()


def _dedup_with_principles(doc_ids: tuple[str, ...]) -> list[str]:
    """Return [00-principles] + doc_ids, deduping 00-principles if already present."""
    result = ["00-principles"]
    for d in doc_ids:
        if d != "00-principles":
            result.append(d)
    return result


_VERSION_RE = re.compile(r"\*\*Version:\*\*\s*(.+)")


def _parse_version(content: str) -> str:
    m = _VERSION_RE.search(content)
    return m.group(1).strip() if m else "unknown"
