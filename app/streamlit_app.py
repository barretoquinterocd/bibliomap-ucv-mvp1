from pathlib import Path
import base64
from typing import Optional
from collections import Counter
import re
import sys

import pandas as pd
import streamlit as st


# ============================================================
# BiblioMap — MVP 1.0
# Interfaz inicial con identidad BiblioMap, BiblioIntel y LEGIN
# Conexión inicial con OpenAlex + Detalle geográfico + Mapa mundial
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
STYLES_DIR = ASSETS_DIR / "styles"
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"

# Permite importar módulos desde la carpeta raíz del proyecto.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.search_openalex import search_openalex, save_results
from modules.group_by_country import group_by_country, group_by_continent, save_geographic_outputs
from modules.generate_map import create_world_map, create_top_countries_bar
from modules.gap_suggester import (
    suggest_preliminary_gaps,
    save_gap_outputs,
    generate_extended_insights,
    save_extended_outputs,
)
from modules.generate_report import generate_report, generate_pdf_report
from modules.biblioquest import BiblioQuestInput, generate_biblioquest_protocol
from modules.biblioquest_report import generate_biblioquest_reports


LOGO_LEGIN = IMAGES_DIR / "logo_legin.png"
LOGO_BIBLIOMAP = IMAGES_DIR / "logo_bibliomap.png"
LOGO_BIBLIOINTEL = IMAGES_DIR / "logo_bibliointel.png"
LOGO_BIBLIOQUEST = IMAGES_DIR / "logo_biblioquest.png"
LOGO_BIBLIOPANGEA_1 = IMAGES_DIR / "logo_bibliopangea_1.png"
LOGO_BIBLIOPANGEA_2 = IMAGES_DIR / "logo_bibliopangea_2.png"
LOGO_BIBLIOPANGEA_3 = IMAGES_DIR / "logo_bibliopangea_3.png"
LOGO_BIBLIOPANGEA = LOGO_BIBLIOPANGEA_3
LOGO_CEAP = IMAGES_DIR / "logo_ceap.png"
LOGO_FACES_UCV = IMAGES_DIR / "logo_faces_ucv.png"
LOGO_UCV = IMAGES_DIR / "logo_ucv.png"

CUSTOM_CSS = STYLES_DIR / "custom.css"

OPENALEX_RESULTS_PATH = PROCESSED_DIR / "openalex_search_results.csv"
GROUP_BY_COUNTRY_PATH = PROCESSED_DIR / "group_by_country.csv"
GROUP_BY_CONTINENT_PATH = PROCESSED_DIR / "group_by_continent.csv"
GAP_SUGGESTIONS_PATH = PROCESSED_DIR / "gap_suggestions.csv"
KEYWORD_SUMMARY_PATH = PROCESSED_DIR / "keyword_summary.csv"
TEMPORAL_SUMMARY_PATH = PROCESSED_DIR / "temporal_summary.csv"
TREND_SUMMARY_PATH = PROCESSED_DIR / "trend_summary.csv"
UNDERSTUDIED_AREAS_PATH = PROCESSED_DIR / "understudied_areas.csv"
RESEARCH_OPPORTUNITIES_PATH = PROCESSED_DIR / "research_opportunities.csv"

REPORT_MARKDOWN_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.md"
REPORT_HTML_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.html"
REPORT_PDF_PATH = EXPORTS_DIR / "bibliomap_preliminary_report.pdf"

BIBLIOQUEST_JSON_PATH = PROCESSED_DIR / "biblioquest_protocol.json"
BIBLIOQUEST_MARKDOWN_PATH = EXPORTS_DIR / "biblioquest_protocol.md"
BIBLIOQUEST_DOCX_PATH = EXPORTS_DIR / "biblioquest_report.docx"
BIBLIOQUEST_PDF_PATH = EXPORTS_DIR / "biblioquest_report.pdf"

REFERENCE_NOTE = (
    "<strong>Fundamentos metodológicos y conceptuales de BiblioIntel/BiblioMap:</strong><br>"
    "Hurtado de Barrera, J. (2014). <em>Cómo formular objetivos de investigación: "
    "Un acercamiento desde la investigación holística</em>. Quirón Ediciones.<br>"
    "Öztürk, O., Kocaman, R., & Kanbach, D. K. (2024). "
    "How to design bibliometric research: An overview and a framework proposal. "
    "<em>Review of Managerial Science, 18</em>(11), 3333–3361. "
    "doi:10.1007/s11846-024-00738-0<br>"
    "Mirabal González, J. F. (s. f.). <em>El árbol para la innovación: "
    "Transformando la empresa a la economía digital</em>. OEM.<br>"
    "Barreto et al. (en desarrollo). <em>Paradigma inteligentizador: "
    "Sinergia de Inteligencias humano-ciencia-inteligencia artificial-creatividad "
    "para la transformación del conocimiento investigativo</em>. "
    "Manuscrito doctoral en preparación."
)


def show_image(path: Path, width: Optional[int] = None, caption: Optional[str] = None) -> None:
    if path.exists():
        st.image(str(path), width=width, caption=caption)
    else:
        st.warning(f"No se encontró el archivo: {path.name}")


def show_centered_image(path: Path, width: int = 310, alt: str = "logo") -> None:
    """Muestra una imagen centrada con HTML para evitar alineación izquierda de st.image dentro de columnas."""
    if not path.exists():
        st.warning(f"No se encontró el archivo: {path.name}")
        return

    suffix = path.suffix.lower().replace(".", "") or "png"
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    html = f'''
    <div style="width: 100%; display: flex; justify-content: center; align-items: center; margin: 0.3rem 0 0.8rem 0;">
        <img src="data:image/{mime};base64,{encoded}" alt="{alt}" style="width: {width}px; max-width: 100%; height: auto; display: block;" />
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def first_existing_path(*paths: Path) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path
    return None


def show_first_image(
    *paths: Path,
    width: Optional[int] = None,
    caption: Optional[str] = None,
    missing_label: str = "imagen",
) -> None:
    image_path = first_existing_path(*paths)
    if image_path:
        st.image(str(image_path), width=width, caption=caption)
    else:
        st.warning(f"No se encontró la {missing_label}.")


def load_css() -> None:
    if CUSTOM_CSS.exists():
        with open(CUSTOM_CSS, "r", encoding="utf-8") as css_file:
            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <style>
        .reference-note {
            max-width: 980px;
            margin-left: auto;
            margin-right: auto;
            text-align: center;
            font-size: 0.88rem;
            color: #444444;
            line-height: 1.45;
            margin-bottom: 1.5rem;
        }

        .geo-note {
            font-size: 0.88rem;
            color: #555555;
        }

        .quest-note {
            border-left: 4px solid #0B5CAD;
            padding: 0.85rem 1rem;
            background-color: rgba(11, 92, 173, 0.08);
            border-radius: 0.35rem;
            margin: 0.75rem 0 1rem 0;
        }

        .quest-warning {
            border-left: 4px solid #CC3344;
            padding: 0.85rem 1rem;
            background-color: rgba(204, 51, 68, 0.08);
            border-radius: 0.35rem;
            margin: 0.75rem 0 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    if "openalex_results" not in st.session_state:
        st.session_state.openalex_results = pd.DataFrame()

    if "country_results" not in st.session_state:
        st.session_state.country_results = pd.DataFrame()

    if "continent_results" not in st.session_state:
        st.session_state.continent_results = pd.DataFrame()

    if "gap_results" not in st.session_state:
        st.session_state.gap_results = pd.DataFrame()

    if "keyword_results" not in st.session_state:
        st.session_state.keyword_results = pd.DataFrame()

    if "temporal_results" not in st.session_state:
        st.session_state.temporal_results = pd.DataFrame()

    if "trend_results" not in st.session_state:
        st.session_state.trend_results = pd.DataFrame()

    if "understudied_results" not in st.session_state:
        st.session_state.understudied_results = pd.DataFrame()

    if "opportunity_results" not in st.session_state:
        st.session_state.opportunity_results = pd.DataFrame()

    if "last_query_metadata" not in st.session_state:
        st.session_state.last_query_metadata = {}
    elif not isinstance(st.session_state.last_query_metadata, dict):
        st.session_state.last_query_metadata = {}

    if "biblioquest_json_path" not in st.session_state:
        st.session_state.biblioquest_json_path = ""

    if "biblioquest_md_path" not in st.session_state:
        st.session_state.biblioquest_md_path = ""

    if "biblioquest_docx_path" not in st.session_state:
        st.session_state.biblioquest_docx_path = ""

    if "biblioquest_pdf_path" not in st.session_state:
        st.session_state.biblioquest_pdf_path = ""


def render_sidebar() -> str:
    with st.sidebar:
        show_image(LOGO_BIBLIOINTEL, width=165)

        st.markdown("### BiblioIntel")
        st.caption("BIBLIOMETRÓLOGO INTELIGENTIZADOR.")
        st.caption(
            "Ecosistema para orientar investigación bibliométrica, sentido metodológico, "
            "brechas, creatividad investigativa y reporte reproducible."
        )

        st.divider()

        st.markdown("#### Ecosistema BiblioIntel")
        st.caption(
            "Diseño, búsqueda, corpus, mapeo, interpretación, brechas, vigilancia, "
            "creatividad investigativa y reporte académico."
        )

        st.divider()

        st.markdown("#### Desarrollo de LEGIN")
        show_image(LOGO_LEGIN, width=125)
        st.caption("Laboratorio Estratégico de Gestión de la Innovación.")

        st.divider()

        menu = st.radio(
            "Navegación",
            [
                "Inicio",
                "BiblioQuest",
                "Buscar tema",
                "BiblioMap",
                "Investigadores",
                "Publicaciones",
                "Brechas preliminares",
                "Reporte preliminar",
                "Aprender bibliometría",
            ],
        )

    return menu


def render_header() -> None:
    show_centered_image(LOGO_BIBLIOINTEL, width=310, alt="BiblioIntel")

    st.markdown(
        f'<div class="reference-note">{REFERENCE_NOTE}</div>',
        unsafe_allow_html=True,
    )


def render_institutional_logos() -> None:
    st.divider()

    st.markdown("### Identidad institucional")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("#### Desarrollo de LEGIN")
        show_image(LOGO_LEGIN, width=145)
        st.caption("LEGIN")

    with col2:
        st.markdown("#### Entidades vinculadas")
        c1, c2, c3 = st.columns(3)

        with c1:
            show_image(LOGO_CEAP, width=125)
            st.markdown('<div class="small-caption">CEAP</div>', unsafe_allow_html=True)

        with c2:
            show_image(LOGO_FACES_UCV, width=145)
            st.markdown('<div class="small-caption">FACES UCV</div>', unsafe_allow_html=True)

        with c3:
            show_image(LOGO_UCV, width=115)
            st.markdown('<div class="small-caption">UCV</div>', unsafe_allow_html=True)


def page_inicio() -> None:
    render_header()

    st.markdown("## Bienvenido a BiblioMap")

    st.write(
        """
        **BiblioMap** es una herramienta informática de orientación bibliométrica
        diseñada para ayudar a estudiantes, tesistas e investigadores a explorar la
        producción científica mundial relacionada con un tema de investigación.
        """
    )

    st.write(
        """
        Su propósito es facilitar una primera aproximación a países, instituciones,
        autores, publicaciones y posibles brechas preliminares de investigación,
        usando fuentes académicas abiertas.
        """
    )

    st.info(
        """
        Los resultados de BiblioMap son orientadores, no conclusiones definitivas.
        La cobertura depende de la fuente consultada, los metadatos disponibles,
        los términos de búsqueda y el periodo seleccionado.
        """
    )

    st.markdown("## Ecosistema BiblioIntel")

    st.write(
        """
        **BiblioIntel** significa **BIBLIOMETRÓLOGO INTELIGENTIZADOR**.
        Es el ecosistema conceptual y tecnológico que enmarca a BiblioMap,
        BiblioQuest, BiblioGap, BiblioReport y las próximas capas de análisis
        bibliometrológico inteligentizador.
        """
    )

    st.write(
        """
        BiblioMap es la primera herramienta visual y educativa del ecosistema,
        orientada al mapeo científico, la identificación de actores académicos
        y la detección preliminar de brechas de investigación. BiblioQuest añade
        el paso previo: formular el sentido, el objetivo, las preguntas y el ajuste
        metodológico antes de buscar datos.
        """
    )

    st.markdown("## Fórmula rectora")

    st.markdown(
        """
        - Humano define sentido.
        - Software procesa evidencia.
        - IA amplifica interpretación.
        - Inteligencia Humana profundiza el conocimiento.
        - IA + IH creaduccen.
        - La creatividad transforma resultados en conocimiento nuevo.
        """
    )

    render_institutional_logos()



def page_biblioquest() -> None:
    """
    Pantalla BiblioQuest: diseño inicial de investigación bibliométrica.
    Genera protocolo JSON/Markdown y reporte Word/PDF.
    """
    header_col, logo_col = st.columns([0.78, 0.22])

    with header_col:
        st.markdown("## BiblioQuest")
        st.caption("De la observación al objetivo")

    with logo_col:
        if LOGO_BIBLIOQUEST.exists():
            st.image(str(LOGO_BIBLIOQUEST), width=300)

    st.info(
        """
        BiblioQuest guía al investigador desde la observación inicial, la situación generadora
        y la curiosidad científica hasta la formulación validada del objetivo general,
        los objetivos específicos, las preguntas bibliométricas, el ajuste metodológico,
        la proyección transformadora y el protocolo inicial exportable.
        """
    )

    with st.expander("Nota metodológica", expanded=False):
        st.markdown(
            """
            Basado en la metodología **HOMI**: sinergia de los aportes intelectuales de:

            - **Hurtado de Barrera**, sobre formulación holística de objetivos de investigación.
            - **Öztürk, Kocaman y Kanbach**, sobre diseño riguroso de investigación bibliométrica.
            - **Mirabal González**, sobre I2E, A3D y 3S.

            Este módulo incorpora además el **paradigma inteligentizador** como marco conceptual propio
            en desarrollo, orientado a la relación humano-ciencia-IA-creatividad, con trazabilidad,
            validación humana y proyección transformadora del conocimiento.
            """
        )

    tabs = st.tabs(
        [
            "1. Observación",
            "2. Objetivos",
            "3. Preguntas",
            "4. Ajuste metodológico",
            "5. Exportar protocolo",
        ]
    )

    with tabs[0]:
        st.markdown("### Observación inicial y situación generadora")

        researcher_name = st.text_input("Nombre del investigador / tecnólogo")
        project_title = st.text_input("Título tentativo del proyecto")
        tentative_topic = st.text_input("Tema tentativo")
        research_area = st.text_input("Área de investigación")

        generative_situation = st.text_area(
            "Situación generadora",
            help="Describe la observación, tensión, vacío o fenómeno que despertó tu curiosidad científica.",
            height=120,
        )

        scientific_curiosity = st.text_area(
            "Curiosidad científica",
            help="¿Qué llamó tu atención y qué deseas comprender?",
            height=120,
        )

        cognitive_purpose = st.text_area(
            "Propósito cognitivo",
            help="Expresa la intención amplia de comprensión, orientación o transformación investigativa.",
            height=120,
        )

        transformative_projection = st.text_area(
            "Proyección transformadora",
            help="¿Qué podría cambiar, mejorar o abrir esta investigación?",
            height=120,
        )

    with tabs[1]:
        st.markdown("### Formulación metodológica")

        study_event = st.text_area(
            "Evento de estudio",
            help="Fenómeno, proceso, estructura, campo o dimensión que será estudiada.",
            height=90,
        )

        unit_of_analysis = st.text_area(
            "Unidad de análisis",
            help="Publicaciones, autores, instituciones, países, fuentes, palabras clave, citas, documentos, etc.",
            height=90,
        )

        context = st.text_area(
            "Contexto",
            help="Campo científico, disciplina, región, base de datos o ámbito académico.",
            height=90,
        )

        temporality = st.text_input(
            "Temporalidad",
            help="Ejemplo: 2015-2026.",
        )

        general_objective = st.text_area(
            "Objetivo general de investigación",
            help="Debe expresar un logro cognitivo central, no una simple actividad técnica.",
            height=120,
        )

        specific_objectives_raw = st.text_area(
            "Objetivos específicos",
            help="Escribe un objetivo por línea.",
            height=140,
        )

    with tabs[2]:
        st.markdown("### Preguntas de investigación")

        main_question = st.text_area(
            "Pregunta principal",
            help="Debe corresponderse con el objetivo general.",
            height=100,
        )

        specific_questions_raw = st.text_area(
            "Preguntas específicas",
            help="Escribe una pregunta por línea.",
            height=140,
        )

        expected_results = st.text_area(
            "Resultados esperados",
            help="¿Qué productos cognitivos, mapas, indicadores, tendencias, brechas o agenda esperas obtener?",
            height=120,
        )

    with tabs[3]:
        st.markdown("### Ajuste bibliométrico, I2E, A3D y 3S")

        bibliometric_justification = st.text_area(
            "Justificación del uso de bibliometría",
            help="Explica por qué la bibliometría es adecuada para responder las preguntas.",
            height=120,
        )

        objective_question_data_analysis_fit = st.text_area(
            "Ajuste objetivo-pregunta-datos-análisis-interpretación",
            help="Explica cómo se conectan objetivo, preguntas, datos, análisis e interpretación.",
            height=120,
        )

        st.markdown("#### Lectura I2E")

        intorno = st.text_area(
            "Intorno",
            help="Necesidades, inquietudes o capacidades internas del investigador, grupo o comunidad académica.",
            height=90,
        )

        entorno = st.text_area(
            "Entorno",
            help="Campo visible, literatura, actores, instituciones, tendencias y producción científica observable.",
            height=90,
        )

        extorno = st.text_area(
            "Extorno",
            help="Campos vecinos, disciplinas externas, regiones, tecnologías o enfoques que pueden aportar novedad.",
            height=90,
        )

        st.markdown("#### 3S")

        support = st.text_area("Soporte", height=80)
        sustenance = st.text_area("Sustento", height=80)
        sustainability = st.text_area("Sostenimiento", height=80)

    with tabs[4]:
        st.markdown("### Generar ficha BiblioQuest")

        st.warning(
            """
            BiblioQuest no certifica por sí solo la novedad científica. Genera una estimación
            preliminar que debe validarse mediante búsqueda sistemática, lectura crítica y juicio experto.
            """
        )

        generate_clicked = st.button("Generar protocolo BiblioQuest", type="primary")

        if generate_clicked:
            input_data = BiblioQuestInput(
                researcher_name=researcher_name,
                project_title=project_title,
                tentative_topic=tentative_topic,
                research_area=research_area,
                generative_situation=generative_situation,
                scientific_curiosity=scientific_curiosity,
                cognitive_purpose=cognitive_purpose,
                transformative_projection=transformative_projection,
                study_event=study_event,
                unit_of_analysis=unit_of_analysis,
                context=context,
                temporality=temporality,
                general_objective=general_objective,
                specific_objectives=[
                    line.strip()
                    for line in specific_objectives_raw.splitlines()
                    if line.strip()
                ],
                main_question=main_question,
                specific_questions=[
                    line.strip()
                    for line in specific_questions_raw.splitlines()
                    if line.strip()
                ],
                expected_results=expected_results,
                bibliometric_justification=bibliometric_justification,
                objective_question_data_analysis_fit=objective_question_data_analysis_fit,
                intorno=intorno,
                entorno=entorno,
                extorno=extorno,
                support=support,
                sustenance=sustenance,
                sustainability=sustainability,
            )

            try:
                with st.spinner("Generando protocolo BiblioQuest y reportes Word/PDF..."):
                    result = generate_biblioquest_protocol(input_data)
                    reports = generate_biblioquest_reports()

                st.session_state.biblioquest_json_path = result["json_path"]
                st.session_state.biblioquest_md_path = result["markdown_path"]
                st.session_state.biblioquest_docx_path = reports["docx_path"]
                st.session_state.biblioquest_pdf_path = reports["pdf_path"]

                st.success("Ficha BiblioQuest generada correctamente.")
                st.caption(f"JSON: {result['json_path']}")
                st.caption(f"Markdown: {result['markdown_path']}")
                st.caption(f"Word: {reports['docx_path']}")
                st.caption(f"PDF: {reports['pdf_path']}")

            except Exception as error:
                st.error("Ocurrió un error al generar la ficha BiblioQuest.")
                st.exception(error)

        st.divider()
        st.markdown("### Descargas BiblioQuest")

        json_path = Path(st.session_state.get("biblioquest_json_path") or BIBLIOQUEST_JSON_PATH)
        md_path = Path(st.session_state.get("biblioquest_md_path") or BIBLIOQUEST_MARKDOWN_PATH)
        docx_path = Path(st.session_state.get("biblioquest_docx_path") or BIBLIOQUEST_DOCX_PATH)
        pdf_path = Path(st.session_state.get("biblioquest_pdf_path") or BIBLIOQUEST_PDF_PATH)

        download_col1, download_col2, download_col3, download_col4 = st.columns(4)

        if md_path.exists():
            with download_col1:
                st.download_button(
                    "Descargar Markdown (.md)",
                    data=md_path.read_bytes(),
                    file_name="biblioquest_protocol.md",
                    mime="text/markdown",
                )
        else:
            with download_col1:
                st.caption("Markdown no generado.")

        if json_path.exists():
            with download_col2:
                st.download_button(
                    "Descargar JSON (.json)",
                    data=json_path.read_bytes(),
                    file_name="biblioquest_protocol.json",
                    mime="application/json",
                )
        else:
            with download_col2:
                st.caption("JSON no generado.")

        if docx_path.exists():
            with download_col3:
                st.download_button(
                    "Descargar Word (.docx)",
                    data=docx_path.read_bytes(),
                    file_name="biblioquest_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        else:
            with download_col3:
                st.caption("Word no generado.")

        if pdf_path.exists():
            with download_col4:
                st.download_button(
                    "Descargar PDF (.pdf)",
                    data=pdf_path.read_bytes(),
                    file_name="biblioquest_report.pdf",
                    mime="application/pdf",
                )
        else:
            with download_col4:
                st.caption("PDF no generado.")

        if md_path.exists():
            with st.expander("Vista previa del protocolo Markdown", expanded=False):
                st.markdown(md_path.read_text(encoding="utf-8"))



# ============================================================
# Keywords / palabras clave para exportación
# ============================================================

KEYWORD_STOPWORDS = {
    # English
    "about", "above", "across", "after", "again", "against", "also", "among", "analysis",
    "and", "another", "because", "been", "before", "being", "between", "both", "can",
    "could", "data", "during", "each", "from", "further", "have", "having", "into",
    "more", "most", "other", "over", "paper", "perspective", "perspectives", "research",
    "result", "results", "study", "studies", "such", "than", "that", "their", "there",
    "these", "this", "through", "under", "using", "were", "what", "when", "where",
    "which", "while", "with", "within", "without", "would",
    # Spanish
    "ademas", "alguna", "algunas", "algunos", "ante", "aqui", "cada", "como",
    "contra", "cual", "cuando", "desde", "donde", "durante", "entre", "esta",
    "estas", "este", "estos", "hacia", "hasta", "investigacion", "menos", "para",
    "pero", "porque", "sobre", "tambien", "tanto", "tener", "tiene", "tienen", "todo",
    "todos", "tras", "una", "unas", "uno", "unos",
}


def _normalize_keyword_text(value: object) -> str:
    """
    Limpia texto para usarlo como palabra clave visible.
    """
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" .;,:|/\\[]{}()'\"")
    return text


def _split_keyword_like_value(value: object, limit: int = 12) -> list[str]:
    """
    Convierte valores existentes de keywords/topics/concepts en una lista limpia.

    Soporta:
    - Cadenas separadas por ;, coma o |
    - Representaciones tipo JSON/texto con display_name
    - Listas simples o listas de diccionarios
    """
    if value is None:
        return []

    if isinstance(value, float) and pd.isna(value):
        return []

    extracted: list[str] = []

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                name = item.get("display_name") or item.get("name") or item.get("title")
                if name:
                    extracted.append(_normalize_keyword_text(name))
            else:
                extracted.append(_normalize_keyword_text(item))
    elif isinstance(value, dict):
        name = value.get("display_name") or value.get("name") or value.get("title")
        if name:
            extracted.append(_normalize_keyword_text(name))
    else:
        text = str(value or "").strip()
        if not text or text.lower() in {"nan", "none", "null", "[]", "{}"}:
            return []

        # Si viene serializado como objetos de OpenAlex, extrae display_name.
        display_names = re.findall(r"['\"]display_name['\"]\s*:\s*['\"]([^'\"]+)['\"]", text)
        if display_names:
            extracted.extend(_normalize_keyword_text(item) for item in display_names)
        else:
            # Separadores habituales en metadatos exportados.
            parts = re.split(r"\s*;\s*|\s*\|\s*|\s*,\s*", text)
            extracted.extend(_normalize_keyword_text(part) for part in parts)

    clean: list[str] = []
    seen = set()

    for item in extracted:
        if not item:
            continue

        item = re.sub(r"[_\-]+", " ", item).strip()
        if not item:
            continue

        key = item.lower()
        if key in seen:
            continue

        seen.add(key)
        clean.append(item)

        if len(clean) >= limit:
            break

    return clean


def _infer_keywords_from_text(title: object, abstract: object, limit: int = 12) -> str:
    """
    Genera palabras clave preliminares desde título y resumen cuando OpenAlex
    no devuelve keywords explícitas en los metadatos recuperados.

    Nota: son keywords inferidas para orientar la lectura, no sustituyen la
    indexación oficial de una revista o base de datos.
    """
    source_text = f"{title or ''}. {abstract or ''}".strip()

    if not source_text or source_text.lower() in {"nan", "none"}:
        return ""

    text = source_text.lower()
    text = re.sub(r"https?://\S+|doi:\S+", " ", text)

    # Frases muy frecuentes que conviene preservar como unidad conceptual.
    phrase_replacements = {
        "artificial intelligence": "artificial_intelligence",
        "machine learning": "machine_learning",
        "deep learning": "deep_learning",
        "large language models": "large_language_models",
        "large language model": "large_language_model",
        "digital transformation": "digital_transformation",
        "knowledge production": "knowledge_production",
        "scientific creativity": "scientific_creativity",
        "higher education": "higher_education",
        "decision making": "decision_making",
        "big data": "big_data",
    }

    for phrase, replacement in phrase_replacements.items():
        text = text.replace(phrase, replacement)

    tokens = re.findall(
        r"[a-záéíóúüñ][a-záéíóúüñ_]{2,}",
        text,
        flags=re.IGNORECASE,
    )

    clean_tokens = []
    for token in tokens:
        token = token.lower().strip("_")
        plain = token.replace("_", " ")

        if plain in KEYWORD_STOPWORDS:
            continue

        if len(plain) < 4 and plain not in {"ai"}:
            continue

        clean_tokens.append(token)

    if not clean_tokens:
        return ""

    counts: Counter[str] = Counter()

    # Mayor peso para términos presentes en el título.
    title_text = str(title or "").lower()
    for token in clean_tokens:
        term = token.replace("_", " ")
        counts[term] += 2 if term in title_text else 1

    # Bigrams orientadores.
    for i in range(len(clean_tokens) - 1):
        first = clean_tokens[i].replace("_", " ")
        second = clean_tokens[i + 1].replace("_", " ")

        if first in KEYWORD_STOPWORDS or second in KEYWORD_STOPWORDS:
            continue

        if first == second:
            continue

        phrase = f"{first} {second}"
        counts[phrase] += 2

    selected: list[str] = []

    for term, _ in counts.most_common():
        term = _normalize_keyword_text(term)

        if not term:
            continue

        lower = term.lower()
        if any(lower == existing.lower() for existing in selected):
            continue

        if len(term) < 4:
            continue

        selected.append(term)

        if len(selected) >= limit:
            break

    return "; ".join(item.title() if item.islower() else item for item in selected)


def _keywords_from_row(row: pd.Series, limit: int = 12) -> str:
    """
    Extrae keywords existentes o las infiere desde título/resumen.
    """
    keyword_candidate_columns = [
        "keywords",
        "keyword",
        "topics",
        "topic",
        "concepts",
        "concept",
        "subjects",
        "subject",
        "fields_of_study",
        "openalex_keywords",
        "openalex_topics",
        "openalex_concepts",
    ]

    for column in keyword_candidate_columns:
        if column not in row.index:
            continue

        # Evita reciclar una columna keywords vacía como si fuera válida.
        values = _split_keyword_like_value(row.get(column), limit=limit)

        if values:
            return "; ".join(values[:limit])

    return _infer_keywords_from_text(
        row.get("title", ""),
        row.get("abstract", ""),
        limit=limit,
    )


def ensure_keywords_last_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garantiza que el DataFrame tenga una columna final 'keywords'.

    Si OpenAlex o el módulo de búsqueda ya entrega keywords/topics/concepts,
    las preserva y limpia. Si no existen, crea keywords preliminares inferidas
    desde título y abstract para que el CSV descargable siempre incluya la
    lectura temática solicitada por el usuario/financista.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    enriched_df = df.copy()

    enriched_df["keywords"] = enriched_df.apply(
        lambda row: _keywords_from_row(row),
        axis=1,
    )

    columns = [column for column in enriched_df.columns if column != "keywords"] + ["keywords"]
    return enriched_df[columns]


def render_results_summary(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No se recuperaron resultados para esta búsqueda.")
        return

    total_records = len(df)
    total_citations = (
        int(df["cited_by_count"].fillna(0).sum())
        if "cited_by_count" in df.columns
        else 0
    )
    years = (
        df["publication_year"].dropna()
        if "publication_year" in df.columns
        else pd.Series(dtype=int)
    )
    countries_count = 0

    if "countries" in df.columns:
        country_values = []
        for item in df["countries"].dropna():
            country_values.extend(
                [country.strip() for country in str(item).split(";") if country.strip()]
            )
        countries_count = len(set(country_values))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Registros recuperados", total_records)

    with col2:
        st.metric("Citas acumuladas", total_citations)

    with col3:
        st.metric("Países detectados", countries_count)

    if not years.empty:
        st.caption(f"Rango de años recuperado: {int(years.min())}–{int(years.max())}")


def build_and_store_geographic_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    country_df = group_by_country(df)
    continent_df = group_by_continent(df)

    st.session_state.country_results = country_df
    st.session_state.continent_results = continent_df

    save_geographic_outputs(country_df, continent_df, str(PROCESSED_DIR))

    return country_df, continent_df


def load_geographic_outputs_from_disk() -> tuple[pd.DataFrame, pd.DataFrame]:
    country_df = pd.DataFrame()
    continent_df = pd.DataFrame()

    if GROUP_BY_COUNTRY_PATH.exists():
        country_df = pd.read_csv(GROUP_BY_COUNTRY_PATH)

    if GROUP_BY_CONTINENT_PATH.exists():
        continent_df = pd.read_csv(GROUP_BY_CONTINENT_PATH)

    if not country_df.empty:
        st.session_state.country_results = country_df

    if not continent_df.empty:
        st.session_state.continent_results = continent_df

    return country_df, continent_df


def get_country_results() -> pd.DataFrame:
    country_df = st.session_state.country_results

    if country_df.empty:
        country_df, _ = load_geographic_outputs_from_disk()

    return country_df


def page_buscar_tema() -> None:
    st.markdown("## Buscar tema")

    st.write(
        """
        Introduce un tema o conjunto de palabras clave. BiblioMap consultará OpenAlex
        y recuperará metadatos bibliométricos básicos para iniciar el análisis.
        """
    )

    with st.form("search_form"):
        tema = st.text_input(
            "Tema de investigación",
            value="inteligencia artificial y creatividad científica",
        )

        palabras_clave = st.text_input(
            "Palabras clave para búsqueda en OpenAlex",
            value="artificial intelligence scientific creativity knowledge production",
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            year_from = st.number_input(
                "Año inicial",
                min_value=1900,
                max_value=2100,
                value=2015,
            )

        with col2:
            year_to = st.number_input(
                "Año final",
                min_value=1900,
                max_value=2100,
                value=2026,
            )

        with col3:
            max_results = st.number_input(
                "Máximo de resultados",
                min_value=10,
                max_value=500,
                value=50,
                step=10,
            )

        submitted = st.form_submit_button("Buscar en OpenAlex")

    if submitted:
        query = palabras_clave.strip() or tema.strip()

        if not query:
            st.error("Debes introducir un tema o palabras clave.")
            return

        try:
            with st.spinner("Consultando OpenAlex y recuperando evidencia bibliométrica..."):
                df = search_openalex(
                    query=query,
                    year_from=int(year_from),
                    year_to=int(year_to),
                    max_results=int(max_results),
                )

                df = ensure_keywords_last_column(df)

            st.session_state.openalex_results = df
            st.session_state.last_query_metadata = {
                "tema": tema,
                "query": query,
                "year_from": int(year_from),
                "year_to": int(year_to),
                "max_results": int(max_results),
                "source": "OpenAlex",
            }

            output_path = PROCESSED_DIR / "openalex_search_results.csv"
            save_results(df, output_path)

            # Garantía adicional: el CSV descargable/procesado conserva
            # 'keywords' como última columna y codificación amigable para Excel.
            df.to_csv(output_path, index=False, encoding="utf-8-sig")

            country_df, continent_df = build_and_store_geographic_outputs(df)

            gap_df, keyword_df, temporal_df = suggest_preliminary_gaps(
                df,
                country_df=country_df,
                continent_df=continent_df,
            )

            save_gap_outputs(
                gap_df,
                keyword_df,
                temporal_df,
                output_dir=PROCESSED_DIR,
            )

            st.session_state.gap_results = gap_df
            st.session_state.keyword_results = keyword_df
            st.session_state.temporal_results = temporal_df

            trend_df, understudied_df, opportunity_df = generate_extended_insights(
                df,
                gap_df=gap_df,
                keyword_df=keyword_df,
                temporal_df=temporal_df,
                country_df=country_df,
                continent_df=continent_df,
            )

            save_extended_outputs(
                trend_df,
                understudied_df,
                opportunity_df,
                output_dir=PROCESSED_DIR,
            )

            st.session_state.trend_results = trend_df
            st.session_state.understudied_results = understudied_df
            st.session_state.opportunity_results = opportunity_df

            st.success(f"Consulta completada. Registros recuperados: {len(df)}")
            st.caption(f"Archivo guardado en: {output_path}")
            st.caption(f"Agrupaciones geográficas guardadas en: {PROCESSED_DIR}")

        except Exception as error:
            st.error("Ocurrió un error al consultar OpenAlex.")
            st.exception(error)

    df_current = st.session_state.openalex_results

    if not df_current.empty:
        df_current = ensure_keywords_last_column(df_current)
        st.session_state.openalex_results = df_current

        # Mantiene actualizado el archivo procesado con keywords al final.
        df_current.to_csv(OPENALEX_RESULTS_PATH, index=False, encoding="utf-8-sig")

        st.divider()
        st.markdown("## Resultados preliminares")

        render_results_summary(df_current)

        display_columns = [
            "title",
            "publication_year",
            "authors",
            "countries",
            "institutions",
            "source",
            "cited_by_count",
            "doi",
            "landing_page_url",
            "keywords",
        ]

        available_columns = [
            column for column in display_columns if column in df_current.columns
        ]

        st.dataframe(
            df_current[available_columns],
            use_container_width=True,
            height=420,
        )

        csv_data = df_current.to_csv(index=False, encoding="utf-8-sig")

        st.download_button(
            label="Descargar resultados CSV",
            data=csv_data,
            file_name="openalex_search_results.csv",
            mime="text/csv",
        )

        st.info(
            """
            Estos resultados son preliminares. La interpretación final corresponde al investigador humano.
            El siguiente desarrollo organizará estos registros por país, institución, autores y publicaciones.
            """
        )


def render_world_map_section() -> None:
    st.markdown("### Mapa mundial")

    st.write(
        """
        Visualización geográfica preliminar de la producción científica recuperada.
        El mapa usa la agrupación por país generada desde los metadatos de OpenAlex.
        """
    )

    country_df = get_country_results()

    if country_df.empty:
        st.warning("Todavía no hay datos para el mapa. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    metric_label = st.selectbox(
        "Métrica del mapa",
        options=["Publicaciones", "Citas acumuladas"],
        index=0,
        key="bibliomap_metric_label",
    )

    metric = "publications" if metric_label == "Publicaciones" else "cited_by_count"

    fig_map = create_world_map(country_df, metric=metric)
    st.plotly_chart(fig_map, use_container_width=True)

    st.caption(
        "Nota: una publicación puede aparecer asociada a más de un país si tiene afiliaciones multinacionales."
    )

    st.divider()

    top_n = st.slider(
        "Número de países en el ranking",
        min_value=5,
        max_value=30,
        value=15,
        step=5,
        key="bibliomap_top_n",
    )

    fig_bar = create_top_countries_bar(country_df, metric=metric, top_n=top_n)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.info(
        """
        Este mapa es una visualización exploratoria. No debe interpretarse como cobertura absoluta del campo,
        sino como una lectura preliminar dependiente de OpenAlex, de los términos de búsqueda y de los metadatos disponibles.
        """
    )


def render_geographic_detail_section() -> None:
    st.markdown("### Distribución geográfica")

    st.write(
        """
        Esta sección organiza los resultados recuperados desde OpenAlex por país y por continente o región amplia.
        Permite observar la distribución preliminar de la producción científica asociada al tema consultado.
        """
    )

    country_df = st.session_state.country_results
    continent_df = st.session_state.continent_results

    if country_df.empty or continent_df.empty:
        country_df, continent_df = load_geographic_outputs_from_disk()

    if country_df.empty or continent_df.empty:
        st.warning("Todavía no hay datos geográficos. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    total_countries = (
        len(country_df[country_df["country_code"] != "Unknown"])
        if "country_code" in country_df.columns
        else len(country_df)
    )
    total_publications_country = int(country_df["publications"].sum()) if "publications" in country_df.columns else 0
    total_citations_country = int(country_df["cited_by_count"].sum()) if "cited_by_count" in country_df.columns else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Países detectados", total_countries)

    with col2:
        st.metric("Apariciones país-publicación", total_publications_country)

    with col3:
        st.metric("Citas acumuladas por país", total_citations_country)

    st.caption(
        "Nota: una misma publicación puede aparecer en más de un país si tiene autorías o afiliaciones multinacionales."
    )

    st.divider()

    st.markdown("#### Distribución por continente o región")

    continent_columns = [
        "continent",
        "publications",
        "cited_by_count",
        "countries",
    ]
    continent_available = [column for column in continent_columns if column in continent_df.columns]

    st.dataframe(
        continent_df[continent_available],
        use_container_width=True,
        height=260,
    )

    continent_csv = continent_df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="Descargar agrupación por continente CSV",
        data=continent_csv,
        file_name="group_by_continent.csv",
        mime="text/csv",
    )

    st.divider()

    st.markdown("#### Distribución por país")

    country_columns = [
        "country_code",
        "country",
        "continent",
        "publications",
        "cited_by_count",
        "institutions",
        "authors",
    ]
    country_available = [column for column in country_columns if column in country_df.columns]

    st.dataframe(
        country_df[country_available],
        use_container_width=True,
        height=520,
    )

    country_csv = country_df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="Descargar agrupación por país CSV",
        data=country_csv,
        file_name="group_by_country.csv",
        mime="text/csv",
    )

    st.info(
        """
        Interpretación preliminar: esta tabla permite identificar concentración geográfica,
        regiones activas y posibles espacios de baja presencia bibliométrica. No debe asumirse
        que la ausencia de registros equivale a inexistencia de investigación; depende de la fuente,
        los metadatos y los términos de búsqueda.
        """
    )


def render_bibliopangea_section() -> None:
    st.markdown("### BiblioPangea — próxima versión")

    logo_path = first_existing_path(
        LOGO_BIBLIOPANGEA_3,
        LOGO_BIBLIOPANGEA_2,
        LOGO_BIBLIOPANGEA_1,
        LOGO_BIBLIOMAP,
    )

    if logo_path:
        _, logo_col, _ = st.columns([1, 2, 1])
        with logo_col:
            st.image(str(logo_path), width=420)

    st.info(
        """
        **BiblioPangea** queda reservado como visualización avanzada dentro de BiblioMap.
        Su sentido será representar continentes del conocimiento inteligentemente unidos
        mediante redes bibliométricas, relaciones entre países, instituciones, autores,
        temas y comunidades científicas.
        """
    )

    st.write(
        """
        En esta versión futura, BiblioPangea podrá integrar mapas geográficos, redes de
        coautoría, co-ocurrencia de palabras clave, clusters temáticos y señales de
        colaboración internacional para mostrar cómo se conectan los continentes del
        conocimiento en torno a un campo científico.
        """
    )

    st.warning(
        """
        Esta sección todavía no ejecuta análisis de red. Se deja como espacio de diseño
        conceptual e iconográfico para la siguiente fase del ecosistema BiblioIntel.
        """
    )


def page_bibliomap() -> None:
    header_col, logo_col = st.columns([0.78, 0.22])

    with header_col:
        st.markdown("## BiblioMap")
        st.caption(
            "Visualización geográfica y bibliométrica preliminar de la producción científica recuperada."
        )

    with logo_col:
        if LOGO_BIBLIOMAP.exists():
            st.image(str(LOGO_BIBLIOMAP), width=400)

    st.write(
        """
        BiblioMap integra el mapa mundial, la distribución geográfica y la proyección
        futura BiblioPangea como componentes visuales del ecosistema BiblioIntel.
        """
    )

    tabs = st.tabs(
        [
            "Mapa mundial",
            "Distribución geográfica",
            "BiblioPangea — próxima versión",
        ]
    )

    with tabs[0]:
        render_world_map_section()

    with tabs[1]:
        render_geographic_detail_section()

    with tabs[2]:
        render_bibliopangea_section()


def page_mapa_mundial() -> None:
    page_bibliomap()


def page_detalle_geografico() -> None:
    page_bibliomap()


def page_publicaciones() -> None:
    st.markdown("## Publicaciones")

    df = st.session_state.openalex_results

    if df.empty and OPENALEX_RESULTS_PATH.exists():
        df = pd.read_csv(OPENALEX_RESULTS_PATH)
        st.session_state.openalex_results = df

    if df.empty:
        st.warning("Todavía no hay resultados. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    df = ensure_keywords_last_column(df)
    st.session_state.openalex_results = df

    display_columns = [
        "title",
        "publication_year",
        "authors",
        "source",
        "doi",
        "landing_page_url",
        "abstract",
        "keywords",
    ]

    available_columns = [column for column in display_columns if column in df.columns]

    st.dataframe(
        df[available_columns],
        use_container_width=True,
        height=500,
    )


def page_investigadores() -> None:
    st.markdown("## Investigadores")

    df = st.session_state.openalex_results

    if df.empty and OPENALEX_RESULTS_PATH.exists():
        df = pd.read_csv(OPENALEX_RESULTS_PATH)
        st.session_state.openalex_results = df

    if df.empty:
        st.warning("Todavía no hay resultados. Primero realiza una búsqueda en la sección 'Buscar tema'.")
        return

    authors_rows = []

    for _, row in df.iterrows():
        authors_raw = str(row.get("authors", "") or "")
        title = row.get("title", "")
        year = row.get("publication_year", "")
        countries = row.get("countries", "")
        institutions = row.get("institutions", "")

        for author in [item.strip() for item in authors_raw.split(";") if item.strip()]:
            authors_rows.append(
                {
                    "author": author,
                    "publication_year": year,
                    "title": title,
                    "countries": countries,
                    "institutions": institutions,
                }
            )

    authors_df = pd.DataFrame(authors_rows)

    if authors_df.empty:
        st.warning("No se detectaron autores en los metadatos recuperados.")
        return

    summary_df = (
        authors_df.groupby("author", as_index=False)
        .agg(
            publications=("title", "count"),
            countries=(
                "countries",
                lambda values: "; ".join(
                    sorted(
                        {
                            item.strip()
                            for value in values
                            for item in str(value).split(";")
                            if item.strip()
                        }
                    )
                ),
            ),
            institutions=(
                "institutions",
                lambda values: "; ".join(
                    sorted(
                        {
                            item.strip()
                            for value in values
                            for item in str(value).split(";")
                            if item.strip()
                        }
                    )
                ),
            ),
        )
        .sort_values("publications", ascending=False)
    )

    st.dataframe(summary_df, use_container_width=True, height=500)


def load_gap_outputs_from_disk() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga salidas de brechas desde data/processed si existen.
    """
    gap_df = pd.DataFrame()
    keyword_df = pd.DataFrame()
    temporal_df = pd.DataFrame()

    if GAP_SUGGESTIONS_PATH.exists():
        gap_df = pd.read_csv(GAP_SUGGESTIONS_PATH)

    if KEYWORD_SUMMARY_PATH.exists():
        keyword_df = pd.read_csv(KEYWORD_SUMMARY_PATH)

    if TEMPORAL_SUMMARY_PATH.exists():
        temporal_df = pd.read_csv(TEMPORAL_SUMMARY_PATH)

    if not gap_df.empty:
        st.session_state.gap_results = gap_df

    if not keyword_df.empty:
        st.session_state.keyword_results = keyword_df

    if not temporal_df.empty:
        st.session_state.temporal_results = temporal_df

    return gap_df, keyword_df, temporal_df


def load_extended_outputs_from_disk() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga tendencias, áreas poco visibles y oportunidades desde data/processed si existen.
    """
    trend_df = pd.DataFrame()
    understudied_df = pd.DataFrame()
    opportunity_df = pd.DataFrame()

    if TREND_SUMMARY_PATH.exists():
        trend_df = pd.read_csv(TREND_SUMMARY_PATH)

    if UNDERSTUDIED_AREAS_PATH.exists():
        understudied_df = pd.read_csv(UNDERSTUDIED_AREAS_PATH)

    if RESEARCH_OPPORTUNITIES_PATH.exists():
        opportunity_df = pd.read_csv(RESEARCH_OPPORTUNITIES_PATH)

    if not trend_df.empty:
        st.session_state.trend_results = trend_df

    if not understudied_df.empty:
        st.session_state.understudied_results = understudied_df

    if not opportunity_df.empty:
        st.session_state.opportunity_results = opportunity_df

    return trend_df, understudied_df, opportunity_df


def page_brechas_preliminares() -> None:
    """
    Muestra brechas preliminares, tendencias, áreas poco visibles y oportunidades.
    """
    st.markdown("## Brechas preliminares")

    st.write(
        """
        Esta sección presenta señales orientadoras de posibles brechas de investigación.
        No son conclusiones definitivas: deben ser revisadas, contrastadas y validadas
        por el investigador humano.
        """
    )

    gap_df = st.session_state.gap_results
    keyword_df = st.session_state.keyword_results
    temporal_df = st.session_state.temporal_results
    trend_df = st.session_state.trend_results
    understudied_df = st.session_state.understudied_results
    opportunity_df = st.session_state.opportunity_results

    if gap_df.empty or keyword_df.empty or temporal_df.empty:
        gap_df, keyword_df, temporal_df = load_gap_outputs_from_disk()

    if trend_df.empty or understudied_df.empty or opportunity_df.empty:
        trend_df, understudied_df, opportunity_df = load_extended_outputs_from_disk()

    if gap_df.empty:
        st.warning(
            "Todavía no hay sugerencias de brechas. Primero realiza una búsqueda en la sección 'Buscar tema' o ejecuta py modules\\gap_suggester.py."
        )
        return

    for column in ["dimension", "signal", "evidence", "suggested_gap", "caution", "priority"]:
        if column not in gap_df.columns:
            gap_df[column] = ""

    gap_df = gap_df.fillna("")
    gap_df["dimension"] = gap_df["dimension"].astype(str)
    gap_df["priority"] = gap_df["priority"].astype(str)

    total_gaps = len(gap_df)
    high_priority = len(gap_df[gap_df["priority"].str.lower() == "alta"])
    dimensions = gap_df["dimension"].nunique()
    total_trends = len(trend_df) if trend_df is not None else 0
    total_understudied = len(understudied_df) if understudied_df is not None else 0
    total_opportunities = len(opportunity_df) if opportunity_df is not None else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Señales de brecha", total_gaps)

    with col2:
        st.metric("Prioridad alta", high_priority)

    with col3:
        st.metric("Tendencias", total_trends)

    with col4:
        st.metric("Oportunidades", total_opportunities)

    st.divider()

    st.markdown("### Filtros de lectura")

    filter_col1, filter_col2 = st.columns(2)

    dimension_options = sorted([value for value in gap_df["dimension"].unique().tolist() if value])
    priority_order = ["Alta", "Media", "Baja"]
    priority_options = [
        priority for priority in priority_order
        if priority in gap_df["priority"].unique().tolist()
    ]
    extra_priorities = sorted(
        [
            priority for priority in gap_df["priority"].unique().tolist()
            if priority and priority not in priority_options
        ]
    )
    priority_options.extend(extra_priorities)

    with filter_col1:
        selected_dimensions = st.multiselect(
            "Filtrar por dimensión",
            options=dimension_options,
            default=dimension_options,
        )

    with filter_col2:
        selected_priorities = st.multiselect(
            "Filtrar por prioridad",
            options=priority_options,
            default=priority_options,
        )

    filtered_df = gap_df[
        gap_df["dimension"].isin(selected_dimensions)
        & gap_df["priority"].isin(selected_priorities)
    ].copy()

    st.caption(
        f"Mostrando {len(filtered_df)} de {len(gap_df)} señales preliminares."
    )

    if filtered_df.empty:
        st.warning("No hay brechas que coincidan con los filtros seleccionados.")
        return

    st.divider()

    main_tabs = st.tabs(
        [
            "Brechas",
            "Tendencias de estudio",
            "Áreas poco visibles",
            "Oportunidades investigativas",
            "Términos y temporalidad",
        ]
    )

    with main_tabs[0]:
        st.markdown("### Resumen visual de brechas")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            dimension_counts = (
                filtered_df.groupby("dimension", as_index=False)
                .size()
                .rename(columns={"size": "señales"})
                .sort_values("señales", ascending=False)
            )

            if not dimension_counts.empty:
                st.markdown("**Señales por dimensión**")
                st.bar_chart(
                    dimension_counts.set_index("dimension")["señales"]
                )

        with chart_col2:
            priority_counts = (
                filtered_df.groupby("priority", as_index=False)
                .size()
                .rename(columns={"size": "señales"})
                .sort_values("señales", ascending=False)
            )

            if not priority_counts.empty:
                st.markdown("**Señales por prioridad**")
                st.bar_chart(
                    priority_counts.set_index("priority")["señales"]
                )

        st.divider()

        st.markdown("### Lectura interpretativa por tarjetas")

        priority_icon = {
            "Alta": "🔴",
            "Media": "🟠",
            "Baja": "🟢",
        }

        for index, row in filtered_df.reset_index(drop=True).iterrows():
            priority = str(row.get("priority", "")).strip()
            dimension = str(row.get("dimension", "")).strip()
            signal = str(row.get("signal", "")).strip()
            evidence = str(row.get("evidence", "")).strip()
            suggested_gap = str(row.get("suggested_gap", "")).strip()
            caution = str(row.get("caution", "")).strip()

            icon = priority_icon.get(priority, "⚪")
            expander_title = f"{icon} {dimension} — {signal}"

            with st.expander(expander_title, expanded=(index < 3)):
                st.markdown(f"**Prioridad:** {priority or 'No indicada'}")
                st.markdown("**Señal detectada:**")
                st.write(signal or "No indicada.")

                st.markdown("**Evidencia bibliométrica usada por BiblioMap:**")
                st.write(evidence or "No disponible.")

                st.markdown("**Brecha preliminar sugerida:**")
                st.write(suggested_gap or "No disponible.")

                st.markdown("**Cautela metodológica:**")
                st.warning(caution or "Debe validarse mediante lectura crítica y contraste con otras fuentes.")

        st.divider()

        st.markdown("### Tabla técnica de brechas")

        with st.expander("Ver tabla completa de brechas preliminares", expanded=False):
            display_columns = [
                "dimension",
                "signal",
                "evidence",
                "suggested_gap",
                "caution",
                "priority",
            ]

            available_columns = [column for column in display_columns if column in filtered_df.columns]

            st.dataframe(
                filtered_df[available_columns],
                use_container_width=True,
                height=420,
            )

        st.download_button(
            label="Descargar brechas filtradas CSV",
            data=filtered_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="gap_suggestions_filtered.csv",
            mime="text/csv",
        )

        st.download_button(
            label="Descargar todas las brechas CSV",
            data=gap_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="gap_suggestions.csv",
            mime="text/csv",
        )

    with main_tabs[1]:
        st.markdown("### Tendencias de estudio detectadas")

        st.write(
            """
            Esta sección resume líneas dominantes, señales emergentes, señales temporales
            y polos visibles dentro de la muestra recuperada.
            """
        )

        if trend_df is None or trend_df.empty:
            st.warning("No hay tendencias disponibles. Ejecuta nuevamente la búsqueda o py modules\\gap_suggester.py.")
        else:
            trend_df = trend_df.fillna("")

            for column in [
                "trend_type",
                "trend",
                "evidence",
                "period_signal",
                "associated_terms",
                "interpretation",
                "suggested_use",
                "caution",
                "strength",
            ]:
                if column not in trend_df.columns:
                    trend_df[column] = ""

            type_options = sorted([value for value in trend_df["trend_type"].astype(str).unique().tolist() if value])

            selected_types = st.multiselect(
                "Filtrar tendencias por tipo",
                options=type_options,
                default=type_options,
            )

            trend_filtered = trend_df[trend_df["trend_type"].astype(str).isin(selected_types)].copy()

            for index, row in trend_filtered.reset_index(drop=True).iterrows():
                trend_type = str(row.get("trend_type", "")).strip()
                trend = str(row.get("trend", "")).strip()
                strength = str(row.get("strength", "")).strip()

                with st.expander(f"📈 {trend_type} — {trend} [{strength}]", expanded=(index < 2)):
                    st.markdown("**Evidencia:**")
                    st.write(row.get("evidence", ""))

                    st.markdown("**Señal temporal o contextual:**")
                    st.write(row.get("period_signal", ""))

                    st.markdown("**Términos asociados:**")
                    st.write(row.get("associated_terms", ""))

                    st.markdown("**Interpretación preliminar:**")
                    st.write(row.get("interpretation", ""))

                    st.markdown("**Uso sugerido:**")
                    st.write(row.get("suggested_use", ""))

                    st.markdown("**Cautela:**")
                    st.warning(row.get("caution", ""))

            with st.expander("Ver tabla técnica de tendencias", expanded=False):
                st.dataframe(trend_filtered, use_container_width=True, height=380)

            st.download_button(
                label="Descargar tendencias CSV",
                data=trend_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="trend_summary_filtered.csv",
                mime="text/csv",
            )

    with main_tabs[2]:
        st.markdown("### Áreas poco estudiadas o poco visibles")

        st.write(
            """
            BiblioMap no afirma que un área no exista: indica si aparece poco o no aparece
            suficientemente en esta muestra, según una lista de dimensiones esperadas.
            """
        )

        if understudied_df is None or understudied_df.empty:
            st.warning("No hay áreas poco visibles disponibles. Ejecuta nuevamente la búsqueda o py modules\\gap_suggester.py.")
        else:
            understudied_df = understudied_df.fillna("")

            for column in [
                "expected_dimension",
                "visibility_level",
                "matched_terms",
                "evidence",
                "possible_gap",
                "suggested_question",
                "how_to_verify",
                "caution",
            ]:
                if column not in understudied_df.columns:
                    understudied_df[column] = ""

            visibility_options = sorted([value for value in understudied_df["visibility_level"].astype(str).unique().tolist() if value])

            selected_visibility = st.multiselect(
                "Filtrar por nivel de visibilidad",
                options=visibility_options,
                default=visibility_options,
            )

            understudied_filtered = understudied_df[
                understudied_df["visibility_level"].astype(str).isin(selected_visibility)
            ].copy()

            visibility_counts = (
                understudied_filtered.groupby("visibility_level", as_index=False)
                .size()
                .rename(columns={"size": "áreas"})
            )

            if not visibility_counts.empty:
                st.markdown("**Áreas por nivel de visibilidad**")
                st.bar_chart(
                    visibility_counts.set_index("visibility_level")["áreas"]
                )

            for index, row in understudied_filtered.reset_index(drop=True).iterrows():
                dimension = str(row.get("expected_dimension", "")).strip()
                visibility = str(row.get("visibility_level", "")).strip()

                with st.expander(f"🔎 {dimension} — visibilidad: {visibility}", expanded=(index < 3)):
                    st.markdown("**Términos encontrados:**")
                    st.write(row.get("matched_terms", ""))

                    st.markdown("**Evidencia:**")
                    st.write(row.get("evidence", ""))

                    st.markdown("**Posible vacío:**")
                    st.write(row.get("possible_gap", ""))

                    st.markdown("**Pregunta de investigación sugerida:**")
                    st.success(row.get("suggested_question", ""))

                    st.markdown("**Cómo verificarlo:**")
                    st.write(row.get("how_to_verify", ""))

                    st.markdown("**Cautela:**")
                    st.warning(row.get("caution", ""))

            with st.expander("Ver tabla técnica de áreas poco visibles", expanded=False):
                st.dataframe(understudied_filtered, use_container_width=True, height=420)

            st.download_button(
                label="Descargar áreas poco visibles CSV",
                data=understudied_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="understudied_areas_filtered.csv",
                mime="text/csv",
            )

    with main_tabs[3]:
        st.markdown("### Oportunidades investigativas")

        st.write(
            """
            Esta sección traduce señales de brecha, tendencias y áreas poco visibles
            en oportunidades preliminares de investigación.
            """
        )

        if opportunity_df is None or opportunity_df.empty:
            st.warning("No hay oportunidades disponibles. Ejecuta nuevamente la búsqueda o py modules\\gap_suggester.py.")
        else:
            opportunity_df = opportunity_df.fillna("")

            for column in [
                "opportunity_type",
                "opportunity",
                "possible_research_question",
                "supporting_signal",
                "recommended_next_step",
                "priority",
            ]:
                if column not in opportunity_df.columns:
                    opportunity_df[column] = ""

            opportunity_priority_options = sorted([value for value in opportunity_df["priority"].astype(str).unique().tolist() if value])

            selected_opportunity_priorities = st.multiselect(
                "Filtrar oportunidades por prioridad",
                options=opportunity_priority_options,
                default=opportunity_priority_options,
            )

            opportunity_filtered = opportunity_df[
                opportunity_df["priority"].astype(str).isin(selected_opportunity_priorities)
            ].copy()

            for index, row in opportunity_filtered.reset_index(drop=True).iterrows():
                opportunity_type = str(row.get("opportunity_type", "")).strip()
                priority = str(row.get("priority", "")).strip()
                opportunity = str(row.get("opportunity", "")).strip()

                with st.expander(f"💡 {opportunity_type} — {priority}", expanded=(index < 3)):
                    st.markdown("**Oportunidad:**")
                    st.write(opportunity)

                    st.markdown("**Pregunta posible:**")
                    st.success(row.get("possible_research_question", ""))

                    st.markdown("**Señal que la respalda:**")
                    st.write(row.get("supporting_signal", ""))

                    st.markdown("**Siguiente paso recomendado:**")
                    st.write(row.get("recommended_next_step", ""))

            with st.expander("Ver tabla técnica de oportunidades", expanded=False):
                st.dataframe(opportunity_filtered, use_container_width=True, height=420)

            st.download_button(
                label="Descargar oportunidades CSV",
                data=opportunity_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="research_opportunities_filtered.csv",
                mime="text/csv",
            )

    with main_tabs[4]:
        st.markdown("### Términos y patrones frecuentes")

        if not keyword_df.empty:
            keyword_df = keyword_df.fillna("")

            for column in ["keyword", "frequency", "type"]:
                if column not in keyword_df.columns:
                    keyword_df[column] = ""

            keyword_df["frequency"] = pd.to_numeric(
                keyword_df["frequency"],
                errors="coerce",
            ).fillna(0).astype(int)

            keyword_types = sorted([value for value in keyword_df["type"].astype(str).unique().tolist() if value])

            selected_keyword_types = st.multiselect(
                "Filtrar términos por tipo",
                options=keyword_types,
                default=keyword_types,
            )

            keyword_filtered = keyword_df[keyword_df["type"].astype(str).isin(selected_keyword_types)].copy()

            top_terms = (
                keyword_filtered.sort_values("frequency", ascending=False)
                .head(20)
            )

            if not top_terms.empty:
                st.markdown("**Ranking de términos y patrones**")
                st.bar_chart(
                    top_terms.set_index("keyword")["frequency"]
                )

            with st.expander("Ver tabla de términos frecuentes", expanded=False):
                keyword_columns = [
                    column for column in ["keyword", "frequency", "type"]
                    if column in keyword_filtered.columns
                ]

                st.dataframe(
                    keyword_filtered[keyword_columns],
                    use_container_width=True,
                    height=320,
                )

            st.download_button(
                label="Descargar términos frecuentes CSV",
                data=keyword_filtered.to_csv(index=False, encoding="utf-8-sig"),
                file_name="keyword_summary_filtered.csv",
                mime="text/csv",
            )
        else:
            st.warning("No hay términos frecuentes disponibles.")

        st.divider()

        st.markdown("### Serie temporal de publicaciones")

        if not temporal_df.empty:
            temporal_df = temporal_df.fillna("")

            for column in ["publication_year", "publications", "cited_by_count"]:
                if column not in temporal_df.columns:
                    temporal_df[column] = 0

            temporal_df["publication_year"] = pd.to_numeric(
                temporal_df["publication_year"],
                errors="coerce",
            ).fillna(0).astype(int)

            temporal_df["publications"] = pd.to_numeric(
                temporal_df["publications"],
                errors="coerce",
            ).fillna(0).astype(int)

            temporal_df["cited_by_count"] = pd.to_numeric(
                temporal_df["cited_by_count"],
                errors="coerce",
            ).fillna(0).astype(int)

            temporal_df = temporal_df[temporal_df["publication_year"] > 0].sort_values("publication_year")

            if not temporal_df.empty:
                chart_df = temporal_df.copy()
                chart_df["publication_year"] = chart_df["publication_year"].astype(str)

                st.markdown("**Publicaciones por año**")
                st.bar_chart(
                    chart_df.set_index("publication_year")["publications"]
                )

                with st.expander("Ver tabla temporal", expanded=False):
                    temporal_columns = [
                        column
                        for column in ["publication_year", "publications", "cited_by_count"]
                        if column in temporal_df.columns
                    ]

                    st.dataframe(
                        temporal_df[temporal_columns],
                        use_container_width=True,
                        height=280,
                    )

                st.download_button(
                    label="Descargar serie temporal CSV",
                    data=temporal_df.to_csv(index=False, encoding="utf-8-sig"),
                    file_name="temporal_summary.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No hay años válidos en la serie temporal.")
        else:
            st.warning("No hay serie temporal disponible.")

    st.info(
        """
        Estas salidas son preliminares. BiblioMap detecta señales a partir de metadatos,
        frecuencias, países, años, fuentes, autores e instituciones. La validación requiere
        lectura crítica, revisión metodológica y contraste con otras bases como Scopus,
        Web of Science, Dimensions, Lens, Google Scholar u otras fuentes pertinentes.
        """
    )


def page_reporte_preliminar() -> None:
    """
    Genera y muestra el reporte bibliométrico preliminar descargable.
    """
    st.markdown("## Reporte preliminar")

    st.write(
        """
        Esta sección genera un informe bibliométrico preliminar a partir de los resultados
        ya procesados por BiblioMap: búsqueda OpenAlex, agrupación geográfica, brechas,
        tendencias, áreas poco visibles y oportunidades investigativas.
        """
    )

    st.info(
        """
        El reporte es orientador. No sustituye una revisión sistemática ni una
        investigación bibliométrica completa. Sirve como primer documento de trabajo
        para lectura crítica, tutoría y delimitación del problema.
        """
    )

    metadata = st.session_state.get("last_query_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        st.session_state.last_query_metadata = metadata

    tema = metadata.get("tema", "")
    query = metadata.get("query", "")
    year_from = metadata.get("year_from", "")
    year_to = metadata.get("year_to", "")
    source = metadata.get("source", "OpenAlex")

    report_query = tema or query or "Tema no especificado"

    st.markdown("### Datos base del reporte")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Fuente", source)

    with col2:
        st.metric("Año inicial", year_from if year_from else "N/D")

    with col3:
        st.metric("Año final", year_to if year_to else "N/D")

    with col4:
        processed_ready = OPENALEX_RESULTS_PATH.exists()
        st.metric("Datos procesados", "Sí" if processed_ready else "No")

    if query:
        st.caption(f"Consulta OpenAlex: {query}")

    st.divider()

    required_files = [
        ("Resultados OpenAlex", OPENALEX_RESULTS_PATH),
        ("Agrupación por país", GROUP_BY_COUNTRY_PATH),
        ("Agrupación por continente", GROUP_BY_CONTINENT_PATH),
        ("Brechas preliminares", GAP_SUGGESTIONS_PATH),
        ("Términos frecuentes", KEYWORD_SUMMARY_PATH),
        ("Serie temporal", TEMPORAL_SUMMARY_PATH),
        ("Tendencias", TREND_SUMMARY_PATH),
        ("Áreas poco visibles", UNDERSTUDIED_AREAS_PATH),
        ("Oportunidades investigativas", RESEARCH_OPPORTUNITIES_PATH),
    ]

    status_rows = []

    for label, path in required_files:
        status_rows.append(
            {
                "Elemento": label,
                "Estado": "Disponible" if path.exists() else "No encontrado",
                "Ruta": str(path.relative_to(BASE_DIR)) if path.exists() else str(path.relative_to(BASE_DIR)),
            }
        )

    status_df = pd.DataFrame(status_rows)

    with st.expander("Ver archivos usados para construir el reporte", expanded=False):
        st.dataframe(status_df, use_container_width=True, height=330)

    missing_files = [label for label, path in required_files if not path.exists()]

    if missing_files:
        st.warning(
            "Faltan algunos archivos procesados. El reporte puede generarse, pero quedará incompleto: "
            + ", ".join(missing_files)
        )

    col_btn1, col_btn2 = st.columns([1, 2])

    with col_btn1:
        generate_clicked = st.button("Generar / actualizar reporte", type="primary")

    with col_btn2:
        st.caption(
            "Recomendación: primero ejecuta una búsqueda en 'Buscar tema' y revisa brechas/tendencias antes de generar el reporte."
        )

    if generate_clicked:
        try:
            with st.spinner("Generando reporte bibliométrico preliminar..."):
                markdown_text, md_path, html_path = generate_report(query=report_query)
                pdf_path = generate_pdf_report(query=report_query)

            st.success("Reporte generado correctamente.")
            st.caption(f"Markdown: {md_path}")
            st.caption(f"HTML: {html_path}")
            st.caption(f"PDF: {pdf_path}")

        except Exception as error:
            st.error("Ocurrió un error al generar el reporte.")
            st.exception(error)

    st.divider()

    st.markdown("### Descargar reporte")

    report_exists = REPORT_MARKDOWN_PATH.exists() or REPORT_HTML_PATH.exists() or REPORT_PDF_PATH.exists()

    if not report_exists:
        st.warning("Todavía no hay reporte generado. Presiona 'Generar / actualizar reporte'.")
        render_footer()
        return

    download_col1, download_col2, download_col3 = st.columns(3)

    if REPORT_MARKDOWN_PATH.exists():
        markdown_text = REPORT_MARKDOWN_PATH.read_text(encoding="utf-8")

        with download_col1:
            st.download_button(
                label="Descargar reporte Markdown (.md)",
                data=markdown_text.encode("utf-8"),
                file_name="bibliomap_preliminary_report.md",
                mime="text/markdown",
            )

        with st.expander("Vista previa del reporte en Markdown", expanded=False):
            st.markdown(markdown_text)

    else:
        with download_col1:
            st.warning("No se encontró el reporte Markdown.")

    if REPORT_HTML_PATH.exists():
        html_text = REPORT_HTML_PATH.read_text(encoding="utf-8")

        with download_col2:
            st.download_button(
                label="Descargar reporte HTML (.html)",
                data=html_text.encode("utf-8"),
                file_name="bibliomap_preliminary_report.html",
                mime="text/html",
            )

        with st.expander("Vista previa técnica del HTML generado", expanded=False):
            st.code(html_text[:8000], language="html")

    else:
        with download_col2:
            st.warning("No se encontró el reporte HTML.")

    if REPORT_PDF_PATH.exists():
        pdf_bytes = REPORT_PDF_PATH.read_bytes()

        with download_col3:
            st.download_button(
                label="Descargar reporte PDF (.pdf)",
                data=pdf_bytes,
                file_name="bibliomap_preliminary_report.pdf",
                mime="application/pdf",
            )
    else:
        with download_col3:
            st.warning("No se encontro el reporte PDF. Instala reportlab y genera el reporte.")

    st.info(
        """
        Para entregar al tutor, puedes compartir el archivo HTML como lectura rápida
        y conservar el Markdown como versión editable del informe preliminar.
        """
    )


def page_aprender_bibliometria() -> None:
    """
    Página pedagógica de BiblioMap.
    """
    st.markdown("## Aprender bibliometría")

    st.write(
        """
        Esta sección convierte a BiblioMap en una herramienta formativa.
        Su propósito es ayudar a leer los resultados bibliométricos con criterio
        metodológico, evitando interpretaciones apresuradas.
        """
    )

    st.info(
        """
        Regla de oro: BiblioMap orienta, no sentencia. Una señal bibliométrica
        debe ser revisada, contextualizada y validada por el investigador humano.
        """
    )

    tabs = st.tabs(
        [
            "Conceptos básicos",
            "Cómo leer BiblioMap",
            "Brechas y tendencias",
            "Método recomendado",
            "Glosario mínimo",
            "Cautelas metodológicas",
        ]
    )

    with tabs[0]:
        st.markdown("### Conceptos básicos")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Bibliometría")
            st.write(
                """
                Es el uso de métodos cuantitativos para estudiar publicaciones,
                citas, autores, instituciones, fuentes y patrones de producción científica.
                Permite observar cómo se organiza y circula el conocimiento en un campo.
                """
            )

            st.markdown("#### Bibliometrología")
            st.write(
                """
                En el ecosistema BiblioIntel, la bibliometrología se entiende como
                el saber aplicado que mide, organiza, interpreta y transforma evidencia
                bibliográfica y científica en conocimiento útil para investigar.
                """
            )

            st.markdown("#### Mapeo bibliométrico")
            st.write(
                """
                Es la representación visual o estructurada de relaciones bibliográficas:
                países, autores, instituciones, temas, citas, coautorías, fuentes o redes.
                """
            )

        with col2:
            st.markdown("#### Producción científica")
            st.write(
                """
                Conjunto de publicaciones recuperadas sobre un tema: artículos,
                libros, capítulos, preprints u otros documentos académicos según
                la cobertura de la fuente consultada.
                """
            )

            st.markdown("#### Citas")
            st.write(
                """
                Las citas son referencias recibidas por una publicación. Pueden indicar
                influencia, visibilidad o circulación, pero no necesariamente calidad.
                """
            )

            st.markdown("#### Fuente académica")
            st.write(
                """
                Base o índice desde donde se recuperan metadatos. En este MVP,
                BiblioMap usa OpenAlex como fuente abierta inicial.
                """
            )

    with tabs[1]:
        st.markdown("### Cómo leer BiblioMap")

        st.markdown("#### 1. Buscar tema")
        st.write(
            """
            Es el punto de entrada. Allí se escribe el tema de investigación y las
            palabras clave. La calidad de la búsqueda depende mucho de estos términos.
            """
        )

        st.markdown("#### 2. Resultados preliminares")
        st.write(
            """
            Muestran los registros recuperados. Deben revisarse títulos, años,
            autores, países, instituciones, fuentes, DOI y enlaces. No todo resultado
            recuperado será necesariamente pertinente.
            """
        )

        st.markdown("#### 3. BiblioMap / mapa mundial")
        st.write(
            """
            Permite observar la distribución geográfica de la producción científica.
            Un país más oscuro indica mayor número de publicaciones o citas, según la métrica seleccionada.
            """
        )

        st.warning(
            """
            Una publicación con autores de varios países puede contar para más de un país.
            Por eso el conteo geográfico puede ser mayor que el número total de documentos.
            """
        )

        st.markdown("#### 4. Distribución geográfica")
        st.write(
            """
            Desagrega los datos por país y región. Es útil para identificar polos
            de producción y zonas de baja presencia relativa.
            """
        )

        st.markdown("#### 5. Investigadores y publicaciones")
        st.write(
            """
            Ayudan a ubicar autores, instituciones, fuentes y documentos relevantes.
            Son puntos de partida para lectura, contacto académico y construcción del estado del arte.
            """
        )

    with tabs[2]:
        st.markdown("### Brechas y tendencias")

        st.markdown("#### Brecha preliminar")
        st.write(
            """
            Es una posible zona de investigación poco desarrollada, poco visible,
            poco conectada o insuficientemente abordada dentro de la muestra recuperada.
            """
        )

        st.markdown("#### Tendencia de estudio")
        st.write(
            """
            Es un patrón visible en la muestra: términos frecuentes, crecimiento reciente,
            concentración temporal, polos geográficos o líneas dominantes.
            """
        )

        st.markdown("#### Área poco visible")
        st.write(
            """
            Es una dimensión que aparece poco o no aparece en títulos y abstracts,
            según la búsqueda realizada. No significa que no exista; significa que
            no fue suficientemente detectada en esta muestra.
            """
        )

        st.markdown("#### Oportunidad investigativa")
        st.write(
            """
            Es una formulación preliminar que convierte una señal bibliométrica en
            una posible pregunta, ruta o foco de investigación.
            """
        )

        st.success(
            """
            Fórmula práctica:
            señal bibliométrica + lectura crítica + contexto humano = oportunidad investigativa.
            """
        )

    with tabs[3]:
        st.markdown("### Método recomendado de uso")

        steps = [
            ("Paso 1. Formular el tema", "Escribe el tema de investigación de forma clara. Luego tradúcelo a palabras clave en español e inglés para mejorar cobertura."),
            ("Paso 2. Ejecutar búsqueda exploratoria", "Haz una primera consulta con 50 a 100 resultados. Revisa si los documentos recuperados realmente pertenecen al tema."),
            ("Paso 3. Ajustar términos", "Si hay ruido, elimina palabras ambiguas. Si hay pocos resultados, agrega sinónimos, conceptos cercanos o términos en inglés."),
            ("Paso 4. Leer BiblioMap y distribución geográfica", "Observa qué países, regiones e instituciones aparecen con más fuerza. Luego revisa qué zonas aparecen poco o no aparecen."),
            ("Paso 5. Revisar brechas y tendencias", "Lee las tarjetas de brechas, tendencias, áreas poco visibles y oportunidades. Tómalas como hipótesis iniciales, no como conclusiones cerradas."),
            ("Paso 6. Validar con lectura crítica", "Selecciona documentos clave, lee abstracts, revisa métodos, compara fuentes y construye una matriz manual de hallazgos."),
            ("Paso 7. Contrastar con otras bases", "Cuando el estudio sea formal, contrasta con Scopus, Web of Science, Dimensions, Lens, Google Scholar u otras fuentes pertinentes."),
        ]

        for title, body in steps:
            st.markdown(f"#### {title}")
            st.write(body)

    with tabs[4]:
        st.markdown("### Glosario mínimo")

        glossary = pd.DataFrame(
            [
                {"Término": "Metadatos", "Significado": "Datos descriptivos de una publicación: título, autores, año, DOI, fuente, instituciones, países y citas."},
                {"Término": "Corpus", "Significado": "Conjunto de documentos recuperados para analizar un tema."},
                {"Término": "Coautoría", "Significado": "Relación entre autores que publican juntos."},
                {"Término": "Afiliación", "Significado": "Institución a la que pertenece un autor en una publicación."},
                {"Término": "Citación", "Significado": "Referencia que una publicación recibe de otra."},
                {"Término": "Fuente", "Significado": "Revista, libro, repositorio o plataforma donde aparece una publicación."},
                {"Término": "Tendencia", "Significado": "Patrón visible de crecimiento, concentración o recurrencia temática."},
                {"Término": "Brecha", "Significado": "Zona poco abordada, poco visible o insuficientemente articulada en la literatura recuperada."},
                {"Término": "OpenAlex", "Significado": "Base abierta de metadatos académicos usada por BiblioMap en este MVP."},
                {"Término": "Validación humana", "Significado": "Revisión crítica que debe hacer el investigador antes de aceptar una señal bibliométrica como hallazgo."},
            ]
        )

        st.dataframe(glossary, use_container_width=True, height=420)

    with tabs[5]:
        st.markdown("### Cautelas metodológicas")

        cautions = [
            "Una base de datos no representa toda la ciencia mundial. OpenAlex tiene amplia cobertura, pero no sustituye todas las fuentes académicas.",
            "Más citas no siempre significa más calidad. Las citas pueden reflejar visibilidad, antigüedad, controversia o centralidad, pero no son juicio definitivo de valor.",
            "La ausencia de resultados no prueba ausencia de investigación. Puede deberse a términos de búsqueda, idioma, cobertura, metadatos incompletos o indexación limitada.",
            "Los años recientes suelen estar incompletos. Muchas publicaciones tardan en indexarse o acumular citas.",
            "Las brechas son hipótesis de trabajo. Deben convertirse en preguntas de investigación mediante lectura crítica, delimitación teórica y validación metodológica.",
        ]

        for caution in cautions:
            st.warning(caution)

        st.info(
            """
            Criterio inteligentizador:
            el software procesa evidencia, la IA amplifica interpretación,
            la inteligencia humana profundiza el conocimiento y la creatividad
            transforma los resultados en nuevas rutas investigativas.
            """
        )


def page_placeholder(title: str, description: str) -> None:
    st.markdown(f"## {title}")
    st.write(description)
    st.warning("Esta sección será desarrollada en las próximas fases del MVP.")


def render_footer() -> None:
    st.divider()
    st.markdown(
        """
        <div class="footer-text">
        BiblioIntel — BiblioQuest + BiblioMap. Desarrollo de LEGIN.
        De la observación al objetivo; del mapa a la inteligencia investigativa.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="BiblioIntel | BiblioMap",
        page_icon="📚",
        layout="wide",
    )

    init_session_state()
    load_css()
    menu = render_sidebar()

    if menu == "Inicio":
        page_inicio()

    elif menu == "BiblioQuest":
        page_biblioquest()

    elif menu == "Buscar tema":
        page_buscar_tema()

    elif menu == "BiblioMap":
        page_bibliomap()

    elif menu == "Investigadores":
        page_investigadores()

    elif menu == "Publicaciones":
        page_publicaciones()

    elif menu == "Brechas preliminares":
        page_brechas_preliminares()

    elif menu == "Reporte preliminar":
        page_reporte_preliminar()

    elif menu == "Aprender bibliometría":
        page_aprender_bibliometria()

    render_footer()


if __name__ == "__main__":
    main()
