import json
import math

from django.db.models import Count
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.transactions.models import Transaction
from apps.fraud_cases.models import FraudAlert
from apps.telecom.models import TelecomCheck
from apps.risk.models import RiskAssessment


class DashboardSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        total_transactions = Transaction.objects.count()

        status_counts = (
            Transaction.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        risk_counts = (
            RiskAssessment.objects.values("risk_level")
            .annotate(count=Count("id"))
            .order_by("risk_level")
        )

        top_rules = (
            FraudAlert.objects.values("rule_code", "rule_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        telecom_signals = (
            TelecomCheck.objects.values("check_type", "result")
            .annotate(count=Count("id"))
            .order_by("check_type")
        )

        recent_alerts = (
            FraudAlert.objects.select_related("transaction")
            .order_by("-created_at")[:10]
        )

        recent_transactions = (
            Transaction.objects.exclude(source_account__isnull=True)
            .exclude(destination_account__isnull=True)
            .exclude(source_account="")
            .exclude(destination_account="")
            .order_by("-created_at")[:20]
        )

        graph_data = build_graph_data(recent_transactions)

        return Response(
            {
                "total_transactions": total_transactions,
                "status_counts": list(status_counts),
                "risk_counts": list(risk_counts),
                "total_fraud_alerts": FraudAlert.objects.count(),
                "critical_alerts": FraudAlert.objects.filter(
                    severity="critical"
                ).count(),
                "high_alerts": FraudAlert.objects.filter(
                    severity="high"
                ).count(),
                "medium_alerts": FraudAlert.objects.filter(
                    severity="medium"
                ).count(),
                "top_rules": list(top_rules),
                "telecom_signals": list(telecom_signals),
                "recent_alerts": [
                    {
                        "reference": alert.reference,
                        "rule_code": alert.rule_code,
                        "rule_name": alert.rule_name,
                        "severity": alert.severity,
                        "score": alert.score,
                        "transaction_id": str(alert.transaction.id),
                        "amount": str(alert.transaction.amount),
                        "currency": alert.transaction.currency,
                        "status": alert.transaction.status,
                        "created_at": alert.created_at,
                    }
                    for alert in recent_alerts
                ],
                "graph_nodes": graph_data["nodes"],
                "graph_edges": graph_data["edges"],
            }
        )


class GuardianDashboardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        response = DashboardSummaryView().get(request)
        data = response.data

        status_counts = data.get("status_counts", [])
        risk_counts = data.get("risk_counts", [])
        top_rules = data.get("top_rules", [])

        data["chart_status_labels"] = json.dumps(
            [item["status"] for item in status_counts]
        )
        data["chart_status_values"] = json.dumps(
            [item["count"] for item in status_counts]
        )

        data["chart_risk_labels"] = json.dumps(
            [item["risk_level"] for item in risk_counts]
        )
        data["chart_risk_values"] = json.dumps(
            [item["count"] for item in risk_counts]
        )

        data["chart_rule_labels"] = json.dumps(
            [item["rule_code"] for item in top_rules]
        )
        data["chart_rule_values"] = json.dumps(
            [item["count"] for item in top_rules]
        )

        return render(request, "dashboard/guardian_dashboard.html", data)


def onboard_page(request):
    return render(request, "dashboard/onboard.html")


def fraud_portal_page(request):
    return render(request, "dashboard/fraud_dashboard.html")


def build_graph_data(transactions):
    accounts = []
    edges_raw = []

    for tx in transactions:
        source = tx.source_account
        destination = tx.destination_account

        if source not in accounts:
            accounts.append(source)

        if destination not in accounts:
            accounts.append(destination)

        edges_raw.append((source, destination))

    if not accounts:
        return {"nodes": [], "edges": []}

    nodes = []
    center_x = 50
    center_y = 50
    radius = 34

    visible_accounts = accounts[:12]

    for index, account in enumerate(visible_accounts):
        angle = (2 * math.pi * index) / max(len(visible_accounts), 1)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        is_source = any(edge[0] == account for edge in edges_raw)
        is_destination = any(edge[1] == account for edge in edges_raw)

        node_type = "source" if is_source else "destination"

        if is_source and is_destination:
            node_type = "source"

        nodes.append(
            {
                "id": account,
                "safe_id": safe_id(account),
                "label": account,
                "type": node_type,
                "x": round(x, 2),
                "y": round(y, 2),
            }
        )

    node_map = {node["id"]: node for node in nodes}
    edges = []

    for source, destination in edges_raw:
        if source not in node_map or destination not in node_map:
            continue

        source_node = node_map[source]
        dest_node = node_map[destination]

        x1 = source_node["x"] + 4
        y1 = source_node["y"] + 3
        x2 = dest_node["x"] + 4
        y2 = dest_node["y"] + 3

        dx = x2 - x1
        dy = y2 - y1

        length = math.sqrt(dx * dx + dy * dy)
        angle = math.degrees(math.atan2(dy, dx))

        edges.append(
            {
                "x": round(x1, 2),
                "y": round(y1, 2),
                "length": round(length, 2),
                "angle": round(angle, 2),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges[:20],
    }


def safe_id(value):
    return (
        str(value)
        .replace(" ", "-")
        .replace("_", "-")
        .replace(".", "-")
        .replace("/", "-")
    )