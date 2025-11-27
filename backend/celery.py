from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# ----------------------------------------
# BASE SCHEDULE (STATIC TASKS)
# ----------------------------------------

app.conf.beat_schedule = {
    "refresh-gmail-tokens-every-10-minutes": {
        "task": "accounts.tasks.refresh_all_user_tokens",
        "schedule": 600.0,
    },

    "sync-gmail-every-5-min": {
        "task": "emails.tasks.sync_gmail_inbox",
        "schedule": 300.0,
    },
}



# ----------------------------------------
# DYNAMIC PER-USER TASKS
# ----------------------------------------

def setup_user_schedules():
    from accounts.models import UserToken  # import inside
    for ut in UserToken.objects.filter(provider="gmail"):
        app.conf.beat_schedule[f"run-full-agent-for-user-{ut.user.id}"] = {
            "task": "emails.tasks.run_full_agent_for_user",
            "schedule": 300.0,
            "args": (ut.user.id,)
        }


@app.on_after_finalize.connect
def load_dynamic_schedules(sender, **kwargs):
    """
    Runs AFTER celery app loads all tasks.
    Dynamically adds 1 schedule per Gmail user.
    """
    setup_user_schedules()
