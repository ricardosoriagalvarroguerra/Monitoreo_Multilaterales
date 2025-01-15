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
    df_activity = pd.read_parquet("activity_iadb.parquet")  # Ajusta la ruta
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
    from pygwalker.api.streamlit import StreamlitRenderer
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(df, kernel_computation=True)
    return renderer

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES: BOX PLOTS
# -----------------------------------------------------------------------------
def boxplot_modalidad(df: pd.DataFrame, titulo_extra: str = ""):
    """
    Muestra dos box plots:
      - X='modalidad_general', Y='duracion_estimada'
      - X='modalidad_general', Y='completion_delay_years'
    """
    needed_cols_m1 = {"modalidad_general", "duracion_estimada"}
    needed_cols_m2 = {"modalidad_general", "completion_delay_years"}

    # Box Plot 1 (duracion_estimada)
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

    # Box Plot 2 (completion_delay_years)
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
    Muestra dos box plots:
      - X='Sector_1', Y='duracion_estimada'
      - X='Sector_1', Y='completion_delay_years'
    """
    needed_cols_s1 = {"Sector_1", "duracion_estimada"}
    needed_cols_s2 = {"Sector_1", "completion_delay_years"}

    # Box Plot 1: duracion_estimada
    if not needed_cols_s1.issubset(df.columns):
        st.warning(f"Faltan columnas para Sector (duracion_estimada): {needed_cols_s1 - set(df.columns)}")
    else:
        df_s1 = df[
            df["Sector_1"].notna() & df["duracion_estimada"].notna()
        ].copy()

        fig_s1 = px.box(
            df_s1,
            x="Sector_1",
            y="duracion_estimada",
            color_discrete_sequence=["#ef233c"],
            title=f"Distribución de Duración Estimada {titulo_extra} (Sector)",
            labels={
                "Sector_1": "Sector_1",
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

    # Box Plot 2: completion_delay_years
    if not needed_cols_s2.issubset(df.columns):
        st.warning(f"Faltan columnas para Sector (completion_delay_years): {needed_cols_s2 - set(df.columns)}")
    else:
        df_s2 = df[
            df["Sector_1"].notna() & df["completion_delay_years"].notna()
        ].copy()

        fig_s2 = px.box(
            df_s2,
            x="Sector_1",
            y="completion_delay_years",
            color_discrete_sequence=["#edf2f4"],
            title=f"Distribución de Atraso en Finalización {titulo_extra} (Sector)",
            labels={
                "Sector_1": "Sector_1",
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


def boxplot_montos(df: pd.DataFrame, titulo_extra: str = ""):
    """
    Nueva pestaña "Montos": 
      - Box Plot 1 (Top 6 Sector_1 en base a value_usd): 
          X='Sector_1', Y='value_usd_millions'
      - Box Plot 2 (todas las modalidades): 
          X='modalidad_general', Y='value_usd_millions'
    """
    st.subheader(f"Box Plots de Montos {titulo_extra}")

    # Primero creamos una columna con 'value_usd_millions' si no existe
    if "value_usd" in df.columns:
        df["value_usd_millions"] = df["value_usd"] / 1_000_000
    else:
        st.warning("No existe la columna 'value_usd' en el dataset.")
        return

    # ============= BOX PLOT 1: TOP 6 SECTOR_1 por 'value_usd_millions' =============
    needed_cols_s = {"Sector_1", "value_usd_millions"}
    if not needed_cols_s.issubset(df.columns):
        st.warning(f"Faltan columnas para Montos (Sector_1, value_usd_millions).")
    else:
        df_s = df[
            df["Sector_1"].notna() &
            df["value_usd_millions"].notna()
        ].copy()

        # Determinar Top 6
        df_agrupado = (
            df_s.groupby("Sector_1", as_index=False)["value_usd_millions"]
            .sum()
            .sort_values("value_usd_millions", ascending=False)
        )
        top_sectores = df_agrupado["Sector_1"].head(6).tolist()

        # Filtrar a top 6
        df_top6 = df_s[df_s["Sector_1"].isin(top_sectores)]

        fig_m1 = px.box(
            df_top6,
            x="Sector_1",
            y="value_usd_millions",
            color_discrete_sequence=["#ef233c"],
            title="Montos (Millones) por Sector_1 (Top 6)",
            labels={
                "Sector_1": "Top 6 Sectores",
                "value_usd_millions": "Value (Millones USD)"
            },
             points=False  # <--- OCULTAR outliers
        )
        fig_m1.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_m1, use_container_width=True)

    # ============= BOX PLOT 2: MODALIDAD_GENERAL vs 'value_usd_millions' =============
    needed_cols_m = {"modalidad_general", "value_usd_millions"}
    if not needed_cols_m.issubset(df.columns):
        st.warning("Faltan columnas para Montos (modalidad_general, value_usd_millions).")
    else:
        df_m = df[
            df["modalidad_general"].notna() &
            df["value_usd_millions"].notna()
        ].copy()

        fig_m2 = px.box(
            df_m,
            x="modalidad_general",
            y="value_usd_millions",
            color_discrete_sequence=["#edf2f4"],
            title="Montos (Millones) por Modalidad (todas las modalidades)",
            labels={
                "modalidad_general": "Modalidad General",
                "value_usd_millions": "Value (Millones USD)"
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

# -----------------------------------------------------------------------------
# SUBPÁGINAS DE DESCRIPTIVO
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    """Subpágina 'Ejecución' con scatter plots y box plots."""
    st.markdown('<p class="subtitle">Subpágina: Ejecución</p>', unsafe_allow_html=True)

    st.write("Aquí se muestran **scatter plots** con filtros y los **box plots** (Modalidad, Sector, Montos).")

    # =========================================================================
    # 1) SCATTER PLOTS (con filtros)
    # =========================================================================
    df_filters = DATASETS["ACTIVITY_IADB"].copy()

    st.sidebar.subheader("Filtros (Ejecución)")

    # Filtro Sector_1
    if "Sector_1" in df_filters.columns:
        list_sectores = sorted(df_filters["Sector_1"].dropna().unique().tolist())
        opciones_sector = ["General"] + list_sectores
        sel_sector = st.sidebar.selectbox("Sector_1:", opciones_sector, index=0)
        if sel_sector != "General":
            df_filters = df_filters[df_filters["Sector_1"] == sel_sector]

    # Filtro activityscope_codename
    if "activityscope_codename" in df_filters.columns:
        list_scopes = sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        opciones_scope = ["General"] + list_scopes
        sel_scope = st.sidebar.selectbox("activityscope_codename:", opciones_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # Filtro value_usd -> slider en millones
    if "value_usd" in df_filters.columns:
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000
        min_val = float(df_filters["value_usd_millions"].min())
        max_val = float(df_filters["value_usd_millions"].max())
        st.sidebar.write("Filtrar por Value (Millones USD):")
        rango_slider = st.sidebar.slider(
            "Rango de montos (Millones)",
            min_val,
            max_val,
            (min_val, max_val),
            step=(max_val - min_val)/100 if (max_val - min_val) > 0 else 1
        )
        df_filters = df_filters[
            (df_filters["value_usd_millions"] >= rango_slider[0]) &
            (df_filters["value_usd_millions"] <= rango_slider[1])
        ]
    else:
        df_filters["value_usd_millions"] = None

    # SCATTER PLOTS
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Aprobaciones Vs Ejecución")
        need_cols_1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if need_cols_1.issubset(df_filters.columns):
            df_scat1 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["completion_delay_years"].notna() &
                df_filters["value_usd_millions"].notna()
            ]
            fig1 = px.scatter(
                df_scat1,
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
            fig1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning(f"No existen todas las columnas {need_cols_1} para el primer scatter plot.")

    with colB:
        st.subheader("Planificación Vs Ejecución")
        need_cols_2 = {"duracion_estimada", "duracion_real"}
        if need_cols_2.issubset(df_filters.columns):
            df_scat2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ]
            fig2 = px.scatter(
                df_scat2,
                x="duracion_estimada",
                y="duracion_real",
                color_discrete_sequence=["#00b4d8"],
                title="Planificación Vs Ejecución (Filtrado)",
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "duracion_real": "Duración Real (años)"
                }
            )
            if not df_scat2.empty:
                mx = max(df_scat2["duracion_estimada"].max(), df_scat2["duracion_real"].max())
                fig2.add_shape(
                    type="line",
                    x0=0,
                    y0=0,
                    x1=mx,
                    y1=mx,
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
        else:
            st.warning(f"No existen todas las columnas {need_cols_2} para el segundo scatter plot.")

    # =========================================================================
    # BOX PLOTS (Global, sin filtros)
    # =========================================================================
    st.markdown("---")
    st.markdown("### Box Plots (Modalidad, Sector, Montos) - Global")

    df_box = DATASETS["ACTIVITY_IADB"].copy()

    tab_mod, tab_sec, tab_montos = st.tabs(["Modalidad", "Sector", "Montos"])

    with tab_mod:
        st.subheader("Box Plots - Modalidad (Global)")
        boxplot_modalidad(df_box, titulo_extra="(Global)")

    with tab_sec:
        st.subheader("Box Plots - Sector (Global)")
        boxplot_sector(df_box, titulo_extra="(Global)")

    with tab_montos:
        st.subheader("Box Plots - Montos (Global)")
        boxplot_montos(df_box, titulo_extra="(Global)")


def subpagina_flujos_agregados():
    """Subpágina 'Flujos Agregados'."""
    st.markdown('<p class="subtitle">Subpágina: Flujos Agregados</p>', unsafe_allow_html=True)
    st.write("Aquí podrías mostrar métricas o gráficos de flujos totales, aprobaciones vs desembolsos, etc.")
    st.info("Placeholder: Implementa la lógica que desees para Flujos Agregados.")

# -----------------------------------------------------------------------------
# PÁGINA PRINCIPAL: DESCRIPTIVO
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)

    # En la barra lateral agregamos la selección de subpáginas
    st.sidebar.title("Subpáginas de Descriptivo")
    subpaginas = ["Ejecución", "Flujos Agregados"]
    eleccion_sub = st.sidebar.radio("Elige una subpágina:", subpaginas, index=0)

    if eleccion_sub == "Ejecución":
        subpagina_ejecucion()
    else:
        subpagina_flujos_agregados()

# -----------------------------------------------------------------------------
# OTRAS PÁGINAS (PLACEHOLDERS)
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
# MENÚ PRINCIPAL (PÁGINAS)
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
    pagina = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()), index=0)
    PAGINAS[pagina]()

# -----------------------------------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
