import logging
import random
import threading
from typing import Optional

import customtkinter as ctk

from src.config import Config
from src.manager import Platform, VirtualNumberManager
from src.receiver import SmsReceiver
from src.gui.styles import *

logger = logging.getLogger("setup")


class SetupWizard(ctk.CTkToplevel):
    def __init__(self, parent, current_number: str,
                 on_number_changed: callable,
                 on_whatsapp_verified: callable,
                 account_sid: str = "", auth_token: str = ""):
        super().__init__(parent)
        self.current_number = current_number
        self.on_number_changed = on_number_changed
        self.on_whatsapp_verified = on_whatsapp_verified
        self._sid = account_sid
        self._token = auth_token

        self.config = Config()
        self.manager = VirtualNumberManager(self.config)
        self.receiver = SmsReceiver(self.config)

        self.whatsapp_verified = False
        self.verification_code: Optional[str] = None

        self.title("WhatsApp")
        self.geometry("500x460")
        self.resizable(False, False)
        self.configure(fg_color=WHATSAPP_DARK_BG)
        self.transient(parent)
        self.update_idletasks()
        self.wait_visibility()
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Configurac\u0327a\u0303o WhatsApp",
                     font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
                     text_color=WHATSAPP_DARK_TEXT).grid(row=0, column=0, pady=(24, 4))

        ctk.CTkLabel(self, text="Compre um nu\u0301mero virtual e verifique seu WhatsApp",
                     font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=1, column=0, pady=(0, 16))

        curr = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_INPUT, corner_radius=BORDER_RADIUS)
        curr.grid(row=2, column=0, padx=32, pady=4, sticky="ew")
        curr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(curr, text="Nu\u0301mero atual:",
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                     text_color=WHATSAPP_DARK_TEXT).grid(row=0, column=0, padx=14, pady=12, sticky="w")
        self.number_label = ctk.CTkLabel(curr, text=self.current_number,
                                         font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                                         text_color=WHATSAPP_TEAL)
        self.number_label.grid(row=0, column=1, padx=14, pady=12, sticky="w")

        buy = ctk.CTkFrame(self, fg_color="transparent")
        buy.grid(row=3, column=0, padx=32, pady=10, sticky="ew")
        buy.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(buy, text="Comprar nu\u0301mero:",
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                     text_color=WHATSAPP_DARK_TEXT).grid(row=0, column=0, padx=(0, 10), pady=6, sticky="w")

        self.provider_var = ctk.StringVar(value="twilio")
        ctk.CTkOptionMenu(buy, values=["twilio", "receive_sms", "numbersolo", "smsbird"],
                          variable=self.provider_var,
                          font=(FONT_FAMILY, FONT_SIZE_SMALL),
                          fg_color=WHATSAPP_DARK_INPUT,
                          button_color=WHATSAPP_TEAL,
                          text_color=WHATSAPP_DARK_TEXT
                          ).grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        self.buy_btn = ctk.CTkButton(buy, text="Comprar",
                                     font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                                     fg_color=WHATSAPP_TEAL, text_color="white",
                                     hover_color=WHATSAPP_GREEN,
                                     width=80, height=30, command=self._buy_number)
        self.buy_btn.grid(row=0, column=2, padx=4, pady=6)

        self.buy_status = ctk.CTkLabel(buy, text="",
                                       font=(FONT_FAMILY, FONT_SIZE_SMALL),
                                       text_color=WHATSAPP_DARK_TEXT_SECONDARY)
        self.buy_status.grid(row=1, column=0, columnspan=3, padx=4, pady=(0, 2), sticky="w")

        ctk.CTkFrame(self, height=1, fg_color=WHATSAPP_DARK_DIVIDER
                     ).grid(row=4, column=0, padx=32, pady=8, sticky="ew")

        ctk.CTkLabel(self, text="Verificac\u0327a\u0303o WhatsApp",
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                     text_color=WHATSAPP_DARK_TEXT).grid(row=5, column=0, pady=(4, 2))

        ctk.CTkLabel(self, text="Um co\u0301digo sera\u0301 enviado via SMS para seu celular",
                     font=(FONT_FAMILY, 10),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=5, column=0, pady=(20, 2))

        wa = ctk.CTkFrame(self, fg_color="transparent")
        wa.grid(row=6, column=0, padx=32, pady=4, sticky="ew")
        wa.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(wa, text="Seu celular:",
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                     text_color=WHATSAPP_DARK_TEXT).grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")

        self.phone_entry = ctk.CTkEntry(wa,
                                        placeholder_text="+5511999999999",
                                        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                                        fg_color=WHATSAPP_DARK_INPUT,
                                        text_color=WHATSAPP_DARK_TEXT,
                                        border_width=0, corner_radius=BORDER_RADIUS_SM, height=34)
        self.phone_entry.grid(row=0, column=1, pady=4, sticky="ew")
        self.phone_entry.insert(0, self.config.phone_number)

        self.send_code_btn = ctk.CTkButton(wa, text="Enviar Co\u0301digo",
                                           font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                                           fg_color=WHATSAPP_TEAL, text_color="white",
                                           hover_color=WHATSAPP_GREEN,
                                           width=100, height=30, command=self._send_verification)
        self.send_code_btn.grid(row=0, column=2, padx=6, pady=4)

        code = ctk.CTkFrame(self, fg_color="transparent")
        code.grid(row=7, column=0, padx=32, pady=4, sticky="ew")
        code.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(code, text="Co\u0301digo recebido:",
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                     text_color=WHATSAPP_DARK_TEXT).grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")

        self.code_entry = ctk.CTkEntry(code,
                                       placeholder_text="000000",
                                       font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                                       fg_color=WHATSAPP_DARK_INPUT,
                                       text_color=WHATSAPP_DARK_TEXT,
                                       border_width=0, corner_radius=BORDER_RADIUS_SM, height=34, width=140)
        self.code_entry.grid(row=0, column=1, pady=4, sticky="w")

        self.confirm_btn = ctk.CTkButton(code, text="Confirmar",
                                         font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                                         fg_color=WHATSAPP_GREEN, text_color="white",
                                         hover_color="#128C7E",
                                         width=90, height=30, state="disabled",
                                         command=self._confirm_code)
        self.confirm_btn.grid(row=0, column=2, padx=6, pady=4)

        self.wa_status = ctk.CTkLabel(self, text="",
                                      font=(FONT_FAMILY, FONT_SIZE_SMALL),
                                      text_color=WHATSAPP_DARK_TEXT_SECONDARY)
        self.wa_status.grid(row=8, column=0, padx=32, pady=(4, 0), sticky="w")

        self.verified_lbl = ctk.CTkLabel(self, text="",
                                         font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                                         text_color=WHATSAPP_LIGHT_GREEN)
        self.verified_lbl.grid(row=9, column=0, pady=(4, 6))

        ctk.CTkButton(self, text="Fechar", font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                      fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                      hover_color=WHATSAPP_DARK_HOVER,
                      command=self.destroy).grid(row=10, column=0, pady=(10, 20))

    def _buy_number(self) -> None:
        provider = self.provider_var.get()
        self.buy_status.configure(text=f"Comprando via {provider}...", text_color=COR_WARNING)
        self.buy_btn.configure(state="disabled")

        def purchase():
            try:
                plat = Platform.SMS
                number = self.manager.purchase_number(provider, platform=plat)
                self.after(0, lambda: self._on_number_bought(number))
            except Exception as e:
                logger.exception("Falha ao comprar nu\u0301mero")
                self.after(0, lambda: self.buy_status.configure(
                    text=f"Erro: {e}", text_color=COR_ERROR))
                self.after(0, lambda: self.buy_btn.configure(state="normal"))

        threading.Thread(target=purchase, daemon=True).start()

    def _on_number_bought(self, number: str) -> None:
        self.current_number = number
        self.number_label.configure(text=number)
        self.buy_status.configure(text=f"Nu\u0301mero {number} adquirido!", text_color=COR_SUCCESS)
        self.buy_btn.configure(state="normal")
        self.on_number_changed(number)

    def _send_verification(self) -> None:
        phone = self.phone_entry.get().strip()
        if not phone.startswith("+"):
            self.wa_status.configure(text="Telefone deve comec\u0327ar com +", text_color=COR_ERROR)
            return

        self.verification_code = str(random.randint(100000, 999999))
        self.send_code_btn.configure(state="disabled")
        self.wa_status.configure(text=f"Enviando co\u0301digo para {phone}...", text_color=COR_WARNING)

        def send():
            try:
                from src.sender import TwilioSender
                target = self.current_number or self.config.twilio_number or "+14155238886"
                sender = TwilioSender(self._sid, self._token, target)
                msg = f"Seu co\u0301digo de verificac\u0327a\u0303o: {self.verification_code}"
                sender.send(phone, msg, "sms")
                self.after(0, lambda: self.wa_status.configure(
                    text=f"Co\u0301digo enviado! Verifique seu SMS", text_color=COR_SUCCESS))
                self.after(0, lambda: self.confirm_btn.configure(state="normal"))
                self.after(0, lambda: self.send_code_btn.configure(state="normal"))
            except Exception as e:
                logger.exception("Falha ao enviar co\u0301digo")
                self.after(0, lambda: self.wa_status.configure(
                    text=f"Falha: {e}. Use: {self.verification_code}", text_color=COR_WARNING))
                self.after(0, lambda: self.confirm_btn.configure(state="normal"))
                self.after(0, lambda: self.send_code_btn.configure(state="normal"))

        threading.Thread(target=send, daemon=True).start()

    def _confirm_code(self) -> None:
        entered = self.code_entry.get().strip()
        if entered == self.verification_code:
            self.whatsapp_verified = True
            self.verified_lbl.configure(text="\u2713 WhatsApp verificado!")
            self.wa_status.configure(text="")
            self.confirm_btn.configure(state="disabled")
            self.send_code_btn.configure(state="disabled")
            self.on_whatsapp_verified()
        else:
            self.wa_status.configure(text="Co\u0301digo incorreto. Tente novamente.", text_color=COR_ERROR)
