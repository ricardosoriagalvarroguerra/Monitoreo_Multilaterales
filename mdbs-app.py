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
    # Ajusta las rutas de tus parquet
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

    # Box Plot (Duración)
    if needed_cols_1.issubset(df.columns):
        df1 = df[df["modalidad_general"].notna() & df["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="modalidad_general",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title="",  # Sin título interno
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

    # Box Plot (Atraso)
    if needed_cols_2.issubset(df.columns):
        df2 = df[df["modalidad_general"].notna() & df["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="modalidad_general",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title="",  # Sin título interno
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
    """
    Calcula la variación interanual (YoY) en base a `value_col`.
    YOY_t = [(value_t / value_{t-Δ}) - 1] * 100
    Devuelve un DataFrame con columnas: [date_col, value_col, yoy, Periodo].
    """
    df_resampled = df.copy()
    df_resampled.set_index(date_col, inplace=True)

    # Sumar 'value_col' según la frecuencia deseada
    df_agg = df_resampled[value_col].resample(freq_code).sum().reset_index()
    df_agg = df_agg.sort_values(date_col)

    # Calculamos el cambio porcentual (en %) vs. 'shift_periods' atrás
    df_agg["yoy"] = df_agg[value_col].pct_change(periods=shift_periods) * 100

    # Formateamos la columna Periodo (etiqueta X)
    if freq_code.upper() == "A":  # Anual
        df_agg["Periodo"] = df_agg[date_col].dt.year.astype(str)
    elif freq_code.upper() in ["Q", "3M"]:  # Trimestral
        df_agg["Periodo"] = (
            df_agg[date_col].dt.year.astype(str) + "T" + df_agg[date_col].dt.quarter.astype(str)
        )
    elif freq_code.upper() in ["6M", "2Q"]:  # Semestral
        sm = (df_agg[date_col].dt.month.sub(1)//6).add(1)
        df_agg["Periodo"] = df_agg[date_col].dt.year.astype(str) + "S" + sm.astype(str)
    else:
        # fallback mensual
        df_agg["Periodo"] = df_agg[date_col].dt.strftime("%Y-%m")

    return df_agg


# -----------------------------------------------------------------------------
# SUBPAGINA EJECUCION (ACTIVITY_IADB)
# -----------------------------------------------------------------------------
def subpagina_ejecucion():
    """
    - Filtros de región, país, sector, modalidad.
    - Scatter “Aprobaciones Vs Ejecución”: size en función de value_usd.
    - Scatter “Planificación Vs Ejecución”: SIN size en función de value_usd, 
      pero con línea diagonal 45°.
    - Boxplots de duración y atraso según modalidad.
    """
    st.markdown('<p class="subtitle">Subpagina: Ejecucion</p>', unsafe_allow_html=True)

    df_ejec = DATASETS["ACTIVITY_IADB"].copy()

    st.sidebar.subheader("Filtros (Ejecucion)")

    # Filtro Region (si existe)
    if "region" in df_ejec.columns:
        regiones = sorted(df_ejec["region"].dropna().unique().tolist())
        sel_region = st.sidebar.selectbox("Region:", ["Todas"] + regiones, index=0)
        if sel_region != "Todas":
            df_ejec = df_ejec[df_ejec["region"] == sel_region]

    # Filtro País (multiselect con 'Todas')
    if "recipientcountry_codename" in df_ejec.columns:
        pais_list = sorted(df_ejec["recipientcountry_codename"].dropna().unique().tolist())
        opt_paises = ["Todas"] + pais_list
        sel_paises = st.sidebar.multiselect("Pais(es):", opt_paises, default=["Todas"])
        if "Todas" not in sel_paises:
            if sel_paises:
                df_ejec = df_ejec[df_ejec["recipientcountry_codename"].isin(sel_paises)]
            else:
                st.warning("No se seleccionó ningún país.")
                return

    # Filtro Sector_1
    if "Sector_1" in df_ejec.columns:
        sec_list = sorted(df_ejec["Sector_1"].dropna().unique().tolist())
        opt_sec = ["General"] + sec_list
        sel_sec = st.sidebar.selectbox("Sector_1:", opt_sec, index=0)
        if sel_sec != "General":
            df_ejec = df_ejec[df_ejec["Sector_1"] == sel_sec]

    # Filtro modalidad_general
    if "modalidad_general" in df_ejec.columns:
        mod_list = sorted(df_ejec["modalidad_general"].dropna().unique().tolist())
        opt_mod = ["Todas"] + mod_list
        sel_mod = st.sidebar.selectbox("Modalidad:", opt_mod, index=0)
        if sel_mod != "Todas":
            df_ejec = df_ejec[df_ejec["modalidad_general"] == sel_mod]

    if df_ejec.empty:
        st.warning("No hay datos tras los filtros (Ejecucion).")
        return

    colA, colB = st.columns(2)

    # Scatter 1: "Aprobaciones Vs Ejecucion" (Burbujas con size en value_usd)
    with colA:
        st.subheader("Aprobaciones Vs Ejecucion")
        needed_1 = {"duracion_estimada", "completion_delay_years", "value_usd"}
        if needed_1.issubset(df_ejec.columns):
            df_scat1 = df_ejec[
                df_ejec["duracion_estimada"].notna() &
                df_ejec["completion_delay_years"].notna() &
                df_ejec["value_usd"].notna()
            ]
            if df_scat1.empty:
                st.warning("No hay datos en 'Aprobaciones Vs Ejecucion' tras filtrar.")
            else:
                fig1 = px.scatter(
                    df_scat1,
                    x="duracion_estimada",
                    y="completion_delay_years",
                    size="value_usd",   # tamaño en función de 'value_usd'
                    size_max=40,
                    color_discrete_sequence=["#00b4d8"],
                    title="",  # Sin título interno
                    labels={
                        "duracion_estimada": "Duracion Est. (años)",
                        "completion_delay_years": "Atraso (años)",
                        "value_usd": "Valor (USD)"
                    }
                )
                fig1.update_layout(
                    font_color="#FFFFFF",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning(f"Faltan columnas en DataFrame: {needed_1 - set(df_ejec.columns)}")

    # Scatter 2: "Planificación Vs Ejecución" (SIN tamaño en value_usd) + diagonal 45°
    with colB:
        st.subheader("Planificacion Vs Ejecucion")
        needed_2 = {"duracion_estimada", "duracion_real"}
        if needed_2.issubset(df_ejec.columns):
            df_scat2 = df_ejec[
                df_ejec["duracion_estimada"].notna() &
                df_ejec["duracion_real"].notna()
            ]
            if df_scat2.empty:
                st.warning("No hay datos en 'Planificacion Vs Ejecucion' tras filtrar.")
            else:
                fig2 = px.scatter(
                    df_scat2,
                    x="duracion_estimada",
                    y="duracion_real",
                    color_discrete_sequence=["#00b4d8"],
                    title="",  # Sin título interno
                    labels={
                        "duracion_estimada": "Duracion Est. (años)",
                        "duracion_real": "Duracion Real (años)"
                    }
                )
                # Agregamos la línea diagonal (45°)
                max_val = max(
                    df_scat2["duracion_estimada"].max(),
                    df_scat2["duracion_real"].max()
                )
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
            st.warning(f"Faltan columnas en DataFrame: {needed_2 - set(df_ejec.columns)}")

    st.markdown("---")
    st.markdown("### Box Plots (Modalidad) - Filtrados")

    boxplot_modalidad(df_ejec, titulo_extra="(Ejecucion)")

# -----------------------------------------------------------------------------
# SUBPAGINA FLUJOS AGREGADOS (OUTGOING_COMMITMENT_IADB)
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    st.markdown('<p class="subtitle">Subpagina: Flujos Agregados</p>', unsafe_allow_html=True)

    df_original = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df_original["transactiondate_isodate"] = pd.to_datetime(df_original["transactiondate_isodate"])

    # -----------------------------
    # Filtros en barra lateral
    # -----------------------------
    st.sidebar.subheader("Filtros (Flujos Agregados)")

    # 1) Filtro region
    if "region" in df_original.columns:
        region_list = sorted(df_original["region"].dropna().unique().tolist())
        sel_region = st.sidebar.selectbox("Region:", ["Todas"] + region_list, 0)
    else:
        sel_region = "Todas"

    # 2) Filtro pais (multiselect con 'Todas'), habilitado solo si region != "Todas"
    df_filtered_for_region = df_original.copy()
    if sel_region != "Todas":
        df_filtered_for_region = df_filtered_for_region[df_filtered_for_region["region"] == sel_region]

    if "recipientcountry_codename" in df_filtered_for_region.columns:
        pais_list = sorted(df_filtered_for_region["recipientcountry_codename"].dropna().unique().tolist())
        opt_paises = ["Todas"] + pais_list
        if sel_region == "Todas":
            # deshabilitamos el multiselect de país
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

    # 3) Filtro modalidad_general
    df = df_filtered_for_region.copy()  # Aplica region
    if "modalidad_general" in df.columns:
        m_list = sorted(df["modalidad_general"].dropna().unique().tolist())
        opt_m = ["Todas"] + m_list
        sel_mod = st.sidebar.selectbox("Modalidad (general):", opt_m, 0)
        if sel_mod != "Todas":
            df = df[df["modalidad_general"] == sel_mod]

    if df.empty:
        st.warning("No hay datos tras los filtros de region/modalidad.")
        return

    # 4) Filtro países si no es "Todas"
    if "Todas" not in sel_paises:
        if sel_paises:
            df = df[df["recipientcountry_codename"].isin(sel_paises)]
        else:
            st.warning("No se seleccionó ningún país.")
            return

    if df.empty:
        st.warning("No hay datos tras filtrar país(es).")
        return

    # 5) Filtro montos (en millones)
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

    # 6) Filtro años
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

    # -----------------------------
    # Seleccion de frecuencia
    # -----------------------------
    freq_opts = ["Trimestral", "Semestral", "Anual"]
    st.markdown("**Frecuencia**")
    freq_choice = st.selectbox("", freq_opts, index=2, label_visibility="collapsed")

    if freq_choice == "Trimestral":
        freq_code = "Q"   # '3M' o 'Q'
        label_x = "Trimestre"
        shift_periods = 4
    elif freq_choice == "Semestral":
        freq_code = "2Q"  # '6M' o '2Q'
        label_x = "Semestre"
        shift_periods = 2
    else:
        freq_code = "A"
        label_x = "Año"
        shift_periods = 1

    # -----------------------------
    # Seleccion "Ver por"
    # -----------------------------
    vistas = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vistas, horizontal=True)

    if df.empty:
        st.warning("No hay datos tras los filtros en Flujos Agregados.")
        return

    # Paleta de colores
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

    # -----------------------------
    # Graficos Stacked
    # -----------------------------
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
            title="",  # Sin título interno
            labels={
                "Periodo": label_x,
                "value_usd_millions": "Monto (Millones USD)"
            }
        )
        fig_time.update_layout(bargap=0, bargroupgap=0)
        fig_time.update_traces(marker_line_color="white", marker_line_width=1)
        fig_time.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_time, use_container_width=True)

    else:
        # MODO "Sectores"
        if "Sector" not in df.columns:
            st.warning("No existe la columna 'Sector' en OUTGOING_COMMITMENT_IADB.")
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

        sorted_top7 = sorted(top_7)
        unique_sectors = sorted_top7 + ["OTROS"]

        # Stacked bar normal
        fig_normal = px.bar(
            df_agg_sec,
            x="Periodo",
            y="value_usd_millions",
            color="Sector_stack",
            barmode="stack",
            category_orders={"Sector_stack": unique_sectors},
            color_discrete_sequence=color_palette,
            title="",  # Sin título interno
            labels={
                "Periodo": label_x,
                "Sector_stack": "Sector",
                "value_usd_millions": "Monto (Millones USD)"
            }
        )
        fig_normal.update_layout(bargap=0, bargroupgap=0)
        fig_normal.update_traces(marker_line_color="white", marker_line_width=1)
        fig_normal.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False  # Ocultamos la leyenda en el stacked normal
        )

        # Percentage stacked bar
        pivoted = df_agg_sec.pivot(index="Periodo", columns="Sector_stack", values="value_usd_millions").fillna(0)
        sums = pivoted.sum(axis=1)
        pivot_pct = pivoted.div(sums, axis=0) * 100
        df_pct = pivot_pct.reset_index().melt(id_vars="Periodo", var_name="Sector_stack", value_name="pct_value")

        fig_pct = px.bar(
            df_pct,
            x="Periodo",
            y="pct_value",
            color="Sector_stack",
            barmode="stack",
            category_orders={"Sector_stack": unique_sectors},
            color_discrete_sequence=color_palette,
            title="",  # Sin título interno
            labels={
                "Periodo": label_x,
                "Sector_stack": "Sector",
                "pct_value": "Porcentaje (%)"
            }
        )
        fig_pct.update_layout(
            bargap=0,
            bargroupgap=0,
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
        )
        fig_pct.update_traces(marker_line_color="white", marker_line_width=1)

        # Mostrar ambos gráficos en columnas, uno al lado del otro
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Evolución de aprobaciones (Millones USD)")
            st.plotly_chart(fig_normal, use_container_width=True)

        with col2:
            st.subheader("Evolución de aprobaciones %")
            st.plotly_chart(fig_pct, use_container_width=True)

    st.info("Flujos agregados: Aprobaciones (Outgoing Commitments).")

    # ----------------------------------------------------------------------------------
    # NUEVA SECCIÓN: DOS GRÁFICOS DE TASA DE CRECIMIENTO INTERANUAL (LINEAS SUAVIZADAS)
    # ----------------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("## Tasa de Crecimiento Interanual (YoY)")

    # -----------------------------
    # 1) Gráfico principal (Global/Región/País)
    # -----------------------------
    df_global_all = df_original.copy()
    df_global_all["transactiondate_isodate"] = pd.to_datetime(df_global_all["transactiondate_isodate"])
    df_global_all = df_global_all[
        (df_global_all["transactiondate_isodate"] >= start_ts) &
        (df_global_all["transactiondate_isodate"] <= end_ts)
    ]

    # dataset de la región
    if sel_region != "Todas":
        df_region_all = df_global_all[df_global_all["region"] == sel_region].copy()
    else:
        df_region_all = pd.DataFrame()

    # dataset de países
    list_countries_data_all = []
    if sel_region != "Todas" and ("Todas" not in sel_paises):
        for c in sel_paises:
            temp_df = df_region_all[df_region_all["recipientcountry_codename"] == c]
            if not temp_df.empty:
                list_countries_data_all.append((c, temp_df))

    yoy_list_all = []
    # i) Global
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

    # ii) Región
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

    # iii) Países
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

    colYoY1, colYoY2 = st.columns(2)

    with colYoY1:
        st.markdown("**(Izquierda) Crecimiento Interanual - General**")
        if yoy_list_all:
            df_yoy_final_all = pd.concat(yoy_list_all, ignore_index=True)
            fig_yoy_all = px.line(
                df_yoy_final_all,
                x="Periodo",
                y="yoy",
                color="Categoria",
                markers=True,
                title="",  # Sin título interno
                labels={
                    "Periodo": "Periodo",
                    "yoy": "Crec. Interanual (%)",
                    "Categoria": ""
                }
            )
            # Suavizamos líneas y agregamos línea punteada en y=0
            fig_yoy_all.update_traces(line_shape="spline")
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
            st.warning("No se pudo calcular Tasa de Crecimiento Interanual - vista general.")

    # -----------------------------
    # 2) Gráfico por modalidad_general
    # -----------------------------
    with colYoY2:
        st.markdown("**(Derecha) Crecimiento Interanual - Por Modalidad**")

        # - Filtramos df_global_all según modalidad
        df_global_mod = df_global_all.copy()
        if sel_mod != "Todas":
            df_global_mod = df_global_mod[df_global_mod["modalidad_general"] == sel_mod]

        # - Región
        if sel_region != "Todas":
            df_region_mod = df_global_mod[df_global_mod["region"] == sel_region].copy()
        else:
            df_region_mod = pd.DataFrame()

        # - Países
        list_countries_data_mod = []
        if sel_region != "Todas" and ("Todas" not in sel_paises):
            for c in sel_paises:
                temp_df = df_region_mod[df_region_mod["recipientcountry_codename"] == c]
                if not temp_df.empty:
                    list_countries_data_mod.append((c, temp_df))

        yoy_list_mod = []

        # i) Global (para la modalidad)
        if not df_global_mod.empty:
            yoy_g_mod = compute_yoy(
                df_global_mod,
                date_col="transactiondate_isodate",
                value_col="value_usd",
                freq_code=freq_code,
                shift_periods=shift_periods
            )
            if sel_mod == "Todas":
                yoy_g_mod["Categoria"] = "Global (Todas Modalidades)"
            else:
                yoy_g_mod["Categoria"] = f"Global (Mod: {sel_mod})"
            yoy_list_mod.append(yoy_g_mod)

        # ii) Región (para la modalidad)
        if not df_region_mod.empty:
            if sel_mod == "Todas":
                cat_name = f"Región {sel_region} (Todas)"
            else:
                cat_name = f"Región {sel_region} (Mod: {sel_mod})"
            yoy_r_mod = compute_yoy(
                df_region_mod,
                date_col="transactiondate_isodate",
                value_col="value_usd",
                freq_code=freq_code,
                shift_periods=shift_periods
            )
            yoy_r_mod["Categoria"] = cat_name
            yoy_list_mod.append(yoy_r_mod)

        # iii) País(es)
        for (country_name, df_country_mod) in list_countries_data_mod:
            yoy_c_mod = compute_yoy(
                df_country_mod,
                date_col="transactiondate_isodate",
                value_col="value_usd",
                freq_code=freq_code,
                shift_periods=shift_periods
            )
            yoy_c_mod["Categoria"] = f"{country_name} (Mod: {sel_mod})"
            yoy_list_mod.append(yoy_c_mod)

        if yoy_list_mod:
            df_yoy_final_mod = pd.concat(yoy_list_mod, ignore_index=True)
            fig_yoy_mod = px.line(
                df_yoy_final_mod,
                x="Periodo",
                y="yoy",
                color="Categoria",
                markers=True,
                title="",  # Sin título interno
                labels={
                    "Periodo": "Periodo",
                    "yoy": "Crec. Interanual (%)",
                    "Categoria": ""
                }
            )
            # Suavizamos líneas y agregamos línea punteada en y=0
            fig_yoy_mod.update_traces(line_shape="spline")
            fig_yoy_mod.add_hline(
                y=0,
                line_dash="dot",
                line_color="white"
            )
            fig_yoy_mod.update_layout(
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
            st.plotly_chart(fig_yoy_mod, use_container_width=True)
        else:
            st.warning("No se pudo calcular Tasa de Crecimiento Interanual por modalidad.")

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
    if "apertura_date" in df_temp.columns:  # ejemplo de fecha
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
                title="",  # Sin título interno
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
    # Suponiendo hay columns lat, lon
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
            title="",  # Sin título interno
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
