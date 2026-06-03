"""
search_openalex.py

Módulo de búsqueda inicial para BiblioMap UCV.

Consulta publicaciones académicas en OpenAlex usando el endpoint /works,
normaliza campos básicos y devuelve un DataFrame listo para futuras fases:
limpieza, agrupación geográfica, tablas, mapas y brechas preliminares.

Prueba desde terminal:
    py modules\\search_openalex.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests


OPENALEX_WORKS_URL = "https://api.openalex.org/works"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def reconstruct_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> str:
    """
    Reconstruye el abstract cuando OpenAlex lo entrega como inverted index.

    OpenAlex suele representar el resumen así:
        {"word": [position1, position2, ...]}

    Esta función reconstruye el texto en orden de posiciones.
    """
    if not inverted_index:
        return ""

    position_to_word: Dict[int, str] = {}

    for word, positions in inverted_index.items():
        for position in positions:
            position_to_word[position] = word

    words = [position_to_word[index] for index in sorted(position_to_word)]
    return " ".join(words)


def safe_get(source: Dict[str, Any], key: str, default: Any = "") -> Any:
    """
    Obtiene un valor de un diccionario sin romper el flujo si falta la clave.
    """
    value = source.get(key, default)
    return default if value is None else value


def extract_authors(work: Dict[str, Any]) -> str:
    """
    Extrae autores desde authorships.
    """
    authorships = work.get("authorships", []) or []
    authors: List[str] = []

    for authorship in authorships:
        author = authorship.get("author", {}) or {}
        name = author.get("display_name")
        if name:
            authors.append(name)

    return "; ".join(dict.fromkeys(authors))


def extract_institutions(work: Dict[str, Any]) -> str:
    """
    Extrae instituciones asociadas a las autorías.
    """
    authorships = work.get("authorships", []) or []
    institutions: List[str] = []

    for authorship in authorships:
        for institution in authorship.get("institutions", []) or []:
            name = institution.get("display_name")
            if name:
                institutions.append(name)

    return "; ".join(dict.fromkeys(institutions))


def extract_countries(work: Dict[str, Any]) -> str:
    """
    Extrae códigos de país desde instituciones asociadas a las autorías.

    En esta fase MVP se devuelven códigos ISO cuando estén disponibles,
    por ejemplo: US, GB, ES, BR, VE.
    """
    authorships = work.get("authorships", []) or []
    countries: List[str] = []

    for authorship in authorships:
        for institution in authorship.get("institutions", []) or []:
            country_code = institution.get("country_code")
            if country_code:
                countries.append(country_code)

    return "; ".join(dict.fromkeys(countries))


def extract_source(work: Dict[str, Any]) -> str:
    """
    Extrae la fuente, revista o venue principal, si está disponible.
    """
    primary_location = work.get("primary_location", {}) or {}
    source = primary_location.get("source", {}) or {}
    return source.get("display_name", "") or ""


def extract_landing_page_url(work: Dict[str, Any]) -> str:
    """
    Extrae URL de la publicación, si está disponible.
    """
    primary_location = work.get("primary_location", {}) or {}
    return primary_location.get("landing_page_url", "") or ""


def extract_open_access_status(work: Dict[str, Any]) -> bool:
    """
    Extrae si el documento aparece como open access.
    """
    open_access = work.get("open_access", {}) or {}
    return bool(open_access.get("is_oa", False))


def normalize_work(work: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte un registro bruto de OpenAlex en una fila tabular.
    """
    return {
        "openalex_id": safe_get(work, "id"),
        "doi": safe_get(work, "doi"),
        "title": safe_get(work, "display_name"),
        "publication_year": safe_get(work, "publication_year"),
        "publication_date": safe_get(work, "publication_date"),
        "type": safe_get(work, "type"),
        "cited_by_count": safe_get(work, "cited_by_count", 0),
        "authors": extract_authors(work),
        "institutions": extract_institutions(work),
        "countries": extract_countries(work),
        "source": extract_source(work),
        "landing_page_url": extract_landing_page_url(work),
        "is_open_access": extract_open_access_status(work),
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
    }


def build_filters(year_from: Optional[int], year_to: Optional[int]) -> Optional[str]:
    """
    Construye filtros temporales para OpenAlex.

    Ejemplo:
        from_publication_date:2015-01-01,to_publication_date:2026-12-31
    """
    filters: List[str] = []

    if year_from:
        filters.append(f"from_publication_date:{int(year_from)}-01-01")

    if year_to:
        filters.append(f"to_publication_date:{int(year_to)}-12-31")

    if not filters:
        return None

    return ",".join(filters)


def search_openalex(
    query: str,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    max_results: int = 100,
    mailto: Optional[str] = None,
    sort: str = "relevance_score:desc",
) -> pd.DataFrame:
    """
    Busca publicaciones en OpenAlex y devuelve un DataFrame normalizado.

    Parámetros:
        query:
            Tema o palabras clave de búsqueda.
        year_from:
            Año inicial opcional.
        year_to:
            Año final opcional.
        max_results:
            Número máximo de resultados a recuperar.
        mailto:
            Correo opcional para identificarse ante OpenAlex.
        sort:
            Ordenamiento de resultados. Por defecto: relevance_score:desc.

    Retorna:
        pandas.DataFrame con metadatos bibliométricos básicos.
    """
    if not query or not query.strip():
        raise ValueError("La consulta no puede estar vacía.")

    if max_results < 1:
        raise ValueError("max_results debe ser mayor que cero.")

    per_page = min(max_results, 200)

    params: Dict[str, Any] = {
        "search": query.strip(),
        "per-page": per_page,
        "page": 1,
        "sort": sort,
    }

    filters = build_filters(year_from, year_to)
    if filters:
        params["filter"] = filters

    if mailto:
        params["mailto"] = mailto

    records: List[Dict[str, Any]] = []

    while len(records) < max_results:
        response = requests.get(
            OPENALEX_WORKS_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        payload = response.json()
        results = payload.get("results", []) or []

        if not results:
            break

        for work in results:
            records.append(normalize_work(work))

            if len(records) >= max_results:
                break

        if len(results) < per_page:
            break

        params["page"] += 1

    return pd.DataFrame(records)


def save_results(df: pd.DataFrame, output_path: Path | str) -> None:
    """
    Guarda resultados en CSV UTF-8.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")


def run_test() -> None:
    """
    Prueba rápida del módulo desde terminal.
    """
    print("Probando conexión con OpenAlex...")

    query = "artificial intelligence scientific creativity knowledge production"

    df = search_openalex(
        query=query,
        year_from=2015,
        year_to=2026,
        max_results=25,
    )

    print("\nConsulta:")
    print(query)

    print("\nColumnas recuperadas:")
    print(list(df.columns))

    print("\nPrimeros resultados:")
    columns_to_show = [
        "title",
        "publication_year",
        "authors",
        "countries",
        "cited_by_count",
    ]

    available_columns = [column for column in columns_to_show if column in df.columns]

    if not df.empty:
        print(df[available_columns].head())
    else:
        print("No se recuperaron resultados.")

    print(f"\nRegistros recuperados: {len(df)}")

    output_path = PROCESSED_DIR / "openalex_test_results.csv"
    save_results(df, output_path)

    print(f"\nArchivo guardado en: {output_path}")


if __name__ == "__main__":
    try:
        run_test()
    except Exception as error:
        print("\nOcurrió un error durante la prueba:")
        print(error)