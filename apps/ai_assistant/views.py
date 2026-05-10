from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.transactions.models import Transaction
from apps.fraud_cases.models import FraudAlert
from apps.telecom.models import TelecomCheck
from apps.risk.models import RiskAssessment


class AIInvestigatorView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

        risk = getattr(transaction, "risk_assessment", None)

        fraud_alerts = FraudAlert.objects.filter(transaction=transaction).order_by("-created_at")
        telecom_checks = TelecomCheck.objects.filter(transaction=transaction).order_by("-created_at")

        key_findings = []

        for check in telecom_checks:
            if check.score > 0:
                key_findings.append(
                    f"{check.check_type.replace('_', ' ').title()} returned {check.result} with score {check.score}."
                )

        for alert in fraud_alerts:
            key_findings.append(
                f"{alert.rule_name} triggered with severity {alert.severity} and score {alert.score}."
            )

        if not key_findings:
            key_findings.append("No major fraud indicators were detected.")

        recommended_action = "Allow transaction"
        if transaction.status == "blocked":
            recommended_action = "Block transaction and escalate to fraud operations immediately."
        elif transaction.status == "delayed":
            recommended_action = "Delay transaction and request manual review."
        elif transaction.status == "flagged":
            recommended_action = "Flag transaction for monitoring and investigator review."

        investigator_summary = {
            "transaction_id": str(transaction.id),
            "customer_msisdn": transaction.customer_msisdn,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "risk_score": transaction.risk_score,
            "risk_level": risk.risk_level if risk else "unknown",
            "decision": risk.decision if risk else "unknown",
            "summary": (
                f"Guardian assessed this {transaction.txn_type} transaction for "
                f"{transaction.amount} {transaction.currency}. The final decision was "
                f"{risk.decision if risk else transaction.status.upper()} with a risk score of "
                f"{transaction.risk_score}."
            ),
            "key_findings": key_findings,
            "recommended_action": recommended_action,
            "investigator_note": (
                "This explanation was generated from telecom intelligence, KYC signals, "
                "AML rules, NFS flow analysis, and transaction behavior."
            ),
        }

        return Response(investigator_summary)