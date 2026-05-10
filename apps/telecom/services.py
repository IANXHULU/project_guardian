from .models import TelecomCheck


def save_check(
    transaction,
    check_type,
    provider_response,
    failed_result,
    failed_key,
    passed_key,
    reference_prefix,
):
    """
    Normalizes and saves provider-style telecom checks such as KYC Match and KYC Tenure.
    """

    failed = bool(provider_response.get("failed", False))
    score = int(provider_response.get("score", 0))
    reference = f"{reference_prefix}-{transaction.customer_msisdn}-{transaction.id}"

    TelecomCheck.objects.create(
        transaction=transaction,
        check_type=check_type,
        provider="CAMARA_MOCK",
        result=failed_result if failed else passed_key,
        score=score,
        reference=reference,
        response_payload={
            **provider_response,
            "reference": reference,
        },
    )

    return {
        failed_key: failed,
        "failed": failed,
        "score": score,
        "reference": reference,
    }


def mock_kyc_match(transaction):
    failed = transaction.customer_msisdn.endswith("777")
    return {
        "failed": failed,
        "matched": not failed,
        "score": 35 if failed else 0,
        "msisdn": transaction.customer_msisdn,
    }


def mock_kyc_tenure(transaction):
    low_tenure = transaction.customer_msisdn.endswith("666")
    return {
        "failed": low_tenure,
        "low_tenure": low_tenure,
        "score": 25 if low_tenure else 0,
        "msisdn": transaction.customer_msisdn,
    }


def run_telecom_checks(transaction):
    telecom_data = {}

    telecom_data["number_verification"] = check_number_verification(transaction)
    telecom_data["sim_swap"] = check_sim_swap(transaction)
    telecom_data["device_swap"] = check_device_swap(transaction)
    telecom_data["location_verification"] = check_location_verification(transaction)

    telecom_data["kyc_match"] = save_check(
        transaction,
        "kyc_match",
        mock_kyc_match(transaction),
        "failed",
        "kyc_mismatch",
        "kyc_matched",
        "TEL-KYC-MATCH",
    )

    telecom_data["kyc_tenure"] = save_check(
        transaction,
        "kyc_tenure",
        mock_kyc_tenure(transaction),
        "low_tenure",
        "low_tenure",
        "normal_tenure",
        "TEL-KYC-TENURE",
    )

    return telecom_data


def check_number_verification(transaction):
    failed = transaction.customer_msisdn.endswith("888")
    score = 35 if failed else 0
    reference = f"TEL-NUMBER-{transaction.customer_msisdn}-{transaction.id}"

    TelecomCheck.objects.create(
        transaction=transaction,
        check_type="number_verification",
        provider="CAMARA_MOCK",
        result="failed" if failed else "verified",
        score=score,
        reference=reference,
        response_payload={
            "msisdn": transaction.customer_msisdn,
            "verified": not failed,
            "reference": reference,
        },
    )

    return {
        "failed": failed,
        "verified": not failed,
        "score": score,
        "reference": reference,
    }


def check_sim_swap(transaction):
    recent = transaction.customer_msisdn.endswith("999")
    score = 40 if recent else 0
    reference = f"TEL-SIM-SWAP-{transaction.customer_msisdn}-{transaction.id}"

    TelecomCheck.objects.create(
        transaction=transaction,
        check_type="sim_swap",
        provider="CAMARA_MOCK",
        result="recent_swap" if recent else "no_recent_swap",
        score=score,
        reference=reference,
        response_payload={
            "msisdn": transaction.customer_msisdn,
            "simSwapDetected": recent,
            "reference": reference,
        },
    )

    return {
        "recent": recent,
        "score": score,
        "reference": reference,
    }


def check_device_swap(transaction):
    device_id = transaction.device_id or ""
    swapped = device_id.upper().endswith("NEW")
    score = 25 if swapped else 0
    reference = f"TEL-DEVICE-SWAP-{device_id}-{transaction.id}"

    TelecomCheck.objects.create(
        transaction=transaction,
        check_type="device_swap",
        provider="CAMARA_MOCK",
        result="device_swapped" if swapped else "known_device",
        score=score,
        reference=reference,
        response_payload={
            "deviceId": transaction.device_id,
            "deviceSwapDetected": swapped,
            "reference": reference,
        },
    )

    return {
        "swapped": swapped,
        "score": score,
        "reference": reference,
    }


def check_location_verification(transaction):
    if transaction.latitude is None or transaction.longitude is None:
        mismatch = True
    else:
        expected_lat = -15.3875
        expected_lng = 28.3228

        lat_diff = abs(float(transaction.latitude) - expected_lat)
        lng_diff = abs(float(transaction.longitude) - expected_lng)

        mismatch = lat_diff > 0.5 or lng_diff > 0.5

    score = 25 if mismatch else 0
    reference = f"TEL-LOCATION-{transaction.customer_msisdn}-{transaction.id}"

    TelecomCheck.objects.create(
        transaction=transaction,
        check_type="location_verification",
        provider="CAMARA_MOCK",
        result="location_mismatch" if mismatch else "location_verified",
        score=score,
        reference=reference,
        response_payload={
            "latitude": transaction.latitude,
            "longitude": transaction.longitude,
            "locationVerified": not mismatch,
            "reference": reference,
        },
    )

    return {
        "mismatch": mismatch,
        "verified": not mismatch,
        "score": score,
        "reference": reference,
    }