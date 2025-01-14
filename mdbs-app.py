import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# PyGWalker
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

# Streamlit Elements
from streamlit_elements import elements, dashboard, mui

import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA Y MODO OSCURO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Mi Aplicación - Elements",
    page_icon="✅",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Fondo de la app (modo oscuro) */
    .main {
        background-color: #1E1E1E !important;
    }

    /* Texto principal */
    .title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        font-size: 1.2rem;
        color: #CCCCCC;
        margin-bottom: 1rem;
    }

    /* Ajustes para texto de Streamlit / Elements en modo oscuro */
    .element-container, .stText, .stMarkdown, .stRadio, .stMultiSelect label {
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 1. CARGA DE DATOS (CACHÉ)
# -----------------------------------------------------------------------------
@st.cache_data
def load_dataframes():
    """Lee y devuelve los DataFrames usados en la aplicación."""
    # Ajusta rutas y nombres a tus archivos reales
    df_iadb = pd.read_parquet("IADB_DASH_BDD.parquet")
    df_location = pd.read_parquet("location_iadb.parquet")
    df_location[["Latitude", "Longitude"]] = df_location["point_pos"].str.split(",", expand=True)
    df_location["Latitude"] = df_location["Latitude"].astype(float)
    df_location["Longitude"] = df_location["Longitude"].astype(float)

    df_activity = pd.read_parquet("activity_iadb.parquet")
    df_outgoing = pd.read_parquet("outgoing_commitment_iadb.parquet")
    df_disbursements = pd.read_parquet("disbursements_data.parquet")

    datasets = {
        "IADB_DASH_BDD": df_iadb,
        "LOCATION_IADB": df_location,
        "ACTIVITY_IADB": df_activity,
        "OUTGOING_IADB": df_outgoing,
        "DISBURSEMENTS_DATA": df_disbursements
    }
    return datasets

DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2. PYGWALKER RENDERER (CACHE)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str) -> StreamlitRenderer:
    df = DATASETS[dataset_name]
    return StreamlitRenderer(df, kernel_computation=True)

# -----------------------------------------------------------------------------
# PÁGINA 1: MONITOREO MULTILATERALES (Elements)
# -----------------------------------------------------------------------------
def page_monitoreo_elements():
    st.markdown('<h1 class="title">Monitoreo Multilaterales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Página principal para el seguimiento de proyectos e información multinacional (Elements).</p>', unsafe_allow_html=True)
    
    # Ejemplo: un dashboard con un card de texto
    layout_monitoreo = [
        dashboard.Item("card_info", 0, 0, 6, 3),
    ]

    with elements("monitoreo"):
        with dashboard.Grid(layout_monitoreo, draggableHandle=".draggable", editable=False):
            with mui.Card(key="card_info", className="draggable", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Información General", subheader="Drag me!")
                with mui.CardContent():
                    st.write("Esta página muestra el monitoreo de multilaterales...")
                    st.write("Puedes extender con más gráficos y layouts.")

# -----------------------------------------------------------------------------
# PÁGINA 2: COOPERACIONES TÉCNICAS (Elements)
# -----------------------------------------------------------------------------
def page_cooperaciones_elements():
    st.markdown('<h1 class="title">Cooperaciones Técnicas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza y analiza las cooperaciones técnicas aprobadas (versión Elements).</p>', unsafe_allow_html=True)

    data = DATASETS["IADB_DASH_BDD"].copy()
    data["Approval Date"] = pd.to_datetime(data["Approval Date"], errors="coerce")
    data["Year"] = data["Approval Date"].dt.year

    layout_coop = [
        dashboard.Item("filters_coop", 0, 0, 4, 3),
        dashboard.Item("chart_coop", 4, 0, 8, 7),
    ]

    with elements("CooperacionesTec"):
        with dashboard.Grid(layout_coop, draggableHandle=".draggable", editable=False):
            # Card Filtros
            with mui.Card(key="filters_coop", className="draggable", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Filtros - Cooperaciones")
                with mui.CardContent():
                    st.write("Aquí irían tus filtros. (Ejemplo minimal)")
                    # Ejemplo: Slider de años
                    min_year, max_year = int(data["Year"].min()), int(data["Year"].max())
                    rango_anios = st.slider("Rango de años:", min_value=min_year, max_value=max_year, value=(min_year, max_year))
                    # Filtramos
                    data = data[(data["Year"] >= rango_anios[0]) & (data["Year"] <= rango_anios[1])]

            # Card Gráfico
            with mui.Card(key="chart_coop", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Gráfico de Cooperaciones Técnicas")
                with mui.CardContent():
                    if data.empty:
                        st.warning("No hay datos con los filtros seleccionados.")
                    else:
                        # Hacemos un gráfico de ejemplo
                        df_agg = data.groupby("Year")["Approval Amount"].sum().reset_index()
                        fig_line = px.line(df_agg, x="Year", y="Approval Amount", markers=True)
                        fig_line.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#FFFFFF"
                        )
                        st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 3: GEODATA (Elements)
# -----------------------------------------------------------------------------
def page_geodata_elements():
    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales (versión Elements).</p>', unsafe_allow_html=True)

    df_location = DATASETS["LOCATION_IADB"].copy()
    if "Sector" not in df_location.columns or "recipientcountry_codename" not in df_location.columns:
        st.error("Faltan columnas ('Sector', 'recipientcountry_codename') en LOCATION_IADB.")
        return

    layout_geo = [
        dashboard.Item("filtros_geo", 0, 0, 4, 3),
        dashboard.Item("mapa_geo", 4, 0, 8, 7),
        dashboard.Item("barras_geo", 0, 3, 12, 5),
    ]

    with elements("GeoDataPage"):
        with dashboard.Grid(layout_geo, draggableHandle=".draggable", editable=False):
            # Card Filtros
            with mui.Card(key="filtros_geo", className="draggable", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Filtros - GeoData")
                with mui.CardContent():
                    sectores_disponibles = df_location["Sector"].dropna().unique()
                    filtro_sector = st.selectbox("Selecciona un sector:", opciones=sectores_disponibles)
                    # Filtrar
                    df_filtered = df_location[df_location["Sector"] == filtro_sector]
                    st.session_state["df_geo_filtered"] = df_filtered  # Guardamos en session_state

            # Card Mapa
            with mui.Card(key="mapa_geo", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Mapa")
                with mui.CardContent():
                    df_filtered = st.session_state.get("df_geo_filtered", pd.DataFrame())
                    if df_filtered.empty:
                        st.warning("No hay datos para el sector seleccionado.")
                    else:
                        # Creamos un mapita con Folium
                        m = folium.Map(location=[df_filtered["Latitude"].mean(), df_filtered["Longitude"].mean()],
                                       zoom_start=4,
                                       tiles="CartoDB dark_matter")
                        marker_cluster = MarkerCluster().add_to(m)
                        for _, row in df_filtered.iterrows():
                            lat, lon = row["Latitude"], row["Longitude"]
                            folium.Marker(location=[lat, lon], popup=row["iatiidentifier"]).add_to(marker_cluster)

                        st_folium(m, width=700, height=500)

            # Card Barras
            with mui.Card(key="barras_geo", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Barras (País vs Cantidad)")
                with mui.CardContent():
                    df_filtered = st.session_state.get("df_geo_filtered", pd.DataFrame())
                    if df_filtered.empty:
                        st.warning("Sin datos para graficar.")
                    else:
                        conteo_por_pais = (
                            df_filtered
                            .groupby("recipientcountry_codename")["iatiidentifier"]
                            .nunique()
                            .reset_index(name="Cantidad Proyectos")
                        )
                        conteo_por_pais = conteo_por_pais.sort_values("Cantidad Proyectos", ascending=True)

                        fig_bar = px.bar(
                            conteo_por_pais,
                            x="Cantidad Proyectos",
                            y="recipientcountry_codename",
                            orientation="h"
                        )
                        fig_bar.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#FFFFFF"
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 4: ANÁLISIS EXPLORATORIO (PYGWALKER + Elements)
# -----------------------------------------------------------------------------
def page_analisis_exploratorio_elements():
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker integrado en un card de Elements.</p>', unsafe_allow_html=True)

    layout_analisis = [
        dashboard.Item("filtros_analisis", 0, 0, 4, 3),
        dashboard.Item("explorer_card", 4, 0, 8, 7),
    ]

    with elements("AnalisisExploratorio"):
        with dashboard.Grid(layout_analisis, draggableHandle=".draggable", editable=False):
            with mui.Card(key="filtros_analisis", className="draggable", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Selecciona la BDD")
                with mui.CardContent():
                    selected_dataset = st.selectbox("Base de datos:", list(DATASETS.keys()))
                    st.session_state["selected_dataset_for_pyg"] = selected_dataset

            with mui.Card(key="explorer_card", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="PyGWalker Explorer")
                with mui.CardContent():
                    ds_name = st.session_state.get("selected_dataset_for_pyg", list(DATASETS.keys())[0])
                    renderer = get_pyg_renderer_by_name(ds_name)
                    renderer.explorer()

# -----------------------------------------------------------------------------
# PÁGINA 5: FLUJOS AGREGADOS (Elements) - con Subpáginas
# -----------------------------------------------------------------------------
def page_flujos_agregados_elements():
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Aprobaciones y Desembolsos con Streamlit Elements.</p>', unsafe_allow_html=True)

    subpages = {
        "Aprobaciones": subpagina_aprobaciones_elements,
        "Desembolsos": subpagina_desembolsos_elements
    }
    choice = st.radio("Selecciona Subpágina:", list(subpages.keys()), horizontal=True)
    subpages[choice]()

# --- Subpágina A: Aprobaciones
def subpagina_aprobaciones_elements():
    st.markdown("### Aprobaciones - Elements")
    # Aquí colocarías tu layout con dashboard, etc.
    # Como ejemplo, haremos un layout minimal:
    layout_apro = [
        dashboard.Item("apro_filters", 0, 0, 4, 3),
        dashboard.Item("apro_chart_year", 4, 0, 8, 7),
        dashboard.Item("apro_chart_sector", 0, 3, 12, 5),
    ]

    df = DATASETS["OUTGOING_IADB"].copy()
    if df.empty:
        st.warning("No hay datos en OUTGOING_IADB.")
        return

    # EJEMPLO: Convertir la columna 'transactiondate_isodate' -> año
    if "transactiondate_isodate" in df.columns:
        df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"], errors="coerce")
        df["year"] = df["transactiondate_isodate"].dt.year
    # Montos a millones
    if "value_usd" in df.columns:
        df["value_usd_millones"] = df["value_usd"] / 1_000_000
    else:
        st.error("No existe la columna 'value_usd' en el dataset de Aprobaciones.")
        return

    with elements("AprobacionesElements"):
        with dashboard.Grid(layout_apro, draggableHandle=".draggable", editable=False):
            # Card Filtros
            with mui.Card(key="apro_filters", className="draggable", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Filtros - Aprobaciones")
                with mui.CardContent():
                    # Filtros de ejemplo
                    # 1) Filtro de año
                    if "year" in df.columns and df["year"].notna().sum() > 0:
                        anio_min, anio_max = int(df["year"].min()), int(df["year"].max())
                        rango_anios = st.slider("Rango de Años:", anio_min, anio_max, (anio_min, anio_max))
                        df = df[(df["year"] >= rango_anios[0]) & (df["year"] <= rango_anios[1])]
                    # 2) Rango de montos
                    if df["value_usd_millones"].notna().sum() > 0:
                        mm_min, mm_max = float(df["value_usd_millones"].min()), float(df["value_usd_millones"].max())
                        rango_mm = st.slider("Rango de montos (Millones):", mm_min, mm_max, (mm_min, mm_max))
                        df = df[(df["value_usd_millones"] >= rango_mm[0]) & (df["value_usd_millones"] <= rango_mm[1])]

                    st.session_state["df_apro_filtered"] = df

            # Card Barras por Año
            with mui.Card(key="apro_chart_year", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Aprobaciones por Año")
                with mui.CardContent():
                    df_filtered = st.session_state.get("df_apro_filtered", pd.DataFrame())
                    if df_filtered.empty:
                        st.warning("No hay datos disponibles para graficar (por año).")
                    else:
                        df_agg = df_filtered.groupby("year")["value_usd_millones"].sum().reset_index()
                        fig_bar = px.bar(
                            df_agg,
                            x="year",
                            y="value_usd_millones",
                            color_discrete_sequence=["#e5e5e5"],
                            labels={"year": "Año", "value_usd_millones": "Valor (Millones USD)"}
                        )
                        fig_bar.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#FFFFFF",
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False)
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

            # Card Barras por Sector
            with mui.Card(key="apro_chart_sector", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Aprobaciones por Sector")
                with mui.CardContent():
                    df_filtered = st.session_state.get("df_apro_filtered", pd.DataFrame())
                    if df_filtered.empty or "Sector" not in df_filtered.columns:
                        st.warning("No hay datos o no existe la columna 'Sector'.")
                    else:
                        df_sec = df_filtered.groupby("Sector")["value_usd_millones"].sum().reset_index()
                        df_sec = df_sec.sort_values("value_usd_millones", ascending=False)

                        fig_bar_sec = px.bar(
                            df_sec,
                            x="Sector",
                            y="value_usd_millones",
                            color_discrete_sequence=["#e5e5e5"],
                            labels={"Sector": "Sector", "value_usd_millones": "Valor (Millones USD)"}
                        )
                        fig_bar_sec.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#FFFFFF",
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False)
                        )
                        st.plotly_chart(fig_bar_sec, use_container_width=True)

# --- Subpágina B: Desembolsos
def subpagina_desembolsos_elements():
    st.markdown("### Desembolsos - Elements")
    layout_desem = [
        dashboard.Item("desem_filters", 0, 0, 4, 3),
        dashboard.Item("desem_chart_year", 4, 0, 8, 7),
        dashboard.Item("desem_chart_sector", 0, 3, 12, 5),
    ]

    df = DATASETS["DISBURSEMENTS_DATA"].copy()
    if df.empty:
        st.warning("No hay datos en DISBURSEMENTS_DATA.")
        return

    # Convertir la columna 'transactiondate_isodate' -> año
    if "transactiondate_isodate" in df.columns:
        df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"], errors="coerce")
        df["year"] = df["transactiondate_isodate"].dt.year
    if "value_usd" in df.columns:
        df["value_usd_millones"] = df["value_usd"] / 1_000_000
    else:
        st.error("No existe la columna 'value_usd' en el dataset de Desembolsos.")
        return

    with elements("DesembolsosElements"):
        with dashboard.Grid(layout_desem, draggableHandle=".draggable", editable=False):
            # Card Filtros
            with mui.Card(key="desem_filters", className="draggable", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Filtros - Desembolsos")
                with mui.CardContent():
                    # Ejemplo: Filtro de año
                    if "year" in df.columns and df["year"].notna().sum() > 0:
                        y_min, y_max = int(df["year"].min()), int(df["year"].max())
                        slider_year = st.slider("Rango de Años:", y_min, y_max, (y_min, y_max))
                        df = df[(df["year"] >= slider_year[0]) & (df["year"] <= slider_year[1])]
                    # Monto
                    if df["value_usd_millones"].notna().sum() > 0:
                        mm_min, mm_max = float(df["value_usd_millones"].min()), float(df["value_usd_millones"].max())
                        slider_mm = st.slider("Rango Montos (Millones):", mm_min, mm_max, (mm_min, mm_max))
                        df = df[(df["value_usd_millones"] >= slider_mm[0]) & (df["value_usd_millones"] <= slider_mm[1])]

                    st.session_state["df_desem_filtered"] = df

            # Card Barras (por Año)
            with mui.Card(key="desem_chart_year", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Desembolsos por Año")
                with mui.CardContent():
                    df_filtered = st.session_state.get("df_desem_filtered", pd.DataFrame())
                    if df_filtered.empty:
                        st.warning("No hay datos para Desembolsos (por Año).")
                    else:
                        df_agg = df_filtered.groupby("year")["value_usd_millones"].sum().reset_index()
                        fig_bar = px.bar(
                            df_agg,
                            x="year",
                            y="value_usd_millones",
                            color_discrete_sequence=["#e5e5e5"],
                            labels={"year": "Año", "value_usd_millones": "Millones USD"}
                        )
                        fig_bar.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#FFFFFF",
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False)
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

            # Card Barras (por Sector)
            with mui.Card(key="desem_chart_sector", sx={"height": "100%", "overflow": "auto"}):
                mui.CardHeader(title="Desembolsos por Sector")
                with mui.CardContent():
                    df_filtered = st.session_state.get("df_desem_filtered", pd.DataFrame())
                    if df_filtered.empty or "Sector" not in df_filtered.columns:
                        st.warning("No hay datos o no existe la columna 'Sector'.")
                    else:
                        df_sec = df_filtered.groupby("Sector")["value_usd_millones"].sum().reset_index()
                        df_sec = df_sec.sort_values("value_usd_millones", ascending=False)
                        fig_bar_sec = px.bar(
                            df_sec,
                            x="Sector",
                            y="value_usd_millones",
                            color_discrete_sequence=["#e5e5e5"],
                            labels={"Sector": "Sector", "value_usd_millones": "Millones USD"}
                        )
                        fig_bar_sec.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#FFFFFF",
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False)
                        )
                        st.plotly_chart(fig_bar_sec, use_container_width=True)

# -----------------------------------------------------------------------------
# DICCIONARIO DE PÁGINAS
# -----------------------------------------------------------------------------
PAGINAS = {
    "Monitoreo Multilaterales": page_monitoreo_elements,
    "Cooperaciones Técnicas": page_cooperaciones_elements,
    "GeoData": page_geodata_elements,
    "Análisis Exploratorio": page_analisis_exploratorio_elements,
    "Flujos Agregados": page_flujos_agregados_elements
}

# -----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    st.sidebar.title("Navegación")
    opciones = list(PAGINAS.keys())
    seleccion = st.sidebar.selectbox("Ir a:", opciones, index=0)
    PAGINAS[seleccion]()

# -----------------------------------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
