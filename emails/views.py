from rest_framework.views import APIView
from rest_framework.response import Response
from .services import list_messages, get_message_detail, list_messages, save_email_to_db
from emails.langgraph.reply_graph import run_reply_agent
from emails.tasks import run_full_agent_for_user

class GmailListMessages(APIView):
    def get(self, request):
        user = request.user

        from emails.models import EmailMessage

        # Fetch emails ONLY for logged-in user
        emails = EmailMessage.objects.filter(user=user).order_by("-internal_date")

        result = []
        for em in emails:
            result.append({
                "id": em.id,
                "gmail_id": em.gmail_id,
                "thread_id": em.thread_id,
                "subject": em.subject,
                "sender": em.sender,
                "snippet": em.snippet,
                "body": em.body,
                "internal_date": em.internal_date,

                # ⭐ Draft fields
                "draft_message_id": em.draft_message_id,
                "draft_body": em.draft_body,
                "draft_created": em.draft_created,
            })

        return Response({"messages": result, "count": len(result)})
    
class GetEmailById(APIView):
    def get(self, request, email_id):
        from emails.models import EmailMessage, EmailIntent

        try:
            em = EmailMessage.objects.get(id=email_id, user=request.user)
        except EmailMessage.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        # Get intent (if exists)
        try:
            intent_obj = EmailIntent.objects.get(email=em)
            intent_data = {
                "intent": intent_obj.intent,
                "confidence": intent_obj.confidence,
            }
        except EmailIntent.DoesNotExist:
            intent_data = {
                "intent": None,
                "confidence": None,
            }

        return Response({
            "id": em.id,
            "gmail_id": em.gmail_id,
            "thread_id": em.thread_id,
            "subject": em.subject,
            "sender": em.sender,
            "recipient": em.recipient,
            "snippet": em.snippet,
            "body": em.body,

            # ⭐ Draft
            "draft_message_id": em.draft_message_id,
            "draft_body": em.draft_body,
            "draft_created": em.draft_created,

            # ⭐ Intent
            "intent": intent_data["intent"],
            "confidence": intent_data["confidence"],
        })


class GmailGetMessage(APIView):
    def get(self, request, msg_id):
        user = request.user
        data = get_message_detail(user, msg_id)
        return Response(data)

class GmailSyncEmails(APIView):
    def get(self, request):
        user = request.user
        
        # get list of messages
        msg_list = list_messages(user).get("messages", [])
        
        saved = []
        for msg in msg_list:
            email_obj, created = save_email_to_db(user, msg)
            saved.append({
                "gmail_id": email_obj.gmail_id,
                "subject": email_obj.subject,
                "created": created
            })

        return Response({
            "synced": len(saved),
            "messages": saved
        })
    
    
class GenerateReplyDraftAgent(APIView):
    def post(self, request, email_id):
        # optional: check that email belongs to request.user for security
        try:
            result = run_reply_agent(email_id)
            return Response({"ok": True, "result": result})
        except Exception as e:
            return Response({"ok": False, "error": str(e)}, status=500)


class RunFullAgent(APIView):
    def post(self, request):
        user = request.user
        run_full_agent_for_user.delay(user.id)
        return Response({"ok": True, "message": "Agent started for your inbox"})
