import logging
from typing import List, Optional

from src.config import Config
from src.manager import VirtualNumberManager, Platform
from src.models import Message

logger = logging.getLogger("receiver")


class SmsReceiver:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()
        self.manager = VirtualNumberManager(self.config)

    def receive_messages(self, contact_phone: str) -> List[Message]:
        messages: List[Message] = []
        try:
            otp = self.manager.get_otp()
            if otp:
                msg = Message(
                    direction="received",
                    content=f"OTP: {otp}",
                    channel="sms",
                    status="received",
                )
                messages.append(msg)
        except Exception as e:
            logger.warning("Erro ao receber SMS: %s", e)
        return messages

    def buy_virtual_number(self, platform: str = "sms") -> Optional[str]:
        try:
            plat = Platform(platform)
            number = self.manager.purchase_number("receive_sms", platform=plat)
            return number
        except Exception as e:
            logger.error("Falha ao comprar numero virtual: %s", e)
            return None

    def close(self) -> None:
        self.manager.close_all()
