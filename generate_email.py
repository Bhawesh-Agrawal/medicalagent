import smtplib
from email.message import EmailMessage

def send_email(subject : str, sender : str, receiver : str, body : str):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    # Send the email via SMTP server
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)