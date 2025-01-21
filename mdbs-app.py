import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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
# 2) CREACION DEL RENDERER DE PYGWALKER (CACHE)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str):
    from pygwalker.api.streamlit import StreamlitRenderer
    df = DATASETS[dataset_name]
    return StreamlitRenderer(df, kernel_computation=True)

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
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
                title="", 
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
                title="",
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


def compute_yoy(df: pd.DataFrame, date_col: str, value_col: str, freq_code: str, shift_periods: int):
    df_resampled = df.copy()
    df_resampled.set_index(date_col, inplace=True)

    df_agg = df_resampled[value_col].resample(freq_code).sum().reset_index()
    df_agg = df_agg.sort_values(date_col)
    df_agg["yoy"] = df_agg[value_col].pct_change(periods=shift_periods) * 100

    if freq_code.upper() == "A":  
        df_agg["Periodo"] = df_agg[date_col].dt.year.astype(str)
    elif freq_code.upper() in ["Q", "3M"]:  
        df_agg["Periodo"] = (
            df_agg[date_col].dt.year.astype(str) + "T" + df_agg[date_col].dt.quarter.astype(str)
        )
    elif freq_code.upper() in ["6M", "2Q"]:  
        sm = (df_agg[date_col].dt.month.sub(1)//6).add(1)
        df_agg["Periodo"] = df_agg[date_col].dt.year.astype(str) + "S" + sm.astype(str)
    else:
        df_agg["Periodo"] = df_agg[date_col].dt.strftime("%Y-%m")

    return df_agg

# -----------------------------------------------------------------------------
# SUBPAGINA EJECUCION
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    st.markdown('<p class="subtitle">Subpagina: Ejecucion</p>', unsafe_allow_html=True)

    df_ejec = DATASETS["ACTIVITY_IADB"].copy()

    st.sidebar.subheader("Filtros (Ejecucion)")

    # 1) Filtro Region
    custom_5fp_countries = ["Argentina", "Bolivia (Plurinational State of)", "Brazil", "Paraguay", "Uruguay"]

    if "region" in df_ejec.columns:
        real_regions = sorted(df_ejec["region"].dropna().unique().tolist())
        # Insertamos "5-FP" solo si no existe
        if "5-FP" not in real_regions:
            real_regions.insert(0, "5-FP")

        sel_region = st.sidebar.selectbox("Region:", ["Todas"] + real_regions, index=0)

        if sel_region == "5-FP":
            df_ejec = df_ejec[df_ejec["recipientcountry_codename"].isin(custom_5fp_countries)]
            if df_ejec.empty:
                st.warning("No hay datos que correspondan a la región 5-FP.")
                return
        elif sel_region == "Todas":
            pass  # No filtramos nada
        else:
            df_ejec = df_ejec[df_ejec["region"] == sel_region]
            if df_ejec.empty:
                st.warning("No hay datos tras filtrar por esta región.")
                return
    else:
        # Si la columna region no existe, mostramos un selectbox básico
        st.warning("No se encontró la columna 'region' en el dataset.")
        sel_region = st.sidebar.selectbox("Region:", ["Todas"], index=0)
        # No filtramos nada

    # 2) Filtro País (single select)
    if "recipientcountry_codename" in df_ejec.columns:
        pais_list = sorted(df_ejec["recipientcountry_codename"].dropna().unique().tolist())
        sel_country = st.sidebar.selectbox("País:", ["Todos"] + pais_list, index=0)
        if sel_country != "Todos":
            df_ejec = df_ejec[df_ejec["recipientcountry_codename"] == sel_country]
            if df_ejec.empty:
                st.warning("No hay datos tras escoger ese país.")
                return
    else:
        st.warning("No se encontró la columna 'recipientcountry_codename'.")
        return

    # Filtro sector (multiselect)
    if "Sector_1" in df_ejec.columns:
        sector_list = sorted(df_ejec["Sector_1"].dropna().unique().tolist())
        st.sidebar.markdown("**Selecciona uno o varios sectores:**")
        sel_sectors = st.sidebar.multiselect("Sector_1:", sector_list, default=[])
        if len(sector_list) > 0:
            if sel_sectors:
                df_ejec["sector_color"] = df_ejec["Sector_1"].apply(
                    lambda x: x if x in sel_sectors else "Otros"
                )
            else:
                df_ejec["sector_color"] = "Otros"
        else:
            df_ejec["sector_color"] = "Otros"
    else:
        df_ejec["sector_color"] = "Otros"

    # Filtro modalidad_general
    if "modalidad_general" in df_ejec.columns:
        mod_list = sorted(df_ejec["modalidad_general"].dropna().unique().tolist())
        opt_mod = ["Todas"] + mod_list
        sel_mod = st.sidebar.selectbox("Modalidad:", opt_mod, index=0)
        if sel_mod != "Todas":
            df_ejec = df_ejec[df_ejec["modalidad_general"] == sel_mod]

    if df_ejec.empty:
        st.warning("No hay datos tras los filtros actuales (Ejecucion).")
        return

    # Filtro interno: activitystatus_codename
    if "activitystatus_codename" in df_ejec.columns:
        df_ejec = df_ejec[df_ejec["activitystatus_codename"].isin(["Closed", "Finalisation"])]
        if df_ejec.empty:
            st.warning("No hay datos con activitystatus_codename = 'Closed' o 'Finalisation'.")
            return
    else:
        st.warning("No se encontró la columna 'activitystatus_codename'.")
        return

    # Gráfico: Planificacion Vs Ejecucion
    st.subheader("Planificacion Vs Ejecucion")
    needed_cols = {"duracion_estimada", "duracion_real", "sector_color", "activitystatus_codename"}
    if needed_cols.issubset(df_ejec.columns):
        df_scat = df_ejec[
            df_ejec["duracion_estimada"].notna() &
            df_ejec["duracion_real"].notna()
        ]
        if df_scat.empty:
            st.warning("No hay datos válidos en 'Planificacion Vs Ejecucion' (valores nulos).")
        else:
            fig = px.scatter(
                df_scat,
                x="duracion_estimada",
                y="duracion_real",
                color="sector_color",  
                hover_data=["activitystatus_codename"],  
                labels={
                    "duracion_estimada": "Duracion Est. (años)",
                    "duracion_real": "Duracion Real (años)",
                    "sector_color": "Sector"
                }
            )
            max_val = max(df_scat["duracion_estimada"].max(), df_scat["duracion_real"].max())
            fig.add_shape(
                type="line",
                x0=0, y0=0, x1=max_val, y1=max_val,
                line=dict(color="white", dash="dot")
            )
            fig.update_layout(
                title="",
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Faltan columnas en DataFrame: {needed_cols - set(df_ejec.columns)}")


# -----------------------------------------------------------------------------
# SUBPAGINA FLUJOS AGREGADOS
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    st.markdown('<p class="subtitle">Subpagina: Flujos Agregados</p>', unsafe_allow_html=True)

    df_original = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df_original["transactiondate_isodate"] = pd.to_datetime(df_original["transactiondate_isodate"])

    # -----------------------------
    # Filtros
    # -----------------------------
    st.sidebar.subheader("Filtros (Flujos Agregados)")

    if "region" in df_original.columns:
        region_list = sorted(df_original["region"].dropna().unique().tolist())
        sel_region = st.sidebar.selectbox("Region:", ["Todas"] + region_list, 0)
    else:
        sel_region = "Todas"

    df_filtered_for_region = df_original.copy()
    if sel_region != "Todas":
        df_filtered_for_region = df_filtered_for_region[df_filtered_for_region["region"] == sel_region]

    if "recipientcountry_codename" in df_filtered_for_region.columns:
        pais_list = sorted(df_filtered_for_region["recipientcountry_codename"].dropna().unique().tolist())
        opt_paises = ["Todas"] + pais_list
        if sel_region == "Todas":
            disabled_countries = True
            sel_paises = ["Todas"]
        else:
            disabled_countries = False

        sel_paises = st.sidebar.multiselect(
            "Pais(es):",
            opt_paises,
            default=["Todas"],
            disabled=disabled_countries
        )
    else:
        sel_paises = ["Todas"]

    df = df_filtered_for_region.copy()
    if "modalidad_general" in df.columns:
        m_list = sorted(df["modalidad_general"].dropna().unique().tolist())
        opt_m = ["Todas"] + m_list
        sel_mod = st.sidebar.selectbox("Modalidad (general):", opt_m, 0)
        if sel_mod != "Todas":
            df = df[df["modalidad_general"] == sel_mod]

    if df.empty:
        st.warning("No hay datos tras los filtros de region/modalidad.")
        return

    if "Todas" not in sel_paises:
        if sel_paises:
            df = df[df["recipientcountry_codename"].isin(sel_paises)]
        else:
            st.warning("No se seleccionó ningún país.")
            return

    if df.empty:
        st.warning("No hay datos tras filtrar país(es).")
        return

    if "value_usd" in df.columns:
        df["value_usd_millions"] = df["value_usd"] / 1_000_000
        min_m = float(df["value_usd_millions"].min())
        max_m = float(df["value_usd_millions"].max())
        sel_range = st.sidebar.slider(
            "Rango Montos (Millones USD):",
            min_value=min_m,
            max_value=max_m,
            value=(min_m, max_m)
        )
        df = df[
            (df["value_usd_millions"] >= sel_range[0]) &
            (df["value_usd_millions"] <= sel_range[1])
        ]

    if df.empty:
        st.warning("No hay datos tras filtrar por montos en millones.")
        return

    min_y = df["transactiondate_isodate"].dt.year.min()
    max_y = df["transactiondate_isodate"].dt.year.max()

    start_year, end_year = st.sidebar.slider(
        "Rango de años:",
        min_value=int(min_y),
        max_value=int(max_y),
        value=(int(min_y), int(max_y)),
        step=1
    )
    start_ts = pd.to_datetime(datetime(start_year, 1, 1))
    end_ts = pd.to_datetime(datetime(end_year, 12, 31))
    df = df[
        (df["transactiondate_isodate"] >= start_ts) &
        (df["transactiondate_isodate"] <= end_ts)
    ]

    if df.empty:
        st.warning("No hay datos tras filtrar por años.")
        return

    freq_opts = ["Trimestral", "Semestral", "Anual"]
    st.markdown("**Frecuencia**")
    freq_choice = st.selectbox("", freq_opts, index=2, label_visibility="collapsed")

    if freq_choice == "Trimestral":
        freq_code = "Q"
        label_x = "Trimestre"
        shift_periods = 4
    elif freq_choice == "Semestral":
        freq_code = "2Q"
        label_x = "Semestre"
        shift_periods = 2
    else:
        freq_code = "A"
        label_x = "Año"
        shift_periods = 1

    vistas = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vistas, horizontal=True)

    if df.empty:
        st.warning("No hay datos tras los filtros en Flujos Agregados.")
        return

    color_palette = [
        "#4361ee",
        "#E86D67",
        "#FFFFFF",
        "#59C3C3",
        "#FBD48A",
        "#B4B3B6",
        "#22223B",
        "#8A84C6"
    ]

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
            sm = (df_agg["transactiondate_isodate"].dt.month.sub(1)//6).add(1)
            df_agg["Periodo"] = (
                df_agg["transactiondate_isodate"].dt.year.astype(str)
                + "S"
                + sm.astype(str)
            )
        else:
            df_agg["Periodo"] = df_agg["transactiondate_isodate"].dt.year.astype(str)

        st.subheader("Stacked Ordered Bar (Fechas) - 1 Serie")

        if df_agg.empty:
            st.warning("No hay datos en este rango de años (Fechas).")
            return

        fig_time = px.bar(
            df_agg,
            x="Periodo",
            y="value_usd_millions",
            color_discrete_sequence=["#c9182c"],
            title="",
            labels={
                "Periodo": label_x,
                "value_usd_millions": "Monto (Millones USD)"
            }
        )
        fig_time.update_layout(
            bargap=0,
            bargroupgap=0,
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig_time.update_traces(marker_line_color="white", marker_line_width=1)
        st.plotly_chart(fig_time, use_container_width=True)

    else:
        if freq_choice == "Trimestral":
            df["Periodo"] = (
                df["transactiondate_isodate"].dt.year.astype(str)
                + "T"
                + df["transactiondate_isodate"].dt.quarter.astype(str)
            )
        elif freq_choice == "Semestral":
            sm = (df["transactiondate_isodate"].dt.month.sub(1)//6).add(1)
            df["Periodo"] = (
                df["transactiondate_isodate"].dt.year.astype(str)
                + "S"
                + sm.astype(str)
            )
        else:
            df["Periodo"] = df["transactiondate_isodate"].dt.year.astype(str)

        df_agg_sec = df.groupby(["Periodo", "Sector"], as_index=False)["value_usd_millions"].sum()
        if df_agg_sec.empty:
            st.warning("No hay datos en estos filtros (Sectores).")
            return

        top_agg = df_agg_sec.groupby("Sector", as_index=False)["value_usd_millions"].sum()
        top_agg = top_agg.sort_values("value_usd_millions", ascending=False)
        top_7 = top_agg["Sector"].head(7).tolist()

        df_agg_sec["Sector_stack"] = df_agg_sec["Sector"].apply(lambda s: s if s in top_7 else "OTROS")
        df_agg_sec = df_agg_sec.groupby(["Periodo", "Sector_stack"], as_index=False)["value_usd_millions"].sum()

        if df_agg_sec.empty:
            st.warning("No hay datos después de agrupar top 7 + 'OTROS'.")
            return

        pivoted = df_agg_sec.pivot(index="Periodo", columns="Sector_stack", values="value_usd_millions").fillna(0)
        sums = pivoted.sum(axis=1)
        pivot_pct = pivoted.div(sums, axis=0) * 100
        df_pct = pivot_pct.reset_index().melt(id_vars="Periodo", var_name="Sector_stack", value_name="pct_value")

        sorted_top7 = sorted(top_7)
        unique_sectors = sorted_top7 + ["OTROS"]

        color_map = {}
        for i, sector_n in enumerate(unique_sectors):
            color_map[sector_n] = color_palette[i % len(color_palette)]

        fig_subplots = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.15,
            subplot_titles=(
                "Evolución de aprobaciones (Millones USD)",
                "Evolución de aprobaciones (%)"
            )
        )
        fig_subplots.update_layout(
            height=800
        )

        # BARRAS (abs)
        for sector_n in unique_sectors:
            df_temp_abs = df_agg_sec[df_agg_sec["Sector_stack"] == sector_n]
            x_vals = df_temp_abs["Periodo"]
            y_vals = df_temp_abs["value_usd_millions"]

            fig_subplots.add_trace(
                go.Bar(
                    x=x_vals,
                    y=y_vals,
                    name=sector_n,
                    legendgroup=sector_n,
                    marker_color=color_map[sector_n],
                    showlegend=True
                ),
                row=1, col=1
            )

        # BARRAS (%)
        for sector_n in unique_sectors:
            df_temp_pct = df_pct[df_pct["Sector_stack"] == sector_n]
            x_vals = df_temp_pct["Periodo"]
            y_vals = df_temp_pct["pct_value"]

            fig_subplots.add_trace(
                go.Bar(
                    x=x_vals,
                    y=y_vals,
                    name=sector_n,
                    legendgroup=sector_n,
                    marker_color=color_map[sector_n],
                    showlegend=False
                ),
                row=2, col=1
            )

        fig_subplots.update_layout(
            barmode="stack",
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="center",
                x=0.5
            )
        )
        fig_subplots.update_xaxes(title_text=label_x, row=2, col=1)
        fig_subplots.update_yaxes(title_text="Millones USD", row=1, col=1)
        fig_subplots.update_yaxes(title_text="Porcentaje (%)", row=2, col=1)
        fig_subplots.update_traces(marker_line_color="white", marker_line_width=1)

        st.plotly_chart(fig_subplots, use_container_width=True)

    st.info("Flujos agregados: Aprobaciones (Outgoing Commitments).")

    st.markdown("---")
    st.markdown("## Tasa de Crecimiento Interanual (YoY)")

    df_global_all = df_original.copy()
    df_global_all["transactiondate_isodate"] = pd.to_datetime(df_global_all["transactiondate_isodate"])
    df_global_all = df_global_all[
        (df_global_all["transactiondate_isodate"] >= start_ts) &
        (df_global_all["transactiondate_isodate"] <= end_ts)
    ]

    if sel_region != "Todas":
        df_region_all = df_global_all[df_global_all["region"] == sel_region].copy()
    else:
        df_region_all = pd.DataFrame()

    list_countries_data_all = []
    if sel_region != "Todas" and ("Todas" not in sel_paises):
        for c in sel_paises:
            temp_df = df_region_all[df_region_all["recipientcountry_codename"] == c]
            if not temp_df.empty:
                list_countries_data_all.append((c, temp_df))

    yoy_list_all = []
    if not df_global_all.empty:
        yoy_g_all = compute_yoy(
            df_global_all,
            date_col="transactiondate_isodate",
            value_col="value_usd",
            freq_code=freq_code,
            shift_periods=shift_periods
        )
        yoy_g_all["Categoria"] = "Global"
        yoy_list_all.append(yoy_g_all)

    if not df_region_all.empty:
        yoy_r_all = compute_yoy(
            df_region_all,
            date_col="transactiondate_isodate",
            value_col="value_usd",
            freq_code=freq_code,
            shift_periods=shift_periods
        )
        yoy_r_all["Categoria"] = f"Región: {sel_region}"
        yoy_list_all.append(yoy_r_all)

    for (country_name, df_country_all) in list_countries_data_all:
        yoy_c_all = compute_yoy(
            df_country_all,
            date_col="transactiondate_isodate",
            value_col="value_usd",
            freq_code=freq_code,
            shift_periods=shift_periods
        )
        yoy_c_all["Categoria"] = f"País: {country_name}"
        yoy_list_all.append(yoy_c_all)

    if yoy_list_all:
        df_yoy_final_all = pd.concat(yoy_list_all, ignore_index=True)
        fig_yoy_all = px.line(
            df_yoy_final_all,
            x="Periodo",
            y="yoy",
            color="Categoria",
            markers=True,
            line_shape="spline",
            title="",
            labels={
                "Periodo": "Periodo",
                "yoy": "Crec. Interanual (%)",
                "Categoria": ""
            }
        )
        fig_yoy_all.add_hline(
            y=0,
            line_dash="dot",
            line_color="white"
        )
        fig_yoy_all.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig_yoy_all, use_container_width=True)
    else:
        st.warning("No se pudo calcular Tasa de Crecimiento Interanual con los filtros actuales.")


# -----------------------------------------------------------------------------
# PAGINA DESCRIPTIVO (DOS SUBPAGINAS)
# -----------------------------------------------------------------------------
def descriptivo():
    st.markdown('<h1 class="title">Descriptivo</h1>', unsafe_allow_html=True)

    st.sidebar.title("Subpaginas de Descriptivo")
    subpags = ["Ejecucion", "Flujos Agregados"]
    choice_sub = st.sidebar.radio("Elige una subpagina:", subpags, index=0)

    if choice_sub == "Ejecucion":
        subpagina_ejecucion()
    else:
        subpagina_flujos_agregados()

# -----------------------------------------------------------------------------
# SERIES TEMPORALES (EJEMPLO)
# -----------------------------------------------------------------------------
def series_temporales():
    st.markdown('<h1 class="title">Series Temporales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ejemplo: line chart de un dataset (placeholder)</p>', unsafe_allow_html=True)

    df_temp = DATASETS["ACTIVITY_IADB"].copy()
    if "apertura_date" in df_temp.columns:
        df_temp["apertura_date"] = pd.to_datetime(df_temp["apertura_date"])
        min_date = df_temp["apertura_date"].min()
        max_date = df_temp["apertura_date"].max()
        sel_range = st.slider("Rango de fechas:", min_value=min_date, max_value=max_date, value=(min_date, max_date))
        mask = (df_temp["apertura_date"] >= sel_range[0]) & (df_temp["apertura_date"] <= sel_range[1])
        df_temp = df_temp[mask]

        if df_temp.empty:
            st.warning("No hay datos en ese rango de fechas.")
            return

        if "value_usd" in df_temp.columns:
            df_g = df_temp.groupby(pd.Grouper(key="apertura_date", freq="M"))["value_usd"].sum().reset_index()
            fig_line = px.line(
                df_g,
                x="apertura_date",
                y="value_usd",
                title="",
                labels={
                    "apertura_date": "Fecha",
                    "value_usd": "Valor (USD)"
                }
            )
            fig_line.update_layout(
                font_color="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No existe 'value_usd' para graficar en line chart.")
    else:
        st.info("No existe 'apertura_date' en este dataset. Placeholder.")

# -----------------------------------------------------------------------------
# ANALISIS GEOESPACIAL (EJEMPLO)
# -----------------------------------------------------------------------------
def analisis_geoespacial():
    st.markdown('<h1 class="title">Analisis Geoespacial</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ejemplo: folium map con MarkerCluster (placeholder)</p>', unsafe_allow_html=True)

    df_geo = DATASETS["ACTIVITY_IADB"].copy()
    if "lat" in df_geo.columns and "lon" in df_geo.columns:
        m = folium.Map(location=[df_geo["lat"].mean(), df_geo["lon"].mean()], zoom_start=5)
        marker_cluster = MarkerCluster().add_to(m)

        for i, row in df_geo.iterrows():
            if not pd.isna(row["lat"]) and not pd.isna(row["lon"]):
                folium.Marker(location=[row["lat"], row["lon"]], 
                              popup=str(row.get("Sector_1", "N/A"))).add_to(marker_cluster)

        st_folium(m, width=700, height=500)
    else:
        st.info("No hay columnas 'lat' y 'lon' en ACTIVITY_IADB. Placeholder geoespacial.")

# -----------------------------------------------------------------------------
# MULTIDIMENSIONAL Y RELACIONES (EJEMPLO)
# -----------------------------------------------------------------------------
def multidimensional_y_relaciones():
    st.markdown('<h1 class="title">Multidimensional y Relaciones</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ejemplo: matriz de correlacion (placeholder)</p>', unsafe_allow_html=True)

    df_multi = DATASETS["ACTIVITY_IADB"].copy()
    numeric_cols = df_multi.select_dtypes(include=[float, int]).columns
    if len(numeric_cols) > 1:
        corr = df_multi[numeric_cols].corr()
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            title="",
        )
        fig_corr.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No hay suficientes columnas numéricas para correlacionar.")

# -----------------------------------------------------------------------------
# MODELOS (EJEMPLO)
# -----------------------------------------------------------------------------
def modelos():
    st.markdown('<h1 class="title">Modelos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Placeholder de entrenamiento de modelos</p>', unsafe_allow_html=True)

    st.write("Ejemplo: Carga scikit-learn y entrena un modelo. Placeholder...")

# -----------------------------------------------------------------------------
# ANALISIS EXPLORATORIO (PyGWalker)
# -----------------------------------------------------------------------------
def analisis_exploratorio():
    st.markdown('<h1 class="title">Analisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar:")
    ds_list = list(DATASETS.keys())
    sel_ds = st.sidebar.selectbox("Dataset:", ds_list, index=0)
    renderer = get_pyg_renderer_by_name(sel_ds)
    renderer.explorer()

# -----------------------------------------------------------------------------
# PAGINAS DEL MENU PRINCIPAL
# -----------------------------------------------------------------------------
def main_descriptivo():
    descriptivo()

def main_series_temporales():
    series_temporales()

def main_geoespacial():
    analisis_geoespacial()

def main_multidimensional():
    multidimensional_y_relaciones()

def main_modelos():
    modelos()

def main_analisis_exploratorio():
    analisis_exploratorio()

PAGINAS = {
    "Descriptivo": main_descriptivo,
    "Series Temporales": main_series_temporales,
    "Analisis Geoespacial": main_geoespacial,
    "Multidimensional y Relaciones": main_multidimensional,
    "Modelos": main_modelos,
    "Analisis Exploratorio": main_analisis_exploratorio
}

def main():
    st.sidebar.title("Navegacion")
    choice = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()), index=0)
    PAGINAS[choice]()

if __name__ == "__main__":
    main()
