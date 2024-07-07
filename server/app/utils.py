"""
chat utility helper functions
"""

# import smtplib
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder
import aiosmtplib
from email.message import EmailMessage
# from typing import List
# from fastapi import BackgroundTasks, FastAPI
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
# from starlette.responses import JSONResponse

# from app.models import EmailSchema
from app.settings import settings

HASHER = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_passwd_hash(passwd: str) -> str:
    """
    returns the hash of the password
    """
    return HASHER.hash(passwd)


def verify_passwd(passwd: str, passwd_hash: str) -> bool:
    """
    verifies the password
    """
    return HASHER.verify(passwd, passwd_hash)


def encode_input(data) -> dict:
    data = jsonable_encoder(data)
    data = {k: v for k, v in data.items() if v is not None}
    return data


async def send_email(subject: str, recipient: str, body: str):
    message = EmailMessage()
    message["From"] = settings.FROM_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.FROM_EMAIL,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
    )


# conf = ConnectionConfig(
#     MAIL_USERNAME=settings.SMTP_USERNAME,
#     MAIL_PASSWORD=settings.SMTP_PASSWORD,
#     MAIL_FROM=settings.FROM_EMAIL,
#     MAIL_PORT=settings.SMTP_PORT,
#     MAIL_SERVER=settings.SMTP_HOST,
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
# )
# async def send_email(subject: str, email: List, body: str):
#     message = MessageSchema(
#         recipients=email,
#         subject = subject,
#         body= f"<p>{body}</p>",
#         subtype=MessageType.html

#     )

#     fm = FastMail(conf)
#     await fm.send_message(message)
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})


# async def send_em(subject: str, recipient: str, body: str):
#     try:
#         with smtplib.SMTP(settings.SMTP_HOST, 587) as server:
#             server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
#             server.sendmail(settings.FROM_EMAIL, recipient, body)
#     except Exception as e:
#         print(f"Failed to send email: {e}")
#         raise
