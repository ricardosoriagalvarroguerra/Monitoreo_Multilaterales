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
    # CARGA DEL DATAFRAME BASE (para aplicar filtros)
    # -------------------------------------------------------------------------
    df_desc = DATASETS["ACTIVITY_IADB"].copy()

    # -------------------------------------------------------------------------
    # BARRA LATERAL - FILTROS
    # -------------------------------------------------------------------------
    st.sidebar.header("Filtros (Descriptivo)")

    # -------------------------------  
    # 1) FILTRO DE SECTOR_1
    # -------------------------------
    if "Sector_1" not in df_desc.columns:
        st.sidebar.warning("Columna 'Sector_1' no encontrada en el dataset. Se omitirá este filtro.")
    else:
        sectores_unicos = sorted(df_desc["Sector_1"].dropna().unique().tolist())
        opciones_sector = ["General"] + sectores_unicos

        sector_seleccionado = st.sidebar.selectbox(
            "Selecciona un Sector (Sector_1):",
            options=opciones_sector,
            index=0
        )

        if sector_seleccionado != "General":
            df_desc = df_desc[df_desc["Sector_1"] == sector_seleccionado]

    # -------------------------------  
    # 2) FILTRO DE activityscope_codename
    # -------------------------------
    if "activityscope_codename" not in df_desc.columns:
        st.sidebar.warning("Columna 'activityscope_codename' no encontrada en el dataset. Se omitirá este filtro.")
    else:
        scopes_unicos = sorted(df_desc["activityscope_codename"].dropna().unique().tolist())
        opciones_scope = ["General"] + scopes_unicos

        scope_seleccionado = st.sidebar.selectbox(
            "Selecciona un activityscope_codename:",
            options=opciones_scope,
            index=0
        )

        if scope_seleccionado != "General":
            df_desc = df_desc[df_desc["activityscope_codename"] == scope_seleccionado]

    # -------------------------------------------------------------------------
    # COLUMNA "value_usd_millions" (si existe 'value_usd')
    # -------------------------------------------------------------------------
    if "value_usd" in df_desc.columns:
        df_desc["value_usd_millions"] = df_desc["value_usd"] / 1_000_000
    else:
        df_desc["value_usd_millions"] = None

    # -------------------------------------------------------------------------
    # MOSTRAR GRÁFICOS (2 COLUMNAS) -> SCATTER PLOTS
    # -------------------------------------------------------------------------
    col1, col2 = st.columns(2)

    # -------------------------------------------------------------------------
    # GRÁFICO 1: Aprobaciones Vs Ejecución
    # -------------------------------------------------------------------------
    with col1:
        st.subheader("Aprobaciones Vs Ejecución")

        needed_cols_1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if not needed_cols_1.issubset(df_desc.columns):
            st.warning(f"Faltan columnas para el primer gráfico: {needed_cols_1 - set(df_desc.columns)}")
        else:
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
                color_discrete_sequence=["#00b4d8"]  # color scatter
            )
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

        needed_cols_2 = {"duracion_estimada", "duracion_real"}
        if not needed_cols_2.issubset(df_desc.columns):
            st.warning(f"Faltan columnas para el segundo gráfico: {needed_cols_2 - set(df_desc.columns)}")
        else:
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
                color_discrete_sequence=["#00b4d8"]  # color scatter
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
            fig2.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------------------------------------------------
    # TABSET PARA LOS BOX PLOTS (SIN FILTROS)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Box Plots")

    df_box = DATASETS["ACTIVITY_IADB"].copy()  # Datos sin filtros

    tab_modalidad, tab_sector = st.tabs(["Modalidad", "Sector"])

    # ==================== TAB: MODALIDAD ====================
    with tab_modalidad:
        st.subheader("Box Plots - Modalidad")

        # =========== 1) BOX PLOT: Modalidad vs Duración Estimada ==============
        needed_cols_box = {"modalidad_general", "duracion_estimada"}
        if not needed_cols_box.issubset(df_box.columns):
            st.warning(f"Faltan columnas para el box plot (modalidad vs duracion_estimada): {needed_cols_box - set(df_box.columns)}")
        else:
            df_boxplot1 = df_box[
                df_box["modalidad_general"].notna() &
                df_box["duracion_estimada"].notna()
            ].copy()

            fig_box1 = px.box(
                df_boxplot1,
                x="modalidad_general",
                y="duracion_estimada",
                labels={
                    "modalidad_general": "Modalidad General",
                    "duracion_estimada": "Duración Estimada (años)"
                },
                title="Distribución de Duración Estimada por Modalidad",
                color_discrete_sequence=["#ef233c"]
            )
            fig_box1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_box1, use_container_width=True)

        # =========== 2) BOX PLOT: Modalidad vs completion_delay_years =========
        needed_cols_box_delay = {"modalidad_general", "completion_delay_years"}
        if not needed_cols_box_delay.issubset(df_box.columns):
            st.warning(f"Faltan columnas para el box plot (modalidad vs completion_delay_years): {needed_cols_box_delay - set(df_box.columns)}")
        else:
            df_boxplot2 = df_box[
                df_box["modalidad_general"].notna() &
                df_box["completion_delay_years"].notna()
            ].copy()

            fig_box2 = px.box(
                df_boxplot2,
                x="modalidad_general",
                y="completion_delay_years",
                labels={
                    "modalidad_general": "Modalidad General",
                    "completion_delay_years": "Atraso (años)"
                },
                title="Distribución de Atraso en Finalización por Modalidad",
                color_discrete_sequence=["#edf2f4"]
            )
            fig_box2.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_box2, use_container_width=True)

    # ==================== TAB: SECTOR ====================
    with tab_sector:
        st.subheader("Box Plots - Sector")

        needed_cols_box2 = {"Sector_1", "value_usd", "duracion_estimada"}
        if not needed_cols_box2.issubset(df_box.columns):
            st.warning(f"Faltan columnas para el box plot (Sector vs duracion_estimada): {needed_cols_box2 - set(df_box.columns)}")
        else:
            # Determinar top 6 sectores segun value_usd
            df_agrupado = (
                df_box.groupby("Sector_1", as_index=False)["value_usd"]
                .sum()
                .sort_values("value_usd", ascending=False)
            )
            top_6_sectores = df_agrupado["Sector_1"].head(6).tolist()

            df_box2a = df_box[
                df_box["Sector_1"].isin(top_6_sectores) &
                df_box["duracion_estimada"].notna()
            ].copy()

            fig_box2a = px.box(
                df_box2a,
                x="Sector_1",
                y="duracion_estimada",
                labels={
                    "Sector_1": "Sector (Top 6)",
                    "duracion_estimada": "Duración Estimada (años)"
                },
                title="Distribución de Duración Estimada - Top 6 Sectores (por Monto)",
                color_discrete_sequence=["#ef233c"]
            )
            fig_box2a.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_box2a, use_container_width=True)

        # =========== 2) BOX PLOT: Sector vs completion_delay_years =========
        needed_cols_box2b = {"Sector_1", "value_usd", "completion_delay_years"}
        if not needed_cols_box2b.issubset(df_box.columns):
            st.warning(f"Faltan columnas para el box plot (Sector vs completion_delay_years): {needed_cols_box2b - set(df_box.columns)}")
        else:
            df_agrupado_2b = (
                df_box.groupby("Sector_1", as_index=False)["value_usd"]
                .sum()
                .sort_values("value_usd", ascending=False)
            )
            top_6_sectores_b = df_agrupado_2b["Sector_1"].head(6).tolist()

            df_box2b = df_box[
                df_box["Sector_1"].isin(top_6_sectores_b) &
                df_box["completion_delay_years"].notna()
            ].copy()

            fig_box2b = px.box(
                df_box2b,
                x="Sector_1",
                y="completion_delay_years",
                labels={
                    "Sector_1": "Sector (Top 6)",
                    "completion_delay_years": "Atraso (años)"
                },
                title="Distribución de Atraso en Finalización - Top 6 Sectores (por Monto)",
                color_discrete_sequence=["#edf2f4"]
            )
            fig_box2b.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_box2b, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 2: SERIES TEMPORALES
# -----------------------------------------------------------------------------
def series_temporales():
    st.markdown('<h1 class="title">Series Temporales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora la evolución de los datos a lo largo del tiempo.</p>', unsafe_allow_html=True)
    st.write("Aquí podrías incluir gráficos de líneas, modelos ARIMA, predicciones, etc.")
    
# -----------------------------------------------------------------------------
# PÁGINA 3: ANÁLISIS GEOSPACIAL
# -----------------------------------------------------------------------------
def analisis_geoespacial():
    st.markdown('<h1 class="title">Análisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza datos en el mapa, distribuciones geográficas, etc.</p>', unsafe_allow_html=True)
    st.write("Aquí iría el mapa interactivo y análisis geoespacial con folium o plotly.")
    
# -----------------------------------------------------------------------------
# PÁGINA 4: MULTIDIMENSIONAL Y RELACIONES
# -----------------------------------------------------------------------------
def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis de relaciones entre variables, correlaciones, PCA, clustering, etc.</p>', unsafe_allow_html=True)
    st.write("Esta sección podría mostrar diagramas de correlación, factores, dendrogramas, etc.")
    
# -----------------------------------------------------------------------------
# PÁGINA 5: MODELOS
# -----------------------------------------------------------------------------
def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Entrena y evalúa modelos predictivos o de clasificación.</p>', unsafe_allow_html=True)
    st.write("Aquí se incluiría la lógica de entrenamiento, validación y métricas de modelos de ML/estadísticos.")
    
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
