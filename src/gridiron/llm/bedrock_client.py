"""Bedrock LLM client.

reason()    → Claude Sonnet (complex reasoning, valuation, decisions)
research()  → Grok via cross-region profile if available, else Claude
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import boto3
import structlog
import yaml

log = structlog.get_logger(__name__)

_CONFIG_PATH = Path(__file__).parents[4] / "config" / "models.yaml"


def _load_config() -> dict[str, Any]:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)  # type: ignore[no-any-return]


class BedrockClient:
    def __init__(self, region: str | None = None) -> None:
        cfg = _load_config()
        self._region = region or cfg.get("bedrock_region", "us-east-1")
        self._reasoning_model: str = cfg["reasoning_model"]
        self._research_model: str = cfg["research_model"]
        self._grok_candidate: str = cfg.get("grok_candidate_model", "")
        self._client = boto3.client("bedrock-runtime", region_name=self._region)
        self._research_model = self._resolve_research_model()

    def _resolve_research_model(self) -> str:
        """Check if Grok is available; fall back to Claude if not."""
        if not self._grok_candidate:
            return self._research_model

        try:
            # Probe with a minimal message to verify Grok availability
            self._invoke(self._grok_candidate, "ping", max_tokens=1)
            log.info("bedrock.grok_available", model=self._grok_candidate)
            return self._grok_candidate
        except Exception as exc:
            log.warning(
                "bedrock.grok_unavailable",
                model=self._grok_candidate,
                error=str(exc),
                fallback=self._reasoning_model,
            )
            return self._reasoning_model

    def _invoke(self, model_id: str, prompt: str, max_tokens: int = 4096) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = self._client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(resp["body"].read())
        content = result.get("content", [])
        if content and isinstance(content, list):
            return str(content[0].get("text", ""))
        return ""

    def reason(self, prompt: str, max_tokens: int = 4096) -> str:
        """Call Claude for complex reasoning tasks."""
        log.info("bedrock.reason", model=self._reasoning_model, prompt_len=len(prompt))
        return self._invoke(self._reasoning_model, prompt, max_tokens)

    def research(self, prompt: str, max_tokens: int = 4096) -> str:
        """Call research model (Grok if available, else Claude) for news synthesis."""
        log.info("bedrock.research", model=self._research_model, prompt_len=len(prompt))
        return self._invoke(self._research_model, prompt, max_tokens)
