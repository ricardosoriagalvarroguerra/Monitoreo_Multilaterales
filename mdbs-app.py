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
    """
    df_activity = pd.read_parquet("activity_iadb.parquet")  # Ajusta la ruta si es necesario

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
    # CARGA DEL DATAFRAME BASE (para aplicar filtros en los scatter plots)
    # -------------------------------------------------------------------------
    df_desc = DATASETS["ACTIVITY_IADB"].copy()

    # -------------------------------------------------------------------------
    # BARRA LATERAL - FILTROS
    # -------------------------------------------------------------------------
    st.sidebar.header("Filtros (Descriptivo)")

    # Filtro 1: Sector_1
    if "Sector_1" not in df_desc.columns:
        st.sidebar.warning("Columna 'Sector_1' no encontrada en el dataset. Se omitirá este filtro.")
    else:
        lista_sectores = sorted(df_desc["Sector_1"].dropna().unique().tolist())
        opciones_sector = ["General"] + lista_sectores
        sector_seleccionado = st.sidebar.selectbox(
            "Selecciona un Sector (Sector_1):",
            options=opciones_sector,
            index=0
        )
        if sector_seleccionado != "General":
            df_desc = df_desc[df_desc["Sector_1"] == sector_seleccionado]

    # Filtro 2: activityscope_codename
    if "activityscope_codename" not in df_desc.columns:
        st.sidebar.warning("Columna 'activityscope_codename' no encontrada en el dataset. Se omitirá este filtro.")
    else:
        lista_scopes = sorted(df_desc["activityscope_codename"].dropna().unique().tolist())
        opciones_scope = ["General"] + lista_scopes
        scope_seleccionado = st.sidebar.selectbox(
            "Selecciona un activityscope_codename:",
            options=opciones_scope,
            index=0
        )
        if scope_seleccionado != "General":
            df_desc = df_desc[df_desc["activityscope_codename"] == scope_seleccionado]

    # -------------------------------------------------------------------------
    # CONVERTIR value_usd -> value_usd_millions (para scatter size)
    # -------------------------------------------------------------------------
    if "value_usd" in df_desc.columns:
        df_desc["value_usd_millions"] = df_desc["value_usd"] / 1_000_000
    else:
        df_desc["value_usd_millions"] = None

    # -------------------------------------------------------------------------
    # SCATTER PLOTS (con los filtros aplicados)
    # -------------------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Aprobaciones Vs Ejecución")
        needed_cols_1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if not needed_cols_1.issubset(df_desc.columns):
            st.warning(f"Faltan columnas para el primer gráfico: {needed_cols_1 - set(df_desc.columns)}")
        else:
            df_plot1 = df_desc[
                df_desc["duracion_estimada"].notna() &
                df_desc["completion_delay_years"].notna() &
                df_desc["value_usd_millions"].notna()
            ].copy()

            fig1 = px.scatter(
                df_plot1,
                x="duracion_estimada",
                y="completion_delay_years",
                size="value_usd_millions",  # tamaño
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "completion_delay_years": "Atraso en Finalización (años)",
                    "value_usd_millions": "Value (Millones USD)"
                },
                title="Aprobaciones Vs Ejecución",
                color_discrete_sequence=["#00b4d8"]
            )
            fig1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Planificación Vs Ejecución")
        needed_cols_2 = {"duracion_estimada", "duracion_real"}
        if not needed_cols_2.issubset(df_desc.columns):
            st.warning(f"Faltan columnas para el segundo gráfico: {needed_cols_2 - set(df_desc.columns)}")
        else:
            df_plot2 = df_desc[
                df_desc["duracion_estimada"].notna() &
                df_desc["duracion_real"].notna()
            ].copy()

            fig2 = px.scatter(
                df_plot2,
                x="duracion_estimada",
                y="duracion_real",
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "duracion_real": "Duración Real (años)"
                },
                title="Planificación Vs Ejecución",
                color_discrete_sequence=["#00b4d8"]
            )
            # Agregamos línea punteada blanca (45°)
            max_range = max(
                df_plot2["duracion_estimada"].max(),
                df_plot2["duracion_real"].max()
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
    # TABS POR PAÍS (SIN FILTROS)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Box Plots por País")

    df_box = DATASETS["ACTIVITY_IADB"].copy()  # sin filtros

    # Definimos los países y sus nombres de la columna 'recipientcountry_codename'
    countries_dict = {
        "Argentina": ["Argentina"],
        "Bolivia": ["Bolivia (Plurinational State of)"],
        "Brazil": ["Brazil"],
        "Paraguay": ["Paraguay"],
        "Uruguay": ["Uruguay"],
        "5-FP": [
            "Argentina",
            "Bolivia (Plurinational State of)",
            "Brazil",
            "Paraguay",
            "Uruguay"
        ]
    }

    # Creamos pestañas (una por país + la de 5-FP)
    tabs_list = list(countries_dict.keys())
    tabs_objects = st.tabs(tabs_list)

    for i, tab_name in enumerate(tabs_list):
        with tabs_objects[i]:
            st.subheader(f"Box Plots - {tab_name}")
            # Obtenemos la lista de países a filtrar
            paises_filtrado = countries_dict[tab_name]

            # BOX PLOT 1: duracion_estimada
            needed_cols_p1 = {"recipientcountry_codename", "duracion_estimada"}
            if not needed_cols_p1.issubset(df_box.columns):
                st.warning(f"Faltan columnas para duracion_estimada: {needed_cols_p1 - set(df_box.columns)}")
            else:
                df_p1 = df_box[
                    df_box["recipientcountry_codename"].isin(paises_filtrado) &
                    df_box["duracion_estimada"].notna()
                ].copy()
                fig_p1 = px.box(
                    df_p1,
                    x="recipientcountry_codename",
                    y="duracion_estimada",
                    labels={
                        "recipientcountry_codename": "País",
                        "duracion_estimada": "Duración Estimada (años)"
                    },
                    title=f"Duración Estimada - {tab_name}",
                    color_discrete_sequence=["#ef233c"]
                )
                fig_p1.update_layout(
                    font_color="#FFFFFF",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_p1, use_container_width=True)

            # BOX PLOT 2: completion_delay_years
            needed_cols_p2 = {"recipientcountry_codename", "completion_delay_years"}
            if not needed_cols_p2.issubset(df_box.columns):
                st.warning(f"Faltan columnas para completion_delay_years: {needed_cols_p2 - set(df_box.columns)}")
            else:
                df_p2 = df_box[
                    df_box["recipientcountry_codename"].isin(paises_filtrado) &
                    df_box["completion_delay_years"].notna()
                ].copy()
                fig_p2 = px.box(
                    df_p2,
                    x="recipientcountry_codename",
                    y="completion_delay_years",
                    labels={
                        "recipientcountry_codename": "País",
                        "completion_delay_years": "Atraso (años)"
                    },
                    title=f"Atraso en Finalización - {tab_name}",
                    color_discrete_sequence=["#edf2f4"]
                )
                fig_p2.update_layout(
                    font_color="#FFFFFF",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_p2, use_container_width=True)

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
