# app/utils/email_utils.py

import os
import aiosmtplib
from email.message import EmailMessage
from typing import List
from pydantic import EmailStr
from app.settings import settings
from app.utils.error_utils import handle_error
from app.utils.retry_decorator import retry
import traceback  # For detailed error logging

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
    message["From"] = str(settings.mail_from)
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
        if settings.mail_ssl:
            smtp = aiosmtplib.SMTP(
                hostname=settings.mail_server,
                port=settings.mail_port,
                use_tls=True,  # SSL/TLS directly
                username=settings.mail_username,
                password=settings.mail_password,
            )
        else:
            smtp = aiosmtplib.SMTP(
                hostname=settings.mail_server,
                port=settings.mail_port,
                use_tls=False,
                start_tls=settings.mail_tls,
                username=settings.mail_username,
                password=settings.mail_password,
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
