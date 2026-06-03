"""
gap_suggester.py

Módulo de sugerencia de brechas preliminares, tendencias de estudio,
áreas poco visibles y oportunidades investigativas para BiblioMap.

Este módulo NO declara brechas definitivas. Genera señales orientadoras
a partir de metadatos bibliométricos recuperados desde OpenAlex.

Entradas esperadas:
    data/processed/openalex_search_results.csv
    data/processed/group_by_country.csv
    data/processed/group_by_continent.csv

Salidas generadas:
    data/processed/gap_suggestions.csv
    data/processed/keyword_summary.csv
    data/processed/temporal_summary.csv
    data/processed/trend_summary.csv
    data/processed/understudied_areas.csv
    data/processed/research_opportunities.csv

Uso desde terminal:
    py modules\\gap_suggester.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OPENALEX_RESULTS_PATH = PROCESSED_DIR / "openalex_search_results.csv"
GROUP_BY_COUNTRY_PATH = PROCESSED_DIR / "group_by_country.csv"
GROUP_BY_CONTINENT_PATH = PROCESSED_DIR / "group_by_continent.csv"

GAP_SUGGESTIONS_PATH = PROCESSED_DIR / "gap_suggestions.csv"
KEYWORD_SUMMARY_PATH = PROCESSED_DIR / "keyword_summary.csv"
TEMPORAL_SUMMARY_PATH = PROCESSED_DIR / "temporal_summary.csv"

TREND_SUMMARY_PATH = PROCESSED_DIR / "trend_summary.csv"
UNDERSTUDIED_AREAS_PATH = PROCESSED_DIR / "understudied_areas.csv"
RESEARCH_OPPORTUNITIES_PATH = PROCESSED_DIR / "research_opportunities.csv"


STOPWORDS = {
    # English
    "the", "and", "for", "with", "from", "into", "that", "this", "these", "those",
    "are", "was", "were", "been", "being", "have", "has", "had", "not", "but",
    "about", "between", "within", "without", "using", "used", "use", "based",
    "study", "studies", "research", "paper", "article", "review", "analysis",
    "approach", "case", "cases", "towards", "toward", "new", "future", "current",
    "can", "may", "will", "could", "should", "would", "also", "than", "then",
    "their", "there", "where", "when", "what", "which", "who", "whose", "why",
    "how", "our", "your", "its", "his", "her", "them", "they", "you", "all",
    "more", "most", "less", "least", "one", "two", "three", "into", "via",

    # Spanish
    "los", "las", "una", "uno", "unos", "unas", "para", "con", "desde", "entre",
    "sobre", "hacia", "como", "este", "esta", "estos", "estas", "ese", "esa",
    "esos", "esas", "por", "del", "que", "cual", "cuales", "donde", "cuando",
    "investigacion", "estudio", "estudios", "analisis", "articulo", "revision",
    "caso", "casos", "nuevo", "nueva", "actual", "tambien", "mas", "menos",
    "sus", "son", "ser", "fue", "han", "sin", "de", "la", "el", "y",
}


LATIN_AMERICA_CODES = {
    "AR", "BO", "BR", "CL", "CO", "CR", "CU", "DO", "EC", "GT", "HN", "MX",
    "NI", "PA", "PE", "PR", "PY", "SV", "UY", "VE"
}


EXPECTED_DIMENSIONS: Dict[str, Dict[str, object]] = {
    "Ética y responsabilidad": {
        "terms": ["ethics", "ethical", "responsibility", "responsible", "accountability", "bias", "fairness"],
        "possible_gap": "dimensión ética, responsabilidad, sesgos, rendición de cuentas o justicia algorítmica",
        "question": "¿Cómo se incorporan criterios éticos y de responsabilidad en el uso del tema estudiado?",
    },
    "Gobernanza y regulación": {
        "terms": ["governance", "policy", "regulation", "regulatory", "law", "legal", "compliance"],
        "possible_gap": "gobernanza, regulación, política institucional o cumplimiento",
        "question": "¿Qué modelos de gobernanza o regulación orientan la adopción del tema en instituciones y comunidades científicas?",
    },
    "América Latina y Caribe": {
        "terms": ["latin", "latam", "caribbean", "venezuela", "colombia", "brazil", "mexico", "chile", "argentina"],
        "possible_gap": "contextualización latinoamericana, caribeña o venezolana",
        "question": "¿Cómo se configura el tema en América Latina y el Caribe frente a los polos dominantes de producción científica?",
    },
    "Educación y formación": {
        "terms": ["education", "educational", "learning", "teaching", "student", "students", "training", "literacy"],
        "possible_gap": "formación, educación superior, alfabetización científica o aprendizaje metodológico",
        "question": "¿Qué usos formativos, pedagógicos o metodológicos se están desarrollando en torno al tema?",
    },
    "Sostenibilidad e impacto socioambiental": {
        "terms": ["sustainability", "sustainable", "environmental", "climate", "ecological", "social impact"],
        "possible_gap": "sostenibilidad, impacto ambiental o responsabilidad socioecológica",
        "question": "¿Qué relación tiene el tema con la sostenibilidad, el bienestar social o el impacto ambiental?",
    },
    "Metodología y diseño de investigación": {
        "terms": ["methodology", "methodological", "method", "methods", "bibliometric", "systematic", "protocol", "framework"],
        "possible_gap": "diseño metodológico, protocolos, validación y calidad de evidencia",
        "question": "¿Qué métodos se están usando y qué limitaciones metodológicas permanecen poco resueltas?",
    },
    "Transferencia tecnológica e innovación": {
        "terms": ["innovation", "technology transfer", "transfer", "commercialization", "industry", "entrepreneurship"],
        "possible_gap": "transferencia tecnológica, innovación aplicada, apropiación o uso sectorial",
        "question": "¿Cómo se transfiere el conocimiento generado hacia aplicaciones, organizaciones o políticas de innovación?",
    },
    "Política pública e institucionalidad": {
        "terms": ["public policy", "policy", "government", "institutional", "institutions", "state", "public sector"],
        "possible_gap": "política pública, gestión institucional y toma de decisiones",
        "question": "¿Qué implicaciones institucionales y de política pública emergen alrededor del tema?",
    },
    "Epistemología y producción de conocimiento": {
        "terms": ["epistemology", "knowledge production", "scientific knowledge", "science", "epistemic", "paradigm"],
        "possible_gap": "fundamentos epistemológicos, producción de conocimiento y cambios paradigmáticos",
        "question": "¿Cómo transforma el tema la producción, validación y circulación del conocimiento científico?",
    },
    "Autoría humana y creatividad": {
        "terms": ["human", "authorship", "creativity", "creative", "creator", "co-creation", "collaboration"],
        "possible_gap": "autoría humana, creatividad, co-creación y agencia del investigador",
        "question": "¿Cómo se reconfigura la creatividad humana, la autoría y la agencia investigativa en este campo?",
    },
}


def split_semicolon_values(value: object) -> List[str]:
    if value is None:
        return []

    text = str(value).strip()

    if not text or text.lower() == "nan":
        return []

    return [item.strip() for item in text.split(";") if item.strip()]


def normalize_text(text: object) -> str:
    if text is None:
        return ""

    value = str(text).lower()
    value = value.replace("á", "a").replace("é", "e").replace("í", "i")
    value = value.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    value = re.sub(r"[^a-z0-9\s-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def tokenize(text: object) -> List[str]:
    normalized = normalize_text(text)
    tokens = []

    for token in normalized.split():
        token = token.strip("- ")

        if len(token) < 4:
            continue

        if token in STOPWORDS:
            continue

        if token.isdigit():
            continue

        tokens.append(token)

    return tokens


def corpus_text(df: pd.DataFrame) -> str:
    texts: List[str] = []

    for column in ["title", "abstract"]:
        if column in df.columns:
            texts.extend(df[column].dropna().astype(str).tolist())

    return normalize_text(" ".join(texts))


def extract_keywords(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["keyword", "frequency"])

    texts: List[str] = []

    for column in ["title", "abstract"]:
        if column in df.columns:
            texts.extend(df[column].dropna().astype(str).tolist())

    counter: Counter[str] = Counter()

    for text in texts:
        counter.update(tokenize(text))

    rows = [
        {"keyword": keyword, "frequency": frequency}
        for keyword, frequency in counter.most_common(top_n)
    ]

    return pd.DataFrame(rows)


def extract_bigrams(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["bigram", "frequency"])

    texts: List[str] = []

    for column in ["title", "abstract"]:
        if column in df.columns:
            texts.extend(df[column].dropna().astype(str).tolist())

    counter: Counter[str] = Counter()

    for text in texts:
        tokens = tokenize(text)

        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i + 1]}"
            counter[bigram] += 1

    rows = [
        {"bigram": bigram, "frequency": frequency}
        for bigram, frequency in counter.most_common(top_n)
    ]

    return pd.DataFrame(rows)


def temporal_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "publication_year" not in df.columns:
        return pd.DataFrame(columns=["publication_year", "publications", "cited_by_count"])

    temporal = df.copy()
    temporal["publication_year"] = pd.to_numeric(
        temporal["publication_year"],
        errors="coerce",
    )

    temporal = temporal.dropna(subset=["publication_year"])
    temporal["publication_year"] = temporal["publication_year"].astype(int)

    if "cited_by_count" not in temporal.columns:
        temporal["cited_by_count"] = 0

    temporal["cited_by_count"] = pd.to_numeric(
        temporal["cited_by_count"],
        errors="coerce",
    ).fillna(0).astype(int)

    return (
        temporal.groupby("publication_year", as_index=False)
        .agg(
            publications=("publication_year", "count"),
            cited_by_count=("cited_by_count", "sum"),
        )
        .sort_values("publication_year")
    )


def source_summary(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty or "source" not in df.columns:
        return pd.DataFrame(columns=["source", "publications"])

    source_df = df.copy()
    source_df["source"] = source_df["source"].fillna("").astype(str).str.strip()
    source_df = source_df[source_df["source"] != ""]

    if source_df.empty:
        return pd.DataFrame(columns=["source", "publications"])

    return (
        source_df.groupby("source", as_index=False)
        .agg(publications=("source", "count"))
        .sort_values("publications", ascending=False)
        .head(top_n)
    )


def institution_summary(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty or "institutions" not in df.columns:
        return pd.DataFrame(columns=["institution", "publications"])

    counter: Counter[str] = Counter()

    for value in df["institutions"].dropna():
        institutions = split_semicolon_values(value)
        counter.update(institutions)

    rows = [
        {"institution": institution, "publications": count}
        for institution, count in counter.most_common(top_n)
    ]

    return pd.DataFrame(rows)


def author_summary(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if df.empty or "authors" not in df.columns:
        return pd.DataFrame(columns=["author", "publications"])

    counter: Counter[str] = Counter()

    for value in df["authors"].dropna():
        authors = split_semicolon_values(value)
        counter.update(authors)

    rows = [
        {"author": author, "publications": count}
        for author, count in counter.most_common(top_n)
    ]

    return pd.DataFrame(rows)


def add_gap(
    rows: List[Dict[str, object]],
    dimension: str,
    signal: str,
    evidence: str,
    suggested_gap: str,
    caution: str,
    priority: str = "Media",
) -> None:
    rows.append(
        {
            "dimension": dimension,
            "signal": signal,
            "evidence": evidence,
            "suggested_gap": suggested_gap,
            "caution": caution,
            "priority": priority,
        }
    )


def suggest_geographic_gaps(
    country_df: pd.DataFrame,
    continent_df: pd.DataFrame,
    rows: List[Dict[str, object]],
) -> None:
    if country_df.empty:
        add_gap(
            rows,
            "Geográfica",
            "No hay agrupación por país disponible.",
            "No se encontró group_by_country.csv o está vacío.",
            "Realizar una búsqueda bibliométrica y generar agrupación por país antes de interpretar brechas geográficas.",
            "La ausencia de datos no equivale a ausencia de investigación.",
            "Alta",
        )
        return

    working = country_df.copy()

    if "publications" not in working.columns:
        return

    working["publications"] = pd.to_numeric(
        working["publications"],
        errors="coerce",
    ).fillna(0).astype(int)

    working["cited_by_count"] = pd.to_numeric(
        working.get("cited_by_count", 0),
        errors="coerce",
    ).fillna(0).astype(int)

    total_publications = int(working["publications"].sum())

    if total_publications <= 0:
        return

    top_country = working.sort_values("publications", ascending=False).head(1)

    if not top_country.empty:
        country = top_country.iloc[0].get("country", "")
        publications = int(top_country.iloc[0].get("publications", 0))
        share = publications / total_publications

        if share >= 0.25:
            add_gap(
                rows,
                "Geográfica",
                "Alta concentración en un país líder.",
                f"{country} concentra {publications} apariciones país-publicación ({share:.1%} del total expandido).",
                "Explorar si existen contextos regionales o nacionales poco estudiados frente al liderazgo del país dominante.",
                "El conteo es expandido por afiliación: una misma publicación puede sumar en varios países.",
                "Alta",
            )

    latin_df = working[working["country_code"].astype(str).str.upper().isin(LATIN_AMERICA_CODES)]
    latin_publications = int(latin_df["publications"].sum()) if not latin_df.empty else 0
    latin_share = latin_publications / total_publications

    if latin_share < 0.10:
        add_gap(
            rows,
            "Geográfica",
            "Baja presencia relativa de América Latina y el Caribe.",
            f"América Latina y el Caribe suma {latin_publications} apariciones país-publicación ({latin_share:.1%} del total expandido).",
            "Explorar una brecha regional latinoamericana: aplicaciones, marcos institucionales, capacidades locales o estudios comparativos desde la región.",
            "La baja presencia puede depender de la fuente OpenAlex, del idioma de búsqueda y de los metadatos de afiliación.",
            "Alta",
        )

    venezuela_df = working[working["country_code"].astype(str).str.upper() == "VE"]

    if venezuela_df.empty or int(venezuela_df["publications"].sum()) == 0:
        add_gap(
            rows,
            "Geográfica",
            "No se detectó Venezuela en los metadatos recuperados.",
            "No aparece el código VE en la agrupación por país.",
            "Explorar una posible oportunidad de investigación situada desde Venezuela o desde instituciones venezolanas.",
            "Debe verificarse con búsquedas en español, variantes terminológicas y otras fuentes académicas.",
            "Alta",
        )

    if not continent_df.empty and "publications" in continent_df.columns:
        cont = continent_df.copy()
        cont["publications"] = pd.to_numeric(
            cont["publications"],
            errors="coerce",
        ).fillna(0).astype(int)

        max_publications = int(cont["publications"].max())

        low_continents = cont[
            (cont["publications"] > 0)
            & (cont["publications"] <= max(1, int(max_publications * 0.15)))
        ]

        if not low_continents.empty:
            regions = "; ".join(low_continents["continent"].astype(str).tolist())

            add_gap(
                rows,
                "Geográfica",
                "Regiones con baja presencia relativa.",
                f"Regiones con baja presencia frente a la región dominante: {regions}.",
                "Evaluar estudios comparativos con regiones subrepresentadas o análisis de transferencia contextual.",
                "La clasificación continental es amplia y preliminar; requiere revisión de afiliaciones.",
                "Media",
            )


def suggest_temporal_gaps(df: pd.DataFrame, rows: List[Dict[str, object]]) -> None:
    temporal = temporal_summary(df)

    if temporal.empty:
        add_gap(
            rows,
            "Temporal",
            "No hay años de publicación suficientes.",
            "No se pudo construir la serie temporal.",
            "Revisar filtros de año o ampliar la búsqueda.",
            "La ausencia de año puede deberse a metadatos incompletos.",
            "Media",
        )
        return

    total_years = len(temporal)

    if total_years < 3:
        add_gap(
            rows,
            "Temporal",
            "Ventana temporal muy estrecha.",
            f"Solo se detectaron {total_years} años con publicaciones.",
            "Ampliar el periodo para identificar evolución del campo, rupturas y tendencias.",
            "Una ventana corta no permite inferir ciclos de consolidación o emergencia.",
            "Media",
        )
        return

    mean_publications = temporal["publications"].mean()
    recent_year = int(temporal["publication_year"].max())
    recent_count = int(
        temporal.loc[
            temporal["publication_year"] == recent_year,
            "publications",
        ].iloc[0]
    )

    if recent_count < mean_publications * 0.5:
        add_gap(
            rows,
            "Temporal",
            "Baja presencia en el año más reciente recuperado.",
            f"El año {recent_year} tiene {recent_count} publicaciones frente a un promedio anual de {mean_publications:.2f}.",
            "Explorar si el tema está disminuyendo, si existe retraso de indexación o si conviene ajustar términos de búsqueda.",
            "Los años recientes suelen estar incompletos por retraso de indexación.",
            "Media",
        )

    peak_row = temporal.sort_values("publications", ascending=False).head(1).iloc[0]
    peak_year = int(peak_row["publication_year"])
    peak_count = int(peak_row["publications"])

    if peak_count >= mean_publications * 2:
        add_gap(
            rows,
            "Temporal",
            "Concentración temporal en un año pico.",
            f"El año {peak_year} concentra {peak_count} publicaciones, por encima del promedio anual de {mean_publications:.2f}.",
            "Analizar qué evento, tecnología, debate o publicación detonó el pico y qué preguntas quedaron abiertas después.",
            "Un pico puede responder a coyunturas editoriales, tecnológicas o de indexación.",
            "Media",
        )


def suggest_thematic_gaps(
    df: pd.DataFrame,
    keyword_df: pd.DataFrame,
    bigram_df: pd.DataFrame,
    rows: List[Dict[str, object]],
) -> None:
    if keyword_df.empty and bigram_df.empty:
        add_gap(
            rows,
            "Temática",
            "No se pudieron extraer términos frecuentes.",
            "Títulos y abstracts insuficientes o vacíos.",
            "Revisar la calidad de metadatos y recuperar abstracts cuando sea posible.",
            "La extracción automática no sustituye análisis de contenido.",
            "Media",
        )
        return

    top_keywords = keyword_df.head(8)["keyword"].tolist() if not keyword_df.empty else []
    top_bigrams = bigram_df.head(8)["bigram"].tolist() if not bigram_df.empty else []

    evidence_parts = []

    if top_keywords:
        evidence_parts.append("Términos frecuentes: " + ", ".join(top_keywords))

    if top_bigrams:
        evidence_parts.append("Bigramas frecuentes: " + ", ".join(top_bigrams))

    evidence = " | ".join(evidence_parts)

    add_gap(
        rows,
        "Temática",
        "Núcleo temático dominante detectado.",
        evidence,
        "Contrastar el núcleo temático dominante con dimensiones menos visibles: contexto local, aplicación sectorial, impacto social, gobernanza, metodología, transferencia o educación.",
        "La frecuencia de términos no equivale a relevancia teórica; debe revisarse lectura cualitativa.",
        "Media",
    )

    corpus = corpus_text(df)

    for label, data in EXPECTED_DIMENSIONS.items():
        terms = data["terms"]
        hits = [term for term in terms if normalize_text(term) in corpus]

        if not hits:
            add_gap(
                rows,
                "Temática",
                f"Baja visibilidad automática de la dimensión: {label}.",
                f"No se detectaron términos asociados a {label} entre títulos y abstracts normalizados.",
                f"Explorar una posible brecha sobre {data['possible_gap']}.",
                "La ausencia automática debe verificarse mediante lectura de títulos, abstracts y búsqueda con términos específicos.",
                "Media",
            )


def suggest_concentration_gaps(df: pd.DataFrame, rows: List[Dict[str, object]]) -> None:
    total_records = len(df)

    if total_records == 0:
        return

    sources = source_summary(df, top_n=10)

    if not sources.empty:
        top_source = sources.iloc[0]
        source_name = top_source["source"]
        source_count = int(top_source["publications"])
        share = source_count / total_records

        if share >= 0.15:
            add_gap(
                rows,
                "Fuentes",
                "Concentración en una fuente o revista principal.",
                f"{source_name} concentra {source_count} registros ({share:.1%} de la muestra recuperada).",
                "Explorar si el campo está concentrado editorialmente y ampliar la búsqueda hacia otras disciplinas, bases o revistas.",
                "La concentración puede depender de la estrategia de búsqueda y de la cobertura de OpenAlex.",
                "Media",
            )

    institutions = institution_summary(df, top_n=10)

    if not institutions.empty:
        top_institution = institutions.iloc[0]
        institution_name = top_institution["institution"]
        institution_count = int(top_institution["publications"])

        if institution_count >= 3:
            add_gap(
                rows,
                "Institucional",
                "Instituciones dominantes detectadas.",
                f"La institución más recurrente es {institution_name}, con {institution_count} apariciones.",
                "Explorar instituciones periféricas o redes emergentes que no aparecen en los núcleos dominantes.",
                "La afiliación institucional puede repetirse por coautorías y metadatos múltiples.",
                "Baja",
            )

    authors = author_summary(df, top_n=10)

    if not authors.empty:
        top_author = authors.iloc[0]
        author_name = top_author["author"]
        author_count = int(top_author["publications"])

        if author_count >= 3:
            add_gap(
                rows,
                "Autoría",
                "Autores recurrentes detectados.",
                f"El autor más recurrente es {author_name}, con {author_count} publicaciones en la muestra.",
                "Explorar autores emergentes, redes periféricas o perspectivas alternativas al núcleo autoral dominante.",
                "La recurrencia autoral no implica liderazgo absoluto del campo; debe revisarse citación, redes y pertinencia temática.",
                "Baja",
            )


def suggest_preliminary_gaps(
    df: pd.DataFrame,
    country_df: Optional[pd.DataFrame] = None,
    continent_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if country_df is None:
        country_df = pd.DataFrame()

    if continent_df is None:
        continent_df = pd.DataFrame()

    rows: List[Dict[str, object]] = []

    keyword_df = extract_keywords(df, top_n=30)
    bigram_df = extract_bigrams(df, top_n=30)
    temporal_df = temporal_summary(df)

    suggest_geographic_gaps(country_df, continent_df, rows)
    suggest_temporal_gaps(df, rows)
    suggest_thematic_gaps(df, keyword_df, bigram_df, rows)
    suggest_concentration_gaps(df, rows)

    if not rows:
        add_gap(
            rows,
            "General",
            "No se detectaron señales fuertes de brecha con las reglas actuales.",
            "La muestra no activó umbrales automáticos de concentración, baja presencia o vacío.",
            "Realizar revisión cualitativa, ampliar términos de búsqueda y contrastar con Scopus, Web of Science u otras fuentes.",
            "La ausencia de señales automáticas no significa ausencia de brechas.",
            "Media",
        )

    gap_df = pd.DataFrame(rows)

    if not bigram_df.empty:
        bigram_export = bigram_df.rename(columns={"bigram": "keyword"})
        bigram_export["type"] = "bigram"
    else:
        bigram_export = pd.DataFrame(columns=["keyword", "frequency", "type"])

    if not keyword_df.empty:
        keyword_export = keyword_df.copy()
        keyword_export["type"] = "keyword"
    else:
        keyword_export = pd.DataFrame(columns=["keyword", "frequency", "type"])

    keyword_export = pd.concat(
        [keyword_export, bigram_export[["keyword", "frequency", "type"]]],
        ignore_index=True,
    )

    return gap_df, keyword_export, temporal_df


def save_gap_outputs(
    gap_df: pd.DataFrame,
    keyword_df: pd.DataFrame,
    temporal_df: pd.DataFrame,
    output_dir: Path | str = PROCESSED_DIR,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    gap_df.to_csv(output_path / "gap_suggestions.csv", index=False, encoding="utf-8-sig")
    keyword_df.to_csv(output_path / "keyword_summary.csv", index=False, encoding="utf-8-sig")
    temporal_df.to_csv(output_path / "temporal_summary.csv", index=False, encoding="utf-8-sig")


def term_counts_by_period(df: pd.DataFrame, terms: List[str]) -> Tuple[Dict[str, int], Dict[str, int], str]:
    """
    Cuenta términos en periodo anterior vs periodo reciente.

    Retorna:
        previous_counts
        recent_counts
        period_label
    """
    if df.empty or "publication_year" not in df.columns:
        return {}, {}, "sin periodo"

    working = df.copy()
    working["publication_year"] = pd.to_numeric(working["publication_year"], errors="coerce")
    working = working.dropna(subset=["publication_year"])
    working["publication_year"] = working["publication_year"].astype(int)

    if working.empty:
        return {}, {}, "sin periodo"

    max_year = int(working["publication_year"].max())
    recent_start = max_year - 2

    previous = working[working["publication_year"] < recent_start]
    recent = working[working["publication_year"] >= recent_start]

    previous_text = corpus_text(previous)
    recent_text = corpus_text(recent)

    previous_counts: Dict[str, int] = {}
    recent_counts: Dict[str, int] = {}

    for term in terms:
        normalized = normalize_text(term)
        previous_counts[term] = previous_text.count(normalized)
        recent_counts[term] = recent_text.count(normalized)

    period_label = f"reciente={recent_start}-{max_year}; previo=< {recent_start}"

    return previous_counts, recent_counts, period_label


def detect_study_trends(
    df: pd.DataFrame,
    keyword_df: pd.DataFrame,
    temporal_df: pd.DataFrame,
    country_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Detecta tendencias de estudio preliminares.

    La tendencia se basa en frecuencia de términos, aparición reciente,
    concentración temporal y concentración geográfica.
    """
    rows: List[Dict[str, object]] = []

    if keyword_df is None or keyword_df.empty:
        keyword_df = extract_keywords(df, top_n=30)

    keyword_only = keyword_df.copy()

    if "type" in keyword_only.columns:
        keyword_only = keyword_only[keyword_only["type"].astype(str) == "keyword"]

    if "frequency" in keyword_only.columns:
        keyword_only["frequency"] = pd.to_numeric(keyword_only["frequency"], errors="coerce").fillna(0).astype(int)

    top_terms = keyword_only.sort_values("frequency", ascending=False).head(10)

    if not top_terms.empty:
        terms = top_terms["keyword"].astype(str).tolist()
        evidence = ", ".join([f"{row.keyword} ({int(row.frequency)})" for row in top_terms.itertuples()])

        rows.append(
            {
                "trend_type": "Dominante",
                "trend": "Núcleo temático dominante de la muestra",
                "evidence": evidence,
                "period_signal": "Frecuencia agregada en títulos y abstracts.",
                "associated_terms": ", ".join(terms),
                "interpretation": "Estos términos marcan el centro visible del corpus recuperado.",
                "suggested_use": "Usarlos para formular el estado del arte inicial y comparar contra dimensiones ausentes o débiles.",
                "caution": "La frecuencia no equivale a importancia teórica; requiere lectura cualitativa.",
                "strength": "Alta",
            }
        )

        previous_counts, recent_counts, period_label = term_counts_by_period(df, terms)

        emerging_terms = []
        declining_terms = []

        for term in terms:
            previous_count = previous_counts.get(term, 0)
            recent_count = recent_counts.get(term, 0)

            if recent_count >= 2 and recent_count >= previous_count:
                emerging_terms.append(f"{term} ({previous_count}->{recent_count})")

            if previous_count >= 3 and recent_count == 0:
                declining_terms.append(f"{term} ({previous_count}->0)")

        if emerging_terms:
            rows.append(
                {
                    "trend_type": "Emergente",
                    "trend": "Términos con mayor visibilidad en el periodo reciente",
                    "evidence": "; ".join(emerging_terms[:10]),
                    "period_signal": period_label,
                    "associated_terms": ", ".join([item.split(" ")[0] for item in emerging_terms[:10]]),
                    "interpretation": "Estos términos pueden indicar líneas recientes de investigación dentro de la muestra.",
                    "suggested_use": "Revisar artículos recientes asociados y evaluar si hay una agenda emergente.",
                    "caution": "Los años recientes pueden estar afectados por retrasos de indexación.",
                    "strength": "Media",
                }
            )

        if declining_terms:
            rows.append(
                {
                    "trend_type": "Descendente",
                    "trend": "Términos con menor visibilidad reciente",
                    "evidence": "; ".join(declining_terms[:10]),
                    "period_signal": period_label,
                    "associated_terms": ", ".join([item.split(" ")[0] for item in declining_terms[:10]]),
                    "interpretation": "Estos términos podrían indicar líneas menos activas o desplazadas por nuevas agendas.",
                    "suggested_use": "Revisar si se trata de agotamiento, cambio terminológico o desplazamiento conceptual.",
                    "caution": "La caída de frecuencia puede deberse a cambios de palabras clave, no a desaparición del tema.",
                    "strength": "Baja",
                }
            )

    if temporal_df is None or temporal_df.empty:
        temporal_df = temporal_summary(df)

    if not temporal_df.empty and "publications" in temporal_df.columns:
        temporal_work = temporal_df.copy()
        temporal_work["publications"] = pd.to_numeric(temporal_work["publications"], errors="coerce").fillna(0).astype(int)

        peak = temporal_work.sort_values("publications", ascending=False).head(1)

        if not peak.empty:
            peak_year = int(peak.iloc[0]["publication_year"])
            peak_count = int(peak.iloc[0]["publications"])

            rows.append(
                {
                    "trend_type": "Temporal",
                    "trend": "Año de mayor concentración de publicaciones",
                    "evidence": f"El año {peak_year} concentra {peak_count} publicaciones en la muestra.",
                    "period_signal": "Serie anual de publicaciones.",
                    "associated_terms": "",
                    "interpretation": "El pico puede indicar un momento de intensificación del debate o de indexación.",
                    "suggested_use": "Revisar los documentos de ese año para identificar detonantes, tecnologías, debates o eventos.",
                    "caution": "Un pico anual no prueba causalidad; requiere interpretación contextual.",
                    "strength": "Media",
                }
            )

    if country_df is not None and not country_df.empty and "publications" in country_df.columns:
        cdf = country_df.copy()
        cdf["publications"] = pd.to_numeric(cdf["publications"], errors="coerce").fillna(0).astype(int)
        top_countries = cdf.sort_values("publications", ascending=False).head(5)

        if not top_countries.empty:
            evidence = "; ".join(
                [
                    f"{row.country} ({int(row.publications)})"
                    for row in top_countries.itertuples()
                    if hasattr(row, "country")
                ]
            )

            rows.append(
                {
                    "trend_type": "Geográfica",
                    "trend": "Polos geográficos visibles en la muestra",
                    "evidence": evidence,
                    "period_signal": "Agrupación por país.",
                    "associated_terms": "",
                    "interpretation": "Estos países aparecen como polos de producción o afiliación dentro del corpus recuperado.",
                    "suggested_use": "Comparar estos polos con regiones poco visibles para construir preguntas situadas.",
                    "caution": "El conteo es expandido por afiliaciones y depende de metadatos disponibles.",
                    "strength": "Media",
                }
            )

    if not rows:
        rows.append(
            {
                "trend_type": "General",
                "trend": "No se detectaron tendencias automáticas fuertes",
                "evidence": "La muestra no activó reglas suficientes de tendencia.",
                "period_signal": "",
                "associated_terms": "",
                "interpretation": "Se requiere ampliar el corpus o enriquecer metadatos.",
                "suggested_use": "Probar nuevos términos, mayor número de resultados y bases complementarias.",
                "caution": "La ausencia de tendencia automática no implica ausencia de tendencia científica.",
                "strength": "Media",
            }
        )

    return pd.DataFrame(rows)


def detect_understudied_areas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta áreas poco visibles comparando el corpus contra dimensiones esperadas.

    No afirma ausencia absoluta. Declara baja visibilidad en la muestra.
    """
    rows: List[Dict[str, object]] = []

    if df.empty:
        return pd.DataFrame(
            columns=[
                "expected_dimension",
                "visibility_level",
                "matched_terms",
                "evidence",
                "possible_gap",
                "suggested_question",
                "how_to_verify",
                "caution",
            ]
        )

    text = corpus_text(df)

    for dimension, data in EXPECTED_DIMENSIONS.items():
        terms: List[str] = list(data["terms"])
        matches = []

        for term in terms:
            normalized = normalize_text(term)
            count = text.count(normalized)

            if count > 0:
                matches.append(f"{term} ({count})")

        total_hits = sum(int(match.rsplit("(", 1)[-1].replace(")", "")) for match in matches) if matches else 0

        if total_hits == 0:
            visibility = "No detectada"
        elif total_hits <= 2:
            visibility = "Baja"
        elif total_hits <= 5:
            visibility = "Moderada"
        else:
            visibility = "Visible"

        if visibility in ["No detectada", "Baja", "Moderada"]:
            rows.append(
                {
                    "expected_dimension": dimension,
                    "visibility_level": visibility,
                    "matched_terms": "; ".join(matches) if matches else "Sin coincidencias automáticas",
                    "evidence": f"Coincidencias automáticas totales en títulos/abstracts: {total_hits}.",
                    "possible_gap": f"Posible baja visibilidad de {data['possible_gap']}.",
                    "suggested_question": data["question"],
                    "how_to_verify": "Ejecutar búsquedas dirigidas en español e inglés, revisar títulos/abstracts manualmente y contrastar con Scopus, Web of Science, Dimensions, Lens o Google Scholar.",
                    "caution": "Baja visibilidad en esta muestra no equivale a inexistencia del tema.",
                }
            )

    if not rows:
        rows.append(
            {
                "expected_dimension": "General",
                "visibility_level": "Visible",
                "matched_terms": "Varias dimensiones esperadas aparecen en el corpus.",
                "evidence": "No se activaron reglas fuertes de baja visibilidad.",
                "possible_gap": "No se detecta brecha temática automática fuerte con las dimensiones esperadas.",
                "suggested_question": "Profundizar con análisis de coocurrencia, redes temáticas y lectura cualitativa.",
                "how_to_verify": "Ampliar corpus y aplicar análisis más fino por clúster temático.",
                "caution": "El resultado depende de la lista de dimensiones esperadas y de los términos configurados.",
            }
        )

    return pd.DataFrame(rows)


def build_research_opportunities(
    gap_df: pd.DataFrame,
    trend_df: pd.DataFrame,
    understudied_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construye oportunidades investigativas a partir de brechas, tendencias y áreas poco visibles.
    """
    rows: List[Dict[str, object]] = []

    if understudied_df is not None and not understudied_df.empty:
        priority_map = {
            "No detectada": "Alta",
            "Baja": "Alta",
            "Moderada": "Media",
            "Visible": "Baja",
        }

        for row in understudied_df.itertuples(index=False):
            dimension = getattr(row, "expected_dimension", "")
            visibility = getattr(row, "visibility_level", "")
            possible_gap = getattr(row, "possible_gap", "")
            question = getattr(row, "suggested_question", "")
            verify = getattr(row, "how_to_verify", "")

            if visibility in ["No detectada", "Baja", "Moderada"]:
                rows.append(
                    {
                        "opportunity_type": "Área poco visible",
                        "opportunity": possible_gap,
                        "possible_research_question": question,
                        "supporting_signal": f"{dimension}: visibilidad {visibility}.",
                        "recommended_next_step": verify,
                        "priority": priority_map.get(visibility, "Media"),
                    }
                )

    if gap_df is not None and not gap_df.empty:
        high_gaps = gap_df[gap_df["priority"].astype(str).str.lower() == "alta"] if "priority" in gap_df.columns else pd.DataFrame()

        for row in high_gaps.head(5).itertuples(index=False):
            dimension = getattr(row, "dimension", "")
            signal = getattr(row, "signal", "")
            suggested_gap = getattr(row, "suggested_gap", "")
            evidence = getattr(row, "evidence", "")

            rows.append(
                {
                    "opportunity_type": "Brecha prioritaria",
                    "opportunity": suggested_gap,
                    "possible_research_question": f"¿Cómo puede investigarse {signal.lower()} en relación con el tema consultado?",
                    "supporting_signal": f"{dimension}: {evidence}",
                    "recommended_next_step": "Revisar manualmente los artículos relacionados, ampliar términos de búsqueda y validar contra otras bases.",
                    "priority": "Alta",
                }
            )

    if trend_df is not None and not trend_df.empty:
        emerging = trend_df[trend_df["trend_type"].astype(str) == "Emergente"] if "trend_type" in trend_df.columns else pd.DataFrame()

        for row in emerging.head(3).itertuples(index=False):
            trend = getattr(row, "trend", "")
            evidence = getattr(row, "evidence", "")
            associated_terms = getattr(row, "associated_terms", "")

            rows.append(
                {
                    "opportunity_type": "Tendencia emergente",
                    "opportunity": f"Profundizar en la tendencia: {trend}.",
                    "possible_research_question": f"¿Qué implicaciones tienen los términos emergentes ({associated_terms}) para el desarrollo del campo?",
                    "supporting_signal": evidence,
                    "recommended_next_step": "Leer los documentos recientes asociados y construir una matriz de temas, métodos y contextos.",
                    "priority": "Media",
                }
            )

    if not rows:
        rows.append(
            {
                "opportunity_type": "General",
                "opportunity": "No se generaron oportunidades automáticas fuertes.",
                "possible_research_question": "¿Qué preguntas emergen al ampliar el corpus y contrastar con otras bases?",
                "supporting_signal": "La muestra requiere mayor refinamiento.",
                "recommended_next_step": "Ampliar búsqueda, ajustar palabras clave y realizar revisión cualitativa.",
                "priority": "Media",
            }
        )

    opportunities = pd.DataFrame(rows)

    if not opportunities.empty:
        priority_rank = {"Alta": 0, "Media": 1, "Baja": 2}
        opportunities["_priority_rank"] = opportunities["priority"].map(priority_rank).fillna(9)
        opportunities = opportunities.sort_values("_priority_rank").drop(columns=["_priority_rank"])

    return opportunities


def generate_extended_insights(
    df: pd.DataFrame,
    gap_df: Optional[pd.DataFrame] = None,
    keyword_df: Optional[pd.DataFrame] = None,
    temporal_df: Optional[pd.DataFrame] = None,
    country_df: Optional[pd.DataFrame] = None,
    continent_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Genera:
        trend_summary
        understudied_areas
        research_opportunities
    """
    if gap_df is None or gap_df.empty or keyword_df is None or keyword_df.empty or temporal_df is None or temporal_df.empty:
        gap_df, keyword_df, temporal_df = suggest_preliminary_gaps(
            df,
            country_df=country_df,
            continent_df=continent_df,
        )

    trend_df = detect_study_trends(
        df,
        keyword_df=keyword_df,
        temporal_df=temporal_df,
        country_df=country_df,
    )

    understudied_df = detect_understudied_areas(df)

    opportunities_df = build_research_opportunities(
        gap_df=gap_df,
        trend_df=trend_df,
        understudied_df=understudied_df,
    )

    return trend_df, understudied_df, opportunities_df


def save_extended_outputs(
    trend_df: pd.DataFrame,
    understudied_df: pd.DataFrame,
    opportunities_df: pd.DataFrame,
    output_dir: Path | str = PROCESSED_DIR,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    trend_df.to_csv(output_path / "trend_summary.csv", index=False, encoding="utf-8-sig")
    understudied_df.to_csv(output_path / "understudied_areas.csv", index=False, encoding="utf-8-sig")
    opportunities_df.to_csv(output_path / "research_opportunities.csv", index=False, encoding="utf-8-sig")


def load_inputs() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not OPENALEX_RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró {OPENALEX_RESULTS_PATH}. Primero ejecuta una búsqueda en BiblioMap."
        )

    df = pd.read_csv(OPENALEX_RESULTS_PATH)

    country_df = pd.DataFrame()
    continent_df = pd.DataFrame()

    if GROUP_BY_COUNTRY_PATH.exists():
        country_df = pd.read_csv(GROUP_BY_COUNTRY_PATH)

    if GROUP_BY_CONTINENT_PATH.exists():
        continent_df = pd.read_csv(GROUP_BY_CONTINENT_PATH)

    return df, country_df, continent_df


if __name__ == "__main__":
    print("Generando sugerencias preliminares, tendencias y oportunidades...")

    try:
        openalex_df, countries_df, continents_df = load_inputs()

        gaps, keywords, temporal = suggest_preliminary_gaps(
            openalex_df,
            country_df=countries_df,
            continent_df=continents_df,
        )

        save_gap_outputs(gaps, keywords, temporal)

        trends, understudied, opportunities = generate_extended_insights(
            openalex_df,
            gap_df=gaps,
            keyword_df=keywords,
            temporal_df=temporal,
            country_df=countries_df,
            continent_df=continents_df,
        )

        save_extended_outputs(trends, understudied, opportunities)

        print("\nBrechas preliminares:")
        print(gaps[["dimension", "signal", "priority"]].head(20))

        print("\nTendencias:")
        print(trends[["trend_type", "trend", "strength"]].head(20))

        print("\nÁreas poco visibles:")
        print(understudied[["expected_dimension", "visibility_level"]].head(20))

        print("\nOportunidades investigativas:")
        print(opportunities[["opportunity_type", "priority"]].head(20))

        print("\nArchivos guardados:")
        print(GAP_SUGGESTIONS_PATH)
        print(KEYWORD_SUMMARY_PATH)
        print(TEMPORAL_SUMMARY_PATH)
        print(TREND_SUMMARY_PATH)
        print(UNDERSTUDIED_AREAS_PATH)
        print(RESEARCH_OPPORTUNITIES_PATH)

    except Exception as error:
        print("\nOcurrió un error:")
        print(error)
