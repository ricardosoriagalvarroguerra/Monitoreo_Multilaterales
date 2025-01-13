import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

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

    # Dataset para la tabla de actividad por país
    df_activity = pd.read_parquet("activity_iadb.parquet")

    # Dataset con transactiondate_isodate, Sector y value_usd
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
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analiza aprobaciones y desembolsos anuales.</p>', unsafe_allow_html=True)

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

    # -- VISTA A: "Mapa y Barras" ---------------------------------------------
    if vista_geo == "Mapa y Barras":
        data_location = DATASETS["LOCATION_IADB"].copy()

        if "Sector" not in data_location.columns or "recipientcountry_codename" not in data_location.columns:
            st.error("Faltan columnas necesarias ('Sector' o 'recipientcountry_codename') en LOCATION_IADB.")
            return

        # Filtro de sector
        st.sidebar.header("Filtros (Mapa y Barras)")
        sectores_disponibles = data_location['Sector'].dropna().unique()
        filtro_sector = st.sidebar.selectbox(
            "Selecciona un sector:",
            options=sectores_disponibles
        )

        # Filtramos
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
            color_discrete_map={filtro_sector: "#ef233c"},
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

        # Gráfico de barras horizontal (con etiquetas de datos, sin título del eje Y)
        fig_bars = go.Figure()
        fig_bars.add_trace(
            go.Bar(
                x=conteo_por_pais["Cantidad de Proyectos"],
                y=conteo_por_pais["recipientcountry_codename"],
                orientation='h',
                marker_color="#ef233c",
                text=conteo_por_pais["Cantidad de Proyectos"],    # Etiquetas de datos
                textposition="outside"                            # Ubicación de etiquetas
            )
        )
        fig_bars.update_layout(
            title="Cantidad de Proyectos por País",
            xaxis_title="Cantidad de Proyectos",  # Lo dejamos o puedes quitarlo si deseas
            yaxis_title=None,                     # Se quita el título del eje Y
            height=600,
            margin=dict(l=20, r=20, t=60, b=20),
            font_color="#FFFFFF",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        # Ocultar grid y ticks
        fig_bars.update_xaxes(showgrid=False, zeroline=False)
        fig_bars.update_yaxes(showgrid=False, zeroline=False)

        col_map, col_bar = st.columns([2, 2], gap="medium")
        with col_map:
            st.plotly_chart(fig_map, use_container_width=True)
        with col_bar:
            st.plotly_chart(fig_bars, use_container_width=True)

    # -- VISTA B: "Proporción Sectores" ---------------------------------------
    elif vista_geo == "Proporción Sectores":
        st.markdown("### Proporción de un Sector vs. Total (Waffle Chart)")

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

        # Filtro de sector (uno solo)
        sectores_disponibles_2 = sorted(data_outgoing["Sector"].dropna().unique())
        filtro_sector_2 = st.sidebar.selectbox(
            "Selecciona un sector para ver su proporción:",
            options=sectores_disponibles_2
        )

        # 4. Filtrar data_outgoing según el rango de años
        data_filtrada = data_outgoing[
            (data_outgoing["year"] >= rango_anios[0]) &
            (data_outgoing["year"] <= rango_anios[1])
        ].copy()

        if data_filtrada.empty:
            st.warning("No hay datos para los años seleccionados.")
            return

        # 5. Calcular el total de value_usd y el valor para el sector elegido
        total_value = data_filtrada["value_usd"].sum()
        sector_value = data_filtrada.loc[data_filtrada["Sector"] == filtro_sector_2, "value_usd"].sum()

        # Crear un DataFrame con 2 filas: [Sector Escogido, "Otros"]
        df_sector_vs_otros = pd.DataFrame({
            "Category": [filtro_sector_2, "Otros"],
            "Amount": [sector_value, total_value - sector_value]
        })

        # 6. Función para generar waffle con 2 categorías
        def generate_waffle_data(
            df, category_col="Category", value_col="Amount",
            total_squares=100, grid_size=10
        ):
            """
            Crea un grid de total_squares (por default 100) con 2 o más categorías.
            """
            total = df[value_col].sum()
            # Calculamos el # de celdas para cada categoría
            df["num_celdas"] = (
                (df[value_col] / total * total_squares)
                .round().astype(int)
            )

            waffle_list = []
            for _, row in df.iterrows():
                waffle_list += [row[category_col]] * row["num_celdas"]

            # Ajuste si falta o sobra
            if len(waffle_list) < total_squares:
                waffle_list += ["Otros"] * (total_squares - len(waffle_list))
            elif len(waffle_list) > total_squares:
                waffle_list = waffle_list[:total_squares]

            waffle_df = pd.DataFrame({"category": waffle_list})
            waffle_df["index"] = waffle_df.index
            waffle_df["x"] = waffle_df["index"] % grid_size
            waffle_df["y"] = waffle_df["index"] // grid_size
            return waffle_df

        # 7. Generar el waffle con 100 celdas (10x10)
        waffle_df = generate_waffle_data(df_sector_vs_otros, 
                                         category_col="Category", 
                                         value_col="Amount",
                                         total_squares=100,  # 10 x 10
                                         grid_size=10)

        # 8. Graficar
        # 2 categorías => se puede usar una paleta pequeña o algo sencillo
        color_sequence = ["#ef233c", "#8d99ae"]  # p.ej. sector=rojo, otros=gris

        fig_waffle = px.scatter(
            waffle_df,
            x="x",
            y="y",
            color="category",
            color_discrete_sequence=color_sequence,
            width=450,
            height=450
        )

        # Ajustes de waffle
        fig_waffle.update_traces(
            marker=dict(
                size=22,
                symbol="square",
                line=dict(width=0)
            )
        )
        fig_waffle.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor="#1E1E1E",
            paper_bgcolor="#1E1E1E",
            font_color="#FFFFFF",
            legend_title_text=""
        )
        fig_waffle.update_yaxes(autorange="reversed")

        # 9. Calcular porcentaje
        if total_value > 0:
            sector_pct = (sector_value / total_value) * 100
        else:
            sector_pct = 0.0

        # Mostrar
        col_waffle, col_pct = st.columns([1, 1], gap="large")

        with col_waffle:
            st.plotly_chart(fig_waffle, use_container_width=True)

        with col_pct:
            st.markdown("#### Resultado")
            st.write(f"**Sector seleccionado**: {filtro_sector_2}")
            st.write(f"**Años analizados**: {rango_anios[0]} - {rango_anios[1]}")
            st.write(f"**Total (USD)**: {total_value:,.2f}")
            st.write(f"**{filtro_sector_2} (USD)**: {sector_value:,.2f}")
            st.write(f"**Porcentaje**: {sector_pct:.2f}%")

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
