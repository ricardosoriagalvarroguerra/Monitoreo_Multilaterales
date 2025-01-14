import streamlit as st
from streamlit_elements import elements, mui

def app_monitoreo():
    st.title("Monitoreo Multilaterales")
    st.write("Bienvenido a la página principal de **Monitoreo Multilaterales**.")
    
    # Ejemplo simple con streamlit-elements
    with elements("monitoreo"):
        with mui.Card(sx={"padding": "16px", "marginTop": "16px"}):
            mui.Typography("Contenido específico para Monitoreo Multilaterales", variant="body1")

def app_geodata():
    st.title("GeoData")
    st.write("Aquí podrás visualizar y analizar datos geoespaciales.")

    # Ejemplo con streamlit-elements
    with elements("geodata"):
        with mui.Card(sx={"padding": "16px", "marginTop": "16px"}):
            mui.Typography("Contenido específico para GeoData", variant="body1")

def app_flujos():
    st.title("Flujos Agregados")
    st.write("Aquí se mostrarán los datos de flujos agregados.")

    # Ejemplo con streamlit-elements
    with elements("flujos"):
        with mui.Card(sx={"padding": "16px", "marginTop": "16px"}):
            mui.Typography("Contenido específico para Flujos Agregados", variant="body1")

def main():
    # Configura la página
    st.set_page_config(page_title="Monitoreo Multilaterales", layout="wide")

    # Menú desplegable (selectbox) para navegar
    opcion = st.selectbox(
        "Selecciona una página",
        ("Monitoreo Multilaterales", "GeoData", "Flujos Agregados")
    )

    # Dependiendo de la elección, mostramos una u otra "sub-app"
    if opcion == "Monitoreo Multilaterales":
        app_monitoreo()
    elif opcion == "GeoData":
        app_geodata()
    elif opcion == "Flujos Agregados":
        app_flujos()

if __name__ == "__main__":
    main()
