from django.utils import timezone
from .models import AlertNotification


def create_critical_fraud_alert(transaction, risk_result):
    subject = f"CRITICAL FRAUD ALERT - Transaction {transaction.id}"

    message = (
        f"Guardian blocked a high-risk transaction.\n\n"
        f"Transaction ID: {transaction.id}\n"
        f"Customer MSISDN: {transaction.customer_msisdn}\n"
        f"Amount: {transaction.amount} {transaction.currency}\n"
        f"Type: {transaction.txn_type}\n"
        f"Source Account: {transaction.source_account}\n"
        f"Destination Account: {transaction.destination_account}\n"
        f"Risk Score: {risk_result.get('score')}\n"
        f"Risk Level: {risk_result.get('risk_level')}\n"
        f"Decision: {risk_result.get('decision')}\n\n"
        f"Explanation:\n{risk_result.get('explanation')}\n\n"
        f"Recommended Action:\n"
        f"Freeze transaction, escalate to fraud operations, and review customer/device identity."
    )

    notification = AlertNotification.objects.create(
        transaction=transaction,
        channel="email",
        status="sent",  # demo mode
        recipient="fraud-ops@guardian.local",
        subject=subject,
        message=message,
        response_payload={
            "demo": True,
            "note": "Email sending is simulated for hackathon demo.",
        },
        sent_at=timezone.now(),
    )

    return notification