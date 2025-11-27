from django.db import models
from django.contrib.auth.models import User

class EmailMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gmail_id = models.CharField(max_length=200, unique=True)
    thread_id = models.CharField(max_length=200)
    
    sender = models.CharField(max_length=300, blank=True, null=True)
    recipient = models.CharField(max_length=300, blank=True, null=True)
    subject = models.CharField(max_length=500, blank=True, null=True)
    
    snippet = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    
    labels = models.JSONField(null=True, blank=True)
    internal_date = models.DateTimeField(null=True, blank=True)

    fetched_at = models.DateTimeField(auto_now_add=True)

    draft_message_id = models.CharField(max_length=200, blank=True, null=True)
    draft_body = models.TextField(blank=True, null=True)
    draft_created = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject} ({self.gmail_id})"
    
class EmailIntent(models.Model):
    email = models.OneToOneField(EmailMessage, on_delete=models.CASCADE)
    intent = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.0)
    raw_response = models.JSONField(null=True, blank=True)
    classified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email.subject} → {self.intent}"

