import streamlit as st

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

# Diccionario de páginas
PAGINAS = {
    "Monitoreo de Multilaterales": monitoreo_multilaterales,
    "Flujos Agregados": flujos_agregados,
    "GeoData": geodata,
    "Curva Histórica": curva_historica
}

def main():
    st.sidebar.title("Navegación")
    # Cambiamos de radio buttons a un menú desplegable (selectbox)
    seleccion = st.sidebar.selectbox("Ir a", list(PAGINAS.keys()))
    
    # Ejecutar la función de la página seleccionada
    PAGINAS[seleccion]()

if __name__ == "__main__":
    main()
