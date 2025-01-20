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
# CONFIGURACION DE PAGINA Y CSS (MODO OSCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Mi Aplicacion - Modo Oscuro",
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
# 1) CARGA DE DATOS (CACHE)
# -----------------------------------------------------------------------------
@st.cache_data
def load_dataframes():
    # Ajusta a tu entorno si difiere:
    df_activity = pd.read_parquet("activity_iadb.parquet")  
    df_outgoing = pd.read_parquet("outgoing_commitment_iadb.parquet")
    df_disb = pd.read_parquet("disbursements_data.parquet")

    return {
        "ACTIVITY_IADB": df_activity,
        "OUTGOING_COMMITMENT_IADB": df_outgoing,
        "DISBURSEMENTS_DATA": df_disb
    }

DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2) PYGWALKER (CACHE)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str):
    from pygwalker.api.streamlit import StreamlitRenderer
    df = DATASETS[dataset_name]
    return StreamlitRenderer(df, kernel_computation=True)

# -----------------------------------------------------------------------------
# AUX: BOX PLOTS
# -----------------------------------------------------------------------------
def boxplot_modalidad(df: pd.DataFrame, titulo_extra: str = ""):
    needed_cols_1 = {"modality_general", "duracion_estimada"}
    needed_cols_2 = {"modality_general", "completion_delay_years"}

    # Box Plot (Duracion)
    if needed_cols_1.issubset(df.columns):
        df1 = df[df["modality_general"].notna() & df["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="modality_general",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title="Distribucion de Duracion " + titulo_extra + " (Modalidad)",
                labels={
                    "modality_general": "Modalidad General",
                    "duracion_estimada": "Duracion (anos)"
                }
            )
            fig1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig1, use_container_width=True)

    # Box Plot (Atraso)
    if needed_cols_2.issubset(df.columns):
        df2 = df[df["modality_general"].notna() & df["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="modality_general",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title="Distribucion de Atraso " + titulo_extra + " (Modalidad)",
                labels={
                    "modality_general": "Modalidad General",
                    "completion_delay_years": "Atraso (anos)"
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

    # Filtra donde Sector y value_usd sean validos
    df_s = df[df["Sector"].notna() & df["value_usd"].notna()]
    if df_s.empty:
        st.warning("No hay datos para top 6 sectores.")
        return

    # Calcula top 6
    sum_sec = (
        df_s.groupby("Sector", as_index=False)["value_usd"]
        .sum()
        .sort_values("value_usd", ascending=False)
    )
    top_6_list = sum_sec["Sector"].head(6).tolist()

    df_top = df[df["Sector"].isin(top_6_list)].copy()
    if df_top.empty:
        st.warning("No hay datos en top 6 sectores.")
        return

    # Box Plot (Duracion)
    if needed_cols_1.issubset(df_top.columns):
        df1 = df_top[df_top["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="Sector",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title="Distribucion Duracion " + titulo_extra + " (Top 6 Sectores)",
                labels={
                    "Sector": "Sector (Top 6)",
                    "duracion_estimada": "Duracion (anos)"
                }
            )
            fig1.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig1, use_container_width=True)

    # Box Plot (Atraso)
    if needed_cols_2.issubset(df_top.columns):
        df2 = df_top[df_top["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="Sector",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title="Distribucion Atraso " + titulo_extra + " (Top 6 Sectores)",
                labels={
                    "Sector": "Sector (Top 6)",
                    "completion_delay_years": "Atraso (anos)"
                }
            )
            fig2.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# SUBPAGINA: EJECUCION (NO cambiar variable Sector_1, mantener modalid_general)
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    """
    Subpagina: Ejecucion
      - Usa "ACTIVITY_IADB"
      - Filtra por Sector_1 (no Sector!)
      - Filtro de modalidad_general
      - Mantener la logica original de Ejecucion (Scatter, Box, etc.)
    """
    st.markdown('<p class="subtitle">Subpagina: Ejecucion</p>', unsafe_allow_html=True)

    # Cargamos dataset de EJECUCION (ACTIVITY_IADB)
    df_filters = DATASETS["ACTIVITY_IADB"].copy()

    st.sidebar.subheader("Filtros (Ejecucion)")

    # 1) Filtro Sector_1 (en lugar de "Sector")
    if "Sector_1" in df_filters.columns:
        list_sec = sorted(df_filters["Sector_1"].dropna().unique().tolist())
        opt_sec = ["General"] + list_sec
        sel_sec = st.sidebar.selectbox("Sector_1:", opt_sec, index=0)
        if sel_sec != "General":
            df_filters = df_filters[df_filters["Sector_1"] == sel_sec]

    # 2) Filtro modalidad_general
    if "modalidad_general" in df_filters.columns:
        mod_list = sorted(df_filters["modalidad_general"].dropna().unique().tolist())
        opt_mod = ["Todas"] + mod_list
        sel_mod = st.sidebar.selectbox("Modalidad:", opt_mod, index=0)
        if sel_mod != "Todas":
            df_filters = df_filters[df_filters["modalidad_general"] == sel_mod]

    # Graficos: Aprobaciones Vs Ejecucion, Planificacion Vs Ejecucion
    # (Asumiendo estas columnas existen: duracion_estimada, completion_delay_years, etc.)
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Aprobaciones Vs Ejecucion")
        needed_1 = {"duracion_estimada", "completion_delay_years"}
        if needed_1.issubset(df_filters.columns):
            df_scat1 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["completion_delay_years"].notna()
            ]
            if df_scat1.empty:
                st.warning("No hay datos en 'Aprobaciones Vs Ejecucion' tras filtrar.")
            else:
                fig1 = px.scatter(
                    df_scat1,
                    x="duracion_estimada",
                    y="completion_delay_years",
                    color_discrete_sequence=["#00b4d8"],
                    title="Aprobaciones Vs Ejecucion (Filtrado)",
                    labels={
                        "duracion_estimada": "Duracion Est. (anos)",
                        "completion_delay_years": "Atraso (anos)"
                    }
                )
                fig1.update_layout(
                    font_color="#FFFFFF",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning(f"No existen columnas suficientes: {needed_1 - set(df_filters.columns)}")

    with colB:
        st.subheader("Planificacion Vs Ejecucion")
        needed_2 = {"duracion_estimada", "duracion_real"}
        if needed_2.issubset(df_filters.columns):
            df_scat2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ]
            if df_scat2.empty:
                st.warning("No hay datos en 'Planificacion Vs Ejecucion' tras filtrar.")
            else:
                fig2 = px.scatter(
                    df_scat2,
                    x="duracion_estimada",
                    y="duracion_real",
                    color_discrete_sequence=["#00b4d8"],
                    title="Planificacion Vs Ejecucion (Filtrado)",
                    labels={
                        "duracion_estimada": "Duracion Est. (anos)",
                        "duracion_real": "Duracion Real (anos)"
                    }
                )
                # linea diagonal
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
            st.warning(f"No existen columnas suficientes: {needed_2 - set(df_filters.columns)}")

    st.markdown("---")
    st.markdown("### Box Plots (Modalidad) - Filtrados")

    # Si deseas box plots por Sector_1, se podria. O solo por modalidad (lo que tenias)
    df_box = df_filters.copy()

    # Box Plot segun modalidad
    boxplot_modalidad(df_box, titulo_extra="(Filtrado Ejecucion)")

    # O si tenias sector con top6, adaptalo a Sector_1. 
    # Por el enunciado, no se solicito un box-plot segun Sector_1, 
    # si lo deseas, implementalo análogo. De lo contrario, omitelo.


# -----------------------------------------------------------------------------
# SUBPAGINA: FLUJOS AGREGADOS (usa variable Sector, y filter de modalidad_general)
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    """
    Subpagina: Flujos Agregados
      - Usa "OUTGOING_COMMITMENT_IADB"
      - Filtra por Sector (top 7 + 'Otros')
      - Filtro de modalidad_general
      - Filtro de Montos (value_usd) en MILLONES
      - Stacked bar normal y porcentaje
    """
    st.markdown('<p class="subtitle">Subpagina: Flujos Agregados</p>', unsafe_allow_html=True)

    df = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"])

    st.sidebar.subheader("Filtros (Flujos Agregados)")

    # 1) Modalidad (modalidad_general)
    if "modalidad_general" in df.columns:
        mods = sorted(df["modalidad_general"].dropna().unique().tolist())
        sel_mod = st.sidebar.selectbox("Modalidad (general):", ["Todas"] + mods, index=0)
        if sel_mod != "Todas":
            df = df[df["modalidad_general"] == sel_mod]

    # 2) Filtro Montos en millones
    if "value_usd" in df.columns:
        df["value_usd_millions"] = df["value_usd"] / 1_000_000
        min_mill = float(df["value_usd_millions"].min())
        max_mill = float(df["value_usd_millions"].max())

        sel_range = st.sidebar.slider(
            "Rango de Montos (Millones USD):",
            min_value=min_mill,
            max_value=max_mill,
            value=(min_mill, max_mill)
        )
        df = df[
            (df["value_usd_millions"] >= sel_range[0]) &
            (df["value_usd_millions"] <= sel_range[1])
        ]

    if df.empty:
        st.warning("No hay datos tras filtrar por modalidad y/o montos (Flujos Agregados).")
        return

    # Filtro Rango de Anos
    min_year = df["transactiondate_isodate"].dt.year.min()
    max_year = df["transactiondate_isodate"].dt.year.max()

    ini_year, fin_year = st.sidebar.slider(
        "Rango de anos:",
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
        st.warning("No hay datos tras filtrar por anos (Flujos Agregados).")
        return

    # Frecuencia
    freq_opciones = ["Trimestral", "Semestral", "Anual"]
    st.markdown("**Frecuencia**")
    freq_choice = st.selectbox("", freq_opciones, index=2, label_visibility="collapsed")

    if freq_choice == "Trimestral":
        freq_code = "Q"
        label_x = "Trimestre"
    elif freq_choice == "Semestral":
        freq_code = "6M"
        label_x = "Semestre"
    else:
        freq_code = "A"
        label_x = "Ano"

    # "Ver por": [Fechas | Sectores]
    vista_options = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vista_options, horizontal=True)

    if df.empty:
        st.warning("No hay datos tras los filtros (Flujos Agregados).")
        return

    # Paleta invertida (8 colores), 'Otros' = #4361ee
    my_inverted_palette = [
        "#4361ee",
        "#E86D67",
        "#FFFFFF",
        "#59C3C3",
        "#FBD48A",
        "#B4B3B6",
        "#22223B",
        "#8A84C6"
    ]

    # -------------------------------------------------------------------------
    # (A) MODO "Fechas"
    # -------------------------------------------------------------------------
    if vista == "Fechas":
        # Resample segun freq_code
        df.set_index("transactiondate_isodate", inplace=True)
        df_agg = df["value_usd"].resample(freq_code).sum().reset_index()
        df_agg["value_usd_millions"] = df_agg["value_usd"] / 1_000_000
        df.reset_index(inplace=True)

        # Crea "Periodo"
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

        st.subheader("Stacked Ordered Bar (Fechas) - 1 Serie")

        if df_agg.empty:
            st.warning("No hay datos en el rango de anos (Fechas).")
            return

        fig_bar_time = px.bar(
            df_agg,
            x="Periodo",
            y="value_usd_millions",
            color_discrete_sequence=["#c9182c"],
            labels={
                "Periodo": label_x,
                "value_usd_millions": "Monto (Millones USD)"
            },
            title=""
        )
        fig_bar_time.update_layout(bargap=0, bargroupgap=0)
        fig_bar_time.update_traces(marker_line_color="white", marker_line_width=1)
        fig_bar_time.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar_time, use_container_width=True)

    # -------------------------------------------------------------------------
    # (B) MODO "Sectores"
    # -------------------------------------------------------------------------
    else:
        if "Sector" not in df.columns:
            st.warning("No existe la columna 'Sector' en el DF de Flujos Agregados.")
            return

        # Calcula Periodo
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

        df_agg_sec["Sector_stack"] = df_agg_sec["Sector"].apply(lambda s: s if s in top_7 else "Otros")
        df_agg_sec = df_agg_sec.groupby(["Periodo", "Sector_stack"], as_index=False)["value_usd_millions"].sum()

        st.subheader("Stacked Ordered Bar Chart (Sectores)")

        if df_agg_sec.empty:
            st.warning("No hay datos despues de agrupar top 7 + 'Otros'.")
            return

        # Orden (alfabetico) + "Otros"
        sorted_top7 = sorted(top_7)
        unique_sectors = sorted_top7 + ["Otros"]

        # 1) Suma
        fig_bar_normal = px.bar(
            df_agg_sec,
            x="Periodo",
            y="value_usd_millions",
            color="Sector_stack",
            barmode="stack",
            category_orders={"Sector_stack": unique_sectors},
            color_discrete_sequence=my_inverted_palette,
            labels={
                "Periodo": label_x,
                "Sector_stack": "Sector",
                "value_usd_millions": "Monto (Millones USD)"
            },
            title="Stacked Ordered Bar (Suma)"
        )
        fig_bar_normal.update_layout(bargap=0, bargroupgap=0)
        fig_bar_normal.update_traces(marker_line_color="white", marker_line_width=1)
        fig_bar_normal.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar_normal, use_container_width=True)

        st.subheader("Percentage Stacked Ordered Bar Chart (Sectores)")

        # 2) Porcentaje
        pivoted = df_agg_sec.pivot(index="Periodo", columns="Sector_stack", values="value_usd_millions").fillna(0)
        pivoted_sum = pivoted.sum(axis=1)
        pivoted_pct = pivoted.div(pivoted_sum, axis=0) * 100
        df_pct = pivoted_pct.reset_index().melt(id_vars="Periodo", var_name="Sector_stack", value_name="pct_value")

        fig_bar_pct = px.bar(
            df_pct,
            x="Periodo",
            y="pct_value",
            color="Sector_stack",
            barmode="stack",
            category_orders={"Sector_stack": unique_sectors},
            color_discrete_sequence=my_inverted_palette,
            labels={
                "Periodo": label_x,
                "Sector_stack": "Sector",
                "pct_value": "Porcentaje (%)"
            },
            title="Stacked Ordered Bar (Porcentaje)"
        )
        fig_bar_pct.update_layout(bargap=0, bargroupgap=0)
        fig_bar_pct.update_traces(marker_line_color="white", marker_line_width=1)
        fig_bar_pct.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar_pct, use_container_width=True)

    st.info("Flujos agregados: Aprobaciones (Outgoing Commitments).")

# -----------------------------------------------------------------------------
# PAGINA "Descriptivo" (DOS SUBPAGINAS)
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)

    st.sidebar.title("Subpaginas de Descriptivo")
    subpag_options = ["Ejecucion", "Flujos Agregados"]
    sel_sub = st.sidebar.radio("Elige una subpagina:", subpag_options, index=0)

    if sel_sub == "Ejecucion":
        subpagina_ejecucion()
    else:
        subpagina_flujos_agregados()

# -----------------------------------------------------------------------------
# OTRAS PAGINAS (PLACEHOLDERS)
# -----------------------------------------------------------------------------
def series_temporales():
    st.markdown('<h1 class="title">Series Temporales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder</p>', unsafe_allow_html=True)

def analisis_geoespacial():
    st.markdown('<h1 class="title">Analisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder</p>', unsafe_allow_html=True)

def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder</p>', unsafe_allow_html=True)

def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder</p>', unsafe_allow_html=True)

def analisis_exploratorio():
    st.markdown('<h1 class="title">Analisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder: PyGWalker</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar")
    ds = st.sidebar.selectbox("Base de datos:", list(DATASETS.keys()))
    renderer = get_pyg_renderer_by_name(ds)
    renderer.explorer()

# -----------------------------------------------------------------------------
# MENU PRINCIPAL (PAGINAS)
# -----------------------------------------------------------------------------
PAGINAS = {
    "Descriptivo": descriptivo,
    "Series Temporales": series_temporales,
    "Analisis Geoespacial": analisis_geoespacial,
    "Multidimensional y Relaciones": multidimensional_y_relaciones,
    "Modelos": modelos,
    "Analisis Exploratorio": analisis_exploratorio
}

def main():
    st.sidebar.title("Navegacion")
    page_choice = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()), index=0)
    PAGINAS[page_choice]()

if __name__ == "__main__":
    main()
