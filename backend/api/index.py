from app.main import app  # noqa: F401 — a Vercel importa "app" a partir daqui

# Nada de lógica aqui de propósito: este ficheiro existe só porque o runtime
# Python da Vercel exige um entrypoint dentro de backend/api/. A aplicação
# real continua inteira em app/main.py, igual ao que corre no Docker.
