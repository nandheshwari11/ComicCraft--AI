import os
import re
import textwrap
from pathlib import Path
from PIL import Image
from PIL import ImageDraw, ImageFont

_pipeline = None

def _safe_filename(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")
    return text[:80] or "panel"

def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    import torch
    from diffusers import StableDiffusionPipeline

    model_id = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    kwargs = {"torch_dtype": dtype}
    _pipeline = StableDiffusionPipeline.from_pretrained(model_id, **kwargs)

    if torch.cuda.is_available():
        _pipeline = _pipeline.to("cuda")
    else:
        _pipeline = _pipeline.to("cpu")

    return _pipeline

def _placeholder_image(prompt: str, path: Path) -> None:
    """Create a local preview panel when a diffusion model is not configured."""
    width, height = 1024, 640
    image = Image.new("RGB", (width, height), "#181a36")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((36, 36, width - 36, height - 36), 32, fill="#2b2f5c", outline="#ffd166", width=5)
    draw.ellipse((90, 125, 330, 365), fill="#ef476f")
    draw.ellipse((690, 260, 925, 495), fill="#06d6a0")
    draw.polygon([(420, 185), (590, 115), (705, 225), (570, 365), (430, 320)], fill="#ffd166")
    font = ImageFont.load_default()
    wrapped = textwrap.wrap(prompt, width=55)[:5]
    draw.text((88, 440), "COMICCRAFT PREVIEW", fill="#ffd166", font=font)
    draw.multiline_text((88, 475), "\n".join(wrapped), fill="white", font=font, spacing=8)
    image.save(path)

def generate_image(prompt: str, filename: str | None = None) -> str:
    output_dir = Path(__file__).resolve().parent.parent / "static" / "panels"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = filename or _safe_filename(prompt)
    if not filename.lower().endswith(".png"):
        filename += ".png"

    path = output_dir / filename

    mode = os.getenv("COMICCRAFT_IMAGE_MODE", "placeholder").lower()
    if mode == "placeholder":
        _placeholder_image(prompt, path)
        return "/static/panels/" + filename
    if mode != "stable-diffusion":
        raise RuntimeError("COMICCRAFT_IMAGE_MODE must be 'placeholder' or 'stable-diffusion'.")

    pipe = _get_pipeline()
    enhanced = (
        f"{prompt}, clean comic illustration, expressive characters, "
        "clear composition, detailed background, high quality"
    )
    image = pipe(
        enhanced,
        num_inference_steps=int(os.getenv("SD_STEPS", "25")),
        guidance_scale=float(os.getenv("SD_GUIDANCE", "7.5"))
    ).images[0]

    image.save(path)
    return "/static/panels/" + filename
