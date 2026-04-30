"""SES email sender + HMAC approval token system.

- Sender: gridiron@datatrav.com (SES IAM role on EC2, no SMTP creds)
- Recipient: travis@datatrav.com
- Tokens: HMAC-SHA256, 72h TTL, single-use
- Templates: Jinja2 HTML
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from pathlib import Path
from typing import Any

import boto3
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from gridiron.agents.base import Decision

log = structlog.get_logger(__name__)

SENDER = "gridiron@datatrav.com"
RECIPIENT = "travis@datatrav.com"
REGION = "us-east-1"
TOKEN_TTL_SECONDS = 72 * 3600  # 72 hours

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def _get_hmac_key() -> bytes:
    """Fetch HMAC signing key from Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=REGION)
    secret = client.get_secret_value(SecretId="digitalmoore/gridiron/hmac-key")
    return secret["SecretString"].encode()


def generate_token(decision_id: str, action: str) -> str:
    """Generate a single-use HMAC token for approve/reject actions.

    Format: {expiry}:{decision_id}:{action}:{hmac_hex}
    """
    expiry = int(time.time()) + TOKEN_TTL_SECONDS
    key = _get_hmac_key()
    message = f"{expiry}:{decision_id}:{action}".encode()
    sig = hmac.new(key, message, hashlib.sha256).hexdigest()
    return f"{expiry}:{decision_id}:{action}:{sig}"


def verify_token(token: str) -> tuple[str, str] | None:
    """Verify token. Returns (decision_id, action) or None if invalid/expired."""
    try:
        parts = token.split(":", 3)
        if len(parts) != 4:
            return None
        expiry_str, decision_id, action, provided_sig = parts
        expiry = int(expiry_str)
        if time.time() > expiry:
            log.warning("ses.token_expired", decision_id=decision_id)
            return None
        key = _get_hmac_key()
        message = f"{expiry}:{decision_id}:{action}".encode()
        expected_sig = hmac.new(key, message, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, provided_sig):
            log.warning("ses.token_invalid_sig", decision_id=decision_id)
            return None
        return decision_id, action
    except Exception as exc:
        log.error("ses.token_verify_error", error=str(exc))
        return None


def send_decision_email(decision: Decision, base_url: str = "https://gridiron.datatrav.net") -> None:
    """Send approval/rejection email for a pending decision."""
    approve_token = generate_token(decision.decision_id, "approve")
    reject_token = generate_token(decision.decision_id, "reject")

    approve_url = f"{base_url}/api/action?token={approve_token}"
    reject_url = f"{base_url}/api/action?token={reject_token}"

    subject = f"[Gridiron] {decision.type.replace('_', ' ').title()}: {decision.summary[:60]}"

    # Render HTML template
    try:
        template = _jinja_env.get_template("decision_email.html")
        html_body = template.render(
            decision=decision,
            approve_url=approve_url,
            reject_url=reject_url,
        )
    except Exception:
        # Fallback to plain text if template missing
        html_body = _plain_fallback(decision, approve_url, reject_url)

    ses = boto3.client("ses", region_name=REGION)
    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [RECIPIENT]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Html": {"Data": html_body, "Charset": "UTF-8"},
                "Text": {
                    "Data": _plain_text(decision, approve_url, reject_url),
                    "Charset": "UTF-8",
                },
            },
        },
    )
    log.info(
        "ses.email_sent",
        decision_id=decision.decision_id,
        type=decision.type,
        league_id=decision.league_id,
    )


def _plain_text(decision: Decision, approve_url: str, reject_url: str) -> str:
    return (
        f"Gridiron Decision: {decision.summary}\n\n"
        f"Type: {decision.type}\n"
        f"League: {decision.league_id}\n\n"
        f"Reasoning:\n{decision.reasoning}\n\n"
        f"Action:\n{json.dumps(decision.proposed_action, indent=2)}\n\n"
        f"APPROVE: {approve_url}\n"
        f"REJECT:  {reject_url}\n\n"
        f"This link expires in 72 hours."
    )


def _plain_fallback(decision: Decision, approve_url: str, reject_url: str) -> str:
    return f"""<html><body style="font-family:sans-serif;max-width:600px;margin:40px auto">
<h2 style="color:#16a34a">Gridiron — {decision.type.replace('_',' ').title()}</h2>
<p><strong>{decision.summary}</strong></p>
<p style="color:#555">{decision.reasoning}</p>
<pre style="background:#f3f4f6;padding:12px;border-radius:6px;font-size:12px">{json.dumps(decision.proposed_action, indent=2)}</pre>
<div style="margin:24px 0">
  <a href="{approve_url}" style="background:#16a34a;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;margin-right:12px">Approve</a>
  <a href="{reject_url}" style="background:#dc2626;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none">Reject</a>
</div>
<p style="color:#9ca3af;font-size:12px">Expires 72 hours from send. Single-use.</p>
</body></html>"""
