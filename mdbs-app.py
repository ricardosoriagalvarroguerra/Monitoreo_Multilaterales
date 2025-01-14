import streamlit as st
from streamlit_elements import elements, mui

def app_monitorio():
    st.title("Monitorio Multilaterales")
    st.write("Aquí va el contenido de Monitorio Multilaterales.")
    with elements("monitorio_multilaterales"):
        with mui.Box(sx={"border": "1px solid #ccc", "padding": "16px"}):
            mui.Typography("Contenido adicional de Monitorio Multilaterales")

def app_geodata():
    st.title("GeoData")
    st.write("Aquí va el contenido de GeoData.")
    with elements("geodata"):
        with mui.Box(sx={"border": "1px solid #ccc", "padding": "16px"}):
            mui.Typography("Contenido adicional de GeoData")

def app_flujos():
    st.title("Flujos Agregados")
    st.write("Aquí va el contenido de Flujos Agregados.")
    with elements("flujos_agregados"):
        with mui.Box(sx={"border": "1px solid #ccc", "padding": "16px"}):
            mui.Typography("Contenido adicional de Flujos Agregados")

def main():
    # Menú lateral
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Ir a:", 
                            ("Monitorio Multilaterales", "GeoData", "Flujos Agregados"))

    if menu == "Monitorio Multilaterales":
        app_monitorio()
    elif menu == "GeoData":
        app_geodata()
    else:
        app_flujos()

if __name__ == "__main__":
    st.set_page_config(page_title="Monitorio Multilaterales", layout="wide")
    main()
