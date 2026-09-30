import json
import os
import time
from typing import Any
MODEL_NAME = os.getenv("GEMINI_FLASH_MODEL", "gemini-flash-lite-latest")


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

def _extract_json(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON array.")
    data = json.loads(text[start:end + 1])
    if not isinstance(data, list) or len(data) != 5 or not all(isinstance(item, dict) for item in data):
        raise ValueError("Gemini must return exactly five outline objects.")
    required = {"title", "scene_description", "image_prompt"}
    if any(not required.issubset(item) for item in data):
        raise ValueError("Gemini outline is missing required panel fields.")
    for number, item in enumerate(data, start=1):
        item["panel"] = number
    return data

def generate_outline(story_prompt: str, character_name: str, setting: str,
                     tone: str, art_style: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("Google Gemini SDK is not installed. Run: pip install -r requirements.txt") from exc
    client = genai.Client(api_key=api_key)

    prompt = f"""
Create a 5-panel comic outline as JSON only.

Story prompt: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return exactly a JSON array with 5 objects. Every object must contain:
panel, title, scene_description, image_prompt.

Make the story coherent from panel 1 to panel 5. The image_prompt should
describe the visual scene clearly and include the requested art style.
Do not include markdown or commentary.
"""
    response = _generate_with_retry(client, prompt)
    if not getattr(response, "text", None):
        raise RuntimeError("Gemini returned no outline text.")
    return _extract_json(response.text)
