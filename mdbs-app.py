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
    """Lee y devuelve los DataFrames usados en la aplicación."""
    # Dataset principal
    df_iadb = pd.read_parquet("IADB_DASH_BDD.parquet")

    # Dataset con lat/long en la columna 'point_pos'
    df_location = pd.read_parquet("location_iadb.parquet")
    df_location[["Latitude", "Longitude"]] = df_location["point_pos"].str.split(",", expand=True)
    df_location["Latitude"] = df_location["Latitude"].astype(float)
    df_location["Longitude"] = df_location["Longitude"].astype(float)

    # Dataset para la tabla de actividad por país
    df_activity = pd.read_parquet("activity_iadb.parquet")

    # Dataset con transactiondate_isodate, Sector y value_usd (para el waffle)
    df_outgoing = pd.read_parquet("outgoing_commitment_iadb.parquet")

    # Diccionario de DataFrames
    datasets = {
        "IADB_DASH_BDD": df_iadb,
        "LOCATION_IADB": df_location,
        "ACTIVITY_IADB": df_activity,
        "OUTGOING_IADB": df_outgoing
    }
    return datasets

DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2. CREACIÓN DEL RENDERER DE PYGWALKER (CACHÉ)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str) -> StreamlitRenderer:
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(
        df,
        kernel_computation=True
    )
    return renderer

# -----------------------------------------------------------------------------
# PÁGINA 1: MONITOREO MULTILATERALES
# -----------------------------------------------------------------------------
def monitoreo_multilaterales():
    st.markdown('<h1 class="title">Monitoreo Multilaterales</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Página principal para el seguimiento de proyectos e información multinacional.</p>', unsafe_allow_html=True)
    
    st.write("Contenido de la página 'Monitoreo Multilaterales'.")

# -----------------------------------------------------------------------------
# PÁGINA 2: COOPERACIONES TÉCNICAS
# -----------------------------------------------------------------------------
def cooperaciones_tecnicas():
    st.markdown('<h1 class="title">Cooperaciones Técnicas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza y analiza las cooperaciones técnicas aprobadas según país y año.</p>', unsafe_allow_html=True)

    data = DATASETS["IADB_DASH_BDD"].copy()
    data["Approval Date"] = pd.to_datetime(data["Approval Date"], errors="coerce")
    data["Year"] = data["Approval Date"].dt.year

    st.sidebar.header("Filtros (Cooperaciones Técnicas)")
    st.sidebar.write("Utiliza estos filtros para refinar la información mostrada:")

    paises_disponibles = ["General", "Argentina", "Bolivia", "Brazil", "Paraguay", "Uruguay"]
    filtro_pais = st.sidebar.multiselect(
        "Selecciona uno o varios países (o General para todos):",
        options=paises_disponibles,
        default=["General"]
    )
    
    rango_anios = st.sidebar.slider(
        "Selecciona el rango de años:",
        2000,
        2024,
        (2000, 2024)
    )
    
    # Filtrar por año
    data = data[(data["Year"] >= 2000) & (data["Year"] <= 2024)]

    if "General" not in filtro_pais:
        data_tc = data[
            (data["Project Type"] == "Technical Cooperation")
            & (data["Project Country"].isin(filtro_pais))
            & (data["Year"] >= rango_anios[0])
            & (data["Year"] <= rango_anios[1])
        ]
        data_tc = data_tc.groupby(["Project Country", "Year"])["Approval Amount"].sum().reset_index()
    else:
        data_tc = data[
            (data["Project Type"] == "Technical Cooperation")
            & (data["Year"] >= rango_anios[0])
            & (data["Year"] <= rango_anios[1])
        ]
        data_tc = data_tc.groupby("Year")["Approval Amount"].sum().reset_index()
    
    st.subheader("Serie de Tiempo de Monto Aprobado")

    color_map = {
        "Argentina": "#8ecae6",
        "Bolivia": "#41af20",
        "Brazil": "#ffb703",
        "Paraguay": "#d00000",
        "Uruguay": "#1c5d99",
    }

    # Gráfico de línea
    if "General" not in filtro_pais:
        fig_line = px.line(
            data_tc,
            x="Year",
            y="Approval Amount",
            color="Project Country",
            title="Evolución del Monto Aprobado (Technical Cooperation)",
            labels={
                "Year": "Año",
                "Approval Amount": "Monto Aprobado",
                "Project Country": "País"
            },
            markers=True,
            color_discrete_map=color_map
        )
    else:
        fig_line = px.line(
            data_tc,
            x="Year",
            y="Approval Amount",
            title="Evolución del Monto Aprobado (Technical Cooperation)",
            labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
            markers=True
        )
        fig_line.update_traces(line_color="#ee6c4d")

    fig_line.update_traces(line_shape='spline')
    fig_line.update_layout(
        legend_title_text="",
        font_color="#FFFFFF",
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(gridcolor="#555555"),
        yaxis=dict(gridcolor="#555555"),
        title_font_color="#FFFFFF"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Porcentaje de TCs
    st.subheader("Porcentaje de Cooperaciones Técnicas en el Total")

    data_filtrado = data[
        (data["Year"] >= rango_anios[0]) & (data["Year"] <= rango_anios[1])
    ]
    resumen_anual_total = data_filtrado.groupby("Year")["Approval Amount"].sum().reset_index()

    if "General" not in filtro_pais:
        resumen_anual_tc = data_tc.groupby(["Year"])["Approval Amount"].sum().reset_index()
    else:
        resumen_anual_tc = data_tc

    porcentaje_tc = resumen_anual_tc.merge(
        resumen_anual_total,
        on="Year",
        suffixes=("_tc", "_total")
    )
    porcentaje_tc["Porcentaje TC"] = (
        porcentaje_tc["Approval Amount_tc"] / porcentaje_tc["Approval Amount_total"] * 100
    )
    
    fig_lollipop = go.Figure()
    for _, row in porcentaje_tc.iterrows():
        fig_lollipop.add_trace(
            go.Scatter(
                x=[0, row["Porcentaje TC"]],
                y=[row["Year"], row["Year"]],
                mode="lines",
                line=dict(color="#999999", width=2),
                showlegend=False
            )
        )
    fig_lollipop.add_trace(
        go.Scatter(
            x=porcentaje_tc["Porcentaje TC"],
            y=porcentaje_tc["Year"],
            mode="markers+text",
            marker=dict(color="crimson", size=10),
            text=round(porcentaje_tc["Porcentaje TC"], 2),
            textposition="middle right",
            textfont=dict(color="#FFFFFF"),
            name="Porcentaje TC"
        )
    )

    fig_lollipop.update_layout(
        title="Porcentaje de Cooperaciones Técnicas en el Total de Aprobaciones",
        xaxis_title="Porcentaje (%)",
        yaxis_title="Año",
        xaxis=dict(showgrid=True, zeroline=False, gridcolor="#555555"),
        yaxis=dict(showgrid=False, zeroline=False),
        font_color="#FFFFFF",
        height=600,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig_lollipop, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 3: FLUJOS AGREGADOS
# -----------------------------------------------------------------------------
def flujos_agregados():
    """
    Página principal de Flujos Agregados con subpáginas:
    - Aprobaciones
    - Desembolsos
    - Instrumentos
    """
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analiza aprobaciones y desembolsos anuales.</p>', unsafe_allow_html=True)

    subpagina = st.sidebar.radio(
        "Selecciona la subpágina:",
        ("Aprobaciones", "Desembolsos", "Instrumentos")
    )

    if subpagina == "Aprobaciones":
        st.markdown("## Aprobaciones")

        # ---------------------------------------------------------------------
        # 1. CARGAR Y PREPARAR DATOS
        # ---------------------------------------------------------------------
        data = DATASETS["OUTGOING_IADB"].copy()

        # Convertimos columna de fecha a datetime
        data["transactiondate_isodate"] = pd.to_datetime(data["transactiondate_isodate"], errors="coerce")
        data["year"] = data["transactiondate_isodate"].dt.year

        # Resumen global (sin filtro), agrupado por año
        resumen_global = (
            data.groupby("year")["value_usd"]
            .sum()
            .reset_index()
            .rename(columns={"year": "Año", "value_usd": "Monto (USD)"})
            .sort_values("Año")
        )

        # Calcular variación interanual (YoY) como %:
        # yoy = (monto_año_actual - monto_año_anterior) / monto_año_anterior * 100
        resumen_global["Var. Interanual (%)"] = (
            resumen_global["Monto (USD)"].pct_change() * 100
        ).fillna(0)

        # ---------------------------------------------------------------------
        # 2. CREAR FILTROS: REGIÓN Y PAÍS
        # ---------------------------------------------------------------------
        st.sidebar.header("Filtros (Aprobaciones)")

        # Filtro por Región (MULTISELECT)
        regiones_disponibles = sorted(data["region"].dropna().unique())
        regiones_seleccionadas = st.sidebar.multiselect(
            "Selecciona una o varias regiones:",
            options=regiones_disponibles,
            default=[]  # sin nada al inicio
        )

        # Filtrar datos por las regiones seleccionadas (si hay)
        if len(regiones_seleccionadas) > 0:
            data_filtrada = data[data["region"].isin(regiones_seleccionadas)].copy()
        else:
            data_filtrada = data.copy()  # sin filtro de región

        # Filtro por País, sólo habilitado si existe al menos una región seleccionada
        if len(regiones_seleccionadas) > 0:
            paises_disponibles = sorted(data_filtrada["recipientcountry_codename"].dropna().unique())
            paises_seleccionados = st.sidebar.multiselect(
                "Selecciona uno o varios países (opcional):",
                options=paises_disponibles,
                default=[]
            )
            if len(paises_seleccionados) > 0:
                data_filtrada = data_filtrada[data_filtrada["recipientcountry_codename"].isin(paises_seleccionados)]
        else:
            # Si no hay región seleccionada, no hay filtro de países
            paises_seleccionados = []

        # Crear nuevo resumen según filtros
        resumen_filtrado = (
            data_filtrada.groupby("year")["value_usd"]
            .sum()
            .reset_index()
            .rename(columns={"year": "Año", "value_usd": "Monto (USD)"})
            .sort_values("Año")
        )
        resumen_filtrado["Var. Interanual (%)"] = (
            resumen_filtrado["Monto (USD)"].pct_change() * 100
        ).fillna(0)

        # ---------------------------------------------------------------------
        # 3. DIBUJAR GRÁFICOS (2 COLUMNAS)
        # ---------------------------------------------------------------------
        col_barras, col_lineas = st.columns(2, gap="medium")

        # ------------------- (A) GRÁFICO DE BARRAS ---------------------------
        with col_barras:
            st.subheader("Monto Total por Año")
            fig_barras = px.bar(
                resumen_filtrado,
                x="Año",
                y="Monto (USD)",
                text="Monto (USD)",
                title="",
            )
            # Quitar fondos
            fig_barras.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                font_color="#FFFFFF"
            )
            fig_barras.update_traces(textposition="outside")
            st.plotly_chart(fig_barras, use_container_width=True)

        # ------------------ (B) GRÁFICO DE LÍNEA (VAR. YoY) ------------------
        with col_lineas:
            st.subheader("Variación Interanual (%)")
            fig_lineas = px.line(
                resumen_filtrado,
                x="Año",
                y="Var. Interanual (%)",
                markers=True
            )
            fig_lineas.update_traces(
                line_shape="spline"
            )
            # Quitar fondos
            fig_lineas.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                font_color="#FFFFFF"
            )
            st.plotly_chart(fig_lineas, use_container_width=True)

    elif subpagina == "Desembolsos":
        st.markdown("## Desembolsos")
        st.markdown("### Esta sección está en desarrollo. Volveremos pronto.")

    elif subpagina == "Instrumentos":
        st.markdown("## Instrumentos")
        st.markdown("### Esta sección está en desarrollo. Volveremos pronto.")


# -----------------------------------------------------------------------------
# PÁGINA 4: GEODATA
# -----------------------------------------------------------------------------
def geodata():
    """
    Página de GeoData en la app Streamlit.
    Incluye 2 vistas:
      A) "Mapa y Barras"
      B) "Proporción Sectores" (solo un sector coloreado y el resto "vacío")
    """

    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales de los proyectos.</p>', unsafe_allow_html=True)

    # Selector de vista en la barra lateral
    vista_geo = st.sidebar.radio(
        "Selecciona la vista de GeoData:",
        ("Mapa y Barras", "Proporción Sectores")
    )

    # -------------------------------------------------------------------------
    # VISTA A: "Mapa y Barras"
    # -------------------------------------------------------------------------
    if vista_geo == "Mapa y Barras":
        # Cargamos el dataframe
        data_location = DATASETS["LOCATION_IADB"].copy()

        # Validar que existan las columnas necesarias
        if "Sector" not in data_location.columns or "recipientcountry_codename" not in data_location.columns:
            st.error("Faltan columnas ('Sector' o 'recipientcountry_codename') en LOCATION_IADB.")
            return

        st.sidebar.header("Filtros (Mapa y Barras)")
        sectores_disponibles = data_location['Sector'].dropna().unique()
        filtro_sector = st.sidebar.selectbox(
            "Selecciona un sector:",
            options=sectores_disponibles
        )

        # Filtrar por sector seleccionado
        data_filtrada_loc = data_location[data_location['Sector'] == filtro_sector]

        if data_filtrada_loc.empty:
            st.warning("No se encontraron datos para el sector seleccionado.")
            return

        # ---------------------- MAPA (Scatter Mapbox) -------------------------
        fig_map = px.scatter_mapbox(
            data_filtrada_loc,
            lat="Latitude",
            lon="Longitude",
            color="Sector",
            color_discrete_map={filtro_sector: "#ef233c"},  # color personalizado
            size_max=15,
            hover_name="iatiidentifier",
            hover_data=["recipientcountry_codename", "Sector"],
            zoom=3,
            center={
                "lat": data_filtrada_loc["Latitude"].mean(),
                "lon": data_filtrada_loc["Longitude"].mean()
            },
            height=600,
            mapbox_style="carto-darkmatter",
            title=f"Proyectos en el Sector: {filtro_sector}"
        )
        fig_map.update_layout(
            margin={"r": 20, "t": 80, "l": 20, "b": 20},
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.04,
                xanchor="right",
                x=0.99
            )
        )

        # ------------------ GRÁFICO DE BARRAS (País vs cantidad) --------------
        conteo_por_pais = (
            data_filtrada_loc
            .groupby("recipientcountry_codename")["iatiidentifier"]
            .nunique()
            .reset_index(name="Cantidad de Proyectos")
        )
        conteo_por_pais = conteo_por_pais.sort_values(by="Cantidad de Proyectos", ascending=True)

        fig_bars = go.Figure()
        fig_bars.add_trace(
            go.Bar(
                x=conteo_por_pais["Cantidad de Proyectos"],
                y=conteo_por_pais["recipientcountry_codename"],
                orientation='h',
                marker_color="#ef233c",  # mismo color del mapa
                text=conteo_por_pais["Cantidad de Proyectos"],
                textposition="outside"
            )
        )
        fig_bars.update_layout(
            title="Cantidad de Proyectos por País",
            xaxis_title="Cantidad de Proyectos",
            yaxis_title=None,  # Sin título en el eje Y
            height=600,
            margin=dict(l=20, r=20, t=60, b=20),
            font_color="#FFFFFF",
            plot_bgcolor="#1E1E1E",
            paper_bgcolor="#1E1E1E"
        )
        fig_bars.update_xaxes(showgrid=False, zeroline=False)
        fig_bars.update_yaxes(showgrid=False, zeroline=False)

        # Mostrar en dos columnas
        col_map, col_bar = st.columns([2, 2], gap="medium")
        with col_map:
            st.plotly_chart(fig_map, use_container_width=True)
        with col_bar:
            st.plotly_chart(fig_bars, use_container_width=True)

    # -------------------------------------------------------------------------
    # VISTA B: "Proporción Sectores" (solo un sector vs. vacío)
    # -------------------------------------------------------------------------
    elif vista_geo == "Proporción Sectores":
        st.markdown("### Proporción de Un Solo Sector (Waffle Chart)")

        # 1. Cargar datos
        data_outgoing = DATASETS["OUTGOING_IADB"].copy()

        # 2. Convertir fecha y extraer año
        data_outgoing["transactiondate_isodate"] = pd.to_datetime(
            data_outgoing["transactiondate_isodate"], errors="coerce"
        )
        data_outgoing["year"] = data_outgoing["transactiondate_isodate"].dt.year

        # 3. Filtros en la barra lateral
        st.sidebar.header("Filtros (Proporción de un Sector)")

        # -- Filtro por país (recipientcountry_codename) --
        countries_disponibles = sorted(data_outgoing["recipientcountry_codename"].dropna().unique())
        filtro_country = st.sidebar.selectbox(
            "Selecciona un país:",
            options=countries_disponibles,
            index=0
        )

        # -- Filtro por rango de años --
        min_year = int(data_outgoing["year"].min())
        max_year = int(data_outgoing["year"].max())
        rango_anios = st.sidebar.slider(
            "Selecciona el rango de años:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )

        # -- Filtro por Sector: un solo sector a mostrar --
        sectores_disponibles = sorted(data_outgoing["Sector"].dropna().unique())
        filtro_sector = st.sidebar.selectbox(
            "Selecciona un sector específico:",
            options=sectores_disponibles,
            index=0
        )

        # 4. Filtrar DataFrame según país y rango de años
        data_filtrada = data_outgoing[
            (data_outgoing["recipientcountry_codename"] == filtro_country) &
            (data_outgoing["year"] >= rango_anios[0]) &
            (data_outgoing["year"] <= rango_anios[1])
        ].copy()

        if data_filtrada.empty:
            st.warning("No se encontraron datos para el país y rango de años seleccionados.")
            return

        # 5. Calcular total y valor del sector elegido
        total_value = data_filtrada["value_usd"].sum()
        sector_value = data_filtrada.loc[data_filtrada["Sector"] == filtro_sector, "value_usd"].sum()
        # Resto se considera "vacío"
        resto_value = total_value - sector_value
        if resto_value < 0:
            resto_value = 0  # por si hay algo extraño de datos

        # 6. Crear DataFrame con 2 categorías: el sector y "vacío"
        df_sectores = pd.DataFrame({
            "Categoria": [filtro_sector, "Vacío"],
            "Amount": [sector_value, resto_value]
        })

        # 7. Función para generar el dataframe de celdas (Waffle)
        def generate_waffle_data(df, total_squares=100, grid_size=10):
            """
            Recibe df con columnas ['Categoria', 'Amount'] y genera un 
            waffle de total_squares celdas en una cuadricula de grid_size x grid_size.
            """
            total_amount = df["Amount"].sum()
            if total_amount == 0:
                df["num_celdas"] = 0
            else:
                df["num_celdas"] = (
                    (df["Amount"] / total_amount) * total_squares
                ).round().astype(int)

            waffle_list = []
            for _, fila in df.iterrows():
                waffle_list += [fila["Categoria"]] * fila["num_celdas"]

            # Ajustar si sobran o faltan celdas
            if len(waffle_list) < total_squares:
                waffle_list += ["Vacío"] * (total_squares - len(waffle_list))
            elif len(waffle_list) > total_squares:
                waffle_list = waffle_list[:total_squares]

            wdf = pd.DataFrame({"category": waffle_list})
            wdf["index"] = wdf.index
            wdf["x"] = wdf["index"] % grid_size
            wdf["y"] = wdf["index"] // grid_size
            return wdf

        waffle_df = generate_waffle_data(df_sectores, total_squares=100, grid_size=10)

        # 8. Asignar colores: el sector -> #c1121f, "Vacío" -> #dee2e6
        color_map = {
            filtro_sector: "#c1121f",
            "Vacío": "#dee2e6"
        }

        # Crear el color_discrete_map para Plotly
        categorias_uniq = waffle_df["category"].unique().tolist()
        discrete_map = {}
        for cat in categorias_uniq:
            if cat in color_map:
                discrete_map[cat] = color_map[cat]
            else:
                discrete_map[cat] = "#dee2e6"  # fallback

        # 9. Construir el scatter (Waffle Chart)
        fig_waffle = px.scatter(
            waffle_df,
            x="x",
            y="y",
            color="category",
            color_discrete_map=discrete_map,
            width=400,
            height=400
        )
        fig_waffle.update_traces(
            marker=dict(
                size=22,
                symbol="square",
                line=dict(width=0)
            )
        )
        fig_waffle.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF",
            legend_title_text=""
        )
        # Invertir eje Y para que el origen esté arriba
        fig_waffle.update_yaxes(autorange="reversed")

        # 10. Calcular porcentaje del sector seleccionado
        if total_value > 0:
            pct_sector = (sector_value / total_value) * 100
        else:
            pct_sector = 0

        # 11. Mostrar la métrica (value box) con el porcentaje del sector
        st.metric(
            label=f"{filtro_sector} ({filtro_country})",
            value=f"{pct_sector:,.2f}%",
            delta=None
        )

        # 12. Renderizar el waffle
        st.plotly_chart(fig_waffle, use_container_width=True)

        # Opcional: ver detalle en tabla
        with st.expander("Ver desglose"):
            st.write("Total Value:", f"{total_value:,.2f}")
            st.write(f"{filtro_sector}:", f"{sector_value:,.2f}")
            st.write("Vacío:", f"{resto_value:,.2f}")
            st.dataframe(df_sectores)



# -----------------------------------------------------------------------------
# PÁGINA 5: ANÁLISIS EXPLORATORIO (PYGWALKER)
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
    "Monitoreo Multilaterales": monitoreo_multilaterales,
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
    "Flujos Agregados": flujos_agregados,
    "GeoData": geodata,
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
