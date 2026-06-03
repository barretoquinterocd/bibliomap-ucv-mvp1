"""
generate_map.py

Módulo de visualización geográfica para BiblioMap.

Corrección aplicada:
- Convierte ISO alfa-2 a ISO alfa-3.
- Usa go.Choropleth con locationmode="ISO-3" explícito.
- Usa escala de color más visible.
"""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


ISO2_TO_ISO3: Dict[str, str] = {
    "AD": "AND", "AE": "ARE", "AF": "AFG", "AG": "ATG", "AI": "AIA",
    "AL": "ALB", "AM": "ARM", "AO": "AGO", "AR": "ARG", "AT": "AUT",
    "AU": "AUS", "AZ": "AZE", "BA": "BIH", "BB": "BRB", "BD": "BGD",
    "BE": "BEL", "BF": "BFA", "BG": "BGR", "BH": "BHR", "BI": "BDI",
    "BJ": "BEN", "BM": "BMU", "BN": "BRN", "BO": "BOL", "BR": "BRA",
    "BS": "BHS", "BT": "BTN", "BW": "BWA", "BY": "BLR", "BZ": "BLZ",
    "CA": "CAN", "CD": "COD", "CF": "CAF", "CG": "COG", "CH": "CHE",
    "CI": "CIV", "CL": "CHL", "CM": "CMR", "CN": "CHN", "CO": "COL",
    "CR": "CRI", "CU": "CUB", "CV": "CPV", "CY": "CYP", "CZ": "CZE",
    "DE": "DEU", "DJ": "DJI", "DK": "DNK", "DM": "DMA", "DO": "DOM",
    "DZ": "DZA", "EC": "ECU", "EE": "EST", "EG": "EGY", "ER": "ERI",
    "ES": "ESP", "ET": "ETH", "FI": "FIN", "FJ": "FJI", "FR": "FRA",
    "GA": "GAB", "GB": "GBR", "GD": "GRD", "GE": "GEO", "GH": "GHA",
    "GM": "GMB", "GN": "GIN", "GQ": "GNQ", "GR": "GRC", "GT": "GTM",
    "GW": "GNB", "GY": "GUY", "HK": "HKG", "HN": "HND", "HR": "HRV",
    "HT": "HTI", "HU": "HUN", "ID": "IDN", "IE": "IRL", "IL": "ISR",
    "IN": "IND", "IQ": "IRQ", "IR": "IRN", "IS": "ISL", "IT": "ITA",
    "JM": "JAM", "JO": "JOR", "JP": "JPN", "KE": "KEN", "KG": "KGZ",
    "KH": "KHM", "KR": "KOR", "KW": "KWT", "KZ": "KAZ", "LA": "LAO",
    "LB": "LBN", "LK": "LKA", "LR": "LBR", "LS": "LSO", "LT": "LTU",
    "LU": "LUX", "LV": "LVA", "LY": "LBY", "MA": "MAR", "MD": "MDA",
    "ME": "MNE", "MG": "MDG", "MK": "MKD", "ML": "MLI", "MM": "MMR",
    "MN": "MNG", "MO": "MAC", "MR": "MRT", "MT": "MLT", "MU": "MUS",
    "MV": "MDV", "MW": "MWI", "MX": "MEX", "MY": "MYS", "MZ": "MOZ",
    "NA": "NAM", "NE": "NER", "NG": "NGA", "NI": "NIC", "NL": "NLD",
    "NO": "NOR", "NP": "NPL", "NZ": "NZL", "OM": "OMN", "PA": "PAN",
    "PE": "PER", "PG": "PNG", "PH": "PHL", "PK": "PAK", "PL": "POL",
    "PR": "PRI", "PT": "PRT", "PY": "PRY", "QA": "QAT", "RO": "ROU",
    "RS": "SRB", "RU": "RUS", "RW": "RWA", "SA": "SAU", "SD": "SDN",
    "SE": "SWE", "SG": "SGP", "SI": "SVN", "SK": "SVK", "SL": "SLE",
    "SN": "SEN", "SO": "SOM", "SR": "SUR", "SV": "SLV", "SY": "SYR",
    "SZ": "SWZ", "TD": "TCD", "TG": "TGO", "TH": "THA", "TJ": "TJK",
    "TN": "TUN", "TR": "TUR", "TT": "TTO", "TW": "TWN", "TZ": "TZA",
    "UA": "UKR", "UG": "UGA", "US": "USA", "UY": "URY", "UZ": "UZB",
    "VE": "VEN", "VN": "VNM", "YE": "YEM", "ZA": "ZAF", "ZM": "ZMB",
    "ZW": "ZWE",
}


def prepare_country_map_data(country_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara datos para el mapa mundial.
    """
    if country_df is None or country_df.empty:
        return pd.DataFrame()

    df = country_df.copy()

    if "country_code" not in df.columns:
        raise ValueError("El DataFrame debe incluir la columna 'country_code'.")

    df["country_code"] = df["country_code"].astype(str).str.upper().str.strip()

    df = df[df["country_code"].notna()]
    df = df[df["country_code"] != ""]
    df = df[df["country_code"] != "UNKNOWN"]
    df = df[df["country_code"] != "NAN"]

    df["iso_alpha3"] = df["country_code"].map(ISO2_TO_ISO3)
    df = df[df["iso_alpha3"].notna()]
    df = df[df["iso_alpha3"] != ""]

    if "publications" not in df.columns:
        df["publications"] = 0

    if "cited_by_count" not in df.columns:
        df["cited_by_count"] = 0

    df["publications"] = pd.to_numeric(df["publications"], errors="coerce").fillna(0).astype(int)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0).astype(int)

    if "country" not in df.columns:
        df["country"] = df["country_code"]

    if "continent" not in df.columns:
        df["continent"] = "Unknown"

    return df


def _metric_label(metric: str) -> str:
    """
    Devuelve etiqueta legible de la métrica.
    """
    if metric == "publications":
        return "Publicaciones"

    if metric == "cited_by_count":
        return "Citas acumuladas"

    return metric


def create_world_map(
    country_df: pd.DataFrame,
    metric: str = "publications",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Crea mapa mundial bibliométrico tipo choropleth usando go.Choropleth.
    """
    df = prepare_country_map_data(country_df)

    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos geográficos disponibles para mostrar.",
            height=650,
            margin=dict(l=0, r=0, t=60, b=0),
        )
        return fig

    if metric not in df.columns:
        raise ValueError(f"La métrica '{metric}' no existe en el DataFrame.")

    if title is None:
        title = f"Mapa mundial por {_metric_label(metric).lower()}"

    zmax = max(float(df[metric].max()), 1.0)

    customdata = df[
        ["country", "country_code", "continent", "publications", "cited_by_count"]
    ].to_numpy()

    fig = go.Figure(
        data=go.Choropleth(
            locations=df["iso_alpha3"],
            z=df[metric],
            locationmode="ISO-3",
            text=df["country"],
            customdata=customdata,
            colorscale=[
                [0.00, "#EAF3FF"],
                [0.20, "#BBD7F2"],
                [0.40, "#7FB3D5"],
                [0.60, "#2E86C1"],
                [0.80, "#0B5394"],
                [1.00, "#08306B"],
            ],
            zmin=0,
            zmax=zmax,
            marker_line_color="white",
            marker_line_width=0.6,
            colorbar=dict(
                title=_metric_label(metric),
                thickness=16,
                len=0.75,
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Código: %{customdata[1]} / %{location}<br>"
                "Región: %{customdata[2]}<br>"
                "Publicaciones: %{customdata[3]}<br>"
                "Citas acumuladas: %{customdata[4]}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_geos(
        projection_type="natural earth",
        showframe=True,
        framecolor="LightGray",
        showcoastlines=True,
        coastlinecolor="LightGray",
        showland=True,
        landcolor="#F7F7F7",
        showocean=True,
        oceancolor="white",
        showcountries=True,
        countrycolor="LightGray",
    )

    fig.update_layout(
        title=title,
        height=650,
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def create_top_countries_bar(
    country_df: pd.DataFrame,
    metric: str = "publications",
    top_n: int = 15,
) -> go.Figure:
    """
    Crea gráfico de barras horizontal con los países principales.
    """
    df = prepare_country_map_data(country_df)

    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles.",
            height=450,
        )
        return fig

    if metric not in df.columns:
        raise ValueError(f"La métrica '{metric}' no existe en el DataFrame.")

    df = df.sort_values(metric, ascending=False).head(top_n)

    hover_data = {}

    for column in ["country_code", "iso_alpha3", "continent", "publications", "cited_by_count"]:
        if column in df.columns:
            hover_data[column] = True

    fig = px.bar(
        df,
        x=metric,
        y="country",
        orientation="h",
        title=f"Top {top_n} países por {_metric_label(metric).lower()}",
        hover_data=hover_data,
    )

    fig.update_layout(
        height=520,
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def create_map(
    country_df: pd.DataFrame,
    metric: str = "publications",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Alias de compatibilidad.
    """
    return create_world_map(
        country_df=country_df,
        metric=metric,
        title=title,
    )


if __name__ == "__main__":
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "data" / "processed" / "group_by_country.csv"

    if not input_path.exists():
        print(f"No se encontró el archivo: {input_path}")
    else:
        df_input = pd.read_csv(input_path)
        df_map = prepare_country_map_data(df_input)

        print("Países preparados para mapa:")
        print(df_map[["country_code", "iso_alpha3", "country", "publications", "cited_by_count"]].head(20))
        print(f"Total países mapeables: {len(df_map)}")

        fig = create_world_map(df_input, metric="publications")

        output_path = base_dir / "data" / "processed" / "world_map_preview.html"
        fig.write_html(output_path)

        print(f"Mapa generado en: {output_path}")
