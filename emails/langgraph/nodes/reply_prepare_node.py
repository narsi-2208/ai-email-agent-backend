from emails.models import EmailMessage, EmailIntent

def reply_prepare_node(state):
    """
    Prepare a world-class email reply prompt for OpenAI.
    Produces:
    - state["prompt"]
    - state["email_obj"]
    - state["to_address"]
    - state["subject"]
    - state["thread_id"]
    """
    email_id = state.get("email_id")
    if not email_id:
        raise ValueError("email_id required")

    # Fetch email
    try:
        email_obj = EmailMessage.objects.get(id=email_id)
    except EmailMessage.DoesNotExist:
        raise ValueError(f"Email {email_id} not found")

    # Intent resolution
    intent = state.get("intent")
    if not intent:
        ei = EmailIntent.objects.filter(email=email_obj).first()
        if ei:
            intent = ei.intent

    # Extract data
    subject = email_obj.subject or "(No Subject)"
    sender = email_obj.sender or "(Unknown Sender)"
    body = email_obj.body or email_obj.snippet or ""
    thread_id = email_obj.thread_id


    system_prompt = """
You are an expert email-writing assistant.
Your job is to write exceptionally clear, polished, helpful emails.

Rules:
- Tone: professional, polite, confident, human.
- Format: 2–5 short paragraphs, each separated by a blank line.
- Keep sentences crisp and easy to read.
- No markdown, no emojis.
- Do NOT include greetings (like "Hi"), sign-offs, or names unless they already exist.
- Avoid robotic tone.
- Do NOT include placeholders like [NAME].
- Reply directly to the sender’s intent.
"""

    # ---------------------------------------------
    # USER PROMPT: FULL EMAIL CONTEXT
    # ---------------------------------------------
    user_prompt = f"""
Write a professional email reply to the following message.

Subject: {subject}
From: {sender}

Email content:
\"\"\"
{body}
\"\"\"

Detected intent: {intent if intent else "unknown"}

Your reply must:
- Address the sender’s request
- Offer helpful next steps
- Use clear professional tone
- Be written as natural English
- Contain multiple paragraphs with line breaks

Write the reply body only.
"""

    # Save to state
    state["email_obj"] = email_obj
    state["prompt"] = {
        "system": system_prompt.strip(),
        "user": user_prompt.strip(),
    }
    state["to_address"] = sender
    state["subject"] = f"Re: {subject}"
    state["thread_id"] = thread_id

    return state
