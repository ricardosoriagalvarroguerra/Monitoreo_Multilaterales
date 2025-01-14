import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y CSS PERSONALIZADO (MODO OSCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Mi Aplicación - Modo Oscuro",
    page_icon="✅",
    layout="wide"
)

# Estilos CSS para Modo Oscuro
st.markdown(
    """
    <style>
    /* Fondo de la app (modo oscuro) */
    .main {
        background-color: #1E1E1E;
    }

    /* Título principal (color claro) */
    .title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }

    /* Subtítulo (un poco más claro que el fondo) */
    .subtitle {
        font-size: 1.2rem;
        color: #CCCCCC;
        margin-bottom: 1rem;
    }

    /* Barras laterales (un tono oscuro) */
    [data-testid="stSidebar"] {
        background-color: #2A2A2A;
    }

    /* Texto en la barra lateral */
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span {
        color: #EEEEEE;
    }

    /* Ajuste del texto por defecto */
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
    # Dataset principal
    df_iadb = pd.read_parquet("IADB_DASH_BDD.parquet")

    # Dataset con lat/long en la columna 'point_pos'
    df_location = pd.read_parquet("location_iadb.parquet")
    df_location[["Latitude", "Longitude"]] = df_location["point_pos"].str.split(",", expand=True)
    df_location["Latitude"] = df_location["Latitude"].astype(float)
    df_location["Longitude"] = df_location["Longitude"].astype(float)

    # Dataset para la tabla de actividad por país
    df_activity = pd.read_parquet("activity_iadb.parquet")

    # Dataset con transactiondate_isodate, Sector y value_usd (para aprobaciones)
    df_outgoing = pd.read_parquet("outgoing_commitment_iadb.parquet")

    # Dataset para la subpágina de "Desembolsos"
    df_disbursements = pd.read_parquet("disbursements_data.parquet")

    # Diccionario de DataFrames
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
# 2. CREACIÓN DEL RENDERER DE PYGWALKER (CACHÉ)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str) -> StreamlitRenderer:
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(
        df,
        kernel_computation=True
    )
    return renderer

# -----------------------------------------------------------------------------
# PÁGINA 1: MONITOREO MULTILATERALES
# -----------------------------------------------------------------------------
def monitoreo_multilaterales():
    st.markdown('<h1 class="title">Monitoreo Multilaterales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Página principal para el seguimiento de proyectos e información multinacional.</p>', unsafe_allow_html=True)
    
    st.write("Contenido de la página 'Monitoreo Multilaterales'.")

# -----------------------------------------------------------------------------
# PÁGINA 2: COOPERACIONES TÉCNICAS
# -----------------------------------------------------------------------------
def cooperaciones_tecnicas():
    st.markdown('<h1 class="title">Cooperaciones Técnicas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza y analiza las cooperaciones técnicas aprobadas según país y año.</p>', unsafe_allow_html=True)

    data = DATASETS["IADB_DASH_BDD"].copy()
    data["Approval Date"] = pd.to_datetime(data["Approval Date"], errors="coerce")
    data["Year"] = data["Approval Date"].dt.year

    st.sidebar.header("Filtros (Cooperaciones Técnicas)")
    st.sidebar.write("Utiliza estos filtros para refinar la información mostrada:")

    paises_disponibles = ["General", "Argentina", "Bolivia", "Brazil", "Paraguay", "Uruguay"]
    filtro_pais = st.sidebar.multiselect(
        "Selecciona uno o varios países (o General para todos):",
        options=paises_disponibles,
        default=["General"]  # Por defecto: "General"
    )
    
    rango_anios = st.sidebar.slider(
        "Selecciona el rango de años:",
        2000,
        2024,
        (2000, 2024)
    )
    
    # Filtrar por año
    data = data[(data["Year"] >= 2000) & (data["Year"] <= 2024)]

    if "General" not in filtro_pais:
        data_tc = data[
            (data["Project Type"] == "Technical Cooperation")
            & (data["Project Country"].isin(filtro_pais))
            & (data["Year"] >= rango_anios[0])
            & (data["Year"] <= rango_anios[1])
        ]
        data_tc = data_tc.groupby(["Project Country", "Year"])["Approval Amount"].sum().reset_index()
    else:
        data_tc = data[
            (data["Project Type"] == "Technical Cooperation")
            & (data["Year"] >= rango_anios[0])
            & (data["Year"] <= rango_anios[1])
        ]
        data_tc = data_tc.groupby("Year")["Approval Amount"].sum().reset_index()
    
    st.subheader("Serie de Tiempo de Monto Aprobado")

    color_map = {
        "Argentina": "#8ecae6",
        "Bolivia": "#41af20",
        "Brazil": "#ffb703",
        "Paraguay": "#d00000",
        "Uruguay": "#1c5d99",
    }

    # Gráfico de línea
    if "General" not in filtro_pais:
        fig_line = px.line(
            data_tc,
            x="Year",
            y="Approval Amount",
            color="Project Country",
            title="Evolución del Monto Aprobado (Technical Cooperation)",
            labels={
                "Year": "Año",
                "Approval Amount": "Monto Aprobado",
                "Project Country": "País"
            },
            markers=True,
            color_discrete_map=color_map
        )
    else:
        fig_line = px.line(
            data_tc,
            x="Year",
            y="Approval Amount",
            title="Evolución del Monto Aprobado (Technical Cooperation)",
            labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
            markers=True
        )
        fig_line.update_traces(line_color="#ee6c4d")

    # Fondo transparente
    fig_line.update_layout(
        legend_title_text="",
        font_color="#FFFFFF",
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(gridcolor="#555555"),
        yaxis=dict(gridcolor="#555555"),
        title_font_color="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Porcentaje de TCs
    st.subheader("Porcentaje de Cooperaciones Técnicas en el Total")

    data_filtrado = data[
        (data["Year"] >= rango_anios[0]) & (data["Year"] <= rango_anios[1])
    ]
    resumen_anual_total = data_filtrado.groupby("Year")["Approval Amount"].sum().reset_index()

    if "General" not in filtro_pais:
        resumen_anual_tc = data_tc.groupby(["Year"])["Approval Amount"].sum().reset_index()
    else:
        resumen_anual_tc = data_tc

    porcentaje_tc = resumen_anual_tc.merge(
        resumen_anual_total,
        on="Year",
        suffixes=("_tc", "_total")
    )
    porcentaje_tc["Porcentaje TC"] = (
        porcentaje_tc["Approval Amount_tc"] / porcentaje_tc["Approval Amount_total"] * 100
    )
    
    # Gráfico Lollipop
    fig_lollipop = go.Figure()
    for _, row in porcentaje_tc.iterrows():
        fig_lollipop.add_trace(
            go.Scatter(
                x=[0, row["Porcentaje TC"]],
                y=[row["Year"], row["Year"]],
                mode="lines",
                line=dict(color="#999999", width=2),
                showlegend=False
            )
        )
    fig_lollipop.add_trace(
        go.Scatter(
            x=porcentaje_tc["Porcentaje TC"],
            y=porcentaje_tc["Year"],
            mode="markers+text",
            marker=dict(color="crimson", size=10),
            text=round(porcentaje_tc["Porcentaje TC"], 2),
            textposition="middle right",
            textfont=dict(color="#FFFFFF"),
            name="Porcentaje TC"
        )
    )

    fig_lollipop.update_layout(
        title="Porcentaje de Cooperaciones Técnicas en el Total de Aprobaciones",
        xaxis_title="Porcentaje (%)",
        yaxis_title="Año",
        xaxis=dict(showgrid=True, zeroline=False, gridcolor="#555555"),
        yaxis=dict(showgrid=False, zeroline=False),
        font_color="#FFFFFF",
        height=600,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_lollipop, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 3: GEODATA (SOLO "Mapa y Barras")
# -----------------------------------------------------------------------------
def geodata():
    """
    Página de GeoData en la app Streamlit.
    Solo muestra la vista de "Mapa y Barras".
    """

    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales de los proyectos.</p>', unsafe_allow_html=True)

    # Cargamos el dataframe
    data_location = DATASETS["LOCATION_IADB"].copy()

    # Validar que existan las columnas necesarias
    if "Sector" not in data_location.columns or "recipientcountry_codename" not in data_location.columns:
        st.error("Faltan columnas ('Sector' o 'recipientcountry_codename') en LOCATION_IADB.")
        return

    st.sidebar.header("Filtros (Mapa y Barras)")
    sectores_disponibles = data_location['Sector'].dropna().unique()
    
    filtro_sector = st.sidebar.selectbox(
        "Selecciona un sector:",
        options=sectores_disponibles
    )

    # Filtrar por sector seleccionado
    data_filtrada_loc = data_location[data_location['Sector'] == filtro_sector]

    if data_filtrada_loc.empty:
        st.warning("No se encontraron datos para el sector seleccionado.")
        return

    # Mapa (Scatter Mapbox)
    fig_map = px.scatter_mapbox(
        data_filtrada_loc,
        lat="Latitude",
        lon="Longitude",
        color="Sector",
        color_discrete_map={filtro_sector: "#ef233c"},
        size_max=15,
        hover_name="iatiidentifier",
        hover_data=["recipientcountry_codename", "Sector"],
        zoom=3,
        center={
            "lat": data_filtrada_loc["Latitude"].mean(),
            "lon": data_filtrada_loc["Longitude"].mean()
        },
        height=600,
        mapbox_style="carto-darkmatter",
        title=f"Proyectos en el Sector: {filtro_sector}"
    )
    fig_map.update_layout(
        margin={"r": 20, "t": 80, "l": 20, "b": 20},
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.04,
            xanchor="right",
            x=0.99
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # Gráfico de Barras (País vs cantidad)
    conteo_por_pais = (
        data_filtrada_loc
        .groupby("recipientcountry_codename")["iatiidentifier"]
        .nunique()
        .reset_index(name="Cantidad de Proyectos")
    )
    conteo_por_pais = conteo_por_pais.sort_values(by="Cantidad de Proyectos", ascending=True)

    fig_bars = go.Figure()
    fig_bars.add_trace(
        go.Bar(
            x=conteo_por_pais["Cantidad de Proyectos"],
            y=conteo_por_pais["recipientcountry_codename"],
            orientation='h',
            marker_color="#ef233c",
            text=conteo_por_pais["Cantidad de Proyectos"],
            textposition="outside"
        )
    )
    fig_bars.update_layout(
        title="Cantidad de Proyectos por País",
        xaxis_title="Cantidad de Proyectos",
        yaxis_title=None,
        height=600,
        margin=dict(l=20, r=20, t=60, b=20),
        font_color="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig_bars.update_xaxes(showgrid=False, zeroline=False)
    fig_bars.update_yaxes(showgrid=False, zeroline=False)

    col_map, col_bar = st.columns([2, 2], gap="medium")
    with col_map:
        st.plotly_chart(fig_map, use_container_width=True)
    with col_bar:
        st.plotly_chart(fig_bars, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 4: ANÁLISIS EXPLORATORIO (PYGWALKER)
# -----------------------------------------------------------------------------
def analisis_exploratorio():
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker (alto rendimiento).</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar")
    selected_dataset = st.sidebar.selectbox("Base de datos:", list(DATASETS.keys()))

    renderer = get_pyg_renderer_by_name(selected_dataset)
    renderer.explorer()

# -----------------------------------------------------------------------------
# NUEVA PÁGINA 5: FLUJOS AGREGADOS
# -----------------------------------------------------------------------------
def subpagina_aprobaciones():
    """Subpágina para mostrar Aprobaciones (outgoing_commitment_iadb.parquet)."""
    st.subheader("Aprobaciones (Outgoing Commitments)")

    # 1) Cargamos el DataFrame de aprobaciones
    df = DATASETS["OUTGOING_IADB"].copy()

    # 2) Convertimos la columna de fecha a datetime y extraemos el año
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"], errors="coerce")
    df["year"] = df["transactiondate_isodate"].dt.year

    # Validar columnas
    if "region" not in df.columns:
        st.error("No se encontró la columna 'region' en el dataset de Aprobaciones.")
        return
    if "recipientcountry_codename" not in df.columns:
        st.error("No se encontró la columna 'recipientcountry_codename' en el dataset de Aprobaciones.")
        return
    if "value_usd" not in df.columns:
        st.error("No se encontró la columna 'value_usd' en el dataset de Aprobaciones.")
        return

    # 3) Filtros en la barra lateral
    st.sidebar.header("Filtros - Aprobaciones")

    # -----------------------------------------------------------
    # Switch entre General y Regiones
    opcion_region = st.sidebar.radio("¿Deseas filtrar por Región?", ["General", "Regiones"], index=0)
    
    if opcion_region == "General":
        # => No filtramos por región ni país, mostramos TODO
        df_region_filtered = df.copy()
    else:
        # => Se activan los filtros de región
        regiones_disponibles = sorted(df["region"].dropna().unique())
        regiones_seleccionadas = st.sidebar.multiselect(
            "Selecciona región(es):",
            options=regiones_disponibles,
            default=regiones_disponibles  # Por defecto, todas
        )
        df_region_filtered = df[df["region"].isin(regiones_seleccionadas)]
        
        # => Una vez elegida(s) región(es), se filtra también por país
        paises_disponibles = sorted(df_region_filtered["recipientcountry_codename"].dropna().unique())
        paises_seleccionados = st.sidebar.multiselect(
            "Selecciona país(es):",
            options=paises_disponibles,
            default=paises_disponibles  # Por defecto, todos
        )
        df_region_filtered = df_region_filtered[df_region_filtered["recipientcountry_codename"].isin(paises_seleccionados)]
    # -----------------------------------------------------------

    # 3.3) Filtro de rango de años (por defecto, min y max del dataset filtrado)
    if df_region_filtered["year"].notnull().sum() == 0:
        # Si no hay datos con 'year', no podemos continuar
        st.warning("No hay datos disponibles para las selecciones de región/país.")
        return

    anio_min, anio_max = int(df_region_filtered["year"].min()), int(df_region_filtered["year"].max())
    rango_anios = st.sidebar.slider(
        "Rango de años:",
        min_value=anio_min,
        max_value=anio_max,
        value=(anio_min, anio_max)  
    )
    df_region_filtered = df_region_filtered[(df_region_filtered["year"] >= rango_anios[0]) & (df_region_filtered["year"] <= rango_anios[1])]

    # 3.4) Filtro de rangos de montos (value_usd) - por defecto, min y max
    if df_region_filtered["value_usd"].notnull().sum() == 0:
        st.warning("No hay valores de 'value_usd' disponibles tras los filtros previos.")
        return

    monto_min, monto_max = float(df_region_filtered["value_usd"].min()), float(df_region_filtered["value_usd"].max())
    rango_montos = st.sidebar.slider(
        "Rango de montos (USD):",
        min_value=monto_min,
        max_value=monto_max,
        value=(monto_min, monto_max)  
    )
    df_region_filtered = df_region_filtered[(df_region_filtered["value_usd"] >= rango_montos[0]) & (df_region_filtered["value_usd"] <= rango_montos[1])]

    # 4) Agrupación por año y cálculo de la sumatoria de value_usd
    if df_region_filtered.empty:
        st.warning("No hay datos disponibles para los filtros actuales.")
        return

    df_agg = df_region_filtered.groupby("year")["value_usd"].sum().reset_index()
    df_agg["value_usd_millones"] = df_agg["value_usd"] / 1_000_000

    # 5) Gráfico de Barras
    fig_bar = px.bar(
        df_agg,
        x="year",
        y="value_usd_millones",
        labels={"year": "Año", "value_usd_millones": "Valor (Millones USD)"},
        title="Sumatoria de Value_USD por Año (en millones)"
    )
    # Fondo transparente
    fig_bar.update_layout(
        font_color="#FFFFFF",
        xaxis=dict(title="Año", gridcolor="#555555"),
        yaxis=dict(title="Monto (Millones USD)", gridcolor="#555555"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla opcional
    if not df_agg.empty:
        st.write("### Detalle de la agregación")
        st.dataframe(df_agg.style.format({"value_usd_millones": "{:,.2f}"}))
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

def subpagina_desembolsos():
    """Subpágina para mostrar Desembolsos (disbursements_data.parquet). 
       Incluye también la lógica de 'General' vs 'Regiones'.
    """
    st.subheader("Desembolsos (Disbursements Data)")

    # 1) Cargamos el DataFrame de desembolsos
    df = DATASETS["DISBURSEMENTS_DATA"].copy()

    # 2) Convertimos la columna de fecha a datetime y extraemos el año
    if "transactiondate_isodate" not in df.columns:
        st.error("No se encontró la columna 'transactiondate_isodate' en el dataset de Desembolsos.")
        return
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"], errors="coerce")
    df["year"] = df["transactiondate_isodate"].dt.year

    # Validar columnas (region, recipientcountry_codename, value_usd)
    if "region" not in df.columns:
        st.error("No se encontró la columna 'region' en el dataset de Desembolsos.")
        return
    if "recipientcountry_codename" not in df.columns:
        st.error("No se encontró la columna 'recipientcountry_codename' en el dataset de Desembolsos.")
        return
    if "value_usd" not in df.columns:
        st.error("No se encontró la columna 'value_usd' en el dataset de Desembolsos.")
        return

    # 3) Filtros en la barra lateral
    st.sidebar.header("Filtros - Desembolsos")

    # -----------------------------------------------------------
    # Switch entre General y Regiones
    opcion_region = st.sidebar.radio("¿Deseas filtrar por Región?", ["General", "Regiones"], index=0)

    if opcion_region == "General":
        # => No filtramos por región ni país
        df_region_filtered = df.copy()
    else:
        regiones_disponibles = sorted(df["region"].dropna().unique())
        regiones_seleccionadas = st.sidebar.multiselect(
            "Selecciona región(es):",
            options=regiones_disponibles,
            default=regiones_disponibles
        )
        df_region_filtered = df[df["region"].isin(regiones_seleccionadas)]

        paises_disponibles = sorted(df_region_filtered["recipientcountry_codename"].dropna().unique())
        paises_seleccionados = st.sidebar.multiselect(
            "Selecciona país(es):",
            options=paises_disponibles,
            default=paises_disponibles
        )
        df_region_filtered = df_region_filtered[df_region_filtered["recipientcountry_codename"].isin(paises_seleccionados)]
    # -----------------------------------------------------------

    if df_region_filtered["year"].notnull().sum() == 0:
        st.warning("No hay datos disponibles para las selecciones de región/país.")
        return

    anio_min, anio_max = int(df_region_filtered["year"].min()), int(df_region_filtered["year"].max())
    rango_anios = st.sidebar.slider(
        "Rango de años:",
        min_value=anio_min,
        max_value=anio_max,
        value=(anio_min, anio_max)
    )
    df_region_filtered = df_region_filtered[(df_region_filtered["year"] >= rango_anios[0]) & (df_region_filtered["year"] <= rango_anios[1])]

    if df_region_filtered["value_usd"].notnull().sum() == 0:
        st.warning("No hay valores de 'value_usd' disponibles tras los filtros previos.")
        return

    monto_min, monto_max = float(df_region_filtered["value_usd"].min()), float(df_region_filtered["value_usd"].max())
    rango_montos = st.sidebar.slider(
        "Rango de montos (USD):",
        min_value=monto_min,
        max_value=monto_max,
        value=(monto_min, monto_max)
    )
    df_region_filtered = df_region_filtered[(df_region_filtered["value_usd"] >= rango_montos[0]) & (df_region_filtered["value_usd"] <= rango_montos[1])]

    if df_region_filtered.empty:
        st.warning("No hay datos disponibles para los filtros actuales.")
        return

    # 4) Agrupar y graficar
    df_agg = df_region_filtered.groupby("year")["value_usd"].sum().reset_index()
    df_agg["value_usd_millones"] = df_agg["value_usd"] / 1_000_000

    fig_bar = px.bar(
        df_agg,
        x="year",
        y="value_usd_millones",
        labels={"year": "Año", "value_usd_millones": "Valor (Millones USD)"},
        title="Sumatoria de Value_USD por Año (en millones) - Desembolsos"
    )
    fig_bar.update_layout(
        font_color="#FFFFFF",
        xaxis=dict(title="Año", gridcolor="#555555"),
        yaxis=dict(title="Monto (Millones USD)", gridcolor="#555555"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla opcional
    if not df_agg.empty:
        st.write("### Detalle de la agregación - Desembolsos")
        st.dataframe(df_agg.style.format({"value_usd_millones": "{:,.2f}"}))
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

def flujos_agregados():
    """Página principal para Flujos Agregados, con subpáginas Aprobaciones y Desembolsos."""
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualización de Aprobaciones y Desembolsos.</p>', unsafe_allow_html=True)

    # Subpáginas internas
    sub_paginas = ["Aprobaciones", "Desembolsos"]
    seleccion_subpagina = st.sidebar.radio("Seleccionar vista:", sub_paginas)

    if seleccion_subpagina == "Aprobaciones":
        subpagina_aprobaciones()
    else:
        subpagina_desembolsos()

# -----------------------------------------------------------------------------
# DICCIONARIO DE PÁGINAS
# -----------------------------------------------------------------------------
PAGINAS = {
    "Monitoreo Multilaterales": monitoreo_multilaterales,
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
    "GeoData": geodata,
    "Análisis Exploratorio": analisis_exploratorio,
    "Flujos Agregados": flujos_agregados
}

# -----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL (NAVEGACIÓN)
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
