import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y CSS PERSONALIZADO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Cooperaciones Técnicas",
    page_icon="✅",
    layout="wide"
)

# CSS inline para toques de diseño (puedes ajustar colores y estilos)
st.markdown(
    """
    <style>
    /* Fondo de la app */
    .main {
        background-color: #F7F9FB;
    }

    /* Título principal */
    .title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #333333;
        margin-bottom: 0.5rem;
    }

    /* Subtítulo */
    .subtitle {
        font-size: 1.2rem;
        color: #555555;
        margin-bottom: 1rem;
    }

    /* Barras laterales */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# FUNCIÓN PARA LA PÁGINA "COOPERACIONES TÉCNICAS"
# -----------------------------------------------------------------------------
def cooperaciones_tecnicas():
    # Encabezados
    st.markdown('<h1 class="title">Cooperaciones Técnicas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visualiza y analiza las cooperaciones técnicas aprobadas según país y año.</p>', unsafe_allow_html=True)

    # Cargar datos desde el archivo Parquet
    file_path = "IADB_DASH_BDD.parquet"  # Asegúrate de usar la ruta correcta
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
        
        fig_line.update_traces(line_shape='spline')  # Línea suavizada
        fig_line.update_layout(
            plot_bgcolor="#FFFFFF", 
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            margin=dict(l=20, r=20, t=60, b=20)
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
                    line=dict(color="#888", width=2),
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
                name="Porcentaje TC"
            )
        )

        # Configuración del gráfico
        fig_lollipop.update_layout(
            title="Porcentaje de Cooperaciones Técnicas en el Total de Aprobaciones",
            xaxis_title="Porcentaje (%)",
            yaxis_title="Año",
            xaxis=dict(showgrid=True, zeroline=False),
            yaxis=dict(showgrid=True, zeroline=False),
            plot_bgcolor="#FFFFFF", 
            paper_bgcolor="rgba(0,0,0,0)",
            height=600,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig_lollipop, use_container_width=True)


# -----------------------------------------------------------------------------
# DICCIONARIO DE PÁGINAS
# -----------------------------------------------------------------------------
PAGINAS = {
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
}

# -----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL (NAVEGACIÓN)
# -----------------------------------------------------------------------------
def main():
    # Barra lateral de navegación
    st.sidebar.title("Navegación")
    seleccion = st.sidebar.selectbox("Ir a:", list(PAGINAS.keys()))
    PAGINAS[seleccion]()

# -----------------------------------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
