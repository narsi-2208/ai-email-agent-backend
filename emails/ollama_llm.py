import ollama
import json

INTENT_SYSTEM_PROMPT = """
You are an email intent classifier.

Given an email (subject + body), classify it into EXACTLY one category:
- meeting
- billing
- complaint
- marketing
- task
- follow-up
- personal
- spam
- inquiry

Respond ONLY in JSON:
{
  "intent": "",
  "confidence": 0.0
}
"""

def classify_email_ollama(text, model = "llama3.1"):
    """
    Main function to classify intent using local ollama model.
    Default: llama3.1 (recommended)
    """
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
    )

    output = response["message"]["content"]

    # Try direct JSON load
    try:
        return json.loads(output)
    except:
        # Try to extract JSON
        import re
        json_str = re.search(r"\{.*\}", output, re.S).group(0)
        return json.loads(json_str)
