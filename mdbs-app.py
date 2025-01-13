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
    st.markdown('<h1 class="title">Flujos Agregados</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analiza aprobaciones y desembolsos anuales.</p>', unsafe_allow_html=True)

    st.write("Aquí vendría la lógica para flujos agregados, según tus datasets.")

# -----------------------------------------------------------------------------
# PÁGINA 4: GEODATA
# -----------------------------------------------------------------------------
def geodata():
    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales de los proyectos.</p>', unsafe_allow_html=True)

    vista_geo = st.sidebar.radio(
        "Selecciona la vista de GeoData:",
        ("Mapa y Barras", "Proporción Sectores")
    )

    # -------------------------------------------------------------------------
    # VISTA A: "Mapa y Barras"
    # -------------------------------------------------------------------------
    if vista_geo == "Mapa y Barras":
        data_location = DATASETS["LOCATION_IADB"].copy()

        if "Sector" not in data_location.columns or "recipientcountry_codename" not in data_location.columns:
            st.error("Faltan columnas necesarias ('Sector' o 'recipientcountry_codename') en LOCATION_IADB.")
            return

        st.sidebar.header("Filtros (Mapa y Barras)")
        sectores_disponibles = data_location['Sector'].dropna().unique()
        filtro_sector = st.sidebar.selectbox(
            "Selecciona un sector:",
            options=sectores_disponibles
        )

        data_filtrada_loc = data_location[data_location['Sector'] == filtro_sector]

        if data_filtrada_loc.empty:
            st.warning("No se encontraron datos para el sector seleccionado.")
            return

        # MAPA
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

        # GRÁFICO DE BARRAS (horizontal)
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
                marker_color="#ef233c",
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

        col_map, col_bar = st.columns([2, 2], gap="medium")
        with col_map:
            st.plotly_chart(fig_map, use_container_width=True)
        with col_bar:
            st.plotly_chart(fig_bars, use_container_width=True)

    # -------------------------------------------------------------------------
    # VISTA B: "Proporción Sectores" (Waffle Chart)
    # -------------------------------------------------------------------------
    elif vista_geo == "Proporción Sectores":
        st.markdown("### Proporción de Sectores (Waffle Chart)")

        # 1. Cargar datos
        data_outgoing = DATASETS["OUTGOING_IADB"].copy()

        # 2. Convertir fecha y extraer año
        data_outgoing["transactiondate_isodate"] = pd.to_datetime(
            data_outgoing["transactiondate_isodate"], errors="coerce"
        )
        data_outgoing["year"] = data_outgoing["transactiondate_isodate"].dt.year

        # 3. Filtros
        st.sidebar.header("Filtros (Proporción Sectores)")
        min_year = int(data_outgoing["year"].min())
        max_year = int(data_outgoing["year"].max())
        rango_anios = st.sidebar.slider(
            "Selecciona el rango de años:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )

        # Selección múltiple de sectores
        sectores_disponibles_waffle = sorted(data_outgoing["Sector"].dropna().unique())
        filtro_sectores = st.sidebar.multiselect(
            "Selecciona uno o varios sectores:",
            options=sectores_disponibles_waffle,
            default=[]
        )

        # 4. Filtrar por rango de años
        data_filtrada = data_outgoing[
            (data_outgoing["year"] >= rango_anios[0]) &
            (data_outgoing["year"] <= rango_anios[1])
        ].copy()

        if data_filtrada.empty:
            st.warning("No se encontraron datos en ese rango de años.")
            return

        # 5. Total y cálculo de montos
        total_value = data_filtrada["value_usd"].sum()

        # Construimos un DF con la(s) categoría(s) seleccionada(s) + "Otros"
        # El primer sector => color #9d0208
        # "Otros" => #ffffff
        # El resto => colores aleatorios en torno a 9d0208
        def random_color():
            """
            Genera un color pastel aleatorio que combine razonablemente
            con #9d0208 (simple heurística).
            """
            import colorsys
            # Generar un color HSL aleatorio y convertirlo a RGB
            h = random.random()  # 0-1
            s = 0.5 + random.random() * 0.4  # 0.5-0.9
            l = 0.4 + random.random() * 0.2  # 0.4-0.6
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            # Convertir a #RRGGBB
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

        # Armar la lista de [Category, Amount]
        sector_rows = []
        selected_sum = 0.0
        color_map = {}  # sector -> color

        for i, sector_sel in enumerate(filtro_sectores):
            sec_val = data_filtrada.loc[data_filtrada["Sector"] == sector_sel, "value_usd"].sum()
            selected_sum += sec_val
            if i == 0:
                # Primer sector => #9d0208
                color_map[sector_sel] = "#9d0208"
            else:
                color_map[sector_sel] = random_color()  # Aleatorio

            sector_rows.append([sector_sel, sec_val])

        otros_val = total_value - selected_sum
        if otros_val < 0:
            otros_val = 0.0
        # Agregamos "Otros" => #ffffff
        sector_rows.append(["Otros", otros_val])
        color_map["Otros"] = "#ffffff"

        df_sectores = pd.DataFrame(sector_rows, columns=["Sector", "Amount"])

        # 6. Función para generar waffle
        def generate_waffle_data(df, total_squares=100, grid_size=10):
            """
            Toma un DataFrame con columnas ["Sector", "Amount"] y genera un waffle de total_squares celdas.
            """
            total_amount = df["Amount"].sum()
            # calcular cuántas celdas por sector
            df["num_celdas"] = (df["Amount"] / total_amount * total_squares).round().astype(int)

            waffle_list = []
            for _, row in df.iterrows():
                waffle_list += [row["Sector"]] * row["num_celdas"]

            # Ajustes si sobra/falta
            if len(waffle_list) < total_squares:
                waffle_list += ["Otros"] * (total_squares - len(waffle_list))
            elif len(waffle_list) > total_squares:
                waffle_list = waffle_list[:total_squares]

            wdf = pd.DataFrame({"category": waffle_list})
            wdf["index"] = wdf.index
            wdf["x"] = wdf["index"] % grid_size
            wdf["y"] = wdf["index"] // grid_size
            return wdf

        waffle_df = generate_waffle_data(df_sectores, total_squares=100, grid_size=10)

        # 7. Construir color_discrete_map para Plotly
        cats_uniq = waffle_df["category"].unique().tolist()
        discrete_map = {}
        for cat in cats_uniq:
            if cat in color_map:
                discrete_map[cat] = color_map[cat]
            else:
                discrete_map[cat] = "#ffffff"  # fallback

        # 8. Crear scatter (Waffle)
        fig_waffle = px.scatter(
            waffle_df,
            x="x",
            y="y",
            color="category",
            color_discrete_map=discrete_map,
            width=500,
            height=500
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
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF",
            legend_title_text=""
        )
        fig_waffle.update_yaxes(autorange="reversed")

        # 9. Mostrar "value box" arriba del waffle chart (porcentajes)
        st.markdown("#### Porcentaje de Sectores Seleccionados")
        if total_value > 0:
            for sec, amt in sector_rows:
                if sec == "Otros":
                    continue
                pct_val = 0.0 if total_value == 0 else (amt / total_value * 100)
                st.write(f"**{sec}**: {pct_val:,.2f}%")
        else:
            st.warning("El total en 'value_usd' es 0. No se pueden calcular porcentajes.")

        st.plotly_chart(fig_waffle, use_container_width=True)

        # Muestra la tabla final
        with st.expander("Ver datos de cada categoría"):
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
