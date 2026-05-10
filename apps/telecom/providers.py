from django.conf import settings
from .camara_client import CamaraClient, CamaraClientError


class MockCamaraProvider:
    def number_verification(self, transaction):
        failed = transaction.customer_msisdn.endswith("888")
        return {
            "failed": failed,
            "verified": not failed,
            "score": 35 if failed else 0,
            "raw": {"verified": not failed, "source": "mock"},
        }

    def sim_swap(self, transaction):
        recent = transaction.customer_msisdn.endswith("999")
        return {
            "recent": recent,
            "score": 40 if recent else 0,
            "raw": {"simSwapDetected": recent, "source": "mock"},
        }

    def device_swap(self, transaction):
        device_id = transaction.device_id or ""
        swapped = device_id.upper().endswith("NEW")
        return {
            "swapped": swapped,
            "score": 25 if swapped else 0,
            "raw": {"deviceSwapDetected": swapped, "source": "mock"},
        }

    def location_verification(self, transaction):
        if transaction.latitude is None or transaction.longitude is None:
            mismatch = True
        else:
            expected_lat = -15.3875
            expected_lng = 28.3228
            mismatch = (
                abs(float(transaction.latitude) - expected_lat) > 0.5
                or abs(float(transaction.longitude) - expected_lng) > 0.5
            )

        return {
            "mismatch": mismatch,
            "verified": not mismatch,
            "score": 25 if mismatch else 0,
            "raw": {"locationVerified": not mismatch, "source": "mock"},
        }
    def kyc_match(self, transaction):
        failed = transaction.customer_msisdn.endswith("777")
        return {
            "failed": failed,
            "matched": not failed,
            "score": 30 if failed else 0,
            "raw": {"kycMatched": not failed, "source": "mock"},
        }


def kyc_tenure(self, transaction):
    low_tenure = transaction.customer_msisdn.endswith("666")
    return {
        "low_tenure": low_tenure,
        "score": 20 if low_tenure else 0,
        "raw": {"lowTenure": low_tenure, "source": "mock"},
    }


class LiveCamaraProvider:
    def __init__(self):
        self.client = CamaraClient()

    def number_verification(self, transaction):
        data = self.client.post(
            settings.NUMBER_VERIFY_PATH,
            {
                "phoneNumber": transaction.customer_msisdn,
            },
        )

        verified = (
            data.get("verified") is True
            or data.get("devicePhoneNumberVerified") is True
            or data.get("phoneNumberVerified") is True
        )

        return {
            "failed": not verified,
            "verified": verified,
            "score": 0 if verified else 35,
            "raw": data,
        }

    def sim_swap(self, transaction):
        data = self.client.post(
            settings.SIM_SWAP_CHECK_PATH,
            {
                "phoneNumber": transaction.customer_msisdn,
                "maxAge": 72,
            },
        )

        recent = (
            data.get("swapped") is True
            or data.get("simSwapDetected") is True
            or data.get("recentSimSwap") is True
        )

        return {
            "recent": recent,
            "score": 40 if recent else 0,
            "raw": data,
        }

    def device_swap(self, transaction):
        data = self.client.post(
            settings.DEVICE_SWAP_CHECK_PATH,
            {
                "phoneNumber": transaction.customer_msisdn,
                "deviceId": transaction.device_id,
            },
        )

        swapped = (
            data.get("swapped") is True
            or data.get("deviceSwapDetected") is True
        )

        return {
            "swapped": swapped,
            "score": 25 if swapped else 0,
            "raw": data,
        }

    def location_verification(self, transaction):
        data = self.client.post(
            settings.LOCATION_VERIFY_PATH,
            {
                "phoneNumber": transaction.customer_msisdn,
                "area": {
                    "areaType": "CIRCLE",
                    "center": {
                        "latitude": transaction.latitude,
                        "longitude": transaction.longitude,
                    },
                    "radius": 500,
                },
            },
        )

        verified = (
            data.get("verified") is True
            or data.get("verificationResult") is True
            or data.get("locationVerified") is True
        )

        return {
            "mismatch": not verified,
            "verified": verified,
            "score": 0 if verified else 25,
            "raw": data,
        }
        
def kyc_match(self, transaction):
    data = self.client.post(
        settings.KYC_MATCH_PATH,
        {
            "phoneNumber": transaction.customer_msisdn,
        },
    )

    matched = (
        data.get("match") is True
        or data.get("matched") is True
        or data.get("kycMatched") is True
    )

    return {
        "failed": not matched,
        "matched": matched,
        "score": 0 if matched else 30,
        "raw": data,
    }


def kyc_tenure(self, transaction):
    data = self.client.post(
        settings.KYC_TENURE_PATH,
        {
            "phoneNumber": transaction.customer_msisdn,
        },
    )

    low_tenure = (
        data.get("lowTenure") is True
        or data.get("tenureRisk") == "low"
    )

    return {
        "low_tenure": low_tenure,
        "score": 20 if low_tenure else 0,
        "raw": data,
    }


class SafeCamaraProvider:
    def __init__(self):
        self.live = LiveCamaraProvider()
        self.mock = MockCamaraProvider()

    def _safe(self, method_name, transaction):
        try:
            return getattr(self.live, method_name)(transaction)
        except CamaraClientError as error:
            fallback = getattr(self.mock, method_name)(transaction)
            fallback["raw"]["fallback"] = True
            fallback["raw"]["live_error"] = str(error)
            return fallback
        except Exception as error:
            fallback = getattr(self.mock, method_name)(transaction)
            fallback["raw"]["fallback"] = True
            fallback["raw"]["live_error"] = str(error)
            return fallback

    def number_verification(self, transaction):
        return self._safe("number_verification", transaction)

    def sim_swap(self, transaction):
        return self._safe("sim_swap", transaction)

    def device_swap(self, transaction):
        return self._safe("device_swap", transaction)

    def location_verification(self, transaction):
        return self._safe("location_verification", transaction)
    
    def kyc_match(self, transaction):
        return self._safe("kyc_match", transaction)


    def kyc_tenure(self, transaction):
        return self._safe("kyc_tenure", transaction)


def get_telecom_provider():
    if settings.CAMARA_MODE == "live":
        return SafeCamaraProvider()
    return MockCamaraProvider()