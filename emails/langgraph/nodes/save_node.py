from langgraph.graph import StateGraph, START, END

from emails.models import EmailIntent

def save_node(state):
    email_obj = state["email_obj"]
    intent = state["intent"]
    confidence = state["confidence"]
    raw = state["llm_raw"]

    obj, _ = EmailIntent.objects.update_or_create(
        email=email_obj,
        defaults={
            "intent": intent,
            "confidence": confidence,
            "raw_response": raw
        }
    )

    state["intent_obj"] = obj
    return state

