
"""
generate_report.py

Generador de reporte bibliométrico preliminar para BiblioMap.

Ubicación:
    01_BiblioMap_UCV/modules/generate_report.py

Entradas:
    data/processed/openalex_search_results.csv
    data/processed/group_by_country.csv
    data/processed/group_by_continent.csv
    data/processed/gap_suggestions.csv
    data/processed/keyword_summary.csv
    data/processed/temporal_summary.csv
    data/processed/trend_summary.csv
    data/processed/understudied_areas.csv
    data/processed/research_opportunities.csv

Salidas:
    data/exports/bibliomap_preliminary_report.md
    data/exports/bibliomap_preliminary_report.html

Uso:
    py modules\\generate_report.py
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPORTS_DIR = BASE_DIR / "data" / "exports"

FILES = {
    "results": PROCESSED_DIR / "openalex_search_results.csv",
    "countries": PROCESSED_DIR / "group_by_country.csv",
    "continents": PROCESSED_DIR / "group_by_continent.csv",
    "gaps": PROCESSED_DIR / "gap_suggestions.csv",
    "keywords": PROCESSED_DIR / "keyword_summary.csv",
    "temporal": PROCESSED_DIR / "temporal_summary.csv",
    "trends": PROCESSED_DIR / "trend_summary.csv",
    "understudied": PROCESSED_DIR / "understudied_areas.csv",
    "opportunities": PROCESSED_DIR / "research_opportunities.csv",
}

DEFAULT_MD_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.md"
DEFAULT_HTML_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.html"
DEFAULT_PDF_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.pdf"


def read_csv(path: Path) -> pd.DataFrame:
    """
    Lee un CSV si existe. Si falla, retorna DataFrame vacío.
    """
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def clean_text(value: object, default: str = "") -> str:
    """
    Convierte valores a texto seguro.
    """
    if value is None:
        return default

    text = str(value).strip()

    if not text or text.lower() == "nan":
        return default

    return text.replace("\n", " ").replace("|", "/")


def sum_column(df: pd.DataFrame, column: str) -> int:
    """
    Suma una columna numérica.
    """
    if df.empty or column not in df.columns:
        return 0

    return int(pd.to_numeric(df[column], errors="coerce").fillna(0).sum())


def count_semicolon_unique(df: pd.DataFrame, column: str) -> int:
    """
    Cuenta valores únicos dentro de campos separados por punto y coma.
    """
    if df.empty or column not in df.columns:
        return 0

    values = set()

    for cell in df[column].dropna().astype(str):
        for item in cell.split(";"):
            item = item.strip()
            if item:
                values.add(item)

    return len(values)


def table_md(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
    max_rows: int = 10,
) -> str:
    """
    Convierte un DataFrame a tabla Markdown simple.
    """
    if df is None or df.empty:
        return "_Sin datos disponibles._"

    work = df.copy()

    if columns:
        available = [col for col in columns if col in work.columns]
        if available:
            work = work[available]

    work = work.head(max_rows).fillna("")

    if work.empty:
        return "_Sin datos disponibles._"

    header = "| " + " | ".join([clean_text(col) for col in work.columns]) + " |"
    sep = "| " + " | ".join(["---"] * len(work.columns)) + " |"

    rows = []

    for _, row in work.iterrows():
        values = [clean_text(value) for value in row.tolist()]
        rows.append("| " + " | ".join(values) + " |")

    return "\n".join([header, sep] + rows)


def load_report_data() -> dict[str, pd.DataFrame]:
    """
    Carga todas las salidas procesadas.
    """
    return {name: read_csv(path) for name, path in FILES.items()}


def infer_period(results_df: pd.DataFrame) -> str:
    """
    Deduce periodo a partir de publication_year.
    """
    if results_df.empty or "publication_year" not in results_df.columns:
        return "No especificado"

    years = pd.to_numeric(results_df["publication_year"], errors="coerce").dropna()

    if years.empty:
        return "No especificado"

    return f"{int(years.min())}-{int(years.max())}"


def build_executive_summary(data: dict[str, pd.DataFrame], query: str) -> str:
    """
    Genera resumen ejecutivo.
    """
    results = data["results"]
    countries = data["countries"]
    gaps = data["gaps"]
    trends = data["trends"]
    opportunities = data["opportunities"]

    total_records = len(results)
    citations = sum_column(results, "cited_by_count")
    country_count = countries["country_code"].nunique() if not countries.empty and "country_code" in countries.columns else 0
    author_count = count_semicolon_unique(results, "authors")
    institution_count = count_semicolon_unique(results, "institutions")

    return f"""
La consulta bibliométrica preliminar sobre **{query or "tema no especificado"}** recuperó **{total_records} registros** y **{citations} citas acumuladas** según los metadatos disponibles.

La muestra permitió identificar aproximadamente **{country_count} países**, **{author_count} autores** y **{institution_count} instituciones**. Además, BiblioMap generó **{len(gaps)} señales preliminares de brecha**, **{len(trends)} tendencias de estudio** y **{len(opportunities)} oportunidades investigativas**.

Estos resultados son orientadores. No constituyen una revisión sistemática ni una investigación bibliométrica completa. Deben validarse mediante lectura crítica y contraste con otras bases académicas.
""".strip()


def build_markdown_report(
    query: str = "",
    generated_by: str = "BiblioMap — Ecosistema BiblioIntel",
) -> str:
    """
    Construye el reporte Markdown completo.
    """
    data = load_report_data()

    results = data["results"]
    countries = data["countries"]
    continents = data["continents"]
    gaps = data["gaps"]
    keywords = data["keywords"]
    temporal = data["temporal"]
    trends = data["trends"]
    understudied = data["understudied"]
    opportunities = data["opportunities"]

    period = infer_period(results)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not countries.empty and "publications" in countries.columns:
        countries = countries.sort_values("publications", ascending=False)

    if not continents.empty and "publications" in continents.columns:
        continents = continents.sort_values("publications", ascending=False)

    if not keywords.empty and "frequency" in keywords.columns:
        keywords = keywords.sort_values("frequency", ascending=False)

    if not results.empty and "cited_by_count" in results.columns:
        results = results.sort_values("cited_by_count", ascending=False)

    report = f"""# Reporte bibliométrico preliminar — BiblioMap

**Tema consultado:** {query or "No especificado"}  
**Periodo recuperado:** {period}  
**Fecha de generación:** {generated_at}  
**Generado por:** {generated_by}  
**Fuente inicial del MVP:** OpenAlex  

---

## 1. Resumen ejecutivo

{build_executive_summary(data, query)}

---

## 2. Indicadores generales

| Indicador | Valor |
| --- | --- |
| Registros recuperados | {len(data["results"])} |
| Citas acumuladas | {sum_column(data["results"], "cited_by_count")} |
| Países detectados | {data["countries"]["country_code"].nunique() if not data["countries"].empty and "country_code" in data["countries"].columns else 0} |
| Autores detectados | {count_semicolon_unique(data["results"], "authors")} |
| Instituciones detectadas | {count_semicolon_unique(data["results"], "institutions")} |
| Brechas preliminares | {len(gaps)} |
| Tendencias de estudio | {len(trends)} |
| Áreas poco visibles | {len(understudied)} |
| Oportunidades investigativas | {len(opportunities)} |

---

## 3. Distribución geográfica

### 3.1 Países principales

{table_md(countries, ["country_code", "country", "continent", "publications", "cited_by_count"], 15)}

### 3.2 Continentes o regiones

{table_md(continents, ["continent", "publications", "cited_by_count", "countries"], 10)}

---

## 4. Tendencias de estudio

{table_md(trends, ["trend_type", "trend", "evidence", "interpretation", "suggested_use", "strength"], 12)}

---

## 5. Brechas preliminares

{table_md(gaps, ["dimension", "signal", "evidence", "suggested_gap", "caution", "priority"], 15)}

---

## 6. Áreas poco visibles o poco estudiadas

{table_md(understudied, ["expected_dimension", "visibility_level", "evidence", "possible_gap", "suggested_question", "caution"], 15)}

---

## 7. Oportunidades investigativas

{table_md(opportunities, ["opportunity_type", "opportunity", "possible_research_question", "supporting_signal", "recommended_next_step", "priority"], 15)}

---

## 8. Términos y patrones frecuentes

{table_md(keywords, ["keyword", "frequency", "type"], 25)}

---

## 9. Serie temporal

{table_md(temporal, ["publication_year", "publications", "cited_by_count"], 30)}

---

## 10. Publicaciones principales recuperadas

{table_md(results, ["title", "publication_year", "authors", "source", "cited_by_count", "doi", "landing_page_url"], 20)}

---

## 11. Advertencia metodológica

Este reporte es **preliminar y orientador**. No sustituye una revisión sistemática, una investigación bibliométrica completa ni una validación definitiva de brechas.

Los resultados dependen de la fuente consultada, los términos de búsqueda, el idioma, el periodo seleccionado, el número máximo de resultados, la cobertura de metadatos y la calidad de los campos recuperados.

La interpretación final corresponde al investigador humano. Toda señal de brecha, tendencia o área poco visible debe contrastarse mediante lectura crítica y, cuando corresponda, con otras bases como Scopus, Web of Science, Dimensions, Lens, Google Scholar u otras fuentes pertinentes.

---

## 12. Criterio inteligentizador

BiblioMap se apoya en la lógica del ecosistema BiblioIntel:

- Humano define sentido.
- Software procesa evidencia.
- IA amplifica interpretación.
- Inteligencia Humana profundiza el conocimiento.
- IA + IH creaduccen.
- La creatividad transforma resultados en conocimiento nuevo.

---

_Reporte generado automáticamente por BiblioMap — Ecosistema BiblioIntel. Desarrollo de LEGIN._
"""
    return report


def markdown_to_html(markdown_text: str) -> str:
    """
    Convierte Markdown básico a HTML simple sin dependencias externas.
    """
    lines = markdown_text.splitlines()
    html_lines = []
    in_table = False
    in_list = False
    first_table_row = True

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_table:
                html_lines.append("</table>")
                in_table = False
                first_table_row = True
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        if stripped == "---":
            if in_table:
                html_lines.append("</table>")
                in_table = False
                first_table_row = True
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr>")
            continue

        if stripped.startswith("# "):
            html_lines.append(f"<h1>{escape(stripped[2:])}</h1>")
            continue

        if stripped.startswith("## "):
            html_lines.append(f"<h2>{escape(stripped[3:])}</h2>")
            continue

        if stripped.startswith("### "):
            html_lines.append(f"<h3>{escape(stripped[4:])}</h3>")
            continue

        if stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{escape(stripped[2:])}</li>")
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]

            if all(cell.replace("-", "").strip() == "" for cell in cells):
                continue

            if not in_table:
                html_lines.append("<table>")
                in_table = True
                first_table_row = True

            tag = "th" if first_table_row else "td"
            row_html = "".join(f"<{tag}>{escape(cell)}</{tag}>" for cell in cells)
            html_lines.append(f"<tr>{row_html}</tr>")
            first_table_row = False
            continue

        if in_table:
            html_lines.append("</table>")
            in_table = False
            first_table_row = True

        if in_list:
            html_lines.append("</ul>")
            in_list = False

        html_lines.append(f"<p>{escape(stripped)}</p>")

    if in_table:
        html_lines.append("</table>")

    if in_list:
        html_lines.append("</ul>")

    body = "\n".join(html_lines)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Reporte bibliométrico preliminar — BiblioMap</title>
<style>
body {{
    font-family: Arial, sans-serif;
    color: #1f2937;
    max-width: 1180px;
    margin: 40px auto;
    padding: 0 24px;
    line-height: 1.55;
}}
h1 {{
    color: #002B5C;
    border-bottom: 4px solid #B00000;
    padding-bottom: 10px;
}}
h2 {{
    color: #002B5C;
    margin-top: 34px;
}}
h3 {{
    color: #374151;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin: 18px 0;
}}
th, td {{
    border: 1px solid #d1d5db;
    padding: 8px;
    vertical-align: top;
}}
th {{
    background: #f3f4f6;
}}
hr {{
    border: 0;
    border-top: 1px solid #d1d5db;
    margin: 28px 0;
}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def save_report(
    markdown_text: str,
    md_path: Path = DEFAULT_MD_PATH,
    html_path: Path = DEFAULT_HTML_PATH,
) -> Tuple[Path, Path]:
    """
    Guarda reporte en Markdown y HTML.
    """
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    md_path.write_text(markdown_text, encoding="utf-8")
    html_path.write_text(markdown_to_html(markdown_text), encoding="utf-8")

    return md_path, html_path


def generate_report(
    query: str = "",
    md_path: Path = DEFAULT_MD_PATH,
    html_path: Path = DEFAULT_HTML_PATH,
) -> Tuple[str, Path, Path]:
    """
    Genera reporte completo.
    """
    markdown_text = build_markdown_report(query=query)
    saved_md, saved_html = save_report(markdown_text, md_path=md_path, html_path=html_path)
    return markdown_text, saved_md, saved_html


# ------------------------------------------------------------
# PDF report support
# ------------------------------------------------------------

def _try_register_pdf_font():
    """
    Register a Unicode-friendly font when available.
    Returns (regular_font, bold_font).
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        candidates = [
            (BASE_DIR / "assets" / "fonts" / "DejaVuSans.ttf", "BiblioFont"),
            (Path("C:/Windows/Fonts/arial.ttf"), "BiblioArial"),
            (Path("C:/Windows/Fonts/calibri.ttf"), "BiblioCalibri"),
            (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), "BiblioDejaVu"),
        ]

        for font_path, font_name in candidates:
            if font_path.exists():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                return font_name, font_name

    except Exception:
        pass

    return "Helvetica", "Helvetica-Bold"


def _pdf_text(value: object, max_chars: int | None = None) -> str:
    """
    Clean text for ReportLab tables and paragraphs.
    """
    text = clean_text(value)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if max_chars is not None and len(text) > max_chars:
        text = text[: max_chars - 3] + "..."

    return text


def _pdf_paragraph(value: object, style, max_chars: int | None = None):
    from reportlab.platypus import Paragraph

    return Paragraph(_pdf_text(value, max_chars=max_chars), style)


def _df_to_pdf_table(df: pd.DataFrame, columns: list[str], max_rows: int, col_widths, small_style):
    """
    Convert a DataFrame to a ReportLab table flowable.
    """
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Table, TableStyle

    if df is None or df.empty:
        return Paragraph("Sin datos disponibles.", small_style)

    work = df.copy()
    available = [column for column in columns if column in work.columns]

    if available:
        work = work[available]

    work = work.head(max_rows).fillna("")

    if work.empty:
        return Paragraph("Sin datos disponibles.", small_style)

    header = [_pdf_paragraph(column, small_style, max_chars=80) for column in work.columns]
    rows = [header]

    for _, row in work.iterrows():
        rows.append([_pdf_paragraph(value, small_style, max_chars=180) for value in row.tolist()])

    table = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF1FB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#002B5C")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D7DE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _add_pdf_header_footer(canvas, doc):
    """
    Draw footer and page number.
    """
    from reportlab.lib.units import inch

    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColorRGB(0.35, 0.35, 0.35)
    footer = "BiblioMap - Ecosistema BiblioIntel. Desarrollo de LEGIN. Reporte preliminar."
    canvas.drawString(doc.leftMargin, 0.45 * inch, footer)
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.45 * inch, f"Pagina {doc.page}")
    canvas.restoreState()


def generate_pdf_report(
    query: str = "",
    pdf_path: Path = DEFAULT_PDF_PATH,
) -> Path:
    """
    Generate a PDF version of the preliminary bibliometric report.

    Requires:
        .\\.venv\\Scripts\\python.exe -m pip install reportlab
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError(
            "Para generar PDF instala ReportLab con: .\\.venv\\Scripts\\python.exe -m pip install reportlab"
        ) from exc

    data = load_report_data()
    results = data["results"]
    countries = data["countries"]
    continents = data["continents"]
    gaps = data["gaps"]
    keywords = data["keywords"]
    temporal = data["temporal"]
    trends = data["trends"]
    understudied = data["understudied"]
    opportunities = data["opportunities"]

    if not countries.empty and "publications" in countries.columns:
        countries = countries.sort_values("publications", ascending=False)

    if not continents.empty and "publications" in continents.columns:
        continents = continents.sort_values("publications", ascending=False)

    if not keywords.empty and "frequency" in keywords.columns:
        keywords = keywords.sort_values("frequency", ascending=False)

    if not results.empty and "cited_by_count" in results.columns:
        results = results.sort_values("cited_by_count", ascending=False)

    regular_font, bold_font = _try_register_pdf_font()

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BiblioTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#002B5C"),
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "BiblioH1",
        parent=styles["Heading1"],
        fontName=bold_font,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#002B5C"),
        spaceBefore=12,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "BiblioBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=9,
        leading=12,
        spaceAfter=8,
    )
    small_style = ParagraphStyle(
        "BiblioSmall",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=7,
        leading=9,
    )
    note_style = ParagraphStyle(
        "BiblioNote",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#4B5563"),
        backColor=colors.HexColor("#F2F7FF"),
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=8,
    )

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.65 * inch,
    )

    page_width = A4[0] - doc.leftMargin - doc.rightMargin
    story = []

    logo_path = BASE_DIR / "assets" / "images" / "logo_bibliomap.png"
    if logo_path.exists():
        try:
            image_reader = ImageReader(str(logo_path))
            image_width, image_height = image_reader.getSize()
            draw_width = 2.4 * inch
            draw_height = draw_width * (image_height / image_width)
            logo = Image(str(logo_path), width=draw_width, height=draw_height)
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 0.12 * inch))
        except Exception:
            pass

    period = infer_period(results)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    story.append(Paragraph("Reporte bibliometrico preliminar", title_style))
    story.append(Paragraph(f"Tema consultado: {_pdf_text(query or 'No especificado')}", body_style))
    story.append(Paragraph(f"Periodo recuperado: {_pdf_text(period)}", body_style))
    story.append(Paragraph(f"Fecha de generacion: {_pdf_text(generated_at)}", body_style))
    story.append(Paragraph("Fuente inicial del MVP: OpenAlex", body_style))
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("1. Resumen ejecutivo", h1_style))
    story.append(Paragraph(build_executive_summary(data, query), body_style))

    metrics = [
        ["Indicador", "Valor"],
        ["Registros recuperados", str(len(data["results"]))],
        ["Citas acumuladas", str(sum_column(data["results"], "cited_by_count"))],
        ["Paises detectados", str(data["countries"]["country_code"].nunique() if not data["countries"].empty and "country_code" in data["countries"].columns else 0)],
        ["Autores detectados", str(count_semicolon_unique(data["results"], "authors"))],
        ["Instituciones detectadas", str(count_semicolon_unique(data["results"], "institutions"))],
        ["Brechas preliminares", str(len(gaps))],
        ["Tendencias de estudio", str(len(trends))],
        ["Areas poco visibles", str(len(understudied))],
        ["Oportunidades investigativas", str(len(opportunities))],
    ]
    metrics_table = Table(metrics, colWidths=[2.6 * inch, 4.6 * inch], hAlign="LEFT")
    metrics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF1FB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#002B5C")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D7DE")),
                ("FONTNAME", (0, 0), (-1, -1), regular_font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(Paragraph("2. Indicadores generales", h1_style))
    story.append(metrics_table)

    story.append(PageBreak())

    story.append(Paragraph("3. Distribucion geografica", h1_style))
    story.append(Paragraph("Paises principales", body_style))
    story.append(_df_to_pdf_table(countries, ["country_code", "country", "continent", "publications", "cited_by_count"], 12, [0.7*inch, 1.5*inch, 1.1*inch, 0.9*inch, 1.0*inch], small_style))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Continentes o regiones", body_style))
    story.append(_df_to_pdf_table(continents, ["continent", "publications", "cited_by_count", "countries"], 8, [1.3*inch, 0.9*inch, 1.0*inch, 4.0*inch], small_style))

    story.append(Paragraph("4. Tendencias de estudio", h1_style))
    story.append(_df_to_pdf_table(trends, ["trend_type", "trend", "evidence", "strength"], 10, [1.0*inch, 2.2*inch, 3.1*inch, 0.8*inch], small_style))

    story.append(Paragraph("5. Brechas preliminares", h1_style))
    story.append(_df_to_pdf_table(gaps, ["dimension", "signal", "suggested_gap", "priority"], 12, [1.0*inch, 2.3*inch, 3.1*inch, 0.8*inch], small_style))

    story.append(PageBreak())

    story.append(Paragraph("6. Areas poco visibles o poco estudiadas", h1_style))
    story.append(_df_to_pdf_table(understudied, ["expected_dimension", "visibility_level", "possible_gap", "suggested_question"], 12, [1.5*inch, 1.0*inch, 2.2*inch, 2.5*inch], small_style))

    story.append(Paragraph("7. Oportunidades investigativas", h1_style))
    story.append(_df_to_pdf_table(opportunities, ["opportunity_type", "opportunity", "possible_research_question", "priority"], 12, [1.3*inch, 2.3*inch, 2.8*inch, 0.8*inch], small_style))

    story.append(Paragraph("8. Terminos y serie temporal", h1_style))
    story.append(Paragraph("Terminos y patrones frecuentes", body_style))
    story.append(_df_to_pdf_table(keywords, ["keyword", "frequency", "type"], 20, [3.5*inch, 1.0*inch, 1.2*inch], small_style))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Serie temporal", body_style))
    story.append(_df_to_pdf_table(temporal, ["publication_year", "publications", "cited_by_count"], 25, [1.8*inch, 1.8*inch, 1.8*inch], small_style))

    story.append(PageBreak())

    story.append(Paragraph("9. Publicaciones principales recuperadas", h1_style))
    story.append(_df_to_pdf_table(results, ["title", "publication_year", "source", "cited_by_count"], 15, [3.7*inch, 0.9*inch, 1.8*inch, 0.8*inch], small_style))

    story.append(Paragraph("10. Advertencia metodologica", h1_style))
    story.append(Paragraph(
        "Este reporte es preliminar y orientador. No sustituye una revision sistematica, una investigacion bibliometrica completa ni una validacion definitiva de brechas. Los resultados dependen de la fuente consultada, los terminos de busqueda, el idioma, el periodo seleccionado, el numero maximo de resultados y la cobertura de metadatos. La interpretacion final corresponde al investigador humano.",
        note_style,
    ))

    story.append(Paragraph("11. Criterio inteligentizador", h1_style))
    story.append(Paragraph(
        "Humano define sentido. Software procesa evidencia. IA amplifica interpretacion. Inteligencia Humana profundiza el conocimiento. IA + IH creaduccen. La creatividad transforma resultados en conocimiento nuevo.",
        body_style,
    ))

    doc.build(story, onFirstPage=_add_pdf_header_footer, onLaterPages=_add_pdf_header_footer)
    return pdf_path


if __name__ == "__main__":
    print("Generando reporte bibliométrico preliminar...")

    markdown, md_path, html_path = generate_report()

    print("\nReporte generado correctamente:")
    print(md_path)
    print(html_path)

    try:
        pdf_path = generate_pdf_report()
        print("PDF generado correctamente:")
        print(pdf_path)
    except Exception as pdf_error:
        print("No se genero PDF automaticamente:")
        print(pdf_error)
