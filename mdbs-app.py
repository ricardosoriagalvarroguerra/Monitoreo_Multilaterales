import streamlit as st
import pandas as pd
import plotly.express as px

# Función para la página Cooperaciones Técnicas
def cooperaciones_tecnicas():
    st.title("Cooperaciones Técnicas")
    
    # Cargar datos desde el archivo
    file_path = "IADB_DASH_BDD.xlsx"  # Cambiar por la ruta correcta si es necesario
    data = pd.read_excel(file_path, sheet_name="Export")
    
    # Filtrar los datos relevantes
    data_tc = data[data["Project Type"] == "Technical Cooperation"]
    
    # Agregar filtro de país
    paises = ["General", "Argentina", "Bolivia", "Brazil", "Paraguay", "Uruguay"]
    filtro_pais = st.selectbox("Selecciona el país (o General para ver todos):", paises)
    
    # Aplicar el filtro de país
    if filtro_pais != "General":
        data_tc = data_tc[data_tc["Project Country"] == filtro_pais]
    
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
        title=f"Serie de Tiempo de Monto Aprobado ({filtro_pais})",
        labels={"Year": "Año", "Approval Amount": "Monto Aprobado"},
    )
    st.plotly_chart(fig_line)
    
    # Gráfico de barras
    fig_bar = px.bar(
        resumen_anual,
        x="Year",
        y="Approval Amount",
        title=f"Gráfico de Barras de Monto Aprobado ({filtro_pais})",
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
    "Cooperaciones Técnicas": cooperaciones_tecnicas  # Nueva página añadida
}

def main():
    st.sidebar.title("Navegación")
    # Menú desplegable en la barra lateral
    seleccion = st.sidebar.selectbox("Ir a", list(PAGINAS.keys()))
    
    # Ejecutar la función de la página seleccionada
    PAGINAS[seleccion]()

if __name__ == "__main__":
    main()
