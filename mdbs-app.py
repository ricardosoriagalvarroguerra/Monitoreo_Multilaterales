import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

import matplotlib.colors as mcolors
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

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
    # Dataset principal (ejemplo)
    df_iadb = pd.read_parquet("IADB_DASH_BDD.parquet")

    # Dataset con lat/long en la columna 'point_pos'
    df_location = pd.read_parquet("location_iadb.parquet")
    # Separar 'point_pos' en columnas 'Latitude' y 'Longitude'
    df_location[["Latitude", "Longitude"]] = df_location["point_pos"].str.split(",", expand=True)
    df_location["Latitude"] = df_location["Latitude"].astype(float)
    df_location["Longitude"] = df_location["Longitude"].astype(float)

    # Dataset para la tabla de actividad por país (nuevo)
    df_activity = pd.read_parquet("activity_iadb.parquet")

    # NUEVO: Dataset outgoing con transactiondate_isodate, Sector y value_usd
    df_outgoing = pd.read_parquet("outgoing_iadb.parquet")

    # Diccionario de DataFrames
    datasets = {
        "IADB_DASH_BDD": df_iadb,
        "LOCATION_IADB": df_location,
        "ACTIVITY_IADB": df_activity,
        "OUTGOING_IADB": df_outgoing  # Reemplazo del anterior disbursmentes
    }
    return datasets

DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2. CREACIÓN DEL RENDERER DE PYGWALKER (CACHÉ) CON KERNEL COMPUTATION
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer_by_name(dataset_name: str) -> StreamlitRenderer:
    """
    Crea un StreamlitRenderer para el dataset especificado.
    kernel_computation=True para alto rendimiento.
    """
    df = DATASETS[dataset_name]
    renderer = StreamlitRenderer(
        df,
        kernel_computation=True  # Acelera cálculos en grandes datasets
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
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analiza aprobaciones y desembolsos anuales.</p>', unsafe_allow_html=True)

    # Opciones de filtros
    flujo_opciones = ["Aprobaciones", "Desembolsos"]
    mdb_opciones = ["IADB"]

    # Filtros en la barra lateral
    st.sidebar.header("Filtros")
    tipo_flujo = st.sidebar.selectbox("Selecciona el tipo de flujo:", flujo_opciones)
    mdb = st.sidebar.selectbox("Selecciona MDB:", mdb_opciones)

    st.write("Aquí vendría la lógica para flujos agregados, según tus datasets.")

# -----------------------------------------------------------------------------
# PÁGINA 4: GEODATA (MODIFICADA)
# -----------------------------------------------------------------------------
def geodata():
    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales de los proyectos.</p>', unsafe_allow_html=True)

    # 1. Selector de subpágina en la barra lateral
    vista_geo = st.sidebar.radio(
        "Selecciona la vista de GeoData:",
        ("Mapa y Barras", "Proporción Sectores")
    )

    # -- VISTA A: "Mapa y Barras" (usando LOCATION_IADB) -----------------------
    if vista_geo == "Mapa y Barras":
        data_location = DATASETS["LOCATION_IADB"].copy()

        if "Sector" not in data_location.columns or "recipientcountry_codename" not in data_location.columns:
            st.error("Faltan columnas necesarias ('Sector' o 'recipientcountry_codename') en LOCATION_IADB.")
            return

        sectores_disponibles = data_location['Sector'].dropna().unique()

        st.sidebar.header("Filtros (GeoData)")
        filtro_sector = st.sidebar.selectbox(
            "Selecciona un sector:",
            options=sectores_disponibles
        )

        data_filtrada_loc = data_location[data_location['Sector'] == filtro_sector]

        if data_filtrada_loc.empty:
            st.warning("No se encontraron datos para el sector seleccionado.")
            return

        # Mapa interactivo
        fig_map = px.scatter_mapbox(
            data_filtrada_loc,
            lat="Latitude",
            lon="Longitude",
            color="Sector",
            color_discrete_map={filtro_sector: "#ef233c"},  # Mismo color
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

        # Conteo de proyectos por país
        conteo_por_pais = (
            data_filtrada_loc
            .groupby("recipientcountry_codename")["iatiidentifier"]
            .nunique()
            .reset_index(name="Cantidad de Proyectos")
        )
        conteo_por_pais = conteo_por_pais.sort_values(by="Cantidad de Proyectos", ascending=True)

        # Gráfico de barras horizontal (sin fondo, sin títulos)
        fig_bars = go.Figure()
        fig_bars.add_trace(
            go.Bar(
                x=conteo_por_pais["Cantidad de Proyectos"],
                y=conteo_por_pais["recipientcountry_codename"],
                orientation='h',
                marker_color="#ef233c",
                text=conteo_por_pais["Cantidad de Proyectos"],
                textposition="outside"
            )
        )
        fig_bars.update_layout(
            title="Cantidad de Proyectos por País",
            xaxis_title=None,
            yaxis_title=None,
            height=600,
            margin=dict(l=20, r=20, t=60, b=20),
            font_color="#FFFFFF",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        # Ocultar grid y ticks
        fig_bars.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
        fig_bars.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)

        col_map, col_bar = st.columns([2, 2], gap="medium")
        with col_map:
            st.plotly_chart(fig_map, use_container_width=True)
        with col_bar:
            st.plotly_chart(fig_bars, use_container_width=True)

    # -- VISTA B: "Proporción Sectores" (usando OUTGOING_IADB) -----------
    elif vista_geo == "Proporción Sectores":
        st.markdown("### Proporción de Proyectos por Sector (Waffle Chart)")

        # 1. Cargar datos outgoing
        data_outgoing = DATASETS["OUTGOING_IADB"].copy()

        # 2. Convertir transactiondate_isodate a datetime y extraer año
        data_outgoing["transactiondate_isodate"] = pd.to_datetime(
            data_outgoing["transactiondate_isodate"], errors="coerce"
        )
        data_outgoing["year"] = data_outgoing["transactiondate_isodate"].dt.year

        # 3. Crear filtro de rango de años en la barra lateral
        min_year = int(data_outgoing["year"].min())
        max_year = int(data_outgoing["year"].max())
        st.sidebar.header("Filtros (Waffle Chart)")
        rango_anios = st.sidebar.slider(
            "Selecciona el rango de años:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )

        # 4. Filtrar data_outgoing según el rango de años
        data_filtrada = data_outgoing[
            (data_outgoing["year"] >= rango_anios[0]) &
            (data_outgoing["year"] <= rango_anios[1])
        ].copy()

        # 5. Agrupar por Sector y sumar value_usd
        conteo_sectores = (
            data_filtrada
            .groupby("Sector")["value_usd"]
            .sum()
            .reset_index(name="TotalValueUSD")
            .sort_values(by="TotalValueUSD", ascending=False)
        )

        # 6. Crear DataFrame para el waffle
        def generate_waffle_data(
            df, 
            category_col="Sector", 
            value_col="TotalValueUSD", 
            total_squares=400,  # 20x20
            grid_size=20
        ):
            """
            Crea un grid de total_squares y asigna celdas a cada categoría 
            según la proporción de 'value_col' en la suma total.
            Retorna un DataFrame con columnas: [category, x, y].
            """
            total = df[value_col].sum()
            # Calcula cuántas celdas le tocan a cada sector (round)
            df["num_celdas"] = (
                (df[value_col] / total * total_squares)
                .round().astype(int)
            )

            waffle_list = []
            for _, row in df.iterrows():
                waffle_list += [row[category_col]] * row["num_celdas"]

            # Ajuste si sobran o faltan celdas
            if len(waffle_list) < total_squares:
                waffle_list += ["Otros"] * (total_squares - len(waffle_list))
            elif len(waffle_list) > total_squares:
                waffle_list = waffle_list[:total_squares]

            waffle_df = pd.DataFrame({"category": waffle_list})
            waffle_df["index"] = waffle_df.index
            waffle_df["x"] = waffle_df["index"] % grid_size
            waffle_df["y"] = waffle_df["index"] // grid_size
            return waffle_df

        waffle_df = generate_waffle_data(conteo_sectores)

        # 7. Graficar scatter con símbolos "square" para simular waffle
        #    Paleta “seria y formal”: por ej. px.colors.sequential.Blues
        color_sequence = px.colors.sequential.Blues

        fig_waffle = px.scatter(
            waffle_df,
            x="x",
            y="y",
            color="category",
            color_discrete_sequence=color_sequence,
            width=650,
            height=650
        )

        # Ajustes visuales para simular un waffle
        fig_waffle.update_traces(
            marker=dict(
                size=22,            # tamaño de los cuadrados
                symbol="square",    # forma cuadrada
                line=dict(width=0)  # sin contorno
            )
        )
        fig_waffle.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor="#1E1E1E",
            paper_bgcolor="#1E1E1E",
            font_color="#FFFFFF",
            legend_title_text="Sector"
        )
        # Invertir el eje y para que la fila 0 aparezca arriba
        fig_waffle.update_yaxes(autorange="reversed")

        # Mostrar waffle chart
        st.plotly_chart(fig_waffle, use_container_width=True)

        # 8. Opcional: mostrar tabla con valores reales
        with st.expander("Ver datos por Sector"):
            st.dataframe(conteo_sectores.reset_index(drop=True))

# -----------------------------------------------------------------------------
# PÁGINA 5: ANÁLISIS EXPLORATORIO (PYGWALKER)
# -----------------------------------------------------------------------------
def analisis_exploratorio():
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con PyGWalker (alto rendimiento).</p>', unsafe_allow_html=True)

    st.sidebar.header("Selecciona la BDD para analizar")
    selected_dataset = st.sidebar.selectbox("Base de datos:", list(DATASETS.keys()))

    # Obtenemos el renderer con kernel_computation=True
    renderer = get_pyg_renderer_by_name(selected_dataset)

    # Mostramos la interfaz exploratoria
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
