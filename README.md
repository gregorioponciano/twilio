# Twilio OTP Bot

Automação para gerenciamento de SMS e OTPs utilizando Twilio, provedores de números virtuais e captura automática de códigos de verificação.

## Funcionalidades

- Integração com API do Twilio para envio/recebimento de SMS
- Suporte a múltiplos provedores de números virtuais (ReceiveSMS, NumberSolo, SMSBird)
- Captura automática de OTPs via e-mail (IMAP)
- Extração de códigos de verificação com regex e OCR (Tesseract)
- Automação com Selenium para interação em páginas web

## Pré-requisitos

- Python 3.10+
- ChromeDriver (para Selenium)
- Tesseract OCR (para captura de OTPs por imagem)

## Instalação

```bash
git clone https://github.com/gregorioponciano/twilio.git
cd twilio
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Configuração

Copie o arquivo de exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com suas chaves do Twilio, provedores de SMS e credenciais de e-mail.

## Uso

```bash
python main.py
```

## Estrutura

```
twilio/
├── main.py              # Ponto de entrada
├── src/
│   ├── cli.py           # CLI principal
│   ├── config.py        # Configurações
│   ├── manager.py       # Gerenciador principal
│   ├── exceptions.py    # Exceções personalizadas
│   ├── providers/       # Provedores de SMS
│   └── extractors/      # Extratores de OTP
├── .env.example         # Exemplo de configuração
├── requirements.txt     # Dependências
└── venv/                # Ambiente virtual
```

## Aviso

Use apenas para fins educacionais ou com autorização. Respeite os termos de serviço dos provedores utilizados.
