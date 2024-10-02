import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.context import CryptContext
import secrets
import string
from dotenv import load_dotenv
import os
from fastapi.responses import FileResponse
from fastapi import HTTPException
from datetime import timedelta
from starlette.templating import Jinja2Templates

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def send_email(recipient_email, subject, email_body):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    try:
        # Establish a secure SMTP connection
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Enable encryption (TLS)
            server.login(smtp_username, smtp_password)

            # Construct the message
            message = MIMEMultipart()
            message["From"] = smtp_username
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(email_body, "html"))

            # Send the email
            server.sendmail(smtp_username, recipient_email, message.as_string())

        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")


def new_account_email(recipient_email, firstname, password):
    # Get request data
    subject = "New Account Created"
    template = templates.get_template("acount_creation_template.html")
    email_body = template.render(
        subject=subject,
        username=recipient_email,
        password=password,
        firstname=firstname,
    )
    send_email(recipient_email, subject, email_body)


def password_change_email(recipient_email, firstname, password):
    # Get request data
    subject = "Password Changed"
    # Render the email template with dynamic data
    template = templates.get_template("password_reset_template.html")
    email_body = template.render(
        subject=subject,
        password=password,
        firstname=firstname,
    )
    send_email(recipient_email, subject, email_body)


def approve_drug_licence(recipient_email, firstname, product):
    # Get request data
    subject = "Drug Product Licence Application Approval Request"

    # Render the email template with dynamic data
    template = templates.get_template("product_licence_approval_template.html")
    email_body = template.render(
        subject=subject,
        product_id=product.id,
        product=product.product_name,
        firstname=firstname,
    )
    send_email(recipient_email, subject, email_body)


def approve_purchase_order_email(
    recipient_email, firstname, requester_detail, request_detail
):
    # Get request data
    subject = "Request for your action"

    # Render the email template with dynamic data
    template = templates.get_template("request_approval_template.html")
    email_body = template.render(
        subject=subject,
        request_id=request_detail.id,
        request=request_detail.request,
        requester=requester_detail.firstname,
        firstname=firstname,
    )
    send_email(recipient_email, subject, email_body)


def reject_request_email(recipient_email, firstname, request_detail):
    # Get request data
    subject = "Request returned for your action"

    # Render the email template with dynamic data
    template = templates.get_template("request_reject_template.html")
    email_body = template.render(
        subject=subject,
        request_id=request_detail.id,
        request=request_detail.request,
        firstname=firstname,
    )
    send_email(recipient_email, subject, email_body)


def generate_random_password(length=12):
    if length < 12:
        raise ValueError("Password length should be at least 12 characters")
    return "".join(
        secrets.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(length)
    )


def validate_file_path(file_path):
    """
    Helper function to validate the file path.
    """
    if not isinstance(file_path, str):
        raise HTTPException(status_code=500, detail="Invalid file path")


def download_file(file_path, filename):
    """
    Helper function to handle file download.
    """
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")


def set_cookie(response, name, value, expires_in_minutes):
    response.set_cookie(
        name,
        value,
        expires=timedelta(minutes=expires_in_minutes).total_seconds(),
        path="/",
        secure=False,
        httponly=True,
        samesite="lax",
    )
