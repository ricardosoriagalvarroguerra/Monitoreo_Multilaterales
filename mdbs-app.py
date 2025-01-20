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
# CONFIGURACIÓN DE PÁGINA Y CSS (MODO OSCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Mi Aplicación - Modo Oscuro",
    page_icon="✅",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #1E1E1E;
    }
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
    [data-testid="stSidebar"] {
        background-color: #2A2A2A;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span {
        color: #EEEEEE;
    }
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
# 2. PYGWALKER (CACHÉ)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str):
    from pygwalker.api.streamlit import StreamlitRenderer
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(df, kernel_computation=True)
    return renderer

# -----------------------------------------------------------------------------
# AUX: BOX PLOTS
# -----------------------------------------------------------------------------
def boxplot_modalidad(df: pd.DataFrame, titulo_extra: str = ""):
    needed_cols_1 = {"modalidad_general", "duracion_estimada"}
    needed_cols_2 = {"modalidad_general", "completion_delay_years"}

    if needed_cols_1.issubset(df.columns):
        df1 = df[df["modalidad_general"].notna() & df["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="modalidad_general",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title=f"Distribución de Duración {titulo_extra} (Modalidad)",
                labels={
                    "modalidad_general": "Modalidad General",
                    "duracion_estimada": "Duración (años)"
                }
            )
            fig1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig1, use_container_width=True)

    if needed_cols_2.issubset(df.columns):
        df2 = df[df["modalidad_general"].notna() & df["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="modalidad_general",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title=f"Distribución de Atraso {titulo_extra} (Modalidad)",
                labels={
                    "modalidad_general": "Modalidad General",
                    "completion_delay_years": "Atraso (años)"
                }
            )
            fig2.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)

def boxplot_sector(df: pd.DataFrame, titulo_extra: str = ""):
    if "value_usd" not in df.columns:
        st.warning("No existe 'value_usd' para calcular top 6 sectores.")
        return

    needed_cols_1 = {"Sector", "duracion_estimada"}
    needed_cols_2 = {"Sector", "completion_delay_years"}

    df_s = df[df["Sector"].notna() & df["value_usd"].notna()]
    if df_s.empty:
        st.warning("No hay datos para Top 6 sectores.")
        return

    sum_sec = (
        df_s.groupby("Sector", as_index=False)["value_usd"]
        .sum()
        .sort_values("value_usd", ascending=False)
    )
    top_6_list = sum_sec["Sector"].head(6).tolist()

    df_top = df[df["Sector"].isin(top_6_list)].copy()
    if df_top.empty:
        st.warning("No hay datos en Top 6 sectores.")
        return

    if needed_cols_1.issubset(df_top.columns):
        df1 = df_top[df_top["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="Sector",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title=f"Distribución Duración {titulo_extra} (Top 6 Sectores)",
                labels={
                    "Sector": "Sector (Top 6)",
                    "duracion_estimada": "Duración (años)"
                }
            )
            fig1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig1, use_container_width=True)

    if needed_cols_2.issubset(df_top.columns):
        df2 = df_top[df_top["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="Sector",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title=f"Distribución Atraso {titulo_extra} (Top 6 Sectores)",
                labels={
                    "Sector": "Sector (Top 6)",
                    "completion_delay_years": "Atraso (años)"
                }
            )
            fig2.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# SUBPÁGINA: EJECUCIÓN
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    st.markdown('<p class="subtitle">Subpágina: Ejecución</p>', unsafe_allow_html=True)

    df_filters = DATASETS["ACTIVITY_IADB"].copy()
    st.sidebar.subheader("Filtros (Ejecución)")

    # Filtro Sector
    if "Sector" in df_filters.columns:
        list_sec = sorted(df_filters["Sector"].dropna().unique().tolist())
        opt_sec = ["General"] + list_sec
        sel_sec = st.sidebar.selectbox("Sector:", opt_sec, index=0)
        if sel_sec != "General":
            df_filters = df_filters[df_filters["Sector"] == sel_sec]

    # Filtro activityscope_codename
    if "activityscope_codename" in df_filters.columns:
        list_scope = sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        opt_scope = ["General"] + list_scope
        sel_scope = st.sidebar.selectbox("activityscope_codename:", opt_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # Filtro Modalidad
    if "modality_general" in df_filters.columns:
        list_mod = sorted(df_filters["modality_general"].dropna().unique().tolist())
        opt_mod = ["Todas"] + list_mod
        sel_mod = st.sidebar.selectbox("Modalidad:", opt_mod, index=0)
        if sel_mod != "Todas":
            df_filters = df_filters[df_filters["modality_general"] == sel_mod]

    # value_usd_millions
    if "value_usd" in df_filters.columns:
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000
    else:
        df_filters["value_usd_millions"] = None

    # SCATTER
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Aprobaciones Vs Ejecución")
        needed_1 = {"duracion_estimada", "completion_delay_years", "value_usd_millions"}
        if needed_1.issubset(df_filters.columns):
            df_scat1 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["completion_delay_years"].notna() &
                df_filters["value_usd_millions"].notna()
            ]
            if df_scat1.empty:
                st.warning("No hay datos disponibles en 'Aprobaciones Vs Ejecución'.")
            else:
                fig1 = px.scatter(
                    df_scat1,
                    x="duracion_estimada",
                    y="completion_delay_years",
                    size="value_usd_millions",
                    color_discrete_sequence=["#00b4d8"],
                    title="Aprobaciones Vs Ejecución (Filtrado)",
                    labels={
                        "duracion_estimada": "Duración Est. (años)",
                        "completion_delay_years": "Atraso (años)",
                        "value_usd_millions": "Value (Millones USD)"
                    }
                )
                fig1.update_layout(
                    font_color="#FFFFFF",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning(f"Faltan columnas: {needed_1 - set(df_filters.columns)}")

    with colB:
        st.subheader("Planificación Vs Ejecución")
        needed_2 = {"duracion_estimada", "duracion_real"}
        if needed_2.issubset(df_filters.columns):
            df_scat2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ]
            if df_scat2.empty:
                st.warning("No hay datos disponibles en 'Planificación Vs Ejecución'.")
            else:
                fig2 = px.scatter(
                    df_scat2,
                    x="duracion_estimada",
                    y="duracion_real",
                    color_discrete_sequence=["#00b4d8"],
                    title="Planificación Vs Ejecución (Filtrado)",
                    labels={
                        "duracion_estimada": "Duración Est. (años)",
                        "duracion_real": "Duración Real (años)"
                    }
                )
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
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(f"Faltan columnas: {needed_2 - set(df_filters.columns)}")

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
# SUBPÁGINA: FLUJOS AGREGADOS
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    """
    Subpágina: Flujos Agregados
      - Filtros: Región->País (con 'Todas'), Modalidad, Frecuencia
      - "Ver por": [Fechas | Sectores]
        -> Fechas: un area chart con color #c9182c (opaco)
        -> Sectores: 
            * Stacked Ordered Area Chart (Top 7 + 'Otros'), opaco
            * Percentage Stacked Ordered Area Chart debajo, también opaco
    """
    st.markdown('<p class="subtitle">Subpágina: Flujos Agregados</p>', unsafe_allow_html=True)

    df = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"])

    st.sidebar.subheader("Filtros (Flujos Agregados)")

    # 1) Región
    if "region" in df.columns:
        regiones = sorted(df["region"].dropna().unique().tolist())
        sel_region = st.sidebar.selectbox("Región:", ["Todas"] + regiones, 0)
        if sel_region != "Todas":
            df = df[df["region"] == sel_region]

    # 2) País(es) (MULTISELECT con "Todas")
    if "recipientcountry_codename" in df.columns:
        pais_list = sorted(df["recipientcountry_codename"].dropna().unique().tolist())
        opt_pais = ["Todas"] + pais_list
        sel_paises = st.sidebar.multiselect("País(es):", opt_pais, default=["Todas"])
        
        if "Todas" not in sel_paises:
            if sel_paises:
                df = df[df["recipientcountry_codename"].isin(sel_paises)]
            else:
                st.warning("No se seleccionó ningún país.")
                return

    # 3) Modalidad
    if "modality_general" in df.columns:
        mod_list = sorted(df["modality_general"].dropna().unique().tolist())
        sel_mod = st.sidebar.selectbox("Modalidad:", ["Todas"] + mod_list, 0)
        if sel_mod != "Todas":
            df = df[df["modality_general"] == sel_mod]

    # Verificamos
    if df.empty:
        st.warning("No hay datos tras aplicar filtros (Región, País, Modalidad).")
        return

    # 4) Rango Años
    min_year = df["transactiondate_isodate"].dt.year.min()
    max_year = df["transactiondate_isodate"].dt.year.max()

    ini_year, fin_year = st.sidebar.slider(
        "Rango de años:",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year)),
        step=1
    )
    start_ts = pd.to_datetime(datetime(ini_year, 1, 1))
    end_ts = pd.to_datetime(datetime(fin_year, 12, 31))

    df = df[
        (df["transactiondate_isodate"] >= start_ts) &
        (df["transactiondate_isodate"] <= end_ts)
    ]
    if df.empty:
        st.warning("No hay datos tras filtrar por años.")
        return

    # 5) Frecuencia
    freqs = ["Trimestral", "Semestral", "Anual"]
    st.markdown("**Frecuencia**")
    freq_choice = st.selectbox("", freqs, index=2, label_visibility="collapsed")

    if freq_choice == "Trimestral":
        freq_code = "Q"
        x_label = "Trimestre"
    elif freq_choice == "Semestral":
        freq_code = "6M"
        x_label = "Semestre"
    else:
        freq_code = "A"
        x_label = "Año"

    # 6) "Ver por": Fechas / Sectores
    vista_opts = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vista_opts, horizontal=True)

    if df.empty:
        st.warning("No hay datos tras estos filtros.")
        return

    # value_usd -> millones
    df["value_usd_millions"] = df["value_usd"] / 1_000_000

    # Paleta invertida + 'Otros' = #4361ee, 8 colores
    my_inverted_palette = [
        "#8A84C6",
        "#22223B",
        "#B4B3B6",
        "#FBD48A",
        "#59C3C3",
        "#FFFFFF",
        "#E86D67",
        "#4361ee"  # 'Otros'
    ]

    # -------------------------------------------------------------------------
    #  A) Vista "Fechas" -> un area chart opaco
    # -------------------------------------------------------------------------
    if vista == "Fechas":
        df.set_index("transactiondate_isodate", inplace=True)
        df_agg = df["value_usd"].resample(freq_code).sum().reset_index()
        df_agg["value_usd_millions"] = df_agg["value_usd"] / 1_000_000
        df.reset_index(inplace=True)

        if freq_choice == "Trimestral":
            df_agg["Periodo"] = (
                df_agg["transactiondate_isodate"].dt.year.astype(str)
                + "T"
                + df_agg["transactiondate_isodate"].dt.quarter.astype(str)
            )
        elif freq_choice == "Semestral":
            sem = (df_agg["transactiondate_isodate"].dt.month.sub(1)//6).add(1)
            df_agg["Periodo"] = (
                df_agg["transactiondate_isodate"].dt.year.astype(str)
                + "S"
                + sem.astype(str)
            )
        else:
            df_agg["Periodo"] = df_agg["transactiondate_isodate"].dt.year.astype(str)

        st.subheader("Stacked Ordered Area Chart (Modo Fechas) - Solo 1 Serie")

        if df_agg.empty:
            st.warning("No hay datos en este rango de años.")
            return

        # Creamos un area chart para 1 sola 'serie'. 
        # => Apilado no se ve, pero conserva la consistencia.
        fig_area_time = px.area(
            df_agg,
            x="Periodo",
            y="value_usd_millions",
            color_discrete_sequence=["#c9182c"],
            title="Area Chart - Fechas (Opaco)",
            labels={
                "Periodo": x_label,
                "value_usd_millions": "Monto (Millones USD)"
            }
        )
        # Sin transparencia
        fig_area_time.update_traces(
            stackgroup="one",
            opacity=1  # opaco
        )
        fig_area_time.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_area_time, use_container_width=True)

    # -------------------------------------------------------------------------
    #  B) Vista "Sectores" -> 
    #       - 1) Stacked Ordered Area Chart (opaco)
    #       - 2) Percentage Stacked Ordered Area Chart (opaco)
    # -------------------------------------------------------------------------
    else:
        if "Sector" not in df.columns:
            st.warning("No existe la columna 'Sector' en el DF.")
            return

        if freq_choice == "Trimestral":
            df["Periodo"] = (
                df["transactiondate_isodate"].dt.year.astype(str)
                + "T"
                + df["transactiondate_isodate"].dt.quarter.astype(str)
            )
        elif freq_choice == "Semestral":
            sem = (df["transactiondate_isodate"].dt.month.sub(1)//6).add(1)
            df["Periodo"] = (
                df["transactiondate_isodate"].dt.year.astype(str)
                + "S"
                + sem.astype(str)
            )
        else:
            df["Periodo"] = df["transactiondate_isodate"].dt.year.astype(str)

        df_agg_sec = df.groupby(["Periodo", "Sector"], as_index=False)["value_usd_millions"].sum()
        if df_agg_sec.empty:
            st.warning("No hay datos de Aprobaciones en estos filtros (Sectores).")
            return

        # Top 7
        global_sum = df_agg_sec.groupby("Sector", as_index=False)["value_usd_millions"].sum()
        global_sum = global_sum.sort_values("value_usd_millions", ascending=False)
        top_7 = global_sum["Sector"].head(7).tolist()

        df_agg_sec["Sector_stack"] = df_agg_sec["Sector"].apply(
            lambda s: s if s in top_7 else "Otros"
        )
        # Re-agrupamos
        df_agg_sec = df_agg_sec.groupby(["Periodo", "Sector_stack"], as_index=False)["value_usd_millions"].sum()

        if df_agg_sec.empty:
            st.warning("No hay datos luego de agrupar top 7 + Otros.")
            return

        # Orden alfabético + "Otros" final
        sorted_top7 = sorted(top_7)
        unique_sectors = sorted_top7 + ["Otros"]

        st.subheader("Stacked Ordered Area Chart - Sectores (Opaco)")

        # 1) Área normal (suma)
        fig_area_normal = px.area(
            df_agg_sec,
            x="Periodo",
            y="value_usd_millions",
            color="Sector_stack",
            category_orders={"Sector_stack": unique_sectors},
            color_discrete_sequence=my_inverted_palette,
            title="Área Apilada (Suma)",
            labels={
                "Periodo": x_label,
                "Sector_stack": "Sector",
                "value_usd_millions": "Monto (Millones USD)"
            },
            groupnorm=None,
            line_group="Sector_stack"
        )
        # Apilado
        fig_area_normal.update_traces(
            stackgroup="one",
            opacity=1  # sin transparencia
        )
        fig_area_normal.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_area_normal, use_container_width=True)

        st.subheader("Percentage Stacked Ordered Area Chart - Sectores (Opaco)")

        # 2) Área en Porcentajes
        fig_area_pct = px.area(
            df_agg_sec,
            x="Periodo",
            y="value_usd_millions",
            color="Sector_stack",
            category_orders={"Sector_stack": unique_sectors},
            color_discrete_sequence=my_inverted_palette,
            title="Área Apilada (Porcentaje)",
            labels={
                "Periodo": x_label,
                "Sector_stack": "Sector",
                "value_usd_millions": "Porcentaje"
            },
            groupnorm="percent",
            line_group="Sector_stack"
        )
        # Apilado, opaco
        fig_area_pct.update_traces(
            stackgroup="one",
            opacity=1
        )
        fig_area_pct.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_area_pct, use_container_width=True)

    st.info("Flujos agregados: Aprobaciones (Outgoing Commitments).")


# -----------------------------------------------------------------------------
# PÁGINA "Descriptivo" (DOS SUBPÁGINAS)
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)

    st.sidebar.title("Subpáginas de Descriptivo")
    subpag_options = ["Ejecución", "Flujos Agregados"]
    sel_sub = st.sidebar.radio("Elige una subpágina:", subpag_options, index=0)

    if sel_sub == "Ejecución":
        subpagina_ejecucion()
    else:
        subpagina_flujos_agregados()

# -----------------------------------------------------------------------------
# OTRAS PÁGINAS (Placeholder)
# -----------------------------------------------------------------------------
def series_temporales():
    st.markdown('<h1 class="title">Series Temporales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder.</p>', unsafe_allow_html=True)

def analisis_geoespacial():
    st.markdown('<h1 class="title">Análisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder.</p>', unsafe_allow_html=True)

def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder.</p>', unsafe_allow_html=True)

def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder.</p>', unsafe_allow_html=True)

def analisis_exploratorio():
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder: PyGWalker.</p>', unsafe_allow_html=True)

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

def main():
    st.sidebar.title("Navegación")
    page_choice = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()), index=0)
    PAGINAS[page_choice]()

if __name__ == "__main__":
    main()
