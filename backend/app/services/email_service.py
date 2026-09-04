import logging

from app.core.config import settings

logger = logging.getLogger("zuri.email")


class EmailService:
    """
    ESTADO ATUAL: simulado — não envia nenhum email real, só regista no log.
    Quando tiveres SMTP configurado (SMTP_HOST + SMTP_USER), troca o corpo de
    send() pelo envio real via smtplib. Nada fora deste ficheiro muda.
    """

    def __init__(self):
        self.is_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    def send(self, to: str, subject: str, body: str) -> None:
        if not self.is_configured:
            logger.info("[EMAIL SIMULADO] Para: %s | Assunto: %s\n%s", to, subject, body)
            return

        # TODO (produção): envio real via SMTP
        # import smtplib
        # from email.mime.text import MIMEText
        # msg = MIMEText(body)
        # msg["Subject"] = subject
        # msg["From"] = settings.SMTP_FROM
        # msg["To"] = to
        # with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        #     server.starttls()
        #     server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        #     server.send_message(msg)
        raise NotImplementedError("Envio real de email ainda não configurado")

    def send_password_reset(self, to: str, reset_token: str) -> None:
        link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        self.send(
            to=to,
            subject="Zuri Wallet — recuperação de senha",
            body=f"Recebemos um pedido para repor a tua senha. Se foste tu, usa este link (válido por 1 hora):\n{link}\n\nSe não foste tu, ignora este email.",
        )
