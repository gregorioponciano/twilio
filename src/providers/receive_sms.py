import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from src.config import Config
from src.exceptions import ParseError, RequestError
from src.extractors.otp import OTPExtractor


class ReceiveSMSProvider:
    def __init__(self, config: Config):
        self.config = config
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.config.user_agent})

    def _build_url(self) -> str:
        return self.config.receive_sms_url.format(phone=self.config.phone_number)

    def fetch_page(self) -> str:
        url = self._build_url()
        for attempt in range(1, self.config.max_retries + 1):
            try:
                resp = self._session.get(url, timeout=self.config.request_timeout)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException as exc:
                if attempt == self.config.max_retries:
                    raise RequestError(f"Falha apos {attempt} tentativas: {exc}")
                time.sleep(2)
        raise RequestError("Erro inesperado no fetch_page")

    def parse_messages(self, html: str) -> List[str]:
        try:
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.find_all("tr")
            if not rows:
                rows = soup.find_all(class_="message-row")
            messages = []
            for row in rows[1:]:
                text = row.get_text(separator=" ", strip=True)
                if text:
                    messages.append(text)
            return messages
        except Exception as exc:
            raise ParseError(f"Falha ao parsear HTML: {exc}")

    def get_otp(self) -> Optional[str]:
        try:
            html = self.fetch_page()
            messages = self.parse_messages(html)
            return OTPExtractor.from_list(messages, self.config.otp_length)
        except Exception as e:
            print(f"Erro no provedor Receive-SMS: {e}")
            return None

    def close(self):
        self._session.close()
