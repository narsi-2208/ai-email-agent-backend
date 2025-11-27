# reply_generate_node.py

from emails.openai_llm import generate_reply_openai


def reply_generate_node(state):
    prompt = state.get("prompt")
    if not prompt:
        raise ValueError("prompt missing in state")

    system_msg = prompt["system"]
    user_msg = prompt["user"]

    # ❗ Get raw plaintext reply (with natural newlines)
    reply_text = generate_reply_openai(system_msg, user_msg)

    # ❗ DO NOT convert newlines to <br> here
    reply_text = reply_text.strip()

    state["reply_text"] = reply_text
    return state
