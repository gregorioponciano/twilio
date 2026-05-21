import argparse
import logging
import time

from dotenv import load_dotenv

from src.config import Config
from src.manager import Platform, VirtualNumberManager

logger = logging.getLogger(__name__)


class OTPSystem:
    def __init__(
        self,
        config: Config = None,
        platform: Platform = Platform.SMS,
        prefer_cheapest: bool = True,
    ):
        self.config = config or Config()
        self.manager = VirtualNumberManager(self.config)
        self.platform = platform
        self.prefer_cheapest = prefer_cheapest

    def run(self):
        logger.info(
            "Monitorando %s para: %s",
            self.platform.value,
            self.config.phone_number,
        )
        logger.info("Polling a cada %s segundos.", self.config.poll_interval)

        if not self.manager.active_number:
            number = self.manager.rotate_number(
                platform=self.platform,
                prefer_cheapest=self.prefer_cheapest,
            )
            logger.info("Numero ativo: %s", number)

        try:
            while True:
                otp = self.manager.get_otp(self.config.otp_length)
                if otp:
                    logger.info("OTP CAPTURADO: %s", otp)
                    print(f"\n>>> CODIGO ENCONTRADO: {otp} <<<\n")
                    break
                time.sleep(self.config.poll_interval)
        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuario.")
        finally:
            self.manager.close_all()


def main():
    parser = argparse.ArgumentParser(description="Sistema de captura de OTP")
    parser.add_argument(
        "--platform",
        choices=[p.value for p in Platform],
        default="sms",
        help="Plataforma alvo (sms, whatsapp, telegram, etc.)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Provedor especifico (receive_sms, numbersolo, smsbird, twilio)",
    )
    parser.add_argument(
        "--no-cheapest",
        action="store_true",
        help="Nao priorizar o provedor mais barato",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    load_dotenv()

    platform = Platform(args.platform)
    config = Config()

    if args.provider:
        manager = VirtualNumberManager(config)
        manager.rotate_number(platform=platform)
    else:
        system = OTPSystem(
            config=config,
            platform=platform,
            prefer_cheapest=not args.no_cheapest,
        )
        system.run()


if __name__ == "__main__":
    main()
