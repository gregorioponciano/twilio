import os
import sys
import subprocess
import importlib.metadata
from pathlib import Path

from dotenv import load_dotenv

# --- CORREÇÃO PARA PYINSTALLER ---
# Descobre se o script está rodando congelado (como executável) ou normal (.py)
if getattr(sys, 'frozen', False):
    # Caminho da pasta onde o arquivo executável "main" está rodando
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Caminho do script original .py
    BASE_DIR = Path(__file__).resolve().parent

REQUIREMENTS_PATH = BASE_DIR / "requirements.txt"
ENV_PATH = BASE_DIR / ".env"
# ---------------------------------

def _ensure_dependencies() -> bool:
    # Se já for o executável do PyInstaller, as dependências já estão embutidas
    if getattr(sys, 'frozen', False):
        return True

    if not REQUIREMENTS_PATH.exists():
        return True
    with open(REQUIREMENTS_PATH, encoding="utf-8") as f:
        pkgs = [line.split("#")[0].strip() for line in f
                if line.strip() and not line.startswith("#")]
    missing = []
    for req in pkgs:
        name = req.split(">=")[0].split("==")[0].split("[")[0].strip()
        try:
            importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(req)
    if not missing:
        return True
    print("Instalando dependencias faltantes...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + missing)
        print("Dependencias instaladas com sucesso.")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao instalar dependencias: {exc}", file=sys.stderr)
        return False


def main() -> None:
    if not _ensure_dependencies():
        sys.exit(1)

    if not ENV_PATH.exists():
        print(f"ERRO: Arquivo .env nao encontrado em: {ENV_PATH}", file=sys.stderr)
        sys.exit(1)

    load_dotenv(ENV_PATH)

    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    number = os.getenv("TWILIO_NUMBER") or os.getenv("TWILIO_FROM_NUMBER", "")

    if not all([sid, token, number]):
        print("ERRO: Credenciais Twilio incompletas no .env", file=sys.stderr)
        print("Verifique TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN e TWILIO_NUMBER", file=sys.stderr)
        sys.exit(1)

    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    from src.gui.app import App
    app = App(sid, token, number)
    app.mainloop()


if __name__ == "__main__":
    main()
    