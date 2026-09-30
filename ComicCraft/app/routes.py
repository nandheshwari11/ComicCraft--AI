import asyncio
import uuid
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.main import templates
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()

class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=3, max_length=1_500)
    character_name: str = Field(min_length=1, max_length=100)
    setting: str = Field(min_length=1, max_length=100)
    tone: str = Field(min_length=1, max_length=100)
    art_style: str = Field(min_length=1, max_length=100)

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

async def create_comic(data: PromptRequest):
    outline = await asyncio.to_thread(
        generate_outline,
        data.story_prompt, data.character_name, data.setting,
        data.tone, data.art_style
    )
    story = await asyncio.to_thread(generate_story, outline, data.character_name, data.tone)

    comic_id = uuid.uuid4().hex[:12]
    image_paths = await asyncio.gather(*[
        asyncio.to_thread(generate_image, panel["image_prompt"], f"{comic_id}_panel_{i}.png")
        for i, panel in enumerate(outline, start=1)
    ])

    layout = build_comic_layout(image_paths, story, outline)
    pdf_path = await asyncio.to_thread(save_pdf, layout)
    return layout, pdf_path

@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )
        layout, pdf_path = await create_comic(data)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"layout": layout, "pdf_path": pdf_path}
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)}
        )

@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):
    try:
        layout, pdf_path = await create_comic(data)
        return JSONResponse({"success": True, "layout": layout, "pdf_path": pdf_path})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/export-success")
async def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_path": pdf_path}
    )

@router.get("/test-image")
async def test_image(prompt: str = "A brave fox in an enchanted forest, anime comic style"):
    try:
        path = generate_image(prompt, "test_panel.png")
        return {"success": True, "image_path": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
