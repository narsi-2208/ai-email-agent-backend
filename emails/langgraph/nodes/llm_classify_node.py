from emails.openai_llm import classify_email_openai

def llm_classify_node(state):
    text = state["email_text"]
    
    # Choose best model:
    result = classify_email_openai(text, model="gpt-4.1-mini")

    # OR: model="phi3"
    # OR: model="mixtral"

    state["intent"] = result["intent"]
    state["confidence"] = result["confidence"]
    state["llm_raw"] = result
    return state

