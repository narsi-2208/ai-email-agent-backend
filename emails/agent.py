from .langgraph.graph import build_intent_graph
import logging

logger = logging.getLogger(__name__)

def run_intent_agent_for_email(email_id):
    g = build_intent_graph()

    # some LangGraph APIs allow `g.run(inputs)` or `g.execute(initial_node, ...)`
    # We'll try a common approach: run graph with inputs
    inputs = {"email_id": email_id}
    try:
        result = g.run(inputs)  # adjust if your LangGraph uses different API
        return {"ok": True, "result": result}
    except Exception as e:
        logger.exception("Agent run failed for email %s: %s", email_id, e)
        return {"ok": False, "error": str(e)}
