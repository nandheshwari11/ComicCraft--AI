# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a story prompt into a five-panel comic and downloadable PDF:
1. User enters story prompt, character, setting, tone and art style.
2. Gemini creates a structured 5-panel outline.
3. Gemini expands the outline into narration/dialogue.
4. Stable Diffusion (or local preview art) generates an illustration for each panel.
5. The layout builder combines images and story text.
6. FPDF exports the comic as a PDF.

## 1. Requirements

- Python 3.10+
- A Gemini API key
- For Stable Diffusion: a suitable GPU is strongly recommended.
- Sufficient disk space for the model.

## 2. Install

### Windows
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 3. Configure

Copy `.env.example` to `.env` and add your Gemini API key. Environment variables are loaded automatically. For compatibility with the existing IDE setup, `env/new.env` is also recognized, but a project-level `.env` is recommended.

`COMICCRAFT_IMAGE_MODE=placeholder` is the default and produces local preview panels without a GPU or a large Hugging Face download. Set it to `stable-diffusion` to use the configured Stable Diffusion model.
When enabling it, install the optional model stack first:

```bash
pip install -r requirements-stable-diffusion.txt
```

## 4. Run

```bash
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## 5. Test image generation

Open:

```text
http://127.0.0.1:8000/test-image?prompt=A%20brave%20fox%20in%20an%20enchanted%20forest
```

## Important

Stable Diffusion v1.5 is large and local image generation can be slow on CPU.
For a GPU machine, CUDA-enabled PyTorch is recommended.

The model names in this starter project mirror the supplied project document.
If a model is unavailable in your current Google/Hugging Face account, update
the corresponding environment variable rather than changing the application flow.

## Development check

```bash
python -m compileall app
```

Generated images and PDFs are saved in `static/panels` and `static/exports`. Image filenames are unique per comic, so simultaneous requests do not overwrite one another.
