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
    
    # Filtrar los datos según el país seleccionado
    if "General" not in filtro_pais:
        data_tc = data[(data["Project Type"] == "Technical Cooperation") & 
                       (data["Project Country"].isin(filtro_pais))]
    else:
        data_tc = data[data["Project Type"] == "Technical Cooperation"]
    
    # Filtrar los datos por el rango de años
    data_tc = data_tc[(data_tc["Year"] >= rango_anios[0]) & (data_tc["Year"] <= rango_anios[1])]
    
    # Agrupar datos por año para Technical Cooperation
    resumen_anual_tc = data_tc.groupby("Year")["Approval Amount"].sum().reset_index()
    
    # Gráfico de serie de tiempo suavizada con marcadores
    fig_line = px.line(
        resumen_anual_tc,
        x="Year",
        y="Approval Amount",
        title="Serie de Tiempo de Monto Aprobado (Technical Cooperation)",
        labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
        markers=True
    )
    fig_line.update_traces(line_shape='spline')  # Línea suavizada
    st.plotly_chart(fig_line)
    
    # Cálculo del porcentaje de cooperaciones técnicas respecto al total
    data_filtrado = data[(data["Year"] >= rango_anios[0]) & (data["Year"] <= rango_anios[1])]
    resumen_anual_total = data_filtrado.groupby("Year")["Approval Amount"].sum().reset_index()
    porcentaje_tc = resumen_anual_tc.merge(
        resumen_anual_total,
        on="Year",
        suffixes=("_tc", "_total")
    )
    porcentaje_tc["Porcentaje TC"] = (
        porcentaje_tc["Approval Amount_tc"] / porcentaje_tc["Approval Amount_total"] * 100
    )
    
    # Gráfico de Lollipop Chart Horizontal
    fig_lollipop = px.bar(
        porcentaje_tc,
        x="Porcentaje TC",
        y="Year",
        orientation="h",
        title="Porcentaje de Cooperaciones Técnicas en el Total de Aprobaciones",
        labels={"Year": "Año", "Porcentaje TC": "Porcentaje (%)"}
    )
    fig_lollipop.update_traces(width=0.01)  # Hacer las barras más delgadas
    fig_lollipop.add_scatter(
        x=porcentaje_tc["Porcentaje TC"],
        y=porcentaje_tc["Year"],
        mode="markers",
        marker=dict(color="red", size=10),
        name="Porcentaje TC"
    )
    st.plotly_chart(fig_lollipop)

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
