from langgraph.graph import StateGraph, START, END
from emails.langgraph.nodes.reply_prepare_node import reply_prepare_node
from emails.langgraph.nodes.reply_generate_node import reply_generate_node
from emails.langgraph.nodes.reply_save_draft_node import reply_save_draft_node

def build_reply_graph():
    workflow = StateGraph(dict)
    workflow.add_node("prepare", reply_prepare_node)
    workflow.add_node("generate", reply_generate_node)
    workflow.add_node("save_draft", reply_save_draft_node)

    workflow.add_edge(START, "prepare")
    workflow.add_edge("prepare", "generate")
    workflow.add_edge("generate", "save_draft")
    workflow.add_edge("save_draft", END)

    return workflow.compile()

reply_graph = build_reply_graph()

def run_reply_agent(email_id: int):
    initial = {"email_id": email_id}
    final = reply_graph.invoke(initial)
    return {
        "email_id": email_id,
        "draft": final.get("draft_result"),
        "reply_text": final.get("reply_text")
    }
