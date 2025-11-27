from celery import shared_task
from django.contrib.auth.models import User
from .services import list_messages, save_email_to_db
from accounts.services import get_valid_access_token
from emails.models import EmailMessage, EmailIntent
from emails.langgraph.reply_graph import run_reply_agent
import logging


logger = logging.getLogger(__name__)

@shared_task
def sync_gmail_inbox():
    """
    Periodic task that goes through all users with Gmail connected,
    fetches their email list, and stores emails in DB.
    """
    from accounts.models import UserToken

    gmail_users = UserToken.objects.filter(provider="gmail")

    total_saved = 0

    for token in gmail_users:
        user = token.user

        # Ensure access token is valid
        access_token = get_valid_access_token(user)
        if not access_token:
            logger.warning(f"User {user.id} has invalid token. Skipping.")
            continue

        logger.info(f"Syncing Gmail for user {user.email}")

        # Fetch latest messages (limit 20 to avoid heavy load)
        result = list_messages(user, max_results=20)
        messages = result.get("messages", [])

        for msg in messages:
            email_obj, created = save_email_to_db(user, msg)
            if created:
                total_saved += 1

    logger.info(f"Gmail sync complete — {total_saved} new emails saved.")
    return {"saved": total_saved}

# @shared_task
# def generate_reply_for_unreplied_emails():
#     """
#     Find emails with an intent that do not have a draft yet (you can add a flag or check labels)
#     and generate drafts for them.
#     """
#     # This example selects EmailMessages without an EmailIntentDraft marker.
#     # If you need a more robust check (e.g., check if EmailIntent exists but no draft), adapt accordingly.
#     unprocessed = EmailMessage.objects.filter(emailintent__isnull=False)  # all classified
#     count = 0
#     for em in unprocessed:
#         # You may want to track if draft already created (via a model field). For now, run and log.
#         try:
#             resp = run_reply_agent(em.id)
#             logger.info("Generated draft for email %s: %s", em.id, resp.get("draft"))
#             count += 1
#         except Exception as exc:
#             logger.exception("Failed to generate draft for email %s: %s", em.id, exc)
#     return {"generated": count}


@shared_task
def run_full_agent_for_user(user_id, limit=20):
    """
    Runs full agent ONLY for one user (intent + reply + draft).
    """
    from django.contrib.auth.models import User
    from emails.models import EmailMessage
    from emails.langgraph.full_agent_graph import run_full_email_agent

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"error": "User not found"}

    # process only this user's emails
    emails_to_process = (
        EmailMessage.objects.filter(user=user, emailintent__isnull=True)
        .order_by("-internal_date")[:limit]
    )

    processed = 0
    failed = 0

    for email_obj in emails_to_process:
        try:
            run_full_email_agent(email_obj.id)
            processed += 1
        except Exception as exc:
            failed += 1

    return {"user": user.email, "processed": processed, "failed": failed}
