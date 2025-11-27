import logging
from datetime import timedelta
import requests
from django.utils import timezone
from django.conf import settings

from .models import UserToken

logger = logging.getLogger(__name__)


def refresh_access_token_for_user(user):
    """
    Refresh Google access token for one user.
    Handles token expiry, invalid_grant (revoked), network failures.
    Returns new access_token or None.
    """
    token = UserToken.objects.filter(user=user, provider="gmail").first()
    if not token:
        logger.warning("No UserToken found for user %s", user.id)
        return None

    if not token.refresh_token:
        logger.error("User %s has no refresh_token stored.", user.id)
        return None

    # Detect if token is still valid
    now = timezone.now()
    if token.token_expiry and token.token_expiry > (now + timedelta(minutes=5)):
        # Valid enough — return without refreshing
        return token.access_token

    try:
        refresh_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token",
        }

        r = requests.post(refresh_url, data=data, timeout=10)
        resp = r.json()

        # ❌ If refresh token is invalid or revoked
        if "error" in resp:
            error = resp.get("error")
            logger.error("Google refresh_token error for user %s: %s", user.id, resp)

            if error == "invalid_grant":
                # Google revoked refresh token → delete it & force re-auth
                token.delete()
                logger.warning("Refresh token revoked for user %s. User must reconnect Gmail.", user.id)
                return None

            return None

        # ✔ Success: Google returned new access token
        access_token = resp["access_token"]
        expires_in = int(resp.get("expires_in", 3600))

        token.access_token = access_token
        token.token_expiry = timezone.now() + timedelta(seconds=expires_in)

        # Google usually does NOT send new refresh_token here — but keep if yes
        if resp.get("refresh_token"):
            token.refresh_token = resp["refresh_token"]

        token.save(update_fields=["access_token", "token_expiry", "refresh_token"])

        logger.info("Refreshed Gmail token for user %s", user.id)
        return access_token

    except requests.RequestException as e:
        logger.exception("Network error refreshing token for user %s: %s", user.id, e)
        return None

    except Exception as e:
        logger.exception("Unexpected error refreshing token for user %s: %s", user.id, e)
        return None


def get_valid_access_token(user):
    """
    Main function to use in Gmail API calls.
    Returns a valid access token (refreshing if needed).
    """
    token = UserToken.objects.filter(user=user, provider="gmail").first()
    if not token:
        logger.warning("User %s has no Gmail connection.", user.id)
        return None

    # If access token still valid
    if token.token_expiry and token.token_expiry > timezone.now() + timedelta(seconds=30):
        return token.access_token

    # Attempt refresh
    new_token = refresh_access_token_for_user(user)
    return new_token
