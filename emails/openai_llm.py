import json
import re
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

INTENT_SYSTEM_PROMPT = """
You are a highly accurate professional email intent classifier.

Given an email (subject + body), classify it into exactly ONE of the following categories:

- meeting       (scheduling, rescheduling, availability, calendar coordination)
- billing       (payments, invoices, charges, receipts, subscriptions)
- complaint     (issues, concerns, dissatisfaction, negative experience)
- marketing     (promotions, announcements, outreach, offers)
- task          (action items, work requests, to-dos)
- follow-up     (checking in, reminders, follow-through)
- personal      (non-work personal communication)
- spam          (irrelevant, unsolicited, suspicious emails)
- inquiry       (question, request for information, asking details)

STRICT RULES:
1. Always respond ONLY in JSON.
2. Intent must be EXACTLY one of the categories above.
3. Confidence must be a float between 0 and 1.
4. Keep output clean and machine-parsable.

Example output:
{
  "intent": "inquiry",
  "confidence": 0.92
}
"""



def classify_email_openai(text: str, model="gpt-4.1-mini"):
    """Return {'intent': '', 'confidence': float}"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
    )

    output = resp.choices[0].message.content.strip()

    # Try to parse JSON
    try:
        return json.loads(output)
    except:
        match = re.search(r"\{.*\}", output, re.S)
        if match:
            return json.loads(match.group(0))
        return {"intent": "unknown", "confidence": 0.0}



def generate_reply_openai(system_prompt: str, user_prompt: str, model="gpt-4.1"):
    """
    Generate well-formatted email reply using OpenAI.
    """

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    reply = resp.choices[0].message.content.strip()

    # Remove accidental code fences
    reply = re.sub(r"^```.*?\n", "", reply)
    reply = re.sub(r"```$", "", reply)

    return reply
