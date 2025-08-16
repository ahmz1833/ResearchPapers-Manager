from app import create_app
from dotenv import load_dotenv  # type: ignore
import os

# Load .env if present
load_dotenv()

app = create_app()

# Basic startup info (evaluated at import)
print(f"[wsgi] Starting app={app.config.get('APP_NAME')} env={os.getenv('FLASK_ENV')}")

# Gunicorn entrypoint exposes 'app'. For local debugging run: python wsgi.py
def main():  # pragma: no cover
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

if __name__ == "__main__":  # pragma: no cover
    main()
