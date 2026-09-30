from datetime import datetime
from pathlib import Path
import unicodedata
from fpdf import FPDF


def _pdf_text(value: str) -> str:
    """Make AI prose safe for FPDF's portable built-in Helvetica font."""
    replacements = str.maketrans({
        "—": "-", "–": "-", "…": "...", "“": '"', "”": '"', "‘": "'", "’": "'",
    })
    normalized = unicodedata.normalize("NFKD", str(value).translate(replacements))
    return normalized.encode("latin-1", "replace").decode("latin-1")

def save_pdf(layout):
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "static" / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = output_dir / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.multi_cell(0, 10, _pdf_text(f"Panel {panel['panel']}: {panel['title']}"))

        image_path = base_dir / panel["image_path"].removeprefix("/")
        if Path(image_path).exists():
            pdf.image(image_path, x=15, y=35, w=180)
            pdf.ln(125)

        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(0, 7, _pdf_text(panel["scene_description"]))
        pdf.ln(3)

        pdf.set_font("Arial", "", 10)
        clean_text = panel["text"].replace("**", "")
        pdf.multi_cell(0, 7, _pdf_text(clean_text))

    pdf.output(str(output_path))
    return "/static/exports/" + filename
