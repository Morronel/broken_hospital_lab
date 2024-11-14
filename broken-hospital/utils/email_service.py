import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

class EmailService:
    def __init__(self, smtp_host='127.0.0.1', smtp_port=5337):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        print(f"Email service configured to use SMTP server at {smtp_host}:{smtp_port}")

    def send_email(self, to_email, subject, html_content):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = 'noreply@brokenhospital.ctf'
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.set_debuglevel(1)
                print(f"Attempting to send email to {to_email} via {self.smtp_host}:{self.smtp_port}")
                server.send_message(msg)
                print(f"Email sent successfully to {to_email}")
                return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def send_confirmation_email(self, to_email, confirmation_token):
        subject = "Confirm Your Broken Hospital Account"
        html_content = f"""
        <h2>Welcome to Broken Hospital!</h2>
        <p>Please confirm your account by clicking the link below:</p>
        <p><a href="http://127.0.0.1:5000/confirm/{confirmation_token}">Confirm Account</a></p>
        <p>If you didn't create this account, please ignore this email.</p>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = 'noreply@brokenhospital.ctf'
        msg['To'] = to_email  # Use the exact email address, preserving any aliases
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)
                return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False