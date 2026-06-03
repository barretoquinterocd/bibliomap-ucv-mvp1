"""
group_by_country.py

Módulo de agrupación geográfica para BiblioMap.

Toma un DataFrame de resultados normalizados desde OpenAlex y genera:
- Tabla por país.
- Tabla por continente.
- Tabla país-continente.
- Conteo de publicaciones.
- Citas acumuladas.
- Instituciones detectadas.
- Autores detectados.

Este módulo prepara la base para:
- Detalle geográfico.
- Mapa mundial.
- Brechas geográficas preliminares.
"""

from __future__ import annotations

from typing import Dict, List, Set

import pandas as pd


# Mapa básico de códigos ISO alfa-2 a nombres de país.
# Puede ampliarse progresivamente según aparezcan nuevos códigos.
COUNTRY_NAMES: Dict[str, str] = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AR": "Argentina",
    "AT": "Austria",
    "AU": "Australia",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "BR": "Brazil",
    "CA": "Canada",
    "CH": "Switzerland",
    "CL": "Chile",
    "CN": "China",
    "CO": "Colombia",
    "CU": "Cuba",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "GR": "Greece",
    "HK": "Hong Kong",
    "HR": "Croatia",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IN": "India",
    "IR": "Iran",
    "IT": "Italy",
    "JP": "Japan",
    "KR": "South Korea",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MX": "Mexico",
    "MY": "Malaysia",
    "NG": "Nigeria",
    "NL": "Netherlands",
    "NO": "Norway",
    "NZ": "New Zealand",
    "PE": "Peru",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "SE": "Sweden",
    "SG": "Singapore",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "TH": "Thailand",
    "TR": "Türkiye",
    "TW": "Taiwan",
    "UA": "Ukraine",
    "US": "United States",
    "UY": "Uruguay",
    "VE": "Venezuela",
    "VN": "Vietnam",
    "ZA": "South Africa",
}


COUNTRY_CONTINENTS: Dict[str, str] = {
    # North America
    "CA": "North America",
    "MX": "North America",
    "US": "North America",

    # Latin America and Caribbean
    "AR": "Latin America and Caribbean",
    "BR": "Latin America and Caribbean",
    "CL": "Latin America and Caribbean",
    "CO": "Latin America and Caribbean",
    "CU": "Latin America and Caribbean",
    "EC": "Latin America and Caribbean",
    "PE": "Latin America and Caribbean",
    "UY": "Latin America and Caribbean",
    "VE": "Latin America and Caribbean",

    # Europe
    "AD": "Europe",
    "AT": "Europe",
    "BE": "Europe",
    "BG": "Europe",
    "CH": "Europe",
    "CZ": "Europe",
    "DE": "Europe",
    "DK": "Europe",
    "EE": "Europe",
    "ES": "Europe",
    "FI": "Europe",
    "FR": "Europe",
    "GB": "Europe",
    "GR": "Europe",
    "HR": "Europe",
    "HU": "Europe",
    "IE": "Europe",
    "IT": "Europe",
    "LT": "Europe",
    "LU": "Europe",
    "NL": "Europe",
    "NO": "Europe",
    "PL": "Europe",
    "PT": "Europe",
    "RO": "Europe",
    "RU": "Europe",
    "SE": "Europe",
    "SI": "Europe",
    "SK": "Europe",
    "UA": "Europe",

    # Asia
    "AE": "Asia",
    "CN": "Asia",
    "HK": "Asia",
    "ID": "Asia",
    "IL": "Asia",
    "IN": "Asia",
    "IR": "Asia",
    "JP": "Asia",
    "KR": "Asia",
    "MY": "Asia",
    "SA": "Asia",
    "SG": "Asia",
    "TH": "Asia",
    "TR": "Asia",
    "TW": "Asia",
    "VN": "Asia",

    # Africa
    "EG": "Africa",
    "NG": "Africa",
    "ZA": "Africa",

    # Oceania
    "AU": "Oceania",
    "NZ": "Oceania",
}


def split_semicolon_values(value: object) -> List[str]:
    """
    Divide valores separados por punto y coma.

    Ejemplo:
        "US; GB; ES" -> ["US", "GB", "ES"]
    """
    if value is None:
        return []

    text = str(value).strip()

    if not text or text.lower() == "nan":
        return []

    return [item.strip() for item in text.split(";") if item.strip()]


def country_name(country_code: str) -> str:
    """
    Devuelve el nombre del país a partir del código ISO alfa-2.
    Si no se encuentra, devuelve el código.
    """
    code = str(country_code).strip().upper()
    return COUNTRY_NAMES.get(code, code)


def continent_name(country_code: str) -> str:
    """
    Devuelve continente o región amplia según código ISO alfa-2.
    """
    code = str(country_code).strip().upper()
    return COUNTRY_CONTINENTS.get(code, "Unknown")


def expand_country_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande los registros para que cada fila represente una publicación-país.

    Si una publicación tiene countries = "US; GB", se generan dos filas:
    una para US y otra para GB.
    """
    rows: List[dict] = []

    for _, row in df.iterrows():
        countries = split_semicolon_values(row.get("countries", ""))

        if not countries:
            countries = ["Unknown"]

        for code in countries:
            normalized_code = code.strip().upper()
            rows.append(
                {
                    "country_code": normalized_code,
                    "country": country_name(normalized_code),
                    "continent": continent_name(normalized_code),
                    "title": row.get("title", ""),
                    "publication_year": row.get("publication_year", ""),
                    "authors": row.get("authors", ""),
                    "institutions": row.get("institutions", ""),
                    "source": row.get("source", ""),
                    "doi": row.get("doi", ""),
                    "landing_page_url": row.get("landing_page_url", ""),
                    "cited_by_count": row.get("cited_by_count", 0),
                }
            )

    return pd.DataFrame(rows)


def unique_join(values: pd.Series) -> str:
    """
    Une valores únicos separados por punto y coma.
    """
    unique_values: Set[str] = set()

    for value in values.dropna():
        for item in split_semicolon_values(value):
            if item:
                unique_values.add(item)

    return "; ".join(sorted(unique_values))


def group_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa resultados por país.

    Retorna:
        country_code
        country
        continent
        publications
        cited_by_count
        institutions
        authors
    """
    expanded = expand_country_rows(df)

    if expanded.empty:
        return pd.DataFrame(
            columns=[
                "country_code",
                "country",
                "continent",
                "publications",
                "cited_by_count",
                "institutions",
                "authors",
            ]
        )

    grouped = (
        expanded.groupby(["country_code", "country", "continent"], as_index=False)
        .agg(
            publications=("title", "count"),
            cited_by_count=("cited_by_count", "sum"),
            institutions=("institutions", unique_join),
            authors=("authors", unique_join),
        )
        .sort_values(["publications", "cited_by_count"], ascending=[False, False])
    )

    return grouped


def group_by_continent(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa resultados por continente o región amplia.
    """
    expanded = expand_country_rows(df)

    if expanded.empty:
        return pd.DataFrame(columns=["continent", "publications", "cited_by_count", "countries"])

    grouped = (
        expanded.groupby("continent", as_index=False)
        .agg(
            publications=("title", "count"),
            cited_by_count=("cited_by_count", "sum"),
            countries=("country", lambda values: "; ".join(sorted(set(values.dropna())))),
        )
        .sort_values(["publications", "cited_by_count"], ascending=[False, False])
    )

    return grouped


def save_geographic_outputs(
    country_df: pd.DataFrame,
    continent_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """
    Guarda salidas geográficas como CSV.
    """
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    country_df.to_csv(output_path / "group_by_country.csv", index=False, encoding="utf-8-sig")
    continent_df.to_csv(output_path / "group_by_continent.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "data" / "processed" / "openalex_search_results.csv"
    fallback_path = base_dir / "data" / "processed" / "openalex_test_results.csv"
    output_dir = base_dir / "data" / "processed"

    if input_path.exists():
        source_path = input_path
    else:
        source_path = fallback_path

    print(f"Leyendo archivo: {source_path}")

    df_input = pd.read_csv(source_path)
    countries = group_by_country(df_input)
    continents = group_by_continent(df_input)

    print("\nAgrupación por país:")
    print(countries.head(10))

    print("\nAgrupación por continente:")
    print(continents.head(10))

    save_geographic_outputs(countries, continents, str(output_dir))

    print("\nArchivos guardados:")
    print(output_dir / "group_by_country.csv")
    print(output_dir / "group_by_continent.csv")
