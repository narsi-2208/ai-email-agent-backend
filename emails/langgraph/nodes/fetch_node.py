from langgraph.graph import StateGraph, START, END
from emails.models import EmailMessage

def fetch_node(state):
    email_id = state["email_id"]
    try:
        email_obj = EmailMessage.objects.get(id=email_id)
    except EmailMessage.DoesNotExist:
        raise ValueError(f"Email with ID {email_id} does not exist")

    state["email_obj"] = email_obj
    state["email_text"] = f"Subject: {email_obj.subject}\n\nBody:\n{email_obj.body}"
    return state
