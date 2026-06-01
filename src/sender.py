import logging
import re
import sys
from pathlib import Path

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

LOG_PATH = Path(__file__).resolve().parent.parent / "app.log"
PHONE_REGEX = re.compile(r"^\+[1-9]\d{6,14}$")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)


class TwilioSender:
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.logger = logging.getLogger(self.__class__.__name__)

    def send(self, to_number: str, message: str, channel: str) -> str:
        if not PHONE_REGEX.match(self.from_number):
            raise ValueError(
                f"Número de origem inválido no .env: {self.from_number}. "
                "Use formato internacional (+5511999999999)."
            )

        kwargs: dict = {"body": message, "to": to_number}
        if channel == "whatsapp":
            kwargs["from_"] = f"whatsapp:{self.from_number}"
            kwargs["to"] = f"whatsapp:{to_number}"
        else:
            kwargs["from_"] = self.from_number

        try:
            msg = self.client.messages.create(**kwargs)
        except TwilioRestException as exc:
            self.logger.error(
                "Falha no envio | para=%s | canal=%s | status=%d | code=%d | msg=%s",
                to_number,
                channel,
                exc.status,
                exc.code,
                strip_ansi(str(exc)),
            )
            raise

        self.logger.info(
            "Mensagem enviada | para=%s | canal=%s | sid=%s",
            to_number,
            channel,
            msg.sid,
        )
        return msg.sid
