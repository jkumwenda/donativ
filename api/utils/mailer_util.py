import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.context import CryptContext
from fastapi import HTTPException
from starlette.templating import Jinja2Templates
from fastapi import HTTPException
from dotenv import load_dotenv
from datetime import datetime  # Import datetime to get the current year

load_dotenv()

YEAR = datetime.now().year

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def send_email(recipient_email, subject, email_body):
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", 25))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            message = MIMEMultipart()
            message["From"] = smtp_username
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(email_body, "html"))
            server.sendmail(smtp_username, recipient_email,
                            message.as_string())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send email. Error: {str(e)}")


def new_account_email(recipient_email, firstname, password):
    subject = "Welcome to Donativ"
    template = templates.get_template("acount_creation_template.html")
    email_body = template.render(
        subject=subject,
        username=recipient_email,
        password=password,
        firstname=firstname,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)


def reset_password_request_email(recipient_email, firstname, reset_token):
    subject = "Password Reset Request"
    template = templates.get_template("password_reset_request_template.html")
    email_body = template.render(
        subject=subject,
        username=recipient_email,
        firstname=firstname,
        reset_token=reset_token,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)


def password_reset_email(recipient_email, firstname):
    subject = "Your Donativ Account password has been reset"
    template = templates.get_template("password_reset_template.html")
    email_body = template.render(
        subject=subject,
        firstname=firstname,
        email=recipient_email,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)


def account_verification_email(recipient_email, firstname):
    subject = "Your Donativ Account has been verified"
    template = templates.get_template(
        "account_verification_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)


def account_verification_request_email(recipient_email, firstname, verification_token):
    subject = "Accout Verification Request"
    template = templates.get_template(
        "account_verification_request_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        verification_token=verification_token,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)


def organisation_verification_request_email(recipient_email, firstname, organisation):
    subject = "Organisation Verification Request"
    template = templates.get_template(
        "organisation_verification_request_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        organisation=organisation.organisation,
        organisation_id=organisation.id,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)


def organisation_approval_status_email(recipient_email, firstname, organisation, status):
    subject = "Organisation Approval Status"
    template = templates.get_template(
        "organisation_approval_status_template.html")
    email_body = template.render(
        subject=subject,
        email=recipient_email,
        firstname=firstname,
        organisation=organisation.organisation,
        organisation_id=organisation.id,
        status=status,
        year=YEAR,
    )
    send_email(recipient_email, subject, email_body)
