from django.contrib import admin
from .models import EmailMessage, EmailIntent


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "subject",
        "sender",
        "internal_date",
        "draft_message_id",
        "has_draft",
    )

    list_filter = ("user", "internal_date")
    search_fields = ("subject", "sender", "recipient", "gmail_id")

    readonly_fields = (
        "gmail_id",
        "thread_id",
        "snippet",
        "body",
        "labels",
        "internal_date",
        "draft_message_id",
        "draft_body",
        "draft_created",
    )

    def has_draft(self, obj):
        return bool(obj.draft_message_id)
    has_draft.boolean = True  # shows ✓ / ✗


@admin.register(EmailIntent)
class EmailIntentAdmin(admin.ModelAdmin):
    list_display = ("email", "intent", "confidence")
    search_fields = ("email__subject", "intent")
