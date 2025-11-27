from django.urls import path
from .views import GmailListMessages, GmailGetMessage, GmailSyncEmails, GenerateReplyDraftAgent, RunFullAgent, GetEmailById

urlpatterns = [
    path("list/", GmailListMessages.as_view()),
    path("detail/<int:email_id>/", GetEmailById.as_view()),
    path("sync/", GmailSyncEmails.as_view()),
    path("agent/reply/<int:email_id>/", GenerateReplyDraftAgent.as_view()),
    path("agent/full/", RunFullAgent.as_view()),

]
