from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.fraud_cases.models import FraudAlert


def run_aml_rules(transaction):
    score = 0
    reasons = []
    references = []

    rule_results = [
        check_one_to_many(transaction),
        check_many_to_one(transaction),
        check_transaction_velocity(transaction),
        check_high_value_transaction(transaction),
        check_dormant_account(transaction),
    ]

    for result in rule_results:
        if result["triggered"]:
            score += result["score"]
            reasons.append(result["reason"])
            references.append(result["reference"])

            FraudAlert.objects.create(
                transaction=transaction,
                rule_code=result["rule_code"],
                rule_name=result["rule_name"],
                severity=result["severity"],
                score=result["score"],
                reference=result["reference"],
                description=result["reason"],
                metadata=result["metadata"],
            )

    return {
        "score": score,
        "reasons": reasons,
        "references": references,
    }


def check_one_to_many(transaction):
    window_start = timezone.now() - timedelta(hours=24)

    if not transaction.source_account:
        return not_triggered("NFS_ONE_TO_MANY")

    unique_destinations = (
        Transaction.objects.filter(
            tenant=transaction.tenant,
            source_account=transaction.source_account,
            created_at__gte=window_start,
        )
        .exclude(destination_account__isnull=True)
        .values_list("destination_account", flat=True)
        .distinct()
    )

    count = unique_destinations.count()
    triggered = count >= 5
    reference = f"NFS-ONE-TO-MANY-{transaction.source_account}-{transaction.id}"

    return {
        "triggered": triggered,
        "rule_code": "NFS_ONE_TO_MANY",
        "rule_name": "One account sending to many accounts",
        "severity": "high",
        "score": 30 if triggered else 0,
        "reference": reference,
        "reason": f"One-to-many flow detected: {transaction.source_account} sent to {count} unique destination accounts within 24 hours.",
        "metadata": {
            "source_account": transaction.source_account,
            "unique_destination_count": count,
            "window_hours": 24,
        },
    }


def check_many_to_one(transaction):
    window_start = timezone.now() - timedelta(hours=24)

    if not transaction.destination_account:
        return not_triggered("NFS_MANY_TO_ONE")

    unique_sources = (
        Transaction.objects.filter(
            tenant=transaction.tenant,
            destination_account=transaction.destination_account,
            created_at__gte=window_start,
        )
        .exclude(source_account__isnull=True)
        .values_list("source_account", flat=True)
        .distinct()
    )

    count = unique_sources.count()
    triggered = count >= 5
    reference = f"NFS-MANY-TO-ONE-{transaction.destination_account}-{transaction.id}"

    return {
        "triggered": triggered,
        "rule_code": "NFS_MANY_TO_ONE",
        "rule_name": "Many accounts sending to one account",
        "severity": "high",
        "score": 30 if triggered else 0,
        "reference": reference,
        "reason": f"Many-to-one flow detected: {count} unique source accounts sent to {transaction.destination_account} within 24 hours.",
        "metadata": {
            "destination_account": transaction.destination_account,
            "unique_source_count": count,
            "window_hours": 24,
        },
    }


def check_transaction_velocity(transaction):
    window_start = timezone.now() - timedelta(hours=1)

    if not transaction.source_account:
        return not_triggered("VELOCITY_SPIKE")

    count = Transaction.objects.filter(
        tenant=transaction.tenant,
        source_account=transaction.source_account,
        created_at__gte=window_start,
    ).count()

    triggered = count >= 5
    reference = f"AML-VELOCITY-{transaction.source_account}-{transaction.id}"

    return {
        "triggered": triggered,
        "rule_code": "VELOCITY_SPIKE",
        "rule_name": "High transaction velocity",
        "severity": "medium",
        "score": 25 if triggered else 0,
        "reference": reference,
        "reason": f"Velocity spike detected: {count} transactions from {transaction.source_account} within 1 hour.",
        "metadata": {
            "source_account": transaction.source_account,
            "transaction_count": count,
            "window_hours": 1,
        },
    }


def check_high_value_transaction(transaction):
    triggered = transaction.amount >= Decimal("5000")
    reference = f"AML-HIGH-VALUE-{transaction.source_account or transaction.customer_msisdn}-{transaction.id}"

    return {
        "triggered": triggered,
        "rule_code": "HIGH_VALUE_TRANSACTION",
        "rule_name": "High-value transaction",
        "severity": "medium",
        "score": 20 if triggered else 0,
        "reference": reference,
        "reason": f"High-value transaction detected: {transaction.amount} {transaction.currency}.",
        "metadata": {
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "threshold": "5000",
        },
    }


def check_dormant_account(transaction):
    if not transaction.source_account:
        return not_triggered("DORMANT_ACCOUNT_ACTIVITY")

    previous_transaction = (
        Transaction.objects.filter(
            tenant=transaction.tenant,
            source_account=transaction.source_account,
        )
        .exclude(id=transaction.id)
        .order_by("-created_at")
        .first()
    )

    if previous_transaction is None:
        return not_triggered("DORMANT_ACCOUNT_ACTIVITY")

    days_since_last_txn = (transaction.created_at - previous_transaction.created_at).days
    triggered = days_since_last_txn >= 90
    reference = f"AML-DORMANT-{transaction.source_account}-{transaction.id}"

    return {
        "triggered": triggered,
        "rule_code": "DORMANT_ACCOUNT_ACTIVITY",
        "rule_name": "Dormant account activity",
        "severity": "high",
        "score": 40 if triggered else 0,
        "reference": reference,
        "reason": f"Dormant account activity detected: account had no transaction for {days_since_last_txn} days.",
        "metadata": {
            "source_account": transaction.source_account,
            "days_since_last_transaction": days_since_last_txn,
            "threshold_days": 90,
        },
    }


def not_triggered(rule_code):
    return {
        "triggered": False,
        "rule_code": rule_code,
        "rule_name": rule_code,
        "severity": "low",
        "score": 0,
        "reference": "",
        "reason": "",
        "metadata": {},
    }