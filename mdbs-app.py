import streamlit as st
import pandas as pd
import plotly.express as px

# Función para la página Monitoreo de Multilaterales
def monitoreo_multilaterales():
    st.title("Monitoreo de Multilaterales")
    st.write("Contenido de Monitoreo de Multilaterales próximamente...")

# Función para la página Flujos Agregados
def flujos_agregados():
    st.title("Flujos Agregados")
    st.write("Contenido de Flujos Agregados próximamente...")

# Función para la página GeoData
def geodata():
    st.title("GeoData")
    st.write("Contenido de GeoData próximamente...")

# Función para la página Curva Histórica
def curva_historica():
    st.title("Curva Histórica")
    st.write("Contenido de Curva Histórica próximamente...")

# Función para la página Workbench
def workbench():
    st.title("Workbench")
    st.write("Contenido de Workbench próximamente...")

# Función para la página Cooperaciones Técnicas
def cooperaciones_tecnicas():
    st.title("Cooperaciones Técnicas")
    
    # Cargar datos desde el archivo Parquet
    file_path = "IADB_DASH_BDD.parquet"  # Cambiar por la ruta correcta si es necesario
    data = pd.read_parquet(file_path)
    
    # Filtrar los datos relevantes
    data_tc = data[data["Project Type"] == "Technical Cooperation"]
    
    # Opciones de filtro en la barra lateral
    st.sidebar.header("Filtros")
    paises_disponibles = ["Argentina", "Bolivia", "Brazil", "Paraguay", "Uruguay"]
    filtro_pais = st.sidebar.multiselect(
        "Selecciona uno o varios países:",
        options=paises_disponibles,
        default=paises_disponibles  # Por defecto muestra todos
    )
    
    # Aplicar el filtro de países seleccionados
    if filtro_pais:
        data_tc = data_tc[data_tc["Project Country"].isin(filtro_pais)]
    
    # Convertir la columna "Approval Date" a datetime
    data_tc["Approval Date"] = pd.to_datetime(data_tc["Approval Date"])
    
    # Agrupar datos por año y calcular el monto total aprobado
    data_tc["Year"] = data_tc["Approval Date"].dt.year
    resumen_anual = data_tc.groupby("Year")["Approval Amount"].sum().reset_index()
    
    # Gráfico de series de tiempo
    fig_line = px.line(
        resumen_anual,
        x="Year",
        y="Approval Amount",
        title="Serie de Tiempo de Monto Aprobado",
        labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
    )
    st.plotly_chart(fig_line)
    
    # Gráfico de barras
    fig_bar = px.bar(
        resumen_anual,
        x="Year",
        y="Approval Amount",
        title="Gráfico de Barras de Monto Aprobado",
        labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
    )
    st.plotly_chart(fig_bar)

# Diccionario de páginas
PAGINAS = {
    "Monitoreo de Multilaterales": monitoreo_multilaterales,
    "Flujos Agregados": flujos_agregados,
    "GeoData": geodata,
    "Curva Histórica": curva_historica,
    "Workbench": workbench,
    "Cooperaciones Técnicas": cooperaciones_tecnicas,
}

# Navegación principal
def main():
    st.sidebar.title("Navegación")
    seleccion = st.sidebar.selectbox("Ir a", list(PAGINAS.keys()))
    PAGINAS[seleccion]()

if __name__ == "__main__":
    main()
