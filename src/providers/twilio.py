import os
from typing import Iterator, Optional


class TwilioProvider:
    def __init__(self):
        try:
            from twilio.rest import Client
        except ImportError:
            raise ImportError("twilio nao instalado. pip install twilio")

        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        )

    def send_sms(self, to_number: str, message: str):
        self.client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_NUMBER"),
            to=to_number,
        )

    def list_messages(self, to_number: str) -> Iterator[str]:
        messages = self.client.messages.list(to=to_number)
        for msg in messages:
            yield msg.body

    def get_otp(self, to_number: str, length: int = 6) -> Optional[str]:
        from src.extractors.otp import OTPExtractor

        for body in self.list_messages(to_number):
            otp = OTPExtractor.from_text(body, length)
            if otp:
                return otp
        return None
