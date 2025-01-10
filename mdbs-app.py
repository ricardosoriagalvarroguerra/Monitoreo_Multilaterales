import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

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
# 1. CARGA DE DATOS (CACHÉ) - LEE EL PARQUET UNA SOLA VEZ
# -----------------------------------------------------------------------------
@st.cache_data
def load_dataframes():
    """Lee y devuelve los DataFrames usados en la aplicación."""
    df_iadb = pd.read_parquet("IADB_DASH_BDD.parquet")
    
    # Si tuvieras más DataFrames, podrías cargarlos aquí y agregarlos a este dict
    datasets = {
        "IADB_DASH_BDD": df_iadb
    }
    return datasets

# Diccionario de DataFrames cargados
DATASETS = load_dataframes()

# -----------------------------------------------------------------------------
# 2. CREACIÓN DEL RENDERER DE PYGWALKER (CACHÉ)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pyg_renderer():
    """
    Instancia el StreamlitRenderer de PyGWalker con parámetros
    de alto rendimiento y lectura/escritura del spec.
    """
    df = DATASETS["IADB_DASH_BDD"]  # Tomamos el DF principal, ajústalo si deseas
    renderer = StreamlitRenderer(
        df,
        kernel_computation=True,   # Acelera cálculos para grandes datasets
        spec_io_mode="rw",         # Permite leer y escribir la configuración
        spec="./gw_config.json"    # Archivo JSON donde se guarda la config
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
    
    # Filtra el DF por año
    data = data[(data["Year"] >= 2000) & (data["Year"] <= 2024)]

    # Filtra por país (si no es "General")
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
    
    # Gráfico 1: Serie de Tiempo
    st.subheader("Serie de Tiempo de Monto Aprobado")
    color_map = {
        "Argentina": "#8ecae6",
        "Bolivia": "#41af20",
        "Brazil": "#ffb703",
        "Paraguay": "#d00000",
        "Uruguay": "#1c5d99",
    }

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

    # Gráfico 2: Porcentaje de TCs
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
    st.markdown('<p class="subtitle">Analiza la información agregada de flujos relacionados con tus proyectos.</p>', unsafe_allow_html=True)
    st.write("Contenido de la página 'Flujos Agregados'.")


# -----------------------------------------------------------------------------
# PÁGINA 4: GEODATA
# -----------------------------------------------------------------------------
def geodata():
    st.markdown('<h1 class="title">GeoData</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos geoespaciales de los proyectos.</p>', unsafe_allow_html=True)
    st.write("Contenido de la página 'GeoData'.")


# -----------------------------------------------------------------------------
# PÁGINA 5: ANÁLISIS EXPLORATORIO (PYGWALKER - STREAMLITRENDERER)
# -----------------------------------------------------------------------------
def analisis_exploratorio():
    """
    Página de Análisis Exploratorio con StreamlitRenderer de PyGwalker.
    Demonstramos el uso de tabs para distintas vistas:
      - Explorer: interfaz completa
      - Data: inicia en la pestaña "data"
      - Charts: gráficos registrados (chart(0), chart(1), etc.)
    """
    st.markdown('<h1 class="title">Análisis Exploratorio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explora datos con Pygwalker en distintas vistas.</p>', unsafe_allow_html=True)

    # Obtenemos el renderer (cacheado), con kernel_computation y spec_io_mode
    renderer = get_pyg_renderer()

    tab1, tab2, tab3 = st.tabs(["Explorer", "Data", "Charts"])

    with tab1:
        st.write("**Interfaz completa**")
        renderer.explorer(height=800)  # Vista "vis" por defecto

    with tab2:
        st.write("**Vista de Datos**")
        renderer.explorer(default_tab="data", height=800)  # Muestra la pestaña "data"

    with tab3:
        st.write("**Algunos Charts Registrados**")
        st.info("Asumiendo que hayas creado y guardado charts en la interfaz, podrían verse aquí.")
        
        st.subheader("Ejemplo: Chart(0)")
        renderer.chart(0, height=400)
        
        st.subheader("Ejemplo: Chart(1)")
        renderer.chart(1, height=400)


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
