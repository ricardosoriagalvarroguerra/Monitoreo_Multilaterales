import streamlit as st
import pandas as pd
import plotly.express as px
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random
from datetime import datetime

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
    Ajusta la ruta/parquet si es necesario.
    """
    df_activity = pd.read_parquet("activity_iadb.parquet")  
    df_outgoing = pd.read_parquet("outgoing_commitment_iadb.parquet")
    df_disb = pd.read_parquet("disbursements_data.parquet")

    datasets = {
        "ACTIVITY_IADB": df_activity,
        "OUTGOING_COMMITMENT_IADB": df_outgoing,
        "DISBURSEMENTS_DATA": df_disb
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
    needed_cols_1 = {"modalidad_general", "duracion_estimada"}
    needed_cols_2 = {"modalidad_general", "completion_delay_years"}

    # Box Plot 1: Duración Estimada
    if not needed_cols_1.issubset(df.columns):
        st.warning(f"Faltan columnas para Modalidad (Duración Estimada): {needed_cols_1 - set(df.columns)}")
    else:
        df_m1 = df[df["modalidad_general"].notna() & df["duracion_estimada"].notna()].copy()

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

    # Box Plot 2: Completion Delay
    if not needed_cols_2.issubset(df.columns):
        st.warning(f"Faltan columnas para Modalidad (Completion Delay): {needed_cols_2 - set(df.columns)}")
    else:
        df_m2 = df[df["modalidad_general"].notna() & df["completion_delay_years"].notna()].copy()

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
    Muestra dos box plots con Top 6 Sectores (en base a 'value_usd'):
      - X='Sector_1', Y='duracion_estimada'
      - X='Sector_1', Y='completion_delay_years'
    """
    if "value_usd" not in df.columns:
        st.warning("No existe la columna 'value_usd' para calcular top 6 sectores.")
        return

    needed_cols_1 = {"Sector_1", "duracion_estimada"}
    needed_cols_2 = {"Sector_1", "completion_delay_years"}

    # Determinar Top 6 Sectores
    df_s = df[df["Sector_1"].notna() & df["value_usd"].notna()].copy()
    agrupado = (
        df_s.groupby("Sector_1", as_index=False)["value_usd"]
        .sum()
        .sort_values("value_usd", ascending=False)
    )
    top_6_sectores = agrupado["Sector_1"].head(6).tolist()

    # Filtramos a top 6
    df_top6 = df[df["Sector_1"].isin(top_6_sectores)].copy()

    # Box Plot 1: Duración Estimada
    if not needed_cols_1.issubset(df_top6.columns):
        st.warning(f"Faltan columnas para Sector (duracion_estimada): {needed_cols_1 - set(df_top6.columns)}")
    else:
        df_s1 = df_top6[df_top6["duracion_estimada"].notna()]

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

    # Box Plot 2: Completion Delay
    if not needed_cols_2.issubset(df_top6.columns):
        st.warning(f"Faltan columnas para Sector (completion_delay_years): {needed_cols_2 - set(df_top6.columns)}")
    else:
        df_s2 = df_top6[df_top6["completion_delay_years"].notna()]

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
# SUBPÁGINA: EJECUCIÓN
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    """
    Subpágina 'Ejecución' con:
      - Filtros (Sector_1, activityscope_codename)
      - Scatter plots: 
         * "Aprobaciones Vs Ejecución" -> size de puntos en base a value_usd_millions
         * "Planificación Vs Ejecución"
      - Box plots: Modalidad, Sector (Top 6)
    """
    st.markdown('<p class="subtitle">Subpágina: Ejecución</p>', unsafe_allow_html=True)

    # 1) FILTROS
    df_filters = DATASETS["ACTIVITY_IADB"].copy()
    st.sidebar.subheader("Filtros (Ejecución)")

    # Filtro 1: Sector_1
    if "Sector_1" in df_filters.columns:
        lista_sectores = sorted(df_filters["Sector_1"].dropna().unique().tolist())
        opciones_sector = ["General"] + lista_sectores
        sel_sector = st.sidebar.selectbox("Sector_1:", opciones_sector, index=0)
        if sel_sector != "General":
            df_filters = df_filters[df_filters["Sector_1"] == sel_sector]

    # Filtro 2: activityscope_codename
    if "activityscope_codename" in df_filters.columns:
        lista_scopes = sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        opciones_scope = ["General"] + lista_scopes
        sel_scope = st.sidebar.selectbox("activityscope_codename:", opciones_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # 2) Generar la columna value_usd_millions (para size en scatter)
    if "value_usd" in df_filters.columns:
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000
    else:
        df_filters["value_usd_millions"] = None

    # 3) SCATTER PLOTS
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Aprobaciones Vs Ejecución")
        needed_cols_1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if needed_cols_1.issubset(df_filters.columns):
            df_scat1 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["completion_delay_years"].notna() &
                df_filters["value_usd_millions"].notna()
            ].copy()

            if df_scat1.empty:
                st.warning("No hay datos disponibles para mostrar en 'Aprobaciones Vs Ejecución' después de aplicar los filtros.")
            else:
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
            missing = needed_cols_1 - set(df_filters.columns)
            st.warning(f"No existen todas las columnas para el primer scatter plot: {missing}")

    with colB:
        st.subheader("Planificación Vs Ejecución")
        needed_cols_2 = {"duracion_estimada", "duracion_real"}
        if needed_cols_2.issubset(df_filters.columns):
            df_scat2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ].copy()

            if df_scat2.empty:
                st.warning("No hay datos disponibles para mostrar en 'Planificación Vs Ejecución' después de aplicar los filtros.")
            else:
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
                # Línea punteada blanca (45°)
                max_val = max(df_scat2["duracion_estimada"].max(), df_scat2["duracion_real"].max())
                fig2.add_shape(
                    type="line",
                    x0=0,
                    y0=0,
                    x1=max_val,
                    y1=max_val,
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
            missing = needed_cols_2 - set(df_filters.columns)
            st.warning(f"No existen todas las columnas para el segundo scatter plot: {missing}")

    # 4) BOX PLOTS (Modalidad, Sector) - usando el mismo DF filtrado
    st.markdown("---")
    st.markdown("### Box Plots (Modalidad, Sector) - Filtrados")

    df_box = df_filters.copy()

    tab_mod, tab_sec = st.tabs(["Modalidad", "Sector"])

    with tab_mod:
        st.subheader("Box Plots - Modalidad (Filtrado)")
        boxplot_modalidad(df_box, titulo_extra="(Filtrado)")

    with tab_sec:
        st.subheader("Box Plots - Sector (Filtrado, Top 6)")
        boxplot_sector(df_box, titulo_extra="(Filtrado)")


# -----------------------------------------------------------------------------
# SUBPÁGINA: FLUJOS AGREGADOS (MÁS FILTROS + OPCIÓN FECHAS/SECTORES)
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    """
    Subpágina: Flujos Agregados
      - Filtro de Region -> País (recipientcountry_codename)
      - Filtro de modality_general
      - Filtro de años
      - Frecuencia (Trimestral, Semestral, Anual)
      - Opción "Ver por": [Fechas | Sectores]
        * Fechas -> barras por periodo
        * Sectores -> barras por Sector_1
    """
    st.markdown('<p class="subtitle">Subpágina: Flujos Agregados</p>', unsafe_allow_html=True)

    # 1) Cargamos DataFrame (Aprobaciones)
    df = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"])

    st.sidebar.subheader("Filtros (Flujos Agregados)")

    # A) Filtro de Región (asumiendo la columna se llama "region")
    if "region" in df.columns:
        lista_regiones = sorted(df["region"].dropna().unique().tolist())
        opciones_regiones = ["Todas"] + lista_regiones
        sel_region = st.sidebar.selectbox("Región:", opciones_regiones, index=0)
        if sel_region != "Todas":
            df = df[df["region"] == sel_region]

    # B) Filtro de País (recipientcountry_codename) -> Sólo los del DF ya filtrado
    if "recipientcountry_codename" in df.columns:
        lista_paises = sorted(df["recipientcountry_codename"].dropna().unique().tolist())
        opciones_paises = ["Todos"] + lista_paises
        sel_pais = st.sidebar.selectbox("País:", opciones_paises, index=0)
        if sel_pais != "Todos":
            df = df[df["recipientcountry_codename"] == sel_pais]

    # C) Filtro de modality_general
    if "modality_general" in df.columns:
        lista_mods = sorted(df["modality_general"].dropna().unique().tolist())
        opciones_mods = ["Todas"] + lista_mods
        sel_mod = st.sidebar.selectbox("Modalidad:", opciones_mods, index=0)
        if sel_mod != "Todas":
            df = df[df["modality_general"] == sel_mod]

    # D) Filtro de Años (slider)
    min_year = df["transactiondate_isodate"].dt.year.min()
    max_year = df["transactiondate_isodate"].dt.year.max()

    start_year, end_year = st.sidebar.slider(
        "Rango de años:",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year)),
        step=1
    )

    start_ts = pd.to_datetime(datetime(start_year, 1, 1))
    end_ts = pd.to_datetime(datetime(end_year, 12, 31))

    df = df[
        (df["transactiondate_isodate"] >= start_ts) &
        (df["transactiondate_isodate"] <= end_ts)
    ].copy()

    # E) Frecuencia (Trimestral, Semestral, Anual)
    freq_opciones = ["Trimestral", "Semestral", "Anual"]
    st.markdown("**Frecuencia**")
    freq_choice = st.selectbox(
        "", 
        freq_opciones, 
        index=2,  # Por defecto "Anual"
        label_visibility="collapsed"
    )

    if freq_choice == "Trimestral":
        freq_code = "Q"
    elif freq_choice == "Semestral":
        freq_code = "6M"
    else:
        freq_code = "A"

    # 2) Opción "Ver por": Fechas o Sectores
    vista_opciones = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vista_opciones, horizontal=True)

    # 3) Logica de Graficación
    if df.empty:
        st.warning("No hay datos disponibles con los filtros seleccionados.")
        return

    # Convertir 'value_usd' a millones
    df["value_usd_millions"] = df["value_usd"] / 1_000_000

    if vista == "Fechas":
        # a) Re-sample por freq_code
        df.set_index("transactiondate_isodate", inplace=True)
        df_agg = df["value_usd"].resample(freq_code).sum().reset_index()
        df_agg["value_usd_millions"] = df_agg["value_usd"] / 1_000_000

        # Creamos una columna "Periodo" para el eje X
        if freq_choice == "Trimestral":
            df_agg["Periodo"] = (
                df_agg["transactiondate_isodate"].dt.year.astype(str) + 
                "T" + 
                df_agg["transactiondate_isodate"].dt.quarter.astype(str)
            )
            x_label = "Trimestre"
        elif freq_choice == "Semestral":
            semester = (df_agg["transactiondate_isodate"].dt.month.sub(1)//6).add(1)
            df_agg["Periodo"] = (
                df_agg["transactiondate_isodate"].dt.year.astype(str) + 
                "S" + 
                semester.astype(str)
            )
            x_label = "Semestre"
        else:  # Anual
            df_agg["Periodo"] = df_agg["transactiondate_isodate"].dt.year.astype(str)
            x_label = "Año"

        st.subheader("Aprobaciones (por Frecuencia)")

        if df_agg.empty:
            st.warning("No hay datos de Aprobaciones en el rango de años seleccionado.")
        else:
            fig_time = px.bar(
                df_agg,
                x="Periodo",
                y="value_usd_millions",
                color_discrete_sequence=["#d90429"],
                labels={
                    "Periodo": x_label,
                    "value_usd_millions": "Monto (Millones USD)"
                },
                title=""
            )
            fig_time.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_time, use_container_width=True)

    else:  # vista == "Sectores"
        # b) Agrupamos por Sector_1
        if "Sector_1" not in df.columns:
            st.warning("No existe la columna 'Sector_1' para agrupar por sector.")
            return

        # Agrupación por Sector
        df_agg_sec = (
            df.groupby("Sector_1", as_index=False)["value_usd_millions"]
            .sum()
            .sort_values("value_usd_millions", ascending=False)
        )

        st.subheader("Aprobaciones (agrupadas por Sector)")

        if df_agg_sec.empty:
            st.warning("No hay datos de Aprobaciones en los filtros seleccionados.")
        else:
            fig_sector = px.bar(
                df_agg_sec,
                x="Sector_1",
                y="value_usd_millions",
                color_discrete_sequence=["#d90429"],
                labels={
                    "Sector_1": "Sector",
                    "value_usd_millions": "Monto (Millones USD)"
                },
                title=""
            )
            fig_sector.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_sector, use_container_width=True)

    st.info("Flujos agregados: Aprobaciones (Outgoing Commitments).")


# -----------------------------------------------------------------------------
# PÁGINA "Descriptivo" (Dos SUBPÁGINAS)
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)

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
    st.markdown('<p class="subtitle">Explora la evolución de los datos a lo largo del tiempo (Placeholder).</p>', unsafe_allow_html=True)

def analisis_geoespacial():
    st.markdown('<h1 class="title">Análisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza datos en el mapa, distribuciones geográficas, etc. (Placeholder)</p>', unsafe_allow_html=True)

def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis de relaciones entre variables, correlaciones, PCA, clustering, etc. (Placeholder)</p>', unsafe_allow_html=True)

def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Entrena y evalúa modelos predictivos o de clasificación (Placeholder).</p>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA "Análisis Exploratorio" (PyGWalker)
# -----------------------------------------------------------------------------
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
