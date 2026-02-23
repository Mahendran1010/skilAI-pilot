import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

class EmailService:

    def __init__(self):
        self.sender_email = os.getenv("EMAIL_ADDRESS")
        self.sender_password = os.getenv("EMAIL_PASSWORD")

    def send_schedule_email(self, recipient_email, schedule_text):
        try:
            msg = EmailMessage()
            msg["Subject"] = "📅 Your Optimized Schedule"
            msg["From"] = self.sender_email
            msg["To"] = recipient_email

            msg.set_content(f"""
Hello,

Here is your AI Optimized Schedule:

{schedule_text}

Stay productive 🚀
            """)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print("Email Error:", e)
            return False