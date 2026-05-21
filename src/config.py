import os
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Config:
    phone_number: str = os.getenv("PRIMARY_PHONE", "+5511999999999")
    otp_length: int = 6
    poll_interval: float = 5.0
    request_timeout: float = 15.0
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    max_retries: int = 3

    # Receive-SMS
    receive_sms_url: str = os.getenv(
        "RECEIVE_SMS_API", "https://receive-sms.com/view/{phone}"
    )

    # Numbersolo
    numbersolo_api_key: Optional[str] = os.getenv("NUMBERSOLO_API_KEY")

    # SMS Bird
    smsbird_api_key: Optional[str] = os.getenv("SMSBIRD_API_KEY")

    # Twilio
    twilio_account_sid: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number: Optional[str] = os.getenv("TWILIO_NUMBER")

    # Email (para fallback de OTP)
    email_user: Optional[str] = os.getenv("EMAIL_USER")
    email_pass: Optional[str] = os.getenv("EMAIL_PASS")
    email_imap_server: str = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
    email_imap_port: int = int(os.getenv("EMAIL_IMAP_PORT", "993"))

    # ChromeDriver
    chrome_driver_path: Optional[str] = os.getenv("CHROME_DRIVER_PATH")
