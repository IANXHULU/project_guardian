from .models import RiskAssessment
from apps.risk.aml_engine import run_aml_rules
from apps.cases.models import FraudCase
from apps.alerts.services import create_critical_fraud_alert
from apps.fraud_detection.services.decision_engine import (
    determine_transaction_action,
    determine_risk_level,
    map_decision_to_transaction_status,
)


def assess_transaction(transaction, telecom_data):
    """
    Assess a transaction using telecom intelligence + AML rules.

    Final flow:
    1. Collect fraud signals
    2. Calculate score
    3. Convert score into risk level and decision
    4. Persist transaction status/risk score
    5. Persist RiskAssessment
    6. Auto-create a fraud case and alert for blocked transactions
    """
    score = 0
    reasons = []
    references = []

    telecom_data = telecom_data or {}

    number_verification = telecom_data.get("number_verification", {}) or {}
    sim_swap = telecom_data.get("sim_swap", {}) or {}
    device_swap = telecom_data.get("device_swap", {}) or {}
    location_verification = telecom_data.get("location_verification", {}) or {}
    kyc_match = telecom_data.get("kyc_match", {}) or {}
    kyc_tenure = telecom_data.get("kyc_tenure", {}) or {}

    if number_verification.get("failed"):
        score += number_verification.get("score", 35)
        reasons.append("Number verification failed")
        references.append(number_verification.get("reference"))

    if sim_swap.get("recent"):
        score += sim_swap.get("score", 40)
        reasons.append("Recent SIM swap detected")
        references.append(sim_swap.get("reference"))

    if device_swap.get("swapped"):
        score += device_swap.get("score", 25)
        reasons.append("Device swap detected")
        references.append(device_swap.get("reference"))

    if location_verification.get("mismatch"):
        score += location_verification.get("score", 25)
        reasons.append("Location verification mismatch")
        references.append(location_verification.get("reference"))

    if kyc_match.get("failed"):
        score += kyc_match.get("score", 30)
        reasons.append("KYC match failed")
        references.append(kyc_match.get("reference"))

    if kyc_tenure.get("failed"):
        score += kyc_tenure.get("score", 25)
        reasons.append("Low KYC tenure")
        references.append(kyc_tenure.get("reference"))

    aml_result = run_aml_rules(transaction) or {}
    score += aml_result.get("score", 0)
    reasons.extend(aml_result.get("reasons", []))
    references.extend(aml_result.get("references", []))

    decision = determine_transaction_action(score)
    risk_level = determine_risk_level(score)
    status = map_decision_to_transaction_status(decision)

    explanation = "; ".join(reasons) if reasons else "No major fraud indicators detected"
    clean_references = [str(ref) for ref in references if ref]

    if clean_references:
        explanation = f"{explanation}. References: {', '.join(clean_references)}"

    transaction.status = status
    transaction.risk_score = score
    transaction.save(update_fields=["status", "risk_score"])

    assessment, _ = RiskAssessment.objects.update_or_create(
        transaction=transaction,
        defaults={
            "total_score": score,
            "risk_level": risk_level,
            "decision": decision,
            "explanation": explanation,
        },
    )

    risk_result = {
        "assessment": assessment,
        "score": score,
        "risk_level": risk_level,
        "decision": decision,
        "status": status,
        "explanation": explanation,
        "references": clean_references,
    }

    if decision == "BLOCK":
        FraudCase.objects.get_or_create(
            transaction=transaction,
            defaults={
                "title": f"Critical Fraud Investigation - {transaction.id}",
                "description": (
                    "Guardian automatically created this case after detecting "
                    f"critical fraud signals for transaction {transaction.id}.\n\n"
                    f"Risk Score: {score}\n"
                    f"Risk Level: {risk_level}\n"
                    f"Decision: {decision}\n"
                    f"Explanation: {explanation}"
                ),
                "priority": "critical" if risk_level == "critical" else "high",
                "status": "open",
            },
        )

        create_critical_fraud_alert(
            transaction=transaction,
            risk_result=risk_result,
        )

    return risk_result
