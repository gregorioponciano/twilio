from typing import Optional

import customtkinter as ctk

from src.models import Contact, Message
from src.repository import MessageRepository
from src.gui.styles import *


class MessageBubble(ctk.CTkFrame):
    def __init__(self, master, message: Message, **kwargs):
        bg = WHATSAPP_DARK_BUBBLE_SENT if message.is_sent else WHATSAPP_DARK_BUBBLE_RECEIVED
        super().__init__(master, fg_color=bg, corner_radius=BORDER_RADIUS_BUBBLE, **kwargs)
        self._setup_ui(message)

    def _setup_ui(self, message: Message) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text=message.content,
            font=(FONT_FAMILY, 13),
            text_color=WHATSAPP_DARK_TEXT, anchor="w",
            wraplength=420, justify="left",
        ).grid(row=0, column=0, padx=(12, 10), pady=(8, 2), sticky="w")

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=1, column=0, padx=(12, 10), pady=(0, 5), sticky="e")

        status_char = {
            "sent": "\u2713",
            "delivered": "\u2713\u2713",
            "failed": "\u2717",
            "sending": "\u23F3",
        }.get(message.status, "")

        status_color = {
            "sent": COR_SENT,
            "delivered": COR_DELIVERED,
            "failed": COR_FAILED,
            "sending": COR_WARNING,
        }.get(message.status, WHATSAPP_DARK_TEXT_SECONDARY)

        if status_char:
            ctk.CTkLabel(bottom, text=status_char,
                         font=(FONT_FAMILY, 10),
                         text_color=status_color).grid(row=0, column=0, padx=(0, 4))

        ctk.CTkLabel(bottom, text=message.time_display,
                     font=(FONT_FAMILY, 10),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=0, column=1)


class ChatView(ctk.CTkFrame):
    def __init__(self, master, on_send_message: callable, **kwargs):
        super().__init__(master, fg_color=WHATSAPP_DARK_CHAT_BG, corner_radius=0, **kwargs)
        self.on_send_message = on_send_message
        self.current_contact: Optional[Contact] = None
        self.message_repo = MessageRepository()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_HEADER, corner_radius=0,
                                   height=HEADER_HEIGHT)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(1, weight=1)

        self.header_avatar = ctk.CTkCanvas(self.header, width=AVATAR_SIZE_SMALL,
                                           height=AVATAR_SIZE_SMALL,
                                           highlightthickness=0, bd=0, bg=WHATSAPP_DARK_HEADER)
        self.header_avatar.grid(row=0, column=0, padx=(12, 8), pady=0)

        info_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w")
        self.header_name = ctk.CTkLabel(info_frame, text="",
                                        font=(FONT_FAMILY, 13, "bold"),
                                        text_color=WHATSAPP_DARK_TEXT, anchor="w")
        self.header_name.grid(row=0, column=0, sticky="w")
        self.header_status = ctk.CTkLabel(info_frame, text="",
                                          font=(FONT_FAMILY, 10),
                                          text_color=WHATSAPP_DARK_TEXT_SECONDARY, anchor="w")
        self.header_status.grid(row=1, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        btn_frame.grid(row=0, column=3, padx=(0, 6))

        self.call_btn = ctk.CTkButton(btn_frame, text="\u260E",
                                      font=(FONT_FAMILY, 12),
                                      fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                                      hover_color=WHATSAPP_TEAL, corner_radius=BORDER_RADIUS_BTN,
                                      width=50, height=32, command=self._on_call)
        self.call_btn.grid(row=0, column=0, padx=3)

        self.delete_btn = ctk.CTkButton(btn_frame, text="\u2716",
                                        font=(FONT_FAMILY, 12),
                                        fg_color="#522", text_color="#E88",
                                        hover_color="#733", corner_radius=BORDER_RADIUS_BTN,
                                        width=50, height=32, command=self._on_delete_chat)
        self.delete_btn.grid(row=0, column=1, padx=3)

        self.messages_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=WHATSAPP_DARK_DIVIDER,
        )
        self.messages_frame.grid(row=1, column=0, sticky="nsew")
        self.messages_frame.grid_columnconfigure(0, weight=1)
        fix_mousewheel(self.messages_frame)

        self.input_frame = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_HEADER, corner_radius=0,
                                        height=INPUT_HEIGHT)
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_propagate(False)

        channel_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        channel_frame.grid(row=0, column=0, padx=(8, 0), pady=0, sticky="w")

        self.channel_var = ctk.StringVar(value="sms")

        ctk.CTkRadioButton(channel_frame, text="SMS",
                           variable=self.channel_var, value="sms",
                           font=(FONT_FAMILY, 10),
                           fg_color=WHATSAPP_TEAL, text_color=WHATSAPP_DARK_TEXT,
                           command=self._on_channel_change).grid(row=0, column=0, padx=(0, 6))

        ctk.CTkRadioButton(channel_frame, text="WA",
                           variable=self.channel_var, value="whatsapp",
                           font=(FONT_FAMILY, 10),
                           fg_color=WHATSAPP_TEAL, text_color=WHATSAPP_DARK_TEXT).grid(row=0, column=1)

        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Digite uma mensagem...",
            font=(FONT_FAMILY, 13),
            fg_color=WHATSAPP_DARK_INPUT,
            text_color=WHATSAPP_DARK_TEXT,
            placeholder_text_color=WHATSAPP_DARK_TEXT_SECONDARY,
            border_width=0, corner_radius=BORDER_RADIUS, height=38,
        )
        self.message_entry.grid(row=0, column=1, padx=8, pady=0, sticky="ew")
        self.message_entry.bind("<KeyRelease>", self._on_input_change)
        self.message_entry.bind("<Return>", lambda e: self._on_send())

        self.char_counter = ctk.CTkLabel(self.input_frame, text="",
                                         font=(FONT_FAMILY, 9),
                                         text_color=WHATSAPP_DARK_TEXT_SECONDARY)
        self.char_counter.grid(row=0, column=1, sticky="se", padx=(0, 4), pady=(28, 0))

        self.send_btn = ctk.CTkButton(self.input_frame, text="\u25B6",
                                      font=(FONT_FAMILY, 12),
                                      fg_color=WHATSAPP_TEAL, text_color="white",
                                      hover_color=WHATSAPP_LIGHT_GREEN,
                                      corner_radius=BORDER_RADIUS_BTN,
                                      width=46, height=34, command=self._on_send)
        self.send_btn.grid(row=0, column=2, padx=(0, 8), pady=0)

        self._show_empty_state()

    def _on_channel_change(self) -> None:
        self._update_char_counter()

    def _on_input_change(self, event=None) -> None:
        self._update_char_counter()

    def _update_char_counter(self) -> None:
        text = self.message_entry.get()
        if self.channel_var.get() == "sms":
            remaining = MAX_SMS_CHARS - len(text)
            color = COR_ERROR if remaining < 0 else WHATSAPP_DARK_TEXT_SECONDARY
            self.char_counter.configure(
                text=f"{len(text)}/{MAX_SMS_CHARS}" if text else "",
                text_color=color,
            )
        else:
            self.char_counter.configure(text="")

    def _show_empty_state(self) -> None:
        for w in self.messages_frame.winfo_children():
            w.destroy()
        frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        frame.grid(row=0, column=0, pady=100)
        ctk.CTkLabel(frame, text="\U0001f4ac",
                     font=(FONT_FAMILY, 40),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=0, column=0)
        ctk.CTkLabel(frame, text="Selecione um contato",
                     font=(FONT_FAMILY, FONT_SIZE_LARGE),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=1, column=0, pady=(16, 0))
        ctk.CTkLabel(frame, text="Escolha um contato ao lado para comec\u0327ar",
                     font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=2, column=0, pady=(4, 0))

    def set_contact(self, contact: Optional[Contact]) -> None:
        self.current_contact = contact
        self._update_header()
        self._load_messages()
        self._update_char_counter()

    def _update_header(self) -> None:
        if not self.current_contact:
            self.header_name.configure(text="Twilio Pro")
            self.header_status.configure(text="")
            self.header_avatar.delete("all")
            self.call_btn.configure(state="disabled", fg_color=WHATSAPP_DARK_INPUT)
            self.delete_btn.configure(state="disabled")
            self.message_entry.configure(state="disabled", placeholder_text="")
            self.send_btn.configure(state="disabled", fg_color="#1f3a38")
            self.char_counter.configure(text="")
            return

        c = self.current_contact
        self.header_name.configure(text=c.name)
        self.header_status.configure(text=c.phone)
        self.header_avatar.delete("all")
        r = AVATAR_SIZE_SMALL // 2
        self.header_avatar.create_oval(0, 0, AVATAR_SIZE_SMALL, AVATAR_SIZE_SMALL,
                                       fill=c.avatar_color, outline="")
        self.header_avatar.create_text(r, r, text=c.initials, fill="white",
                                       font=(FONT_FAMILY, FONT_SIZE_AVATAR, "bold"))
        self.call_btn.configure(state="normal", fg_color=WHATSAPP_DARK_INPUT)
        self.delete_btn.configure(state="normal")
        self.message_entry.configure(state="normal",
                                     placeholder_text="Digite uma mensagem...")
        self.send_btn.configure(state="normal", fg_color=WHATSAPP_TEAL)

    def _load_messages(self) -> None:
        for w in self.messages_frame.winfo_children():
            w.destroy()

        if not self.current_contact:
            self._show_empty_state()
            return

        messages = self.message_repo.list_by_contact(self.current_contact.id)
        if not messages:
            frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
            frame.grid(row=0, column=0, pady=100)
            ctk.CTkLabel(frame, text="\U0001f4e9",
                         font=(FONT_FAMILY, 40),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=0, column=0)
            ctk.CTkLabel(frame, text="Nenhuma mensagem ainda",
                         font=(FONT_FAMILY, FONT_SIZE_LARGE),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=1, column=0, pady=(16, 0))
            ctk.CTkLabel(frame, text="Digite sua mensagem e pressione Enter",
                         font=(FONT_FAMILY, FONT_SIZE_SMALL),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=2, column=0, pady=(4, 0))
            return

        for i, msg in enumerate(messages):
            bubble = MessageBubble(self.messages_frame, msg)
            bubble.grid(row=i, column=0, sticky="e" if msg.is_sent else "w",
                        padx=(70 if msg.is_sent else 14, 14 if msg.is_sent else 70),
                        pady=(2, 2))

        self.after(50, lambda: self.messages_frame._parent_canvas.yview_moveto(1.0))

    def add_message(self, message: Message) -> None:
        if not self.current_contact or message.contact_id != self.current_contact.id:
            return

        for w in self.messages_frame.winfo_children():
            if isinstance(w, ctk.CTkFrame):
                children = w.winfo_children()
                if children and isinstance(children[0], ctk.CTkLabel) and (
                    "Nenhuma" in (children[0].cget("text") or "")
                ):
                    w.destroy()
                    break

        count = len(self.messages_frame.winfo_children())
        bubble = MessageBubble(self.messages_frame, message)
        bubble.grid(row=count, column=0, sticky="e" if message.is_sent else "w",
                    padx=(70 if message.is_sent else 14, 14 if message.is_sent else 70),
                    pady=(2, 2))
        self.after(50, lambda: self.messages_frame._parent_canvas.yview_moveto(1.0))

    def _on_send(self) -> None:
        if not self.current_contact:
            return
        text = self.message_entry.get().strip()
        if not text:
            return
        channel = self.channel_var.get()

        if channel == "sms" and len(text) > MAX_SMS_CHARS:
            return

        self.message_entry.delete(0, "end")
        self._update_char_counter()
        self.on_send_message(self.current_contact, text, channel)

    def _on_call(self) -> None:
        if self.current_contact and hasattr(self.master, "on_call_contact"):
            self.master.on_call_contact(self.current_contact)

    def _on_delete_chat(self) -> None:
        if self.current_contact and hasattr(self.master, "on_delete_chat"):
            self.master.on_delete_chat(self.current_contact)
