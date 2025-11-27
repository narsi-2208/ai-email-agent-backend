import requests
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserToken
from .models import EmailMessage
from django.utils import timezone
import base64
from email.mime.text import MIMEText
from django.conf import settings
from email.mime.multipart import MIMEMultipart


GOOGLE_GMAIL_API = "https://www.googleapis.com/gmail/v1/users/me"


def get_valid_access_token(user):
    """Return a fresh access token, refreshing it if needed."""
    token = UserToken.objects.filter(user=user, provider="gmail").first()
    if not token:
        return None

    # if token expired, refresh it
    if token.token_expiry <= timezone.now():
        refresh_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token",
        }
        r = requests.post(refresh_url, data=data).json()
        token.access_token = r["access_token"]
        token.token_expiry = timezone.now(
        ) + timedelta(seconds=r["expires_in"])
        token.save()

    return token.access_token


def list_messages(user, max_results=10):
    """Fetch email message metadata from Gmail."""
    access_token = get_valid_access_token(user)
    if not access_token:
        return {"error": "User is not connected to Gmail."}

    url = f"{GOOGLE_GMAIL_API}/messages?maxResults={max_results}&q=-label:DRAFT"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers).json()
    return response


def get_message_detail(user, message_id):
    """Fetch full email message including headers + snippet."""
    access_token = get_valid_access_token(user)
    if not access_token:
        return {"error": "User is not connected to Gmail."}

    url = f"{GOOGLE_GMAIL_API}/messages/{message_id}?format=full"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers).json()
    return response


def extract_email_details(message):
    headers = message.get("payload", {}).get("headers", [])
    data = {
        "subject": "",
        "sender": "",
        "recipient": "",
        "body": "",
    }

    # extract headers
    for h in headers:
        if h["name"] == "Subject":
            data["subject"] = h["value"]
        if h["name"] == "From":
            data["sender"] = h["value"]
        if h["name"] == "To":
            data["recipient"] = h["value"]

    # extract body
    body_data = message["payload"].get("parts", [])
    body_text = ""

    for part in body_data:
        if part["mimeType"] == "text/plain":
            import base64
            raw = part["body"]["data"]
            decoded = base64.urlsafe_b64decode(raw + "===")
            body_text += decoded.decode("utf-8", errors="ignore")

    data["body"] = body_text
    return data


def save_email_to_db(user, msg):
    gmail_id = msg["id"]
    thread_id = msg["threadId"]

    full_msg = get_message_detail(user, gmail_id)

    # ⭐️ Skip Gmail drafts
    if "DRAFT" in full_msg.get("labelIds", []):
        return None, False

    details = extract_email_details(full_msg)

    email_obj, created = EmailMessage.objects.update_or_create(
        user=user,
        gmail_id=gmail_id,
        defaults={
            "thread_id": thread_id,
            "sender": details["sender"],
            "recipient": details["recipient"],
            "subject": details["subject"],
            "snippet": full_msg.get("snippet", ""),
            "body": details["body"],
            "labels": full_msg.get("labelIds", []),
            "internal_date": timezone.datetime.fromtimestamp(
                int(full_msg.get("internalDate", "0")) / 1000
            ),
        },
    )

    return email_obj, created


# ... existing functions: get_valid_access_token, list_messages, get_message_detail, save_email_to_db, etc.


def create_gmail_draft(user, to_address, subject, body_html, thread_id=None):
    access_token = get_valid_access_token(user)
    if not access_token:
        return {"error": "no_valid_token"}

    # ⭐ Gmail requires multipart for HTML to render properly
    message = MIMEMultipart("alternative")
    message["To"] = to_address
    message["Subject"] = subject

    # Add ONLY the HTML part — Gmail will format it correctly
    html_part = MIMEText(body_html, "html", "utf-8")
    message.attach(html_part)

    raw_bytes = message.as_bytes()
    raw = base64.urlsafe_b64encode(raw_bytes).decode("utf-8").rstrip("=")

    payload = {"message": {"raw": raw}}
    if thread_id:
        payload["message"]["threadId"] = thread_id

    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()
