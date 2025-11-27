from celery import shared_task
from datetime import timedelta
from django.utils import timezone
import logging

from .models import UserToken
from .services import refresh_access_token_for_user

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def refresh_all_user_tokens(self):
    """
    Cron job: refresh Gmail access tokens for all users whose tokens
    will expire within next 15 minutes.
    Run every 10 minutes in celery beat.
    """
    window = timezone.now() + timedelta(minutes=15)

    tokens = UserToken.objects.filter(
        provider="gmail",
        token_expiry__lte=window   # expiring soon
    )

    refreshed = 0
    deleted = 0

    for t in tokens:
        user = t.user
        try:
            new_token = refresh_access_token_for_user(user)
            if new_token:
                refreshed += 1
            else:
                # Possibly invalid_grant → token deleted inside service
                if not UserToken.objects.filter(user=user, provider="gmail").exists():
                    deleted += 1
        except Exception as e:
            logger.exception("Failed during token refresh for user %s: %s", user.id, e)

    logger.info("Token refresh summary → refreshed: %s, removed invalid: %s", refreshed, deleted)

    return {"refreshed": refreshed, "invalid_removed": deleted}
