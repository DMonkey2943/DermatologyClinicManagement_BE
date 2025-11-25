# app/utils/email.py
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

async def send_email_async(to_email: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = settings.email_from
    message["To"] = to_email
    message["Subject"] = subject

    # Nội dung HTML (có thể tùy chỉnh)
    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.email_host,
            port=settings.email_port,
            start_tls=True,
            username=settings.email_username,
            password=settings.email_password,
        )
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")  # Log lỗi, không raise để tránh block create