import re
from django.utils import timezone
from emails.services import create_gmail_draft
import html


def extract_email(address):
    match = re.search(r'[\w\.-]+@[\w\.-]+', address or "")
    return match.group(0) if match else None


def format_reply_as_html(text: str):
    """Convert plaintext AI reply into Gmail-ready HTML with proper spacing."""
    if not text:
        return ""

    # Escape unsafe characters
    safe = html.escape(text)

    # Split into paragraphs by double newline
    paragraphs = safe.split("\n\n")

    html_paragraphs = []
    for p in paragraphs:
        # Replace single newlines inside a paragraph with <br>
        p_html = p.replace("\n", "<br>")
        html_paragraphs.append(
            f"<p style='margin:0 0 12px; font-family:Arial; font-size:14px;'>{p_html}</p>"
        )

    return "<div style='font-family:Arial; font-size:14px; line-height:1.5;'>" + "".join(html_paragraphs) + "</div>"


def reply_save_draft_node(state):
    email_obj = state["email_obj"]
    user = email_obj.user

    # Clean up 'to' email
    raw_sender = state.get("to_address") or email_obj.sender
    clean_email = extract_email(raw_sender) or user.email

    subject = state.get("subject") or f"Re: {email_obj.subject}"

    # ⭐ Convert AI plaintext reply → HTML
    raw_reply = state.get("reply_text", "")
    body_html = format_reply_as_html(raw_reply)

    thread_id = state.get("thread_id")

    # Create Gmail draft
    result = create_gmail_draft(
        user=user,
        to_address=clean_email,
        subject=subject,
        body_html=body_html,
        thread_id=thread_id
    )

    # Save in DB
    email_obj.draft_message_id = result.get("id")
    email_obj.draft_body = body_html
    email_obj.draft_created = timezone.now()
    email_obj.save(
        update_fields=["draft_message_id", "draft_body", "draft_created"]
    )

    state["draft_result"] = result
    return state
