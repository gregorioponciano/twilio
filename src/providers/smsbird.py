import os
from typing import Optional

import requests

from src.exceptions import RequestError


class SMSBirdProvider:
    BASE_URL = "https://api.smsbird.com/v2"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SMSBIRD_API_KEY")
        if not self.api_key:
            raise ValueError("SMSBIRD_API_KEY nao definido no .env")
        self._session = requests.Session()
        self._session.headers.update({
            "X-Api-Key": self.api_key,
            "Accept": "application/json",
        })

    def send_sms(self, to: str, message: str) -> dict:
        url = f"{self.BASE_URL}/sms/send"
        payload = {"to": to, "message": message}
        resp = self._session.post(url, json=payload)
        if not resp.ok:
            raise RequestError(
                f"SMS Bird send falhou: {resp.status_code} {resp.text}"
            )
        return resp.json()

    def check_balance(self) -> float:
        url = f"{self.BASE_URL}/balance"
        resp = self._session.get(url)
        if not resp.ok:
            raise RequestError(
                f"SMS Bird balance falhou: {resp.status_code} {resp.text}"
            )
        return resp.json().get("balance", 0.0)

    def close(self):
        self._session.close()
