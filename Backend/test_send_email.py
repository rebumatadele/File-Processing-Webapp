# test_send_email.py

import asyncio
from app.utils.email_utils import send_email

async def test_email():
    subject = "Test Email"
    recipients = ["rebumatadele4@gmail.com"]
    body = "<p>This is a test email sent from the FastAPI application.</p>"

    try:
        await send_email(subject, recipients, body)
        print("Test email sent successfully.")
    except Exception as e:
        print(f"Failed to send test email: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())
