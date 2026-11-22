"""Deterministic eligibility rules engine.

No LLM, no network, no randomness. Scheme rules are data (data/schemes.json);
this module contains no scheme-specific logic.
"""
import logging

logger = logging.getLogger(__name__)

STATUS_ORDER = {"likely_eligible": 0, "maybe": 1, "not_eligible": 2}

OPERATORS = {
    "eq": lambda actual, expected: actual == expected,
    "neq": lambda actual, expected: actual != expected,
    "gt": lambda actual, expected: actual > expected,
    "gte": lambda actual, expected: actual >= expected,
    "lt": lambda actual, expected: actual < expected,
    "lte": lambda actual, expected: actual <= expected,
    "in": lambda actual, expected: actual in expected,
    "not_in": lambda actual, expected: actual not in expected,
    "exists": lambda actual, expected: actual is not None,
}


def apply_op(op, actual, expected):
    """Apply one rule operator. Raises ValueError for an unknown operator."""
    if op not in OPERATORS:
        raise ValueError(f"Unknown rule operator: {op}")
    return OPERATORS[op](actual, expected)


def evaluate(profile, scheme):
    """Evaluate every rule of one scheme against a profile.

    Returns {"scheme_id", "status", "matched_rules", "failed_rules", "unknown_rules"}.
    Each rule entry is {"id", "field", "reason"}.
    """
    matched, failed, unknown = [], [], []
    for rule in scheme["rules"]:
        entry = {"id": rule["id"], "field": rule["field"], "reason": rule["reason"]}
        op = rule["op"]
        if op not in OPERATORS:
            # Logged by operator name only; profile values are never logged.
            logger.warning("Unknown rule operator: %s", op)
            unknown.append(entry)
            continue
        actual = profile.get(rule["field"])
        if actual is None:
            unknown.append(entry)
        elif apply_op(op, actual, rule.get("value")):
            matched.append(entry)
        else:
            failed.append(entry)

    if failed:
        status = "not_eligible"
    elif unknown:
        status = "maybe"
    else:
        status = "likely_eligible"

    return {
        "scheme_id": scheme["id"],
        "status": status,
        "matched_rules": matched,
        "failed_rules": failed,
        "unknown_rules": unknown,
    }


def match_all(profile, schemes):
    """Evaluate all schemes. Sorted likely_eligible, maybe, not_eligible (stable)."""
    results = [evaluate(profile, scheme) for scheme in schemes]
    return sorted(results, key=lambda result: STATUS_ORDER[result["status"]])
