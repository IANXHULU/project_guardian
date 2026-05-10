import requests
from django.conf import settings


class CamaraClientError(Exception):
    pass


class CamaraClient:
    def __init__(self):
        self.base_url = getattr(settings, "CAMARA_BASE_URL", "")
        self.api_key = getattr(settings, "CAMARA_API_KEY", "")
        self.host = getattr(settings, "CAMARA_HOST", "")
        self.timeout = getattr(settings, "CAMARA_TIMEOUT", 15)

    def post(self, path: str, payload: dict) -> dict:
        if not self.base_url:
            raise CamaraClientError("CAMARA_BASE_URL is not configured.")

        if not self.api_key:
            raise CamaraClientError("CAMARA_API_KEY is not configured.")

        if not self.host:
            raise CamaraClientError("CAMARA_HOST is not configured.")

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "x-rapidapi-key": self.api_key,
                    "x-rapidapi-host": self.host,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )

            if response.status_code >= 400:
                raise CamaraClientError(
                    f"CAMARA request failed: {response.status_code} {response.text}"
                )

            try:
                return response.json()
            except ValueError:
                raise CamaraClientError(
                    f"CAMARA returned invalid JSON: {response.text}"
                )

        except requests.Timeout:
            raise CamaraClientError("CAMARA request timed out.")

        except requests.ConnectionError:
            raise CamaraClientError("Could not connect to CAMARA API.")

        except requests.RequestException as e:
            raise CamaraClientError(f"CAMARA request error: {str(e)}")