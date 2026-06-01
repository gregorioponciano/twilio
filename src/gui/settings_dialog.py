import os
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from src.gui.styles import *

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

SETTINGS_FIELDS = [
    ("section", "Twilio"),
    ("TWILIO_ACCOUNT_SID", "Account SID", ""),
    ("TWILIO_AUTH_TOKEN", "Auth Token", ""),
    ("TWILIO_NUMBER", "Numero de Origem", "+14155238886"),
    ("section", "Usuario"),
    ("PRIMARY_PHONE", "Seu Telefone", "+5511999999999"),
    ("APP_PASSWORD", "Senha do App", ""),
    ("section", "Provedores"),
    ("RECEIVE_SMS_API", "Receive-SMS URL", "https://receive-sms.com/view/{phone}"),
    ("NUMBERSOLO_API", "Numbersolo API", "https://numbersolo.com/api/buy/{country}/{operator}"),
    ("NUMBERSOLO_API_KEY", "Numbersolo Key", ""),
    ("SMSBIRD_API", "SMS Bird API", "https://api.smsbird.com/v2/sms/send"),
    ("SMSBIRD_API_KEY", "SMS Bird Key", ""),
    ("section", "E-mail"),
    ("EMAIL_USER", "E-mail", ""),
    ("EMAIL_PASS", "Senha", ""),
    ("EMAIL_IMAP_SERVER", "IMAP Server", "imap.gmail.com"),
    ("EMAIL_IMAP_PORT", "IMAP Port", "993"),
    ("section", "Chrome"),
    ("CHROME_DRIVER_PATH", "ChromeDriver Path", "/usr/local/bin/chromedriver"),
    ("section", "Internas"),
    ("OTP_LENGTH", "Tamanho OTP", "6"),
    ("POLL_INTERVAL", "Intervalo Polling (s)", "5"),
    ("REQUEST_TIMEOUT", "Timeout Request (s)", "15"),
    ("MAX_RETRIES", "Max Retentativas", "3"),
]


def _read_env() -> dict:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip().strip("\"'")
    return env


def _write_env(env: dict) -> None:
    lines = []
    for item in SETTINGS_FIELDS:
        if item[0] == "section":
            lines.append("")
            lines.append(f"# {item[1]}")
            continue
        key = item[0]
        default = item[2]
        val = env.get(key, default)
        if val == default and key in ("SMSBIRD_API_KEY", "NUMBERSOLO_API_KEY",
                                       "EMAIL_USER", "EMAIL_PASS", "CHROME_DRIVER_PATH"):
            val = default
        if val.isdigit():
            lines.append(f'{key}={val}')
        else:
            lines.append(f'{key}="{val}"')
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save: callable):
        super().__init__(parent)
        self.on_save = on_save
        self.env_data = _read_env()
        self.entries: dict[str, ctk.CTkEntry] = {}

        self.title("Configuracoes")
        self.geometry("520x480")
        self.configure(fg_color=WHATSAPP_DARK_BG)
        self.transient(parent)
        self._build_ui()
        self.update_idletasks()
        self.wait_visibility()
        self.grab_set()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=WHATSAPP_DARK_DIVIDER)
        scroll.grid(row=0, column=0, sticky="nsew", padx=24, pady=(12, 0))
        scroll.grid_columnconfigure(1, weight=1)

        fix_mousewheel(scroll)

        row = 0
        for item in SETTINGS_FIELDS:
            if item[0] == "section":
                if row > 0:
                    ctk.CTkFrame(scroll, height=1, fg_color=WHATSAPP_DARK_DIVIDER
                                 ).grid(row=row, column=0, columnspan=3, sticky="ew", pady=(10, 6))
                    row += 1
                ctk.CTkLabel(scroll, text=item[1],
                             font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                             text_color=WHATSAPP_DARK_TEXT
                             ).grid(row=row, column=0, columnspan=3, sticky="w", pady=(4, 6))
                row += 1
                continue

            key, label, default = item
            is_secret = any(k in key.lower() for k in ("token", "password", "pass", "key", "auth"))
            show = "*" if is_secret and key != "APP_PASSWORD" else ""

            ctk.CTkLabel(scroll, text=label,
                         font=(FONT_FAMILY, FONT_SIZE_SMALL),
                         text_color=WHATSAPP_DARK_TEXT
                         ).grid(row=row, column=0, padx=(0, 8), pady=3, sticky="w")

            val = self.env_data.get(key, default)
            entry = ctk.CTkEntry(scroll, font=(FONT_FAMILY, FONT_SIZE_SMALL),
                                 fg_color=WHATSAPP_DARK_INPUT,
                                 text_color=WHATSAPP_DARK_TEXT,
                                 border_width=0, corner_radius=BORDER_RADIUS_SM, height=30,
                                 show=show)
            entry.grid(row=row, column=1, pady=3, sticky="ew")
            entry.insert(0, str(val))
            self.entries[key] = entry

            if default and not is_secret:
                ctk.CTkLabel(scroll, text=f"padrao: {default}",
                             font=(FONT_FAMILY, 8),
                             text_color=WHATSAPP_DARK_TEXT_SECONDARY
                             ).grid(row=row, column=2, padx=(6, 0), pady=3, sticky="w")
            row += 1

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=1, column=0, pady=(12, 18))

        ctk.CTkButton(btns, text="Salvar", font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                       fg_color=WHATSAPP_TEAL, text_color="white",
                       hover_color=WHATSAPP_GREEN, corner_radius=BORDER_RADIUS_BTN,
                       width=100, command=self._save).grid(row=0, column=0, padx=6)

        ctk.CTkButton(btns, text="Cancelar", font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                       fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                       hover_color=WHATSAPP_DARK_HOVER, corner_radius=BORDER_RADIUS_BTN,
                       width=100, command=self.destroy).grid(row=0, column=1, padx=6)

    def _save(self) -> None:
        for key, entry in self.entries.items():
            val = entry.get().strip()
            self.env_data[key] = val

        _write_env(self.env_data)

        import dotenv
        dotenv.load_dotenv(ENV_PATH, override=True)

        self.on_save(self.env_data)
        self.destroy()
