import re

def _panel_text(story: str, panel_number: int) -> str:
    pattern = rf"PANEL\s*{panel_number}\s*:(.*?)(?=PANEL\s*\d+\s*:|$)"
    match = re.search(pattern, story, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else story

def build_comic_layout(image_paths, story, outline):
    layout = []
    for i, panel in enumerate(outline, start=1):
        layout.append({
            "panel": i,
            "title": panel.get("title", f"Panel {i}"),
            "scene_description": panel.get("scene_description", ""),
            "image_prompt": panel.get("image_prompt", ""),
            "image_path": image_paths[i - 1] if i - 1 < len(image_paths) else "",
            "text": _panel_text(story, i),
        })
    return layout
