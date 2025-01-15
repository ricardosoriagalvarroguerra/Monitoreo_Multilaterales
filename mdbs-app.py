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
# FUNCIONES AUXILIARES (BOX PLOTS)
# -----------------------------------------------------------------------------
def boxplot_modalidad(df: pd.DataFrame, titulo_extra: str = ""):
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

    # 1) Box Plot (duracion_estimada)
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

    # 2) Box Plot (completion_delay_years)
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
# SUBPÁGINA 1: EJECUCIÓN
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    st.markdown('<p class="subtitle">Vista de Ejecución</p>', unsafe_allow_html=True)

    st.write("En esta subpágina, mostramos los **scatter plots** con filtros y **box plots** (Modalidad, Sector, Países).")

    # =========================================================================
    # SCATTER PLOTS (con filtros)
    # =========================================================================
    df_filters = DATASETS["ACTIVITY_IADB"].copy()

    # Filtros en barra lateral
    st.sidebar.subheader("Filtros (Ejecución)")
    if "Sector_1" in df_filters.columns:
        opciones_sector = ["General"] + sorted(df_filters["Sector_1"].dropna().unique().tolist())
        sel_sector = st.sidebar.selectbox("Sector_1 (Ejecución)", opciones_sector, index=0)
        if sel_sector != "General":
            df_filters = df_filters[df_filters["Sector_1"] == sel_sector]

    if "activityscope_codename" in df_filters.columns:
        opciones_scope = ["General"] + sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        sel_scope = st.sidebar.selectbox("activityscope_codename (Ejecución)", opciones_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # Convertir a millones
    if "value_usd" in df_filters.columns:
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000
    else:
        df_filters["value_usd_millions"] = None

    # Scatter 1
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Aprobaciones Vs Ejecución")
        needed_scat1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if needed_scat1.issubset(df_filters.columns):
            df_scat1 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["completion_delay_years"].notna() &
                df_filters["value_usd_millions"].notna()
            ].copy()
            fig_sc1 = px.scatter(
                df_scat1,
                x="duracion_estimada",
                y="completion_delay_years",
                size="value_usd_millions",
                color_discrete_sequence=["#00b4d8"],
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "completion_delay_years": "Atraso (años)",
                    "value_usd_millions": "Value (Millones USD)"
                },
                title="Aprobaciones Vs Ejecución (Filtrado)"
            )
            fig_sc1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_sc1, use_container_width=True)
        else:
            st.warning(f"No se tienen todas las columnas para Scatter 1: {needed_scat1 - set(df_filters.columns)}")

    # Scatter 2
    with colB:
        st.subheader("Planificación Vs Ejecución")
        needed_scat2 = {"duracion_estimada", "duracion_real"}
        if needed_scat2.issubset(df_filters.columns):
            df_scat2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ].copy()
            fig_sc2 = px.scatter(
                df_scat2,
                x="duracion_estimada",
                y="duracion_real",
                color_discrete_sequence=["#00b4d8"],
                labels={
                    "duracion_estimada": "Duración Estimada (años)",
                    "duracion_real": "Duración Real (años)"
                },
                title="Planificación Vs Ejecución (Filtrado)"
            )
            # Línea punteada
            if not df_scat2.empty:
                max_val = max(df_scat2["duracion_estimada"].max(), df_scat2["duracion_real"].max())
                fig_sc2.add_shape(
                    type="line",
                    x0=0,
                    y0=0,
                    x1=max_val,
                    y1=max_val,
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
        else:
            st.warning(f"No se tienen todas las columnas para Scatter 2: {needed_scat2 - set(df_filters.columns)}")

    # =========================================================================
    # BOX PLOTS (Global, sin filtros)
    # =========================================================================
    st.markdown("---")
    st.markdown("### Box Plots (Modalidad, Sector, Países)")

    df_box = DATASETS["ACTIVITY_IADB"].copy()  # sin filtros

    # Definimos 3 tabs: "Modalidad", "Sector", "Países"
    tab_mod, tab_sec, tab_pais = st.tabs(["Modalidad", "Sector", "Países"])

    # 1) MODALIDAD
    with tab_mod:
        st.subheader("Box Plots - Modalidad (Global)")
        boxplot_modalidad(df_box, titulo_extra="(Global)")

    # 2) SECTOR
    with tab_sec:
        st.subheader("Box Plots - Sector (Global)")
        boxplot_sector(df_box, titulo_extra="(Global)")

    # 3) PAISES
    with tab_pais:
        st.subheader("Box Plots - Países (Subtabs)")

        # Subtabs: Arg, Bolivia, Brazil, Paraguay, Uruguay, 5-FP
        countries = {
            "Argentina": ["Argentina"],
            "Bolivia": ["Bolivia (Plurinational State of)"],
            "Brazil": ["Brazil"],
            "Paraguay": ["Paraguay"],
            "Uruguay": ["Uruguay"],
            "5-FP": [
                "Argentina", "Bolivia (Plurinational State of)",
                "Brazil", "Paraguay", "Uruguay"
            ]
        }
        sub_tabs = st.tabs(list(countries.keys()))

        for i, (pais_tab, pais_list) in enumerate(countries.items()):
            with sub_tabs[i]:
                st.write(f"**País(es)**: {pais_list}")
                df_pais = df_box[
                    df_box["recipientcountry_codename"].isin(pais_list)
                ].copy()
                # Modalidad
                st.markdown("#### Modalidad")
                boxplot_modalidad(df_pais, titulo_extra=f"({pais_tab})")

                # Sector
                st.markdown("#### Sector")
                boxplot_sector(df_pais, titulo_extra=f"({pais_tab})")


# -----------------------------------------------------------------------------
# SUBPÁGINA 2: FLUJOS AGREGADOS
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    st.markdown('<p class="subtitle">Flujos Agregados</p>', unsafe_allow_html=True)
    st.write("Aquí podrías mostrar gráficos de montos totales, líneas de tiempo de desembolsos, etc.")
    st.write("**Ejemplo placeholder**: Aún no implementado, personaliza según tus datos de flujos.")

# -----------------------------------------------------------------------------
# PÁGINA PRINCIPAL: DESCRIPTIVO (CON 2 SUBPÁGINAS)
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)

    # Añadimos un selectbox/radio en la barra lateral (o en el main) para subpáginas
    # Aquí se elige en la parte principal para ejemplificar.
    subpaginas = ["Ejecución", "Flujos Agregados"]
    eleccion_sub = st.radio("Selecciona subpágina de Descriptivo:", subpaginas, index=0)

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
# DICCIONARIO DE PÁGINAS (MENÚ PRINCIPAL)
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
