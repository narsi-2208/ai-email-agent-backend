# full_agent_graph.py

from langgraph.graph import StateGraph, START, END

from emails.langgraph.graph import intent_graph
from emails.langgraph.reply_graph import reply_graph
from emails.models import EmailMessage


def build_full_agent_graph():
    g = StateGraph(dict)

    # run intent graph first
    g.add_node("intent_agent", intent_graph)

    # then run reply graph
    g.add_node("reply_agent", reply_graph)

    g.add_edge(START, "intent_agent")
    g.add_edge("intent_agent", "reply_agent")
    g.add_edge("reply_agent", END)

    return g.compile()


full_agent_graph = build_full_agent_graph()


def run_full_email_agent(email_id: int):
    initial = {"email_id": email_id}
    final = full_agent_graph.invoke(initial)

    return {
        "email_id": email_id,
        "intent": final.get("intent"),
        "confidence": final.get("confidence"),
        "reply_text": final.get("reply_text"),
        "draft": final.get("draft_result")
    }