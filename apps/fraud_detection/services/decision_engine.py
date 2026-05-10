"""
Guardian transaction decision engine.

This module converts a final numeric risk score into a business decision.
Keep this file small and deterministic so the thresholds are easy to audit.
"""


def determine_transaction_action(risk_score: int) -> str:
    """
    Return the final transaction decision for a given risk score.

    Decisions:
    - APPROVE: transaction can continue
    - HOLD: transaction should be held/flagged for manual review
    - BLOCK: transaction should be blocked immediately
    """
    score = int(risk_score or 0)

    if score >= 70:
        return "BLOCK"

    if score >= 40:
        return "HOLD"

    return "APPROVE"


def map_decision_to_transaction_status(decision: str) -> str:
    """
    Map business decision values to Transaction.status choices.
    """
    return {
        "APPROVE": "approved",
        "HOLD": "flagged",
        "BLOCK": "blocked",
    }.get(decision, "pending")


def determine_risk_level(risk_score: int) -> str:
    """
    Convert the numeric score into a readable risk level.
    """
    score = int(risk_score or 0)

    if score >= 90:
        return "critical"

    if score >= 70:
        return "high"

    if score >= 40:
        return "medium"

    return "low"
