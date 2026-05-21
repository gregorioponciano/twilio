import re
from typing import Optional


class OTPExtractor:
    @staticmethod
    def from_text(text: str, length: int = 6) -> Optional[str]:
        text_clean = text.replace("-", "")
        pattern = re.compile(rf"(?<!\d)\d{{{length}}}(?!\d)")
        match = pattern.search(text_clean)
        if match:
            return match.group()
        return None

    @staticmethod
    def from_image(image_url: str) -> Optional[str]:
        try:
            from io import BytesIO

            import pytesseract
            import requests
            from PIL import Image

            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            text = pytesseract.image_to_string(img).strip()
            return OTPExtractor.from_text(text)
        except ImportError:
            print("pytesseract/Pillow nao instalado. pip install pytesseract Pillow")
            return None
        except Exception as e:
            print(f"Erro ao extrair OTP de imagem: {e}")
            return None

    @staticmethod
    def from_list(messages: list, length: int = 6) -> Optional[str]:
        for msg in messages:
            otp = OTPExtractor.from_text(msg, length)
            if otp:
                return otp
        return None
