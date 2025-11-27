from langgraph.graph import StateGraph, START, END
from emails.langgraph.nodes.clean_node import clean_node
from emails.langgraph.nodes.fetch_node import fetch_node
from emails.langgraph.nodes.llm_classify_node import llm_classify_node
from emails.langgraph.nodes.save_node import save_node


def build_intent_graph():

    workflow = StateGraph(dict)

    # Register nodes
    workflow.add_node("clean", clean_node)
    workflow.add_node("fetch", fetch_node)
    workflow.add_node("classify", llm_classify_node)
    workflow.add_node("save", save_node)

    # Define graph flow
    workflow.add_edge(START, "clean")
    workflow.add_edge("clean", "fetch")
    workflow.add_edge("fetch", "classify")
    workflow.add_edge("classify", "save")
    workflow.add_edge("save", END)

    return workflow.compile()


intent_graph = build_intent_graph()

# Entry point


def run_intent_agent(email_id: int):
    initial_state = {"email_id": email_id}
    final_state = intent_graph.invoke(initial_state)
    return {
        "email_id": email_id,
        "intent": final_state["intent"],
        "confidence": final_state["confidence"]
    }
