import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

import matplotlib.colors as mcolors  # Para usar TABLEAU_COLORS u otras paletas
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

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
    # Separar 'point_pos' (ej: "40.7128,-74.0060") en columnas 'Latitude' y 'Longitude'
    df_location[["Latitude", "Longitude"]] = df_location["point_pos"].str.split(",", expand=True)
    # Convertir a float
    df_location["Latitude"] = df_location["Latitude"].astype(float)
    df_location["Longitude"] = df_location["Longitude"].astype(float)

    # Dataset para la tabla de actividad por país (nuevo)
    df_activity = pd.read_parquet("activity_iadb.parquet")

    # Diccionario de DataFrames
    datasets = {
        "IADB_DASH_BDD": df_iadb,
        "LOCATION_IADB": df_location,
        "ACTIVITY_IADB": df_activity
    }
    return datasets

DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2. CREACIÓN DEL RENDERER DE PYGWALKER (CACHÉ) CON KERNEL COMPUTATION
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str) -> StreamlitRenderer:
    """
    Crea un StreamlitRenderer para el dataset especificado.
    kernel_computation=True para alto rendimiento.
    """
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(
        df,
        kernel_computation=True  # Acelera cálculos en grandes datasets
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
        default=["General"]
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

    fig_line.update_traces(line_shape='spline')
    fig_line.update_layout(
        legend_title_text="",
        font_color="#FFFFFF",
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(gridcolor="#555555"),
        yaxis=dict(gridcolor="#555555"),
        title_font_color="#FFFFFF"
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
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig_lollipop, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 3: FLUJOS AGREGADOS
# -----------------------------------------------------------------------------
def flujos_agregados():
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analiza aprobaciones y desembolsos anuales.</p>', unsafe_allow_html=True)

    # Opciones de filtros
    flujo_opciones = ["Aprobaciones", "Desembolsos"]
    mdb_opciones = ["IADB"]

    # Filtros en la barra lateral
    st.sidebar.header("Filtros")
    tipo_flujo = st.sidebar.selectbox("Selecciona el tipo de flujo:", flujo_opciones)
    mdb = st.sidebar.selectbox("Selecciona MDB:", mdb_opciones)

    # Selección de país
    if tipo_flujo == "Desembolsos":
        df = disbursement_data.copy()
    else:  # Aprobaciones
        df = outgoing_commitment_data.copy()

    paises_disponibles = sorted(df["recipientcountry_codename"].dropna().unique())
    filtro_pais = st.sidebar.multiselect(
        "Selecciona país(es):",
        options=paises_disponibles,
        default=paises_disponibles
    )

    # Filtrar el DataFrame por país
    df_filtrado = df[df["recipientcountry_codename"].isin(filtro_pais)]

    # Agrupar datos por año y calcular la suma de value_usd
    resumen_anual = (
        df_filtrado.groupby("year")["value_usd"]
        .sum()
        .reset_index()
        .sort_values(by="year")
    )

    # Gráfico de barras
    st.subheader(f"Evolución anual de {tipo_flujo.lower()} en {mdb}")
    fig_bar = px.bar(
        resumen_anual,
        x="year",
        y="value_usd",
        labels={"year": "Año", "value_usd": "Valor en USD"},
        title=f"Total de {tipo_flujo.lower()} por año",
        text_auto=True,
        height=500
    )
    fig_bar.update_layout(
        xaxis=dict(title="Año"),
        yaxis=dict(title="Valor en USD"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 4: GEODATA (MODIFICADA)
# -----------------------------------------------------------------------------
def geodata():
    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales de los proyectos.</p>', unsafe_allow_html=True)
    
    # 1. Cargar el DataFrame de ubicación
    data_location = DATASETS["LOCATION_IADB"].copy()

    # Verificar la existencia de las columnas necesarias
    if "Sector" not in data_location.columns or "recipientcountry_codename" not in data_location.columns:
        st.error("Faltan columnas necesarias ('Sector' o 'recipientcountry_codename') en el dataset.")
        return

    # 2. Obtener la lista de sectores únicos disponibles
    sectores_disponibles = data_location['Sector'].dropna().unique()
    
    # 3. Crear un filtro en la barra lateral para seleccionar un solo sector
    st.sidebar.header("Filtros (GeoData)")
    filtro_sector = st.sidebar.selectbox(
        "Selecciona un sector:",
        options=sectores_disponibles
    )

    # 4. Filtrar el DataFrame en función del sector seleccionado
    data_filtrada_loc = data_location[data_location['Sector'] == filtro_sector]
    
    # Si no hay datos tras filtrar, mostrar advertencia y salir
    if data_filtrada_loc.empty:
        st.warning("No se encontraron datos para el sector seleccionado.")
        return

    # 5. Crear un mapa interactivo con Plotly Express
    #    - Se fuerza el color para el sector al valor "#ef233c"
    fig = px.scatter_mapbox(
        data_filtrada_loc,
        lat="Latitude",
        lon="Longitude",
        color="Sector",
        color_discrete_map={filtro_sector: "#ef233c"},  # Puntos en "#ef233c"
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

    # Ajustar la posición de la leyenda para no chocar con el título/subtítulo
    fig.update_layout(
        margin={"r":20, "t":80, "l":20, "b":20},
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.04,      # Ubicarla justo por debajo del título
            xanchor="right",
            x=0.99
        )
    )

    # 6. Crear una tabla con la cantidad de proyectos por país
    conteo_por_pais = (
        data_filtrada_loc
        .groupby("recipientcountry_codename")["iatiidentifier"]
        .nunique()
        .reset_index(name="Cantidad de Proyectos")
    )
    # Ordenar
    conteo_por_pais = conteo_por_pais.sort_values(by="Cantidad de Proyectos", ascending=False)
    # Quitar índice original
    conteo_por_pais = conteo_por_pais.reset_index(drop=True)

    # Disponer mapa y tabla en columnas lado a lado (mismo ancho)
    col_map, col_table = st.columns([2, 2], gap="medium")

    with col_map:
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Cantidad de Proyectos por País")
        conteo_por_pais_styled = conteo_por_pais.style.hide(axis="index")
        st.dataframe(conteo_por_pais_styled, use_container_width=True, height=800)

# -----------------------------------------------------------------------------
# PÁGINA 5: ANÁLISIS EXPLORATORIO (PYGWALKER)
# -----------------------------------------------------------------------------
def analisis_exploratorio():
    """
    Página de Análisis Exploratorio con PyGWalker y kernel_computation=True.
    Se añade un selector en la barra lateral para elegir la BDD a analizar.
    """
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker (alto rendimiento).</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar")
    selected_dataset = st.sidebar.selectbox("Base de datos:", list(DATASETS.keys()))

    # Obtenemos el renderer con kernel_computation=True
    renderer = get_pyg_renderer_by_name(selected_dataset)

    # Mostramos la interfaz exploratoria
    renderer.explorer()

# -----------------------------------------------------------------------------
# DICCIONARIO DE PÁGINAS
# -----------------------------------------------------------------------------
PAGINAS = {
    "Monitoreo Multilaterales": monitoreo_multilaterales,
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
    "Flujos Agregados": flujos_agregados,
    "GeoData": geodata,
    "Análisis Exploratorio": analisis_exploratorio
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
