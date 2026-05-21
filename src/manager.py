import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

from src.config import Config
from src.exceptions import (
    NoProviderAvailableError,
    PlatformNotSupportedError,
    ProviderNotFoundError,
)
from src.providers.numbersolo import NumbersoloProvider
from src.providers.receive_sms import ReceiveSMSProvider
from src.providers.smsbird import SMSBirdProvider
from src.providers.twilio import TwilioProvider


class Platform(Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    VOICE = "voice"
    SIGNAL = "signal"
    VIBER = "viber"
    LINE = "line"
    WECHAT = "wechat"


@dataclass
class NumberProvider:
    name: str
    platforms: Set[Platform] = field(default_factory=set)
    cost_per_buy: float = 0.0

    def supports(self, platform: Platform) -> bool:
        return platform in self.platforms

    def ensure_supports(self, platform: Platform) -> None:
        if not self.supports(platform):
            raise PlatformNotSupportedError(self.name, platform.value)


class VirtualNumberManager:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()

        self.providers: Dict[str, NumberProvider] = {
            "receive_sms": NumberProvider(
                name="Receive-SMS",
                platforms={Platform.SMS},
                cost_per_buy=0.0,
            ),
            "numbersolo": NumberProvider(
                name="Numbersolo",
                platforms={Platform.SMS, Platform.WHATSAPP},
                cost_per_buy=1.5,
            ),
            "smsbird": NumberProvider(
                name="SMS Bird",
                platforms={Platform.SMS},
                cost_per_buy=0.1,
            ),
            "twilio": NumberProvider(
                name="Twilio",
                platforms={Platform.SMS, Platform.VOICE, Platform.WHATSAPP},
                cost_per_buy=0.0,
            ),
        }

        self._instances: Dict[str, object] = {
            "receive_sms": ReceiveSMSProvider(self.config),
            "numbersolo": (
                NumbersoloProvider(self.config.numbersolo_api_key)
                if self.config.numbersolo_api_key
                else None
            ),
            "smsbird": (
                SMSBirdProvider(self.config.smsbird_api_key)
                if self.config.smsbird_api_key
                else None
            ),
            "twilio": (
                TwilioProvider()
                if self.config.twilio_account_sid
                else None
            ),
        }

        self.active_number: Optional[str] = None
        self.number_history: List[str] = []

    # ── Busca e Roteamento ──────────────────────────────────────

    def get_provider(self, provider_name: str) -> NumberProvider:
        if provider_name not in self.providers:
            raise ProviderNotFoundError(provider_name)
        return self.providers[provider_name]

    def providers_for_platform(self, platform: Platform) -> List[NumberProvider]:
        return [p for p in self.providers.values() if p.supports(platform)]

    def cheapest_for_platform(self, platform: Platform) -> Optional[NumberProvider]:
        candidates = self.providers_for_platform(platform)
        if not candidates:
            return None
        return min(candidates, key=lambda p: p.cost_per_buy)

    # ── Compra / Rotação ────────────────────────────────────────

    def purchase_number(
        self,
        provider_name: str,
        platform: Optional[Platform] = None,
        country: str = "BR",
    ) -> str:
        provider = self.get_provider(provider_name)
        if platform is not None:
            provider.ensure_supports(platform)

        instance = self._instances.get(provider_name)
        number: Optional[str] = None

        if isinstance(instance, NumbersoloProvider):
            number = instance.buy_number(country=country)
        elif isinstance(instance, TwilioProvider):
            number = self.config.twilio_number or "+14155238886"

        if not number:
            number = self._fake_number(country)

        if provider.cost_per_buy > 0:
            print(f"Custo: ${provider.cost_per_buy:.2f} via {provider.name}")

        self.number_history.append(number)
        self.active_number = number
        print(f"Numero virtual comprado: {number} via {provider.name}")
        time.sleep(1)
        return number

    def rotate_number(
        self, platform: Platform = Platform.SMS, prefer_cheapest: bool = True
    ) -> str:
        if prefer_cheapest:
            provider = self.cheapest_for_platform(platform)
        else:
            candidates = self.providers_for_platform(platform)
            provider = candidates[0] if candidates else None

        if provider is None:
            fallback = self.config.phone_number
            print(
                f"Nenhum provedor para {platform.value}. "
                f"Usando fallback {fallback}."
            )
            return fallback

        provider_key = self._key_for_provider(provider)
        return self.purchase_number(
            provider_key,
            platform=platform,
        )

    def get_otp(self, length: int = 6) -> Optional[str]:
        instance = self._get_active_instance()
        if isinstance(instance, ReceiveSMSProvider):
            return instance.get_otp()
        if isinstance(instance, TwilioProvider) and self.active_number:
            return instance.get_otp(self.active_number, length)
        return None

    # ── Internos ────────────────────────────────────────────────

    def _fake_number(self, country: str) -> str:
        import random
        return f"+55{country}{random.randint(1190000000, 1199999999)}"

    def _key_for_provider(self, provider: NumberProvider) -> str:
        for key, p in self.providers.items():
            if p is provider:
                return key
        raise ProviderNotFoundError(provider.name)

    def _get_active_instance(self) -> Optional[object]:
        if not self.active_number:
            return None
        for instance in self._instances.values():
            if instance is not None:
                return instance
        return None

    def close_all(self):
        for instance in self._instances.values():
            if hasattr(instance, "close"):
                instance.close()
