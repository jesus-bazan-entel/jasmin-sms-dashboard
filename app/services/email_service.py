from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.config = settings
        # In a real app, you would initialize your SMTP client here
        logger.info("EmailService initialized")

    async def send_password_reset_email(self, email_to: str, token: str):
        # This is a placeholder. In a real application, you would use
        # a library like aiosmtplib to send an actual email.
        reset_link = f"{settings.BASE_URL}/reset-password?token={token}"

        subject = "Password Reset Request"
        body = f"Please use the following link to reset your password: {reset_link}"

        logger.info(f"--- FAKE EMAIL ---")
        logger.info(f"To: {email_to}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body}")
        logger.info(f"--------------------")

        # This simulates a successful email send for now
        return True

# You can create a single instance to be used across the app
email_service = EmailService()
