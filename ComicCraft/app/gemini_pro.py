import os
import time
MODEL_NAME = os.getenv("GEMINI_PRO_MODEL", "gemini-flash-lite-latest")


def _generate_with_retry(client, prompt: str):
    """Retry only transient Gemini capacity failures."""
    for attempt in range(3):
        try:
            return client.models.generate_content(model=MODEL_NAME, contents=prompt)
        except Exception as exc:
            message = str(exc).upper()
            transient = "503" in message or "UNAVAILABLE" in message or "HIGH DEMAND" in message
            if not transient or attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))

def generate_story(outline, character_name: str, tone: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("Google Gemini SDK is not installed. Run: pip install -r requirements.txt") from exc
    client = genai.Client(api_key=api_key)

    prompt = f"""
Expand this 5-panel outline into a complete comic story.

Character: {character_name}
Tone: {tone}

For each panel return:
PANEL N: <title>
CAPTION: <short ambient caption>
NARRATION: <2-4 sentences>
DIALOGUE: <short character dialogue>

Keep the character, setting and story continuity consistent.
Do not invent additional panels.

Outline:
{outline}
"""
    response = _generate_with_retry(client, prompt)
    if not getattr(response, "text", None):
        raise RuntimeError("Gemini returned no story text.")
    return response.text.strip()
