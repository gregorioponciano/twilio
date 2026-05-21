import os
import time
from typing import Optional


class WhatsAppCapture:
    def __init__(self, chrome_driver_path: Optional[str] = None):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
        except ImportError:
            raise ImportError("selenium nao instalado. pip install selenium")

        path = chrome_driver_path or os.getenv("CHROME_DRIVER_PATH")
        service = Service(path) if path else None
        self.driver = webdriver.Chrome(service=service)

    def scan_whatsapp_qr(self):
        self.driver.get("https://web.whatsapp.com")
        print("Abra o WhatsApp no celular e escaneie o QR Code.")
        input("Pressione Enter apos escanear...")

    def extract_otp(self) -> Optional[str]:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            from src.extractors.otp import OTPExtractor
        except ImportError:
            raise ImportError("selenium nao instalado. pip install selenium")

        wait = WebDriverWait(self.driver, 30)
        phone = os.getenv("PRIMARY_PHONE")
        if not phone:
            raise ValueError("PRIMARY_PHONE nao definido no .env")

        try:
            search_box = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            search_box.send_keys(phone)
            time.sleep(2)
            messages = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[@dir="auto"]//span[@class="_ao3e"]')
                )
            )
            for msg in messages:
                otp = OTPExtractor.from_text(msg.text)
                if otp:
                    return otp
            return None
        except Exception as e:
            print(f"Erro ao capturar WhatsApp: {e}")
            return None

    def close(self):
        self.driver.quit()
