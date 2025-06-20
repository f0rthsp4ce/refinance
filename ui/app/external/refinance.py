import requests
from app.config import Config
from app.exceptions.base import ApplicationError
from flask import session


class RefinanceAPI:
    token: str | None = None
    url: str = Config.REFINANCE_API_BASE_URL

    def http(self, method: str, endpoint: str, params=None, data=None):
        try:
            r = requests.request(
                method,
                f"{self.url}/{endpoint}",
                params=params,
                json=data,
                timeout=5,
                headers={"X-Token": self.token} if self.token else {},
            )
            if r.status_code != 200:
                e = r.json()
                raise ApplicationError(e)
            return r
        except requests.exceptions.RequestException as e:
            raise ApplicationError(f"Request to API failed: {e}")

    def __init__(self, token: str | None) -> None:
        self.token = token


def get_refinance_api_client() -> RefinanceAPI:
    token = session.get("token")
    return RefinanceAPI(token)
