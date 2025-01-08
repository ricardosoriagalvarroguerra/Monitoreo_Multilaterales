import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Función para la página Cooperaciones Técnicas
def cooperaciones_tecnicas():
    st.title("Cooperaciones Técnicas")
    
    # Cargar datos desde el archivo Parquet
    file_path = "IADB_DASH_BDD.parquet"  # Cambiar por la ruta correcta si es necesario
    data = pd.read_parquet(file_path)
    
    # Convertir la columna "Approval Date" a datetime
    data["Approval Date"] = pd.to_datetime(data["Approval Date"])
    data["Year"] = data["Approval Date"].dt.year
    
    # Opciones de filtro en la barra lateral
    st.sidebar.header("Filtros")
    
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
        min_year, max_year, (min_year, max_year)
    )
    
    # Filtrar los datos según el país seleccionado y rango de años
    if "General" not in filtro_pais:
        data_tc = data[
            (data["Project Type"] == "Technical Cooperation") & 
            (data["Project Country"].isin(filtro_pais)) &
            (data["Year"] >= rango_anios[0]) & 
            (data["Year"] <= rango_anios[1])
        ]
        # Agrupar por país y año para evitar múltiples puntos en el mismo año
        data_tc = data_tc.groupby(["Project Country", "Year"])["Approval Amount"].sum().reset_index()
    else:
        data_tc = data[
            (data["Project Type"] == "Technical Cooperation") &
            (data["Year"] >= rango_anios[0]) & 
            (data["Year"] <= rango_anios[1])
        ]
        data_tc = data_tc.groupby("Year")["Approval Amount"].sum().reset_index()
    
    # Gráfico de serie de tiempo con series separadas por país
    if "General" not in filtro_pais:
        fig_line = px.line(
            data_tc,
            x="Year",
            y="Approval Amount",
            color="Project Country",  # Diferenciar series por país
            title="Serie de Tiempo de Monto Aprobado (Technical Cooperation)",
            labels={"Year": "Año", "Approval Amount": "Monto Aprobado", "Project Country": "País"},
            markers=True
        )
    else:
        fig_line = px.line(
            data_tc,
            x="Year",
            y="Approval Amount",
            title="Serie de Tiempo de Monto Aprobado (Technical Cooperation)",
            labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
            markers=True
        )
    fig_line.update_traces(line_shape='spline')  # Línea suavizada
    st.plotly_chart(fig_line)

# Diccionario de páginas
PAGINAS = {
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
}

# Navegación principal
def main():
    st.sidebar.title("Navegación")
    seleccion = st.sidebar.selectbox("Ir a", list(PAGINAS.keys()))
    PAGINAS[seleccion]()

if __name__ == "__main__":
    main()
