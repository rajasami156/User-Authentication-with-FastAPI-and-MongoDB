import os
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib

# Load environment variables
load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_MAIL_DEFAULT_SENDER = os.getenv("SMTP_MAIL_DEFAULT_SENDER")
SMTP_MAIL_USE_SSL = True

def send_recovery_email(email: str, recovery_code: str):
    message = EmailMessage()
    message["From"] = SMTP_MAIL_DEFAULT_SENDER
    message["To"] = email
    message["Subject"] = "Password Recovery Code"
    message.set_content(f"Your password recovery code is: {recovery_code}")

    try:
        with smtplib.SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT) as smtp:
            smtp.login(SMTP_USERNAME , SMTP_PASSWORD)
            smtp.send_message(message)
            return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

def test_email():
    result = send_recovery_email("nicesami156@gmail.com", "123456")

    print(result)

if __name__ == "__main__":
    test_email()
