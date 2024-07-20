import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:

    def __init__(
        self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587
    ) -> None:
        """Initialize the EmailSender with SMTP server details.

        Args:
            smtp_server (str, optional): The SMTP server address. Defaults to 'smtp.gmail.com'.
            smtp_port (int, optional): The SMTP server port. Defaults to 587.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(
        self,
        username: str,
        password: str,
        sender_mail: str,
        receiver_mail: str,
        subject: str,
        content_body: str,
        attachment: str = None,
    ) -> bool:
        """Send an email using SMTP.

        Args:
            username (str): Username for SMTP login.
            password (str): Password for SMTP login.
            sender_mail (str): Email address of the sender.
            receiver_mail (str): Email address of the receiver.
            subject (str): Subject of the email.
            content_body (str): Body content of the email.
            attachment (str): Path of file to attach

        Raises:
            ValueError: If SMTP login credentials are not set.
            ValueError: If SMTP login credentials are invalid.
            ValueError: For other errors during the email sending process.

        Returns:
            bool: Status of email sent
        """
        try:
            if not username or not password:
                raise ValueError("SMTP login credentials must be provided")

            mail = smtplib.SMTP(self.smtp_server, self.smtp_port)
            mail.ehlo()
            mail.starttls()
            mail.login(username, password)

            msg = MIMEMultipart()
            msg["From"] = sender_mail
            msg["To"] = receiver_mail
            msg["Subject"] = subject
            msg.attach(MIMEText(content_body, "plain"))

            if attachment:
                filename = os.path.basename(attachment)
                attachment = open(attachment, "rb")
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", f"attachment; filename={filename}"
                )
                msg.attach(part)

            mail.sendmail(sender_mail, receiver_mail, msg.as_string())
            mail.close()
            return True
        except smtplib.SMTPAuthenticationError as auth_error:
            raise ValueError(
                "Failed to authenticate with the SMTP server: Invalid login credentials"
            ) from auth_error
        except Exception as exc:
            raise ValueError("Unable to send the mail") from exc
