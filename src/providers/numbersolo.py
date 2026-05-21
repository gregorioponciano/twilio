import os
from typing import Optional

import requests

from src.exceptions import RequestError


class NumbersoloProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NUMBERSOLO_API_KEY")
        if not self.api_key:
            raise ValueError("NUMBERSOLO_API_KEY nao definido no .env")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        })

    def buy_number(self, country: str = "BR", operator: str = "any") -> str:
        url = f"https://numbersolo.com/api/buy/{country}/{operator}"
        resp = self._session.post(url)
        if not resp.ok:
            raise RequestError(
                f"Numbersolo buy falhou: {resp.status_code} {resp.text}"
            )
        data = resp.json()
        return data.get("phone_number", "")

    def get_sms(self, phone_number: str) -> list:
        url = f"https://numbersolo.com/api/sms/{phone_number}"
        resp = self._session.get(url)
        if not resp.ok:
            raise RequestError(
                f"Numbersolo sms falhou: {resp.status_code} {resp.text}"
            )
        return resp.json().get("messages", [])

    def close(self):
        self._session.close()
