from typing import Callable

import customtkinter as ctk

from src.repository import CallLogRepository, ContactRepository
from src.gui.styles import *


class CallLogView(ctk.CTkFrame):
    def __init__(self, master, on_back: Callable[[], None], **kwargs):
        super().__init__(master, fg_color=WHATSAPP_DARK_CHAT_BG, corner_radius=0, **kwargs)
        self.on_back = on_back
        self.call_repo = CallLogRepository()
        self.contact_repo = ContactRepository()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_HEADER, corner_radius=0, height=HEADER_HEIGHT)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(header, text="\u2190 Voltar", font=(FONT_FAMILY, FONT_SIZE_SMALL),
                      fg_color="transparent", text_color=WHATSAPP_TEAL,
                      hover_color=WHATSAPP_DARK_HOVER, corner_radius=BORDER_RADIUS_BTN,
                      width=80, height=30, command=self.on_back
                      ).grid(row=0, column=0, padx=8, pady=0)

        ctk.CTkLabel(header, text="Histo\u0301rico de Chamadas",
                     font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                     text_color=WHATSAPP_DARK_TEXT, anchor="w"
                     ).grid(row=0, column=1, sticky="w", padx=(4, 0), pady=0)

        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=WHATSAPP_DARK_DIVIDER,
        )
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        fix_mousewheel(self.scroll)

    def load(self) -> None:
        for w in self.scroll.winfo_children():
            w.destroy()

        logs = self.call_repo.list_all()
        if not logs:
            frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
            frame.grid(row=0, column=0, pady=80)
            ctk.CTkLabel(frame, text="\U0001f4de",
                         font=(FONT_FAMILY, 40),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=0, column=0)
            ctk.CTkLabel(frame, text="Nenhuma chamada registrada",
                         font=(FONT_FAMILY, FONT_SIZE_LARGE),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=1, column=0, pady=(16, 0))
            ctk.CTkLabel(frame, text="As ligac\u0327o\u0303es aparecem aqui ao clicar em Ligar",
                         font=(FONT_FAMILY, FONT_SIZE_SMALL),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=2, column=0, pady=(4, 0))
            return

        for i, log in enumerate(logs):
            contact = self.contact_repo.get_by_id(log.contact_id)
            name = contact.name if contact else f"ID {log.contact_id}"
            phone = contact.phone if contact else ""

            item = ctk.CTkFrame(self.scroll, fg_color="transparent", corner_radius=0, height=60)
            item.grid(row=i, column=0, sticky="ew", padx=0, pady=0)
            item.grid_columnconfigure(1, weight=1)
            item.grid_propagate(False)

            icon = "\u260E" if log.direction == "outgoing" else "\U0001f4f1"

            status_color = WHATSAPP_DARK_TEXT
            if log.status == "missed":
                status_color = COR_ERROR
            elif log.status == "completed":
                status_color = COR_SUCCESS

            ctk.CTkLabel(item, text=icon, font=(FONT_FAMILY, FONT_SIZE_LARGE),
                         text_color=status_color).grid(row=0, column=0, padx=(16, 10))

            ctk.CTkLabel(item, text=name, font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                         text_color=WHATSAPP_DARK_TEXT, anchor="w"
                         ).grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(item, text=f"{phone}  |  {log.time_display}",
                         font=(FONT_FAMILY, 10),
                         text_color=WHATSAPP_DARK_TEXT_SECONDARY
                         ).grid(row=0, column=2, padx=(8, 8), sticky="w")

            if log.duration_display:
                ctk.CTkLabel(item, text=log.duration_display, font=(FONT_FAMILY, 10),
                             text_color=WHATSAPP_DARK_TEXT_SECONDARY
                             ).grid(row=0, column=3, padx=(0, 16), sticky="e")

            ctk.CTkFrame(item, height=1, fg_color=WHATSAPP_DARK_DIVIDER
                         ).grid(row=1, column=0, columnspan=4, sticky="ew")
