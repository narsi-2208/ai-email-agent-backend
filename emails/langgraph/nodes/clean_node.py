from langgraph.graph import StateGraph, START, END


def clean_node(state):
    email_id = state.get("email_id")

    if not email_id:
        raise ValueError("email_id is required")

    try:
        email_id = int(email_id)
    except:
        raise ValueError("email_id must be an integer")

    state["email_id"] = email_id
    return state
