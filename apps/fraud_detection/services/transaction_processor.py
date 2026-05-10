"""
Compatibility wrapper for fraud transaction processing.

The real transaction ingestion flow lives in apps.transactions.
This wrapper exists only for callers that explicitly use the fraud_detection service layer.
"""

from apps.telecom.services import run_telecom_checks
from apps.risk.engine import assess_transaction


def process_transaction(transaction):
    telecom_data = run_telecom_checks(transaction)
    risk_result = assess_transaction(transaction, telecom_data)

    return {
        "transaction_id": str(transaction.id),
        "status": risk_result["status"],
        "risk_score": risk_result["score"],
        "risk_level": risk_result["risk_level"],
        "decision": risk_result["decision"],
        "explanation": risk_result["explanation"],
        "references": risk_result["references"],
        "telecom_checks": telecom_data,
    }
