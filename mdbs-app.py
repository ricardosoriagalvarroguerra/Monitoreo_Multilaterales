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
    """
    Lee y devuelve los DataFrames usados en la aplicación.
    Actualiza las rutas/parquet si es necesario.
    """
    df_activity = pd.read_parquet("activity_iadb.parquet")
    
    datasets = {
        "ACTIVITY_IADB": df_activity
    }
    return datasets

DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2. CREACIÓN DEL RENDERER DE PYGWALKER (CACHÉ)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str):
    """
    Crea el objeto de PyGWalker para exploración de datos interactiva.
    """
    from pygwalker.api.streamlit import StreamlitRenderer
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(
        df,
        kernel_computation=True
    )
    return renderer

# -----------------------------------------------------------------------------
# PÁGINA 1: DESCRIPTIVO
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis descriptivo de los datos.</p>', unsafe_allow_html=True)
    st.write("Esta sección mostrará las estadísticas descriptivas, distribución de variables, etc.")

    # -------------------------------------------------------------------------
    # BARRA LATERAL - FILTROS
    # -------------------------------------------------------------------------
    st.sidebar.header("Filtros (Descriptivo)")
    
    # Cargamos el dataframe base
    df_desc = DATASETS["ACTIVITY_IADB"].copy()

    # 1) FILTRO DE SECTOR (single-select con opción "General")
    sectores_disponibles = sorted(df_desc["Sector"].dropna().unique().tolist())
    sectores_opciones = ["General"] + sectores_disponibles
    
    sector_seleccionado = st.sidebar.selectbox(
        "Selecciona un Sector:",
        options=sectores_opciones,
        index=0
    )
    
    if sector_seleccionado != "General":
        df_desc = df_desc[df_desc["Sector"] == sector_seleccionado]

    # 2) FILTRO DE activityscope_codename (single-select con opción "General")
    scopes_disponibles = sorted(df_desc["activityscope_codename"].dropna().unique().tolist())
    scopes_opciones = ["General"] + scopes_disponibles

    scope_seleccionado = st.sidebar.selectbox(
        "Selecciona actividad (activityscope_codename):",
        options=scopes_opciones,
        index=0
    )

    if scope_seleccionado != "General":
        df_desc = df_desc[df_desc["activityscope_codename"] == scope_seleccionado]

    # -------------------------------------------------------------------------
    # CREAMOS COLUMNA "value_usd_millions"
    # -------------------------------------------------------------------------
    df_desc["value_usd_millions"] = df_desc["value_usd"] / 1_000_000

    # -------------------------------------------------------------------------
    # MOSTRAR GRÁFICOS (2 COLUMNAS)
    # -------------------------------------------------------------------------
    col1, col2 = st.columns(2)

    # -------------------------------------------------------------------------
    # GRÁFICO 1: Aprobaciones Vs Ejecución
    # -------------------------------------------------------------------------
    with col1:
        st.subheader("Aprobaciones Vs Ejecución")

        df_chart1 = df_desc[
            df_desc["duracion_estimada"].notna() &
            df_desc["completion_delay_years"].notna() &
            df_desc["value_usd_millions"].notna()
        ].copy()

        fig1 = px.scatter(
            df_chart1,
            x="duracion_estimada",
            y="completion_delay_years",
            size="value_usd_millions",  # Tamaño de los puntos
            labels={
                "duracion_estimada": "Duración Estimada (años)",
                "completion_delay_years": "Atraso en Finalización (años)",
                "value_usd_millions": "Value (Millones USD)"
            },
            title="Aprobaciones Vs Ejecución",
            color_discrete_sequence=["#00b4d8"]
        )
        # Ajuste de layout para modo oscuro
        fig1.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig1, use_container_width=True)

    # -------------------------------------------------------------------------
    # GRÁFICO 2: Planificación Vs Ejecución
    # -------------------------------------------------------------------------
    with col2:
        st.subheader("Planificación Vs Ejecución")

        df_chart2 = df_desc[
            df_desc["duracion_estimada"].notna() &
            df_desc["duracion_real"].notna()
        ].copy()

        fig2 = px.scatter(
            df_chart2,
            x="duracion_estimada",
            y="duracion_real",
            labels={
                "duracion_estimada": "Duración Estimada (años)",
                "duracion_real": "Duración Real (años)"
            },
            title="Planificación Vs Ejecución",
            color_discrete_sequence=["#00b4d8"]
        )
        # Línea de 45 grados (punteada, blanca)
        max_range = max(
            df_chart2["duracion_estimada"].max(),
            df_chart2["duracion_real"].max()
        )
        fig2.add_shape(
            type="line",
            x0=0,
            y0=0,
            x1=max_range,
            y1=max_range,
            line=dict(color="white", dash="dot")
        )

        # Ajuste de layout para modo oscuro
        fig2.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 2: SERIES TEMPORALES
# -----------------------------------------------------------------------------
def series_temporales():
    st.markdown('<h1 class="title">Series Temporales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora la evolución de los datos a lo largo del tiempo.</p>', unsafe_allow_html=True)
    st.write("Aquí podrías incluir gráficos de líneas, modelos ARIMA, predicciones, etc.")
    # TODO: Implementar tus visualizaciones de series de tiempo
    
# -----------------------------------------------------------------------------
# PÁGINA 3: ANÁLISIS GEOSPACIAL
# -----------------------------------------------------------------------------
def analisis_geoespacial():
    st.markdown('<h1 class="title">Análisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza datos en el mapa, distribuciones geográficas, etc.</p>', unsafe_allow_html=True)
    st.write("Aquí iría el mapa interactivo y análisis geoespacial con folium o plotly.")
    # TODO: Implementar lógica de mapas o análisis geoespacial

# -----------------------------------------------------------------------------
# PÁGINA 4: MULTIDIMENSIONAL Y RELACIONES
# -----------------------------------------------------------------------------
def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis de relaciones entre variables, correlaciones, PCA, clustering, etc.</p>', unsafe_allow_html=True)
    st.write("Esta sección podría mostrar diagramas de correlación, factores, dendrogramas, etc.")
    # TODO: Implementar lógica de análisis multivariante, correlaciones, PCA, etc.

# -----------------------------------------------------------------------------
# PÁGINA 5: MODELOS
# -----------------------------------------------------------------------------
def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Entrena y evalúa modelos predictivos o de clasificación.</p>', unsafe_allow_html=True)
    st.write("Aquí se incluiría la lógica de entrenamiento, validación y métricas de modelos de ML/estadísticos.")
    # TODO: Implementar pipelines de Machine Learning, métricas, etc.

# -----------------------------------------------------------------------------
# PÁGINA 6: ANÁLISIS EXPLORATORIO (PYGWALKER)
# -----------------------------------------------------------------------------
def analisis_exploratorio():
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker (alto rendimiento).</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar")
    selected_dataset = st.sidebar.selectbox("Base de datos:", list(DATASETS.keys()))

    renderer = get_pyg_renderer_by_name(selected_dataset)
    renderer.explorer()

# -----------------------------------------------------------------------------
# DICCIONARIO DE PÁGINAS
# -----------------------------------------------------------------------------
PAGINAS = {
    "Descriptivo": descriptivo,
    "Series Temporales": series_temporales,
    "Análisis Geoespacial": analisis_geoespacial,
    "Multidimensional y Relaciones": multidimensional_y_relaciones,
    "Modelos": modelos,
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
