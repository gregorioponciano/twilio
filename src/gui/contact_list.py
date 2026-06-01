from typing import Callable, Optional

import customtkinter as ctk

from src.models import Contact
from src.repository import ContactRepository, MessageRepository
from src.gui.styles import *


class ContactItem(ctk.CTkFrame):
    def __init__(self, master, contact: Contact, last_msg: str, last_time: str,
                 is_active: bool, on_click: Callable[[Contact], None], **kwargs):
        super().__init__(master,
                         fg_color=WHATSAPP_DARK_ACTIVE if is_active else "transparent",
                         corner_radius=0, height=CONTACT_ITEM_HEIGHT, **kwargs)
        self.contact = contact
        self.on_click_fn = on_click
        self._is_active = is_active
        self._setup_ui(contact, last_msg, last_time)
        self._bind_events()

    def _setup_ui(self, contact: Contact, last_msg: str, last_time: str) -> None:
        self.grid_columnconfigure(2, weight=1)
        self.grid_propagate(False)

        canvas = ctk.CTkCanvas(self, width=AVATAR_SIZE, height=AVATAR_SIZE,
                               highlightthickness=0, bd=0, bg=WHATSAPP_DARK_SIDEBAR)
        canvas.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=11, sticky="w")
        r = AVATAR_SIZE // 2
        canvas.create_oval(0, 0, AVATAR_SIZE, AVATAR_SIZE, fill=contact.avatar_color, outline="")
        canvas.create_text(r, r, text=contact.initials, fill="white",
                           font=(FONT_FAMILY, FONT_SIZE_AVATAR, "bold"))

        ctk.CTkLabel(self, text=contact.name,
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=WHATSAPP_DARK_TEXT, anchor="w"
                     ).grid(row=0, column=2, sticky="sw", pady=(14, 0))

        ctk.CTkLabel(self, text=last_time,
                     font=(FONT_FAMILY, 10),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY, anchor="e"
                     ).grid(row=0, column=3, sticky="se", padx=(0, 14), pady=(14, 0))

        preview = last_msg or "Sem mensagens"
        if len(preview) > 45:
            preview = preview[:45] + "\u2026"
        ctk.CTkLabel(self, text=preview,
                     font=(FONT_FAMILY, 11),
                     text_color=WHATSAPP_DARK_TEXT_SECONDARY, anchor="w"
                     ).grid(row=1, column=2, columnspan=2, sticky="nw", pady=(0, 14))

        ctk.CTkFrame(self, height=1, fg_color=WHATSAPP_DARK_DIVIDER
                     ).grid(row=2, column=0, columnspan=4, sticky="ew")

    def _bind_events(self) -> None:
        def on_enter(e):
            if not self._is_active:
                self.configure(fg_color=WHATSAPP_DARK_HOVER)
        def on_leave(e):
            if not self._is_active:
                self.configure(fg_color="transparent")
        def on_click(e):
            self.on_click_fn(self.contact)

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.bind("<Button-1>", on_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", on_click, add="+")

    def set_active(self, active: bool) -> None:
        self._is_active = active
        self.configure(fg_color=WHATSAPP_DARK_ACTIVE if active else "transparent")


class ContactListPanel(ctk.CTkFrame):
    def __init__(self, master, on_select_contact: Callable[[Contact], None],
                 on_new_contact: Callable[[], None],
                 on_show_calls: Callable[[], None], **kwargs):
        super().__init__(master, fg_color=WHATSAPP_DARK_SIDEBAR, corner_radius=0, width=320, **kwargs)
        self.on_select_contact = on_select_contact
        self.on_new_contact = on_new_contact
        self.on_show_calls = on_show_calls
        self.contact_repo = ContactRepository()
        self.message_repo = MessageRepository()
        self.selected_contact: Optional[Contact] = None
        self.contact_widgets: dict[int, ContactItem] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        search_frame = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_HEADER, corner_radius=0,
                                    height=HEADER_HEIGHT)
        search_frame.grid(row=0, column=0, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_propagate(False)

        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar ou comec\u0327ar conversa",
            font=(FONT_FAMILY, 12),
            fg_color=WHATSAPP_DARK_INPUT,
            text_color=WHATSAPP_DARK_TEXT,
            placeholder_text_color=WHATSAPP_DARK_TEXT_SECONDARY,
            border_width=0, corner_radius=BORDER_RADIUS, height=34,
        )
        self.search_entry.grid(row=0, column=0, padx=10, pady=11, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())

        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=WHATSAPP_DARK_DIVIDER,
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        fix_mousewheel(self.list_frame)

        bottom = ctk.CTkFrame(self, fg_color=WHATSAPP_DARK_HEADER, corner_radius=0, height=56)
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.grid_columnconfigure((0, 1, 2), weight=1)
        bottom.grid_propagate(False)

        ctk.CTkButton(bottom, text="Chamadas",
                      font=(FONT_FAMILY, FONT_SIZE_SMALL),
                      fg_color="transparent", text_color=WHATSAPP_DARK_TEXT,
                      hover_color=WHATSAPP_DARK_HOVER,
                      command=self.on_show_calls
                      ).grid(row=0, column=0, padx=4, pady=10, sticky="ew")

        ctk.CTkButton(bottom, text="+ Novo",
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                      fg_color=WHATSAPP_TEAL, text_color="white",
                      hover_color=WHATSAPP_LIGHT_GREEN,
                      corner_radius=BORDER_RADIUS_BTN,
                      command=self.on_new_contact
                      ).grid(row=0, column=2, padx=4, pady=10, sticky="ew")

    def load_contacts(self) -> None:
        self._rebuild(self.contact_repo.list_all())

    def _on_search(self) -> None:
        query = self.search_entry.get().strip()
        contacts = self.contact_repo.search(query) if query else self.contact_repo.list_all()
        self._rebuild(contacts)

    def _rebuild(self, contacts: list[Contact]) -> None:
        for w in self.contact_widgets.values():
            w.destroy()
        self.contact_widgets.clear()

        last_msgs = self.message_repo.last_for_each_contact()

        if not contacts:
            query = self.search_entry.get().strip()
            if query:
                msg = f'Nenhum resultado para "{query}"'
            else:
                msg = "Nenhum contato\nClique em + Novo para adicionar"
            lbl = ctk.CTkLabel(self.list_frame, text=msg,
                               font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                               text_color=WHATSAPP_DARK_TEXT_SECONDARY, justify="center")
            lbl.grid(row=0, column=0, pady=40, padx=20)
            return

        for contact in contacts:
            msg = last_msgs.get(contact.id)
            last_text = msg.content[:45] + "\u2026" if msg and len(msg.content) > 45 else (msg.content or "")
            last_time = msg.time_display if msg else ""
            is_active = self.selected_contact and self.selected_contact.id == contact.id
            item = ContactItem(
                self.list_frame, contact, last_text, last_time, is_active,
                on_click=self._on_contact_click,
            )
            item.grid(row=len(self.contact_widgets), column=0, sticky="ew")
            self.contact_widgets[contact.id] = item

    def _on_contact_click(self, contact: Contact) -> None:
        self.selected_contact = contact
        for cid, w in self.contact_widgets.items():
            w.set_active(cid == contact.id)
        self.on_select_contact(contact)

    def refresh_last_message(self, contact_id: int) -> None:
        msg = self.message_repo.last_for_contact(contact_id)
        item = self.contact_widgets.get(contact_id)
        if item and msg:
            for child in item.winfo_children():
                if isinstance(child, ctk.CTkLabel) and child.cget("text") in (
                    item.contact.name,
                ):
                    continue
