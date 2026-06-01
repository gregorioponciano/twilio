from typing import Optional

import customtkinter as ctk

from src.models import AVAILABLE_COLORS, Contact
from src.gui.styles import *


class ContactDialog(ctk.CTkToplevel):
    def __init__(self, parent, contact: Optional[Contact] = None):
        super().__init__(parent)
        self.contact = contact
        self.result: Optional[Contact] = None
        self.selected_color = contact.avatar_color if contact else AVAILABLE_COLORS[0]
        self._setup_ui()

    def _setup_ui(self) -> None:
        is_edit = self.contact is not None
        self.title("Editar Contato" if is_edit else "Novo Contato")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color=WHATSAPP_DARK_BG)
        self.transient(self.master)
        self.update_idletasks()
        self.wait_visibility()
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Editar Contato" if is_edit else "Novo Contato",
                             font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
                             text_color=WHATSAPP_DARK_TEXT)
        title.grid(row=0, column=0, pady=(24, 16))

        fields = ctk.CTkFrame(self, fg_color="transparent")
        fields.grid(row=1, column=0, padx=32, pady=0, sticky="ew")
        fields.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fields, text="Nome",
                     font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=0, column=0, padx=(0, 8), pady=(0, 2), sticky="w")
        self.name_entry = ctk.CTkEntry(fields, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                                       placeholder_text="Ex: Maria Silva",
                                       fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                                       border_width=0, corner_radius=BORDER_RADIUS_SM, height=36)
        self.name_entry.grid(row=1, column=0, columnspan=2, pady=(0, 12), sticky="ew")
        if self.contact:
            self.name_entry.insert(0, self.contact.name)

        ctk.CTkLabel(fields, text="Telefone",
                     font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=2, column=0, padx=(0, 8), pady=(0, 2), sticky="w")
        self.phone_entry = ctk.CTkEntry(fields, font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                                        placeholder_text="+5511999999999",
                                        fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                                        border_width=0, corner_radius=BORDER_RADIUS_SM, height=36)
        self.phone_entry.grid(row=3, column=0, columnspan=2, pady=(0, 16), sticky="ew")
        if self.contact:
            self.phone_entry.insert(0, self.contact.phone)

        ctk.CTkLabel(fields, text="Cor do avatar",
                     font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY).grid(row=4, column=0, padx=(0, 8), pady=(0, 4), sticky="w")

        color_frame = ctk.CTkFrame(fields, fg_color="transparent")
        color_frame.grid(row=5, column=0, columnspan=2, pady=(0, 8), sticky="w")

        for i, color in enumerate(AVAILABLE_COLORS):
            btn = ctk.CTkButton(color_frame, text="", width=28, height=28,
                                fg_color=color, hover_color=color,
                                corner_radius=14, command=lambda c=color: self._select_color(c))
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=3)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=2, column=0, pady=(16, 24))

        ctk.CTkButton(btns, text="Cancelar", font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                       fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                       hover_color=WHATSAPP_DARK_HOVER, corner_radius=BORDER_RADIUS_BTN,
                       width=110, command=self.destroy).grid(row=0, column=0, padx=6)

        ctk.CTkButton(btns, text="Salvar", font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                       fg_color=WHATSAPP_TEAL, text_color="white",
                       hover_color=WHATSAPP_GREEN, corner_radius=BORDER_RADIUS_BTN,
                       width=110, command=self._on_save).grid(row=0, column=1, padx=6)

        self.bind("<Return>", lambda e: self._on_save())
        self.name_entry.focus_set()

    def _select_color(self, color: str) -> None:
        self.selected_color = color

    def _on_save(self) -> None:
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not name:
            self._show_error("O nome e\u0301 obrigato\u0301rio")
            return
        if not phone:
            self._show_error("O telefone e\u0301 obrigato\u0301rio")
            return
        if not phone.startswith("+"):
            self._show_error("Formato: +5511999999999")
            return

        if self.contact:
            self.result = self.contact
            self.result.name = name
            self.result.phone = phone
            self.result.avatar_color = self.selected_color
        else:
            self.result = Contact(
                name=name,
                phone=phone,
                avatar_color=self.selected_color,
            )
        self.destroy()

    def _show_error(self, msg: str) -> None:
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkLabel) and w.cget("text_color") == "#FF5252":
                w.destroy()
        ctk.CTkLabel(self, text=msg, font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     text_color="#FF5252").grid(row=3, column=0, pady=(0, 8))
