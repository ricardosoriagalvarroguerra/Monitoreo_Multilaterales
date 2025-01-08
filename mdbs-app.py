import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# PÁGINA 1: COOPERACIONES TÉCNICAS
# -----------------------------------------------------------------------------
def cooperaciones_tecnicas():
    # Encabezados
    st.markdown('<h1 class="title">Cooperaciones Técnicas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza y analiza las cooperaciones técnicas aprobadas según país y año.</p>', unsafe_allow_html=True)

    # Cargar datos desde el archivo Parquet
    file_path = "IADB_DASH_BDD.parquet"  # Ajusta la ruta si corresponde
    data = pd.read_parquet(file_path)

    # Conversión de la columna "Approval Date" a datetime
    data["Approval Date"] = pd.to_datetime(data["Approval Date"])
    data["Year"] = data["Approval Date"].dt.year

    # -------------------------------------------------------------------------
    # SIDEBAR: FILTROS
    # -------------------------------------------------------------------------
    st.sidebar.header("Filtros")
    st.sidebar.write("Utiliza estos filtros para refinar la información mostrada:")

    # Filtro de país
    paises_disponibles = ["General", "Argentina", "Bolivia", "Brazil", "Paraguay", "Uruguay"]
    filtro_pais = st.sidebar.multiselect(
        "Selecciona uno o varios países (o General para todos):",
        options=paises_disponibles,
        default=["General"]
    )
    
    # Filtro de rango de años
    min_year = int(data["Year"].min())
    max_year = int(data["Year"].max())
    rango_anios = st.sidebar.slider(
        "Selecciona el rango de años:",
        min_year,
        max_year,
        (min_year, max_year)
    )
    
    # -------------------------------------------------------------------------
    # PROCESAMIENTO DE DATOS
    # -------------------------------------------------------------------------
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
    
    # -------------------------------------------------------------------------
    # SECCIÓN DE GRÁFICAS
    # -------------------------------------------------------------------------
    with st.container():
        st.subheader("Serie de Tiempo de Monto Aprobado")

        # Gráfico de serie de tiempo
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
                markers=True
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
        
        # Ajustes para modo oscuro
        fig_line.update_traces(line_shape='spline')
        fig_line.update_layout(
            plot_bgcolor="#2E2E2E",  # Fondo interno de la gráfica
            paper_bgcolor="rgba(0,0,0,0)",  # Fondo "transparente" que se asienta sobre #1E1E1E
            legend_title_text="",
            font_color="#FFFFFF",  # Texto claro
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(gridcolor="#555555"),
            yaxis=dict(gridcolor="#555555"),
            title_font_color="#FFFFFF"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------------------------------------------------------
    # CÁLCULO Y GRÁFICA DEL PORCENTAJE DE TCs
    # -------------------------------------------------------------------------
    with st.container():
        st.subheader("Porcentaje de Cooperaciones Técnicas en el Total")

        data_filtrado = data[
            (data["Year"] >= rango_anios[0]) 
            & (data["Year"] <= rango_anios[1])
        ]
        resumen_anual_total = data_filtrado.groupby("Year")["Approval Amount"].sum().reset_index()
        
        # Unificamos la fuente de datos usada antes (data_tc) para resumir
        if "General" not in filtro_pais:
            resumen_anual_tc = data_tc.groupby(["Year"])["Approval Amount"].sum().reset_index()
        else:
            resumen_anual_tc = data_tc

        # Merge para calcular el % respecto al total
        porcentaje_tc = resumen_anual_tc.merge(
            resumen_anual_total,
            on="Year",
            suffixes=("_tc", "_total")
        )
        porcentaje_tc["Porcentaje TC"] = (
            porcentaje_tc["Approval Amount_tc"] / porcentaje_tc["Approval Amount_total"] * 100
        )
        
        # Gráfico Lollipop Chart
        fig_lollipop = go.Figure()

        # Líneas delgadas (barras verticales)
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

        # Puntos (círculos)
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

        # Configuración del gráfico
        fig_lollipop.update_layout(
            title="Porcentaje de Cooperaciones Técnicas en el Total de Aprobaciones",
            xaxis_title="Porcentaje (%)",
            yaxis_title="Año",
            xaxis=dict(showgrid=True, zeroline=False, gridcolor="#555555"),
            yaxis=dict(showgrid=True, zeroline=False, gridcolor="#555555"),
            plot_bgcolor="#2E2E2E",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF",
            height=600,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig_lollipop, use_container_width=True)


# -----------------------------------------------------------------------------
# PÁGINA 2 (EJEMPLO): PROYECTOS DE INVERSIÓN
# -----------------------------------------------------------------------------
def proyectos_inversion():
    st.markdown('<h1 class="title">Proyectos de Inversión</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza y analiza los proyectos de inversión según tus criterios.</p>', unsafe_allow_html=True)

    # Aquí podrías incluir tu lógica, lectura de datos y gráficas específicas:
    st.write("Aquí iría el contenido de la página 'Proyectos de Inversión'.")


# -----------------------------------------------------------------------------
# PÁGINA 3 (EJEMPLO): OTROS PROYECTOS U OTRAS SECCIONES
# -----------------------------------------------------------------------------
def otros_proyectos():
    st.markdown('<h1 class="title">Otras Secciones o Proyectos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sección para visualizar y analizar otros datos o proyectos.</p>', unsafe_allow_html=True)

    # Aquí podrías incluir tu lógica, lectura de datos y gráficas específicas:
    st.write("Contenido de la página 'Otros Proyectos'.")


# -----------------------------------------------------------------------------
# DICCIONARIO DE PÁGINAS
# -----------------------------------------------------------------------------
PAGINAS = {
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
    "Proyectos de Inversión": proyectos_inversion,
    "Otros Proyectos": otros_proyectos
}

# -----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL (NAVEGACIÓN)
# -----------------------------------------------------------------------------
def main():
    st.sidebar.title("Navegación")
    seleccion = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()))
    PAGINAS[seleccion]()

# -----------------------------------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
