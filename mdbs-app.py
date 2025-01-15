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
    Ajusta la ruta si tu archivo se llama distinto.
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
# FUNCIONES AUXILIARES (BOX PLOTS)
# -----------------------------------------------------------------------------
def boxplot_modalidad(df: pd.DataFrame, titulo_extra: str = ""):
    """
    Muestra dos box plots sobre 'modalidad_general':
      1) X=modalidad_general, Y=duracion_estimada, color=#ef233c
      2) X=modalidad_general, Y=completion_delay_years, color=#edf2f4
    """
    needed_cols_m1 = {"modalidad_general", "duracion_estimada"}
    needed_cols_m2 = {"modalidad_general", "completion_delay_years"}

    # Box Plot 1 (Duración Estimada)
    if not needed_cols_m1.issubset(df.columns):
        st.warning(f"Faltan columnas para Modalidad (Duración Estimada): {needed_cols_m1 - set(df.columns)}")
    else:
        df_m1 = df[
            df["modalidad_general"].notna() &
            df["duracion_estimada"].notna()
        ].copy()

        fig_m1 = px.box(
            df_m1,
            x="modalidad_general",
            y="duracion_estimada",
            color_discrete_sequence=["#ef233c"],
            title=f"Distribución de Duración Estimada {titulo_extra} (Modalidad)",
            labels={
                "modalidad_general": "Modalidad General",
                "duracion_estimada": "Duración Estimada (años)"
            }
        )
        fig_m1.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_m1, use_container_width=True)

    # Box Plot 2 (Completion Delay)
    if not needed_cols_m2.issubset(df.columns):
        st.warning(f"Faltan columnas para Modalidad (Completion Delay): {needed_cols_m2 - set(df.columns)}")
    else:
        df_m2 = df[
            df["modalidad_general"].notna() &
            df["completion_delay_years"].notna()
        ].copy()

        fig_m2 = px.box(
            df_m2,
            x="modalidad_general",
            y="completion_delay_years",
            color_discrete_sequence=["#edf2f4"],
            title=f"Distribución de Atraso en Finalización {titulo_extra} (Modalidad)",
            labels={
                "modalidad_general": "Modalidad General",
                "completion_delay_years": "Atraso (años)"
            }
        )
        fig_m2.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_m2, use_container_width=True)


def boxplot_sector(df: pd.DataFrame, titulo_extra: str = ""):
    """
    Muestra dos box plots sobre 'Sector_1' (Top 6 por value_usd):
      1) X=Sector_1, Y=duracion_estimada, color=#ef233c
      2) X=Sector_1, Y=completion_delay_years, color=#edf2f4
    """
    needed_cols_s = {"Sector_1", "value_usd"}
    if not needed_cols_s.issubset(df.columns):
        st.warning(f"Faltan columnas para Sector (value_usd, Sector_1): {needed_cols_s - set(df.columns)}")
        return

    # Determinamos los Top 6 sectores
    df_agg = (
        df.groupby("Sector_1", as_index=False)["value_usd"]
        .sum()
        .sort_values("value_usd", ascending=False)
    )
    top_sectores = df_agg["Sector_1"].head(6).tolist()

    # 1) Box Plot (Duración Estimada)
    needed_cols_s1 = {"Sector_1", "duracion_estimada"}
    if not needed_cols_s1.issubset(df.columns):
        st.warning(f"Faltan columnas para Sector (duracion_estimada): {needed_cols_s1 - set(df.columns)}")
    else:
        df_s1 = df[
            df["Sector_1"].isin(top_sectores) &
            df["duracion_estimada"].notna()
        ].copy()

        fig_s1 = px.box(
            df_s1,
            x="Sector_1",
            y="duracion_estimada",
            color_discrete_sequence=["#ef233c"],
            title=f"Distribución de Duración Estimada {titulo_extra} (Top 6 Sectores)",
            labels={
                "Sector_1": "Sector_1 (Top 6)",
                "duracion_estimada": "Duración Estimada (años)"
            }
        )
        fig_s1.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_s1, use_container_width=True)

    # 2) Box Plot (Completion Delay)
    needed_cols_s2 = {"Sector_1", "completion_delay_years"}
    if not needed_cols_s2.issubset(df.columns):
        st.warning(f"Faltan columnas para Sector (completion_delay_years): {needed_cols_s2 - set(df.columns)}")
    else:
        df_s2 = df[
            df["Sector_1"].isin(top_sectores) &
            df["completion_delay_years"].notna()
        ].copy()

        fig_s2 = px.box(
            df_s2,
            x="Sector_1",
            y="completion_delay_years",
            color_discrete_sequence=["#edf2f4"],
            title=f"Distribución de Atraso en Finalización {titulo_extra} (Top 6 Sectores)",
            labels={
                "Sector_1": "Sector_1 (Top 6)",
                "completion_delay_years": "Atraso (años)"
            }
        )
        fig_s2.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_s2, use_container_width=True)


# -----------------------------------------------------------------------------
# PÁGINA 1: DESCRIPTIVO
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis descriptivo de los datos.</p>', unsafe_allow_html=True)

    st.write("Sección con Scatter Plots (filtro) y Box Plots por Modalidad, Sector y Países.")

    # -------------------------------------------------------------------------
    # 1) SCATTER PLOTS (con filtros en la barra lateral)
    # -------------------------------------------------------------------------
    df_filters = DATASETS["ACTIVITY_IADB"].copy()

    st.sidebar.header("Filtros (Scatter Plots)")

    # Filtro Sector_1
    if "Sector_1" not in df_filters.columns:
        st.sidebar.warning("No existe 'Sector_1'. Se omite filtro.")
    else:
        opciones_sector = ["General"] + sorted(df_filters["Sector_1"].dropna().unique().tolist())
        sel_sector = st.sidebar.selectbox("Sector_1", opciones_sector, index=0)
        if sel_sector != "General":
            df_filters = df_filters[df_filters["Sector_1"] == sel_sector]

    # Filtro activityscope_codename
    if "activityscope_codename" not in df_filters.columns:
        st.sidebar.warning("No existe 'activityscope_codename'. Se omite filtro.")
    else:
        opciones_scope = ["General"] + sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        sel_scope = st.sidebar.selectbox("activityscope_codename", opciones_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # Convertir a millones
    if "value_usd" in df_filters.columns:
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000
    else:
        df_filters["value_usd_millions"] = None

    # Mostramos 2 scatter plots
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Aprobaciones Vs Ejecución")
        need_scatter1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if not need_scatter1.issubset(df_filters.columns):
            st.warning(f"No están todas las columnas {need_scatter1} para el primer scatter.")
        else:
            df_sc1 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["completion_delay_years"].notna() &
                df_filters["value_usd_millions"].notna()
            ].copy()
            fig_sc1 = px.scatter(
                df_sc1,
                x="duracion_estimada",
                y="completion_delay_years",
                size="value_usd_millions",
                color_discrete_sequence=["#00b4d8"],
                title="Aprobaciones Vs Ejecución (Filtrado)",
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "completion_delay_years": "Atraso (años)",
                    "value_usd_millions": "Value (Millones USD)"
                }
            )
            fig_sc1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_sc1, use_container_width=True)

    with colB:
        st.subheader("Planificación Vs Ejecución")
        need_scatter2 = {"duracion_estimada", "duracion_real"}
        if not need_scatter2.issubset(df_filters.columns):
            st.warning(f"No están todas las columnas {need_scatter2} para el segundo scatter.")
        else:
            df_sc2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ].copy()
            fig_sc2 = px.scatter(
                df_sc2,
                x="duracion_estimada",
                y="duracion_real",
                color_discrete_sequence=["#00b4d8"],
                title="Planificación Vs Ejecución (Filtrado)",
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "duracion_real": "Duración Real (años)"
                }
            )
            # Línea punteada blanca (45°)
            if not df_sc2.empty:
                max_rango = max(df_sc2["duracion_estimada"].max(), df_sc2["duracion_real"].max())
                fig_sc2.add_shape(
                    type="line",
                    x0=0,
                    y0=0,
                    x1=max_rango,
                    y1=max_rango,
                    line=dict(color="white", dash="dot")
                )
            fig_sc2.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_sc2, use_container_width=True)

    # -------------------------------------------------------------------------
    # 2) TABS PRINCIPALES: MODALIDAD, SECTOR, PAISES
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Box Plots (sin filtros de arriba)")

    df_box = DATASETS["ACTIVITY_IADB"].copy()  # sin filtros

    tab_modalidad, tab_sector, tab_paises = st.tabs(["Modalidad", "Sector", "Países"])

    # ===========================  TAB MODALIDAD  ==============================
    with tab_modalidad:
        st.subheader("Box Plots - Modalidad (Global)")
        boxplot_modalidad(df_box, titulo_extra="(Global)")

    # ===========================  TAB SECTOR  ==============================
    with tab_sector:
        st.subheader("Box Plots - Sector (Global)")
        boxplot_sector(df_box, titulo_extra="(Global)")

    # ===========================  TAB PAISES  ==============================
    with tab_paises:
        st.subheader("Box Plots - Países")

        # Definimos sub-pestañas: Argentina, Bolivia, Brazil, Paraguay, Uruguay, 5-FP
        countries = {
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

        sub_tabs = st.tabs(list(countries.keys()))

        for i, (pais_tab, pais_list) in enumerate(countries.items()):
            with sub_tabs[i]:
                st.write(f"**País(es):** {pais_list}")

                # Filtrar df_box por el/los país(es)
                df_country = df_box[
                    df_box["recipientcountry_codename"].isin(pais_list)
                ].copy()

                # 1) Box Plots de Modalidad
                st.markdown("#### Modalidad")
                boxplot_modalidad(df_country, titulo_extra=f"({pais_tab})")

                # 2) Box Plots de Sector
                st.markdown("#### Sector")
                boxplot_sector(df_country, titulo_extra=f"({pais_tab})")

# -----------------------------------------------------------------------------
# OTRAS PÁGINAS (PLACEHOLDER)
# -----------------------------------------------------------------------------
def series_temporales():
    st.markdown('<h1 class="title">Series Temporales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora la evolución de los datos a lo largo del tiempo.</p>', unsafe_allow_html=True)

def analisis_geoespacial():
    st.markdown('<h1 class="title">Análisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza datos en el mapa, distribuciones geográficas, etc.</p>', unsafe_allow_html=True)

def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis de relaciones entre variables, correlaciones, PCA, clustering, etc.</p>', unsafe_allow_html=True)

def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Entrena y evalúa modelos predictivos o de clasificación.</p>', unsafe_allow_html=True)

def analisis_exploratorio():
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker (alto rendimiento).</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar")
    ds = st.sidebar.selectbox("Base de datos:", list(DATASETS.keys()))
    renderer = get_pyg_renderer_by_name(ds)
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
    choice = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()), index=0)
    PAGINAS[choice]()

# -----------------------------------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
