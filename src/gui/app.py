import logging
import os
import threading
from typing import Optional

import customtkinter as ctk
from twilio.base.exceptions import TwilioRestException

from src.models import CallLog, Contact, Message
from src.repository import CallLogRepository, ContactRepository, MessageRepository
from src.receiver import SmsReceiver
from src.sender import TwilioSender
from src.gui.call_log_view import CallLogView
from src.gui.chat_view import ChatView
from src.gui.contact_list import ContactListPanel
from src.gui.dialogs import ContactDialog
from src.gui.setup_wizard import SetupWizard
from src.gui.settings_dialog import SettingsDialog
from src.gui.help_dialog import HelpDialog
from src.gui.styles import *

logger = logging.getLogger("app")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
WHATSAPP_MARKER = os.path.join(DATA_DIR, ".whatsapp_verified")


class App(ctk.CTk):
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        super().__init__()
        self.title("Twilio Pro")
        self.configure(fg_color=WHATSAPP_DARK_BG)

        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self.sender = TwilioSender(account_sid, auth_token, from_number)
        self.receiver = SmsReceiver()

        self.contact_repo = ContactRepository()
        self.message_repo = MessageRepository()
        self.call_repo = CallLogRepository()

        self.current_contact: Optional[Contact] = None
        self.chat_view: Optional[ChatView] = None
        self.contact_list: Optional[ContactListPanel] = None
        self.call_log_view: Optional[CallLogView] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.wa_indicator: Optional[ctk.CTkLabel] = None
        self.current_view = "chat"

        self.withdraw()
        env_password = os.getenv("APP_PASSWORD", "")
        if env_password:
            if not self._check_password(env_password):
                self.destroy()
                return

        self._build_ui()
        self._load_data()
        self._check_whatsapp_status()
        self.deiconify()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _check_password(self, expected: str) -> bool:
        import tkinter.simpledialog as sd
        from tkinter import messagebox

        for attempt in range(3):
            pw = sd.askstring("Twilio Pro", "Digite a senha:", show="*", parent=self)
            if pw is None:
                return False
            if pw.strip() == expected:
                return True
            messagebox.showerror("Erro", f"Senha incorreta. Tentativa {attempt + 1}/3.")
        messagebox.showerror("Erro", "Numero maximo de tentativas excedido.")
        return False

    def _build_ui(self) -> None:
        self.geometry("1100x680")
        self.minsize(900, 550)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_HEADER, corner_radius=0, height=HEADER_HEIGHT)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.grid_columnconfigure(2, weight=1)
        top.grid_propagate(False)

        ctk.CTkLabel(top, text="Twilio Pro",
                     font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
                     text_color=WHATSAPP_DARK_TEXT
                     ).grid(row=0, column=0, padx=16, pady=0, sticky="w")

        self.wa_indicator = ctk.CTkLabel(top, text="\u26ab SMS",
                                         font=(FONT_FAMILY, FONT_SIZE_XS, "bold"),
                                         text_color=WHATSAPP_DARK_TEXT_SECONDARY)
        self.wa_indicator.grid(row=0, column=1, padx=(4, 16), pady=0)

        self.status_label = ctk.CTkLabel(top, text="Pronto",
                                         font=(FONT_FAMILY, FONT_SIZE_SMALL),
                                         text_color=WHATSAPP_TEAL)
        self.status_label.grid(row=0, column=2, sticky="e")

        wa_btn = ctk.CTkButton(top, text="WhatsApp",
                               font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                               fg_color=WHATSAPP_TEAL, text_color="white",
                               hover_color=WHATSAPP_LIGHT_GREEN,
                               corner_radius=BORDER_RADIUS_BTN, width=90, height=32,
                               command=self._open_setup)
        wa_btn.grid(row=0, column=3, padx=4, pady=0)

        cfg_btn = ctk.CTkButton(top, text="\u2699",
                                font=(FONT_FAMILY, 18),
                                fg_color="transparent", text_color=WHATSAPP_DARK_TEXT,
                                hover_color=WHATSAPP_DARK_HOVER,
                                width=36, height=32, command=self._open_settings)
        cfg_btn.grid(row=0, column=4, padx=4, pady=0)

        help_btn = ctk.CTkButton(top, text="\u2753",
                                 font=(FONT_FAMILY, 16),
                                 fg_color="transparent", text_color=WHATSAPP_DARK_TEXT,
                                 hover_color=WHATSAPP_DARK_HOVER,
                                 width=36, height=32, command=self._open_help)
        help_btn.grid(row=0, column=5, padx=(4, 12), pady=0)

        self.contact_list = ContactListPanel(
            self,
            on_select_contact=self._on_select_contact,
            on_new_contact=self._on_new_contact,
            on_show_calls=self._show_call_log,
        )
        self.contact_list.grid(row=1, column=0, sticky="nswe")

        self.chat_view = ChatView(self, on_send_message=self._on_send_message)
        self.chat_view.grid(row=1, column=1, sticky="nswe")
        self.chat_view.master = self

        self.call_log_view = CallLogView(self, on_back=self._hide_call_log)

        self._toast_widget: Optional[ctk.CTkLabel] = None

    def _toast(self, message: str, color: str = COR_SUCCESS) -> None:
        if self._toast_widget:
            try:
                self._toast_widget.destroy()
            except Exception:
                pass
        self._toast_widget = ctk.CTkLabel(
            self, text="  " + message + "  ",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            fg_color=color, text_color="white",
            corner_radius=BORDER_RADIUS,
        )
        self._toast_widget.place(relx=0.5, rely=0.92, anchor="center")
        self.after(TOAST_DURATION, self._hide_toast)

    def _hide_toast(self) -> None:
        if self._toast_widget:
            try:
                self._toast_widget.destroy()
            except Exception:
                pass
            self._toast_widget = None

    def _open_settings(self) -> None:
        def on_save(env: dict):
            number = env.get("TWILIO_NUMBER", self._from_number)
            if number != self._from_number:
                self._from_number = number
                self.sender = TwilioSender(self._account_sid, self._auth_token, number)
            self._account_sid = env.get("TWILIO_ACCOUNT_SID", self._account_sid)
            self._auth_token = env.get("TWILIO_AUTH_TOKEN", self._auth_token)
            self._toast("Configuracoes salvas", COR_SUCCESS)
            self._check_whatsapp_status()

        SettingsDialog(self, on_save)

    def _open_help(self) -> None:
        HelpDialog(self)

    def _open_setup(self) -> None:
        def on_number_changed(number: str):
            self._from_number = number
            self.sender = TwilioSender(self._account_sid, self._auth_token, number)
            self._toast(f"Numero alterado para {number}", COR_INFO)

        def on_whatsapp_verified():
            self._update_whatsapp_indicator(True)
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(WHATSAPP_MARKER, "w") as f:
                f.write(self._from_number)
            self._toast("WhatsApp ativado!", COR_SUCCESS)

        SetupWizard(self, self._from_number,
                    on_number_changed, on_whatsapp_verified,
                    self._account_sid, self._auth_token)

    def _check_whatsapp_status(self) -> None:
        if os.path.exists(WHATSAPP_MARKER):
            self._update_whatsapp_indicator(True)

    def _update_whatsapp_indicator(self, verified: bool) -> None:
        if self.wa_indicator:
            self.wa_indicator.configure(
                text="\U0001f7e2 SMS+WA" if verified else "\u26ab SMS",
                text_color=COR_SUCCESS if verified else WHATSAPP_DARK_TEXT_SECONDARY,
            )

    def _load_data(self) -> None:
        if self.contact_list:
            self.contact_list.load_contacts()

    def _on_select_contact(self, contact: Contact) -> None:
        self.current_contact = contact
        if self.chat_view:
            self.chat_view.set_contact(contact)
        if self.current_view == "calls":
            self._hide_call_log()

    def _on_new_contact(self) -> None:
        dialog = ContactDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.contact_repo.save(dialog.result)
            if self.contact_list:
                self.contact_list.load_contacts()
            self._toast(f"Contato {dialog.result.name} salvo!", COR_SUCCESS)

    def _on_send_message(self, contact: Contact, text: str, channel: str) -> None:
        self._set_status("Enviando...")

        msg = Message(
            contact_id=contact.id, direction="sent", content=text,
            channel=channel, status="sending",
        )
        self.message_repo.save(msg)
        self.chat_view and self.chat_view.add_message(msg)
        self.contact_list and self.contact_list.refresh_last_message(contact.id)

        def send():
            if not self.sender:
                self.after(0, lambda: self._toast("Erro interno ao enviar", COR_ERROR))
                return
            try:
                sid = self.sender.send(contact.phone, text, channel)
                msg.status = "sent"
                self.message_repo.save(msg)
                self.after(0, lambda: self.chat_view and self.chat_view.set_contact(self.current_contact))
                self.after(0, lambda: self.contact_list and self.contact_list.refresh_last_message(contact.id))
                self.after(0, lambda: self._toast(f"Enviado via {channel.upper()}", COR_SUCCESS))
                self.after(0, lambda: self._set_status(""))
            except TwilioRestException as exc:
                logger.error("Erro Twilio: code=%d msg=%s", exc.code, str(exc))
                msg.status = "failed"
                self.message_repo.save(msg)
                self.after(0, lambda: self.chat_view and self.chat_view.set_contact(self.current_contact))
                err = _err_msg(exc, channel)
                self.after(0, lambda: self._toast(err, COR_ERROR))
                self.after(0, lambda: self._set_status(""))
            except Exception as exc:
                logger.exception("Falha no envio")
                msg.status = "failed"
                self.message_repo.save(msg)
                self.after(0, lambda: self.chat_view and self.chat_view.set_contact(self.current_contact))
                self.after(0, lambda: self._toast(str(exc), COR_ERROR))
                self.after(0, lambda: self._set_status(""))

        threading.Thread(target=send, daemon=True).start()

    def on_call_contact(self, contact: Contact) -> None:
        self._toast(f"Chamando {contact.name}...", COR_INFO)

        import random, time

        def call_thread():
            time.sleep(1)
            duration = random.randint(5, 300)
            log = CallLog(
                contact_id=contact.id, direction="outgoing",
                duration=duration, status="completed",
            )
            self.call_repo.save(log)
            self.after(0, lambda: self._toast(
                f"Chamada com {contact.name} - {log.duration_display}", COR_SUCCESS))

        threading.Thread(target=call_thread, daemon=True).start()

    def on_delete_chat(self, contact: Contact) -> None:
        import tkinter.messagebox as mb
        if not mb.askyesno("Apagar conversa",
                           f"Tem certeza que deseja apagar todas as\n"
                           f"mensagens com {contact.name}?"):
            return
        self.message_repo.delete_by_contact(contact.id)
        if self.chat_view:
            self.chat_view.set_contact(contact)
        if self.contact_list:
            self.contact_list.load_contacts()
        self._toast(f"Conversa com {contact.name} apagada", COR_WARNING)

    def _show_call_log(self) -> None:
        if self.chat_view:
            self.chat_view.grid_remove()
        if self.call_log_view:
            self.call_log_view.grid(row=1, column=1, sticky="nswe")
            self.call_log_view.load()
        self.current_view = "calls"

    def _hide_call_log(self) -> None:
        if self.call_log_view:
            self.call_log_view.grid_remove()
        if self.chat_view:
            self.chat_view.grid(row=1, column=1, sticky="nswe")
        self.current_view = "chat"

    def _set_status(self, text: str) -> None:
        if self.status_label:
            if text:
                self.status_label.configure(text=text)
            else:
                self.status_label.configure(text="Pronto")

    def _on_close(self) -> None:
        self.receiver.close()
        self.destroy()


def _err_msg(exc: TwilioRestException, channel: str = "sms") -> str:
    msg = str(exc)
    if exc.code == 63007:
        return f"Numero nao habilitado para {channel.upper()}. Use Setup Whats."
    if exc.code == 21211:
        return "Numero de destino invalido."
    if exc.code == 21610:
        return "Destino nao elegivel para WhatsApp."
    if exc.code == 21608:
        return "Origem nao verificado para WhatsApp."
    if exc.status == 401:
        return "Credenciais Twilio invalidas."
    if exc.status == 403:
        return "Conta Twilio suspensa."
    if exc.status == 404:
        return "Numero de origem nao encontrado na conta."
    if "not been verified" in msg.lower():
        return "WhatsApp nao verificado. Use Setup Whats."
    if "not sms capable" in msg.lower():
        return "Numero sem capacidade SMS."
    return msg
