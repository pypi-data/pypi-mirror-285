import os
import pytest
from dotenv import load_dotenv
from elsai_agent_hub.tools.email_sender import EmailSender

load_dotenv()


@pytest.fixture
def input_credentials():
    sender = os.getenv("SENDER_EMAIL")
    receiver = os.getenv("RECEIVER_EMAIL")
    login = os.getenv("LOGIN_MAIL")
    password = os.getenv("PASSWORD")
    subject = "Test Mail!"
    body = "Hey Howdy!"
    return (sender, receiver, login, password, subject, body)


def test_send_email(input_credentials):
    sender, receiver, login, password, subject, body = input_credentials
    response = EmailSender().send_email(
        username=login,
        password=password,
        sender_mail=sender,
        receiver_mail=receiver,
        subject=subject,
        content_body=body,
    )
    assert response == True
