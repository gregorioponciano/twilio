import customtkinter as ctk

from src.gui.styles import *


HELP_SECTIONS = [
    {
        "title": "Visão Geral",
        "body": (
            "Twilio Pro e um aplicativo de mensagens e chamadas que usa a API Twilio.\n"
            "Todas as configuracoes ficam no arquivo .env na raiz do projeto.\n"
            "Voce pode editar diretamente pelo botao de engrenagem (Configuracoes)."
        ),
    },
    {
        "title": "1. Credenciais Twilio (OBRIGATORIO)",
        "body": (
            "TWILIO_ACCOUNT_SID e TWILIO_AUTH_TOKEN:\n"
            " -> Acesse https://console.twilio.com\n"
            " -> Copie do dashboard (Account SID e Auth Token)\n\n"
            "TWILIO_NUMBER:\n"
            " -> Numero comprado no Twilio (ex: +14155238886)\n"
            " -> Deve estar habilitado para SMS"
        ),
    },
    {
        "title": "2. Senha do App",
        "body": (
            "APP_PASSWORD:\n"
            " -> Define a senha exigida ao iniciar o app\n"
            " -> Se estiver vazia, o login e pulado\n"
            " -> Altere quando quiser pela tela de Configuracoes"
        ),
    },
    {
        "title": "3. Numero Virtual (Opcional)",
        "body": (
            "Para comprar numeros de outros provedores:\n"
            "RECEIVE_SMS_API / NUMBERSOLO_API / SMSBIRD_API:\n"
            " -> URLs dos servicos de numero virtual\n"
            " -> Preencha as chaves de API correspondentes\n"
            " -> Use o botao WhatsApp > Comprar para testar"
        ),
    },
    {
        "title": "4. E-mail (Opcional)",
        "body": (
            "EMAIL_USER / EMAIL_PASS:\n"
            " -> Usado por alguns provedores de numero virtual\n"
            " -> Configure IMAP (padrao Gmail: imap.gmail.com:993)"
        ),
    },
    {
        "title": "5. Passo a Passo Rapido",
        "body": (
            "1. Crie uma conta em https://twilio.com\n"
            "2. Compre um numero com capacidade SMS\n"
            "3. Preencha SID, Auth Token e numero no .env\n"
            "4. Defina APP_PASSWORD (opcional)\n"
            "5. Execute: python3 main.py\n"
            "6. Use Configuracoes para alterar sem sair do app"
        ),
    },
    {
        "title": "6. Resolucao de Problemas",
        "body": (
            "Erro 63007: numero nao habilitado para o canal\n"
            "Erro 401/403: credenciais Twilio incorretas\n"
            "Erro 404: numero de origem nao encontrado\n"
            "WhatsApp nao verificado: use o botao WhatsApp\n"
            "Sempre salve as configs antes de tentar enviar"
        ),
    },
]


class HelpDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ajuda - Configuracao")
        self.geometry("520x500")
        self.configure(fg_color=WHATSAPP_DARK_BG)
        self.transient(parent)
        self._build_ui()
        self.update_idletasks()
        self.wait_visibility()
        self.grab_set()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Como Configurar o Twilio Pro",
                     font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
                     text_color=WHATSAPP_DARK_TEXT
                     ).grid(row=0, column=0, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=WHATSAPP_DARK_DIVIDER)
        scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))
        scroll.grid_columnconfigure(0, weight=1)
        fix_mousewheel(scroll)

        row = 0
        for sec in HELP_SECTIONS:
            header = ctk.CTkFrame(scroll, fg_color=WHATSAPP_DARK_HEADER,
                                  corner_radius=BORDER_RADIUS_SM)
            header.grid(row=row, column=0, sticky="ew", pady=(6, 0))
            header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(header, text=sec["title"],
                         font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                         text_color=WHATSAPP_TEAL
                         ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

            ctk.CTkLabel(header, text=sec["body"],
                         font=(FONT_FAMILY, FONT_SIZE_SMALL),
                         text_color=WHATSAPP_DARK_TEXT, justify="left",
                         wraplength=440
                         ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

            row += 1

        ctk.CTkButton(self, text="Fechar", font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                      fg_color=WHATSAPP_DARK_INPUT, text_color=WHATSAPP_DARK_TEXT,
                      hover_color=WHATSAPP_DARK_HOVER,
                      command=self.destroy
                      ).grid(row=2, column=0, pady=(10, 18))
