"""Farmer profile extraction for "Claim What's Yours".

Calls the Anthropic Messages API directly over httpx (no SDK). Never logs
the user text or the extracted profile.
"""

import json
import logging
import os
import re
from typing import Callable, Optional

import httpx

logger = logging.getLogger(__name__)

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-haiku-4-5"
MAX_TOKENS = 512
MAX_ATTEMPTS = 2
TIMEOUT_SECONDS = 20.0

FALLBACK = {"error": "extraction_failed", "fallback": "manual_form"}

SYSTEM_PROMPT = (
    "Extract farmer profile fields from the user's text. Return JSON only, "
    "no other text, with exactly these keys: age, gender, occupation, "
    "land_acres, land_ownership, annual_income, category, district, "
    "has_bank_account, is_income_tax_payer. Use null for any value the user "
    "did not clearly state. Never guess income, land or category. Never output "
    "or ask for Aadhaar, bank account, or any ID number."
)

PROFILE_KEYS = (
    "age",
    "gender",
    "occupation",
    "land_acres",
    "land_ownership",
    "annual_income",
    "category",
    "district",
    "has_bank_account",
    "is_income_tax_payer",
)

NUMBER_KEYS = ("land_acres", "annual_income")
STRING_KEYS = ("gender", "occupation", "land_ownership", "category", "district")

_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


def _is_sensitive(key: str) -> bool:
    k = key.lower()
    if "aadhaar" in k or "ifsc" in k:
        return True
    if k == "has_bank_account":
        return False
    return "account" in k


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_profile(raw) -> Optional[dict]:
    """Return a validated profile dict (all PROFILE_KEYS present) or None if invalid."""
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    fence = _FENCE_RE.match(text)
    if fence:
        text = fence.group(1)
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None

    profile = {key: None for key in PROFILE_KEYS}
    for key in PROFILE_KEYS:
        if key not in data or _is_sensitive(key):
            continue
        value = data[key]

        if key == "age":
            if value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                return None
            profile[key] = value
        elif key in NUMBER_KEYS:
            if value is None:
                continue
            if not _is_number(value):
                return None
            profile[key] = value
        elif key == "is_income_tax_payer":
            if value is None:
                continue
            if not isinstance(value, bool):
                return None
            profile[key] = value
        elif key == "has_bank_account":
            # Spec: drop this field (leave it unset) if it is not a bool or null.
            if isinstance(value, bool):
                profile[key] = value
        elif key in STRING_KEYS:
            if value is None:
                continue
            if not isinstance(value, str):
                return None
            profile[key] = value

    profile["missing_fields"] = [key for key in PROFILE_KEYS if profile[key] is None]
    return profile


def _default_post(payload: dict) -> str:
    """POST the payload to the Anthropic Messages API and return the first text block."""
    headers = {
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    response = httpx.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()["content"][0]["text"]


def extract_profile(text: str, post: Optional[Callable[[dict], str]] = None) -> dict:
    """Extract a farmer profile from free text.

    `post` is an injectable callable post(payload) -> assistant text. When it is
    None, the real API is used, but only if ANTHROPIC_API_KEY is set.
    Returns the profile dict (with missing_fields), or FALLBACK on failure.
    """
    if post is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return dict(FALLBACK)
        post = _default_post

    payload = {
        "model": os.environ.get("ANTHROPIC_MODEL") or DEFAULT_MODEL,
        "max_tokens": MAX_TOKENS,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": text}],
    }

    for _ in range(MAX_ATTEMPTS):
        try:
            raw = post(payload)
        except Exception as exc:  # log class name only, never the text
            logger.warning("profile extraction call failed: %s", type(exc).__name__)
            continue
        profile = _parse_profile(raw)
        if profile is not None:
            return profile
        logger.warning("profile extraction returned an invalid response")

    return dict(FALLBACK)
