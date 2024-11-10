# app/utils/email_utils.py

import os
import aiosmtplib
from email.message import EmailMessage
from typing import List
from pydantic import EmailStr
from pydantic_settings import BaseSettings
from app.utils.file_utils import handle_error
from app.utils.retry_decorator import retry
from dotenv import load_dotenv
import traceback  # For detailed error logging

# Load environment variables
load_dotenv()

class EmailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    class Config:
        env_prefix = ''  # No prefix, adjust if your env variables have a prefix

# Initialize email settings
try:
    email_settings = EmailSettings()
except Exception as e:
    handle_error("EmailSettingsError", f"Failed to load email settings: {e}")
    raise e

@retry(max_retries=3, initial_wait=2, backoff_factor=2, exceptions=(aiosmtplib.SMTPException,))
async def send_email(
    subject: str,
    recipients: List[str],  # Changed to List[str] since we're using plain strings
    body: str,
    attachments: List[str] = None
):
    """
    Sends an email with optional attachments using aiosmtplib.

    Args:
        subject (str): Subject of the email.
        recipients (List[str]): List of recipient email addresses.
        body (str): Body of the email in HTML format.
        attachments (List[str], optional): List of file paths to attach. Defaults to None.
    """
    message = EmailMessage()
    message["From"] = str(email_settings.MAIL_FROM)
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body, subtype="html")

    # Attach files if any
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    message.add_attachment(
                        file_data,
                        maintype="application",
                        subtype="octet-stream",
                        filename=file_name
                    )
            except FileNotFoundError:
                handle_error("AttachmentError", f"Attachment file not found: {file_path}")
            except Exception as e:
                handle_error("AttachmentError", f"Failed to attach file {file_path}: {e}")

    try:
        # Determine if SSL is needed
        if email_settings.MAIL_SSL:
            smtp = aiosmtplib.SMTP(
                hostname=email_settings.MAIL_SERVER,
                port=email_settings.MAIL_PORT,
                use_tls=True,  # SSL/TLS directly
                username=email_settings.MAIL_USERNAME,
                password=email_settings.MAIL_PASSWORD,
            )
        else:
            smtp = aiosmtplib.SMTP(
                hostname=email_settings.MAIL_SERVER,
                port=email_settings.MAIL_PORT,
                use_tls=False,
                start_tls=email_settings.MAIL_TLS,
                username=email_settings.MAIL_USERNAME,
                password=email_settings.MAIL_PASSWORD,
            )

        await smtp.connect()
        await smtp.send_message(message)
        await smtp.quit()
        print("Email sent successfully.")  # Debug log
    except aiosmtplib.SMTPException as e:
        error_trace = traceback.format_exc()
        handle_error("EmailError", f"Failed to send email: {e}\n{error_trace}")
        raise e  # To trigger retry
    except Exception as e:
        error_trace = traceback.format_exc()
        handle_error("EmailError", f"Unexpected error when sending email: {e}\n{error_trace}")
        raise e  # To trigger retry
