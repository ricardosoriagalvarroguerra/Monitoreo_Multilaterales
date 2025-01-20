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
    from pygwalker.api.streamlit import StreamlitRenderer
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(df, kernel_computation=True)
    return renderer

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES: BOX PLOTS
# -----------------------------------------------------------------------------
def boxplot_modalidad(df: pd.DataFrame, titulo_extra: str = ""):
    needed_cols_1 = {"modality_general", "duracion_estimada"}
    needed_cols_2 = {"modality_general", "completion_delay_years"}

    # Box Plot (Duración)
    if needed_cols_1.issubset(df.columns):
        df1 = df[df["modality_general"].notna() & df["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="modality_general",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title=f"Distribución de Duración {titulo_extra} (Modalidad)",
                labels={
                    "modality_general": "Modalidad General",
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
        df2 = df[df["modality_general"].notna() & df["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="modality_general",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title=f"Distribución de Atraso {titulo_extra} (Modalidad)",
                labels={
                    "modality_general": "Modalidad General",
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

    # Box Plot (Duración)
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

    # Box Plot (Atraso)
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

    # 1) Filtro Sector
    if "Sector" in df_filters.columns:
        list_sec = sorted(df_filters["Sector"].dropna().unique().tolist())
        opt_sec = ["General"] + list_sec
        sel_sec = st.sidebar.selectbox("Sector:", opt_sec, index=0)
        if sel_sec != "General":
            df_filters = df_filters[df_filters["Sector"] == sel_sec]

    # 2) Filtro activityscope_codename
    if "activityscope_codename" in df_filters.columns:
        list_scope = sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        opt_scope = ["General"] + list_scope
        sel_scope = st.sidebar.selectbox("activityscope_codename:", opt_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # 3) Filtro Modalidad (modality_general)
    if "modality_general" in df_filters.columns:
        list_mod = sorted(df_filters["modality_general"].dropna().unique().tolist())
        opt_mod = ["Todas"] + list_mod
        sel_mod = st.sidebar.selectbox("Modalidad:", opt_mod, index=0)
        if sel_mod != "Todas":
            df_filters = df_filters[df_filters["modality_general"] == sel_mod]

    # 4) Filtro Montos en MILLONES
    if "value_usd" in df_filters.columns:
        # primero creamos la columna 'value_usd_millions'
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000

        min_mill = float(df_filters["value_usd_millions"].min())
        max_mill = float(df_filters["value_usd_millions"].max())
        sel_mill = st.sidebar.slider(
            "Rango de Montos (Millones USD):",
            min_value=min_mill,
            max_value=max_mill,
            value=(min_mill, max_mill)
        )
        df_filters = df_filters[
            (df_filters["value_usd_millions"] >= sel_mill[0]) &
            (df_filters["value_usd_millions"] <= sel_mill[1])
        ]
    else:
        df_filters["value_usd_millions"] = None

    if df_filters.empty:
        st.warning("No hay datos tras aplicar los filtros (Ejecución).")
        return

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
                st.warning("No hay datos disponibles para 'Aprobaciones Vs Ejecución' (después de filtros).")
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
                st.warning("No hay datos disponibles para 'Planificación Vs Ejecución' (después de filtros).")
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
# SUBPÁGINA: FLUJOS AGREGADOS (Filtro 'value_usd' en millones + Modalidad)
# -----------------------------------------------------------------------------
def subpagina_flujos_agregados():
    """
    Subpágina: Flujos Agregados
      - Filtros: 
          * Región->País('Todas'), 
          * Modalidad (modality_general),
          * Frecuencia,
          * Montos (value_usd) en millones
      - "Ver por": [Fechas | Sectores]
        -> Fechas: stacked bar normal (1 color c9182c)
        -> Sectores: 
           * Stacked Ordered Bar Chart (Top 7 + 'Otros')
           * Percentage Stacked Ordered Bar Chart (sin data labels)
    """
    st.markdown('<p class="subtitle">Subpágina: Flujos Agregados</p>', unsafe_allow_html=True)

    df = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"])

    st.sidebar.subheader("Filtros (Flujos Agregados)")

    # 1) Filtro Región
    if "region" in df.columns:
        regiones = sorted(df["region"].dropna().unique().tolist())
        sel_region = st.sidebar.selectbox("Región:", ["Todas"] + regiones, 0)
        if sel_region != "Todas":
            df = df[df["region"] == sel_region]

    # 2) Filtro País (con 'Todas')
    if "recipientcountry_codename" in df.columns:
        pais_list = sorted(df["recipientcountry_codename"].dropna().unique().tolist())
        opt_paises = ["Todas"] + pais_list
        sel_paises = st.sidebar.multiselect("País(es):", opt_paises, default=["Todas"])
        if "Todas" not in sel_paises:
            if sel_paises:
                df = df[df["recipientcountry_codename"].isin(sel_paises)]
            else:
                st.warning("No se seleccionó ningún país.")
                return

    # 3) Filtro Modalidad
    if "modality_general" in df.columns:
        mods = sorted(df["modality_general"].dropna().unique().tolist())
        sel_mod = st.sidebar.selectbox("Modalidad:", ["Todas"] + mods, 0)
        if sel_mod != "Todas":
            df = df[df["modality_general"] == sel_mod]

    if df.empty:
        st.warning("No hay datos tras filtros de Región/País/Modalidad.")
        return

    # 4) Filtro Montos (value_usd) en millones
    if "value_usd" in df.columns:
        df["value_usd_millions"] = df["value_usd"] / 1_000_000
        min_million = float(df["value_usd_millions"].min())
        max_million = float(df["value_usd_millions"].max())

        sel_million = st.sidebar.slider(
            "Rango de Montos (Millones USD):",
            min_value=min_million,
            max_value=max_million,
            value=(min_million, max_million)
        )
        df = df[
            (df["value_usd_millions"] >= sel_million[0]) &
            (df["value_usd_millions"] <= sel_million[1])
        ]

    if df.empty:
        st.warning("No hay datos tras filtrar por Montos en millones (value_usd).")
        return

    # 5) Rango de Años
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

    # 6) Frecuencia
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
        label_x = "Año"

    # 7) "Ver por": Fechas | Sectores
    vista_options = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vista_options, horizontal=True)

    if df.empty:
        st.warning("No hay datos tras los filtros (Flujos Agregados).")
        return

    # Convertimos a millones para graficar
    df["value_usd_millions"] = df["value_usd"] / 1_000_000

    # Paleta invertida, 'Otros' = #4361ee
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
    # MODO "Fechas"
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

        st.subheader("Stacked Ordered Bar (Fechas) - 1 Serie")

        if df_agg.empty:
            st.warning("No hay datos en el rango de años (Fechas).")
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
    # MODO "Sectores"
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
        df_agg_sec = df_agg_sec.groupby(["Periodo", "Sector_stack"], as_index=False)["value_usd_millions"].sum()

        st.subheader("Stacked Ordered Bar Chart (Sectores)")

        if df_agg_sec.empty:
            st.warning("No hay datos luego de agrupar top 7 + 'Otros'.")
            return

        # Orden alfabético + 'Otros' final
        sorted_top7 = sorted(top_7)
        unique_sectors = sorted_top7 + ["Otros"]

        # 1) Normal
        fig_bar_normal = px.bar(
            df_agg_sec,
            x="Periodo",
            y="value_usd_millions",
            color="Sector_stack",
            barmode="stack",
            category_orders={"Sector_stack":

A continuación verás el **código completo** actualizado para incluir:

1. **Filtro de Montos (`value_usd`) en millones**: 
   - Se construye una nueva columna `value_usd_millions`, y se hace un **slider** con el rango en millones.
   - Los datos se filtran en base a ese rango (en millones), **antes** de graficar.

2. **Filtro de Modalidad (`modality_general`)**:  
   - Aparece explícitamente en las subpáginas **“Ejecución”** y **“Flujos Agregados”** (si no existía o estaba oculto, ahora lo verás claramente).
   - El usuario puede escoger “Todas” (no filtra) o seleccionar una modalidad en particular.

> Ajusta los **nombres de columnas** y las **rutas** de tus archivos `.parquet` si difieren de tu entorno real.

---

## Código Completo

```python
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
# 1) CARGA DE DATOS (CACHÉ)
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
# 2) PYGWALKER (CACHÉ)
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
    needed_cols_1 = {"modality_general", "duracion_estimada"}
    needed_cols_2 = {"modality_general", "completion_delay_years"}

    if needed_cols_1.issubset(df.columns):
        df1 = df[df["modality_general"].notna() & df["duracion_estimada"].notna()]
        if not df1.empty:
            fig1 = px.box(
                df1,
                x="modality_general",
                y="duracion_estimada",
                color_discrete_sequence=["#ef233c"],
                title=f"Distribución de Duración {titulo_extra} (Modalidad)",
                labels={
                    "modality_general": "Modalidad General",
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
        df2 = df[df["modality_general"].notna() & df["completion_delay_years"].notna()]
        if not df2.empty:
            fig2 = px.box(
                df2,
                x="modality_general",
                y="completion_delay_years",
                color_discrete_sequence=["#edf2f4"],
                title=f"Distribución de Atraso {titulo_extra} (Modalidad)",
                labels={
                    "modality_general": "Modalidad General",
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
    """
    Subpágina: Ejecución
      - Filtros: 
        * Sector
        * activityscope_codename
        * modalidad_general
        * Montos (value_usd) en MILLONES
      - Gráficos: Aprobaciones Vs Ejecución, Planificación Vs Ejecución, Box Plots
    """
    st.markdown('<p class="subtitle">Subpágina: Ejecución</p>', unsafe_allow_html=True)

    df_filters = DATASETS["ACTIVITY_IADB"].copy()
    st.sidebar.subheader("Filtros (Ejecución)")

    # 1) Filtro Sector
    if "Sector" in df_filters.columns:
        list_sec = sorted(df_filters["Sector"].dropna().unique().tolist())
        opt_sec = ["General"] + list_sec
        sel_sec = st.sidebar.selectbox("Sector:", opt_sec, index=0)
        if sel_sec != "General":
            df_filters = df_filters[df_filters["Sector"] == sel_sec]

    # 2) Filtro activityscope_codename
    if "activityscope_codename" in df_filters.columns:
        list_scope = sorted(df_filters["activityscope_codename"].dropna().unique().tolist())
        opt_scope = ["General"] + list_scope
        sel_scope = st.sidebar.selectbox("activityscope_codename:", opt_scope, index=0)
        if sel_scope != "General":
            df_filters = df_filters[df_filters["activityscope_codename"] == sel_scope]

    # 3) Filtro Modalidad (modality_general)
    if "modality_general" in df_filters.columns:
        list_mod = sorted(df_filters["modality_general"].dropna().unique().tolist())
        opt_mod = ["Todas"] + list_mod
        sel_mod = st.sidebar.selectbox("Modalidad:", opt_mod, index=0)
        if sel_mod != "Todas":
            df_filters = df_filters[df_filters["modality_general"] == sel_mod]

    # 4) Filtro Montos (MILLONES)
    if "value_usd" in df_filters.columns:
        df_filters["value_usd_millions"] = df_filters["value_usd"] / 1_000_000
        min_mill = float(df_filters["value_usd_millions"].min())
        max_mill = float(df_filters["value_usd_millions"].max())

        rango_mill = st.sidebar.slider(
            "Rango de Montos (Millones USD):",
            min_value=min_mill,
            max_value=max_mill,
            value=(min_mill, max_mill)
        )
        df_filters = df_filters[
            (df_filters["value_usd_millions"] >= rango_mill[0]) &
            (df_filters["value_usd_millions"] <= rango_mill[1])
        ]
    else:
        # si no existe value_usd, definimos la columna
        df_filters["value_usd_millions"] = None

    if df_filters.empty:
        st.warning("No hay datos tras aplicar filtros (Ejecución).")
        return

    # GRÁFICOS
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
                st.warning("No hay datos en 'Aprobaciones Vs Ejecución' después de filtrar.")
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
            st.warning(f"Faltan columnas para el scatter plot: {needed_1 - set(df_filters.columns)}")

    with colB:
        st.subheader("Planificación Vs Ejecución")
        needed_2 = {"duracion_estimada", "duracion_real"}
        if needed_2.issubset(df_filters.columns):
            df_scat2 = df_filters[
                df_filters["duracion_estimada"].notna() &
                df_filters["duracion_real"].notna()
            ]
            if df_scat2.empty:
                st.warning("No hay datos en 'Planificación Vs Ejecución' después de filtrar.")
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

    # BOX PLOTS
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


def subpagina_flujos_agregados():
    """
    Subpágina: Flujos Agregados
      - Filtros: 
          * Región->País('Todas')
          * Modalidad (modality_general)
          * Frecuencia
          * Montos (value_usd) en MILLONES
      - "Ver por": [Fechas | Sectores]
        -> Fechas: Stacked bar (1 color #c9182c)
        -> Sectores: 
           * Stacked Ordered Bar Chart (Top 7 + 'Otros')
           * Percentage Stacked Ordered Bar Chart (sin data labels)
    """
    st.markdown('<p class="subtitle">Subpágina: Flujos Agregados</p>', unsafe_allow_html=True)

    df = DATASETS["OUTGOING_COMMITMENT_IADB"].copy()
    df["transactiondate_isodate"] = pd.to_datetime(df["transactiondate_isodate"])

    st.sidebar.subheader("Filtros (Flujos Agregados)")

    # 1) Filtro Región
    if "region" in df.columns:
        regiones = sorted(df["region"].dropna().unique().tolist())
        sel_region = st.sidebar.selectbox("Región:", ["Todas"] + regiones, 0)
        if sel_region != "Todas":
            df = df[df["region"] == sel_region]

    # 2) Filtro País (multiselect con 'Todas')
    if "recipientcountry_codename" in df.columns:
        pais_list = sorted(df["recipientcountry_codename"].dropna().unique().tolist())
        opt_paises = ["Todas"] + pais_list
        sel_paises = st.sidebar.multiselect("País(es):", opt_paises, default=["Todas"])
        if "Todas" not in sel_paises:
            if sel_paises:
                df = df[df["recipientcountry_codename"].isin(sel_paises)]
            else:
                st.warning("No se seleccionó ningún país.")
                return

    # 3) Filtro Modalidad
    if "modality_general" in df.columns:
        mods = sorted(df["modality_general"].dropna().unique().tolist())
        sel_mod = st.sidebar.selectbox("Modalidad:", ["Todas"] + mods, 0)
        if sel_mod != "Todas":
            df = df[df["modality_general"] == sel_mod]

    if df.empty:
        st.warning("No hay datos tras filtros (Región, País, Modalidad).")
        return

    # 4) Filtro Montos (MILLONES)
    if "value_usd" in df.columns:
        df["value_usd_millions"] = df["value_usd"] / 1_000_000
        min_mill = float(df["value_usd_millions"].min())
        max_mill = float(df["value_usd_millions"].max())

        sel_millones = st.sidebar.slider(
            "Rango de Montos (Millones USD):",
            min_value=min_mill,
            max_value=max_mill,
            value=(min_mill, max_mill)
        )
        df = df[
            (df["value_usd_millions"] >= sel_millones[0]) &
            (df["value_usd_millions"] <= sel_millones[1])
        ]

    if df.empty:
        st.warning("No hay datos tras filtrar por Montos en millones (value_usd).")
        return

    # 5) Rango de Años
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

    # 6) Frecuencia
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
        label_x = "Año"

    # 7) "Ver por": Fechas o Sectores
    vista_options = ["Fechas", "Sectores"]
    vista = st.radio("Ver por:", vista_options, horizontal=True)

    if df.empty:
        st.warning("No hay datos tras los filtros (Flujos Agregados).")
        return

    # Paleta invertida con 'Otros' = #4361ee
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
    # (A) VISTA "Fechas" -> stacked bar con 1 color (#c9182c)
    # -------------------------------------------------------------------------
    if vista == "Fechas":
        df.set_index("transactiondate_isodate", inplace=True)
        df_agg = df["value_usd"].resample(freq_code).sum().reset_index()
        df_agg["value_usd_millions"] = df_agg["value_usd"] / 1_000_000
        df.reset_index(inplace=True)

        # Creamos "Periodo"
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
            st.warning("No hay datos en este rango de años (Fechas).")
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
        # Barras juntas, borde blanco
        fig_bar_time.update_layout(bargap=0, bargroupgap=0)
        fig_bar_time.update_traces(marker_line_color="white", marker_line_width=1)
        fig_bar_time.update_layout(
            font_color="#FFFFFF",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar_time, use_container_width=True)

    # -------------------------------------------------------------------------
    # (B) VISTA "Sectores"
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
        df_agg_sec = df_agg_sec.groupby(["Periodo", "Sector_stack"], as_index=False)["value_usd_millions"].sum()

        st.subheader("Stacked Ordered Bar Chart (Sectores)")

        if df_agg_sec.empty:
            st.warning("No hay datos tras agrupar top 7 + 'Otros'.")
            return

        # Orden alfabético + 'Otros' final
        sorted_top7 = sorted(top_7)
        unique_sectors = sorted_top7 + ["Otros"]

        # 1) Normal
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

        # 2) Porcentaje (sin data labels)
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
            # No text_auto => sin data labels
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
# OTRAS PÁGINAS (PLACEHOLDERS)
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
