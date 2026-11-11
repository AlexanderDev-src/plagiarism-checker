from pathlib import Path

from fpdf import FPDF

FONT = Path(__file__).parent / "fonts" / "NotoSansThai-Regular.ttf"


def cell(pdf: FPDF, h: float, text: str) -> None:
    # fpdf2 leaves the cursor at the right margin after multi_cell; reset it so the next line has width
    pdf.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")


def build_report(data: dict) -> bytes:
    """PDF bytes for a /api/check result: overall similarity, then each source with its passages."""
    pdf = FPDF()
    pdf.add_font("thai", fname=str(FONT))
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("thai", size=18)
    cell(pdf, 10, "Plagiarism report")
    pdf.set_font("thai", size=11)
    cell(pdf, 7, f"Document: {data['filename']} ({data['chars']} characters)")
    cell(pdf, 7, f"Similarity: {data['similarity']}%")
    if data.get("search_error"):
        cell(pdf, 7, f"Note: {data['search_error']}")

    for match in data["matches"]:
        pdf.ln(4)
        pdf.set_font("thai", size=12)
        cell(pdf, 7, f"{match['url']} ({match['similarity']}%)")
        pdf.set_font("thai", size=10)
        for passage in match["passages"]:
            cell(pdf, 6, f"  - {passage}")

    if not data["matches"]:
        pdf.ln(4)
        cell(pdf, 7, "No similar passages found.")
    return bytes(pdf.output())
