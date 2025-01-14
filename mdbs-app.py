import streamlit as st
from streamlit_elements import elements, mui, html
import plotly.express as px
import pandas as pd
from collections import defaultdict

def app_monitoreo():
    st.title("Monitoreo Multilaterales")
    st.write("Bienvenido a la página principal de **Monitoreo Multilaterales**.")

    with elements("monitoreo"):
        # Reemplazamos mui.Card por mui.Box
        with mui.Box(sx={"padding": "16px", "marginTop": "16px", "border": "1px solid #ccc", "borderRadius": "8px"}):
            mui.Typography("Contenido específico para Monitoreo Multilaterales", variant="body1")

def app_geodata():
    st.title("GeoData")
    st.write("Aquí podrás visualizar y analizar datos geoespaciales.")

    # Submenú interno de GeoData
    subpagina = st.sidebar.selectbox("Subpágina de GeoData", ["Principal", "Montos"])

    if subpagina == "Principal":
        # Vista principal de GeoData
        with elements("geodata"):
            # Reemplazamos mui.Card por mui.Box
            with mui.Box(sx={"padding": "16px", "marginTop": "16px", "border": "1px solid #ccc", "borderRadius": "8px"}):
                mui.Typography("Contenido específico para GeoData", variant="body1")

    elif subpagina == "Montos":
        st.subheader("Visualización de montos")

        # Filtro por Sector
        sector_filtrado = st.selectbox("Selecciona el Sector", ["Todos", "Salud", "Educación", "Infraestructura"])

        # Datos de ejemplo
        data = [
            {
                "id": 1,
                "point_pos": "19.4326,-99.1332",  # CDMX
                "value_usd": 1000,
                "recipientcountry_codename": "MEX",
                "Sector": "Salud"
            },
            {
                "id": 2,
                "point_pos": "40.7128,-74.0060",  # NYC
                "value_usd": 2000,
                "recipientcountry_codename": "USA",
                "Sector": "Educación"
            },
            {
                "id": 3,
                "point_pos": "48.8566,2.3522",    # París
                "value_usd": 1500,
                "recipientcountry_codename": "FRA",
                "Sector": "Salud"
            },
            {
                "id": 4,
                "point_pos": "34.0522,-118.2437", # Los Ángeles
                "value_usd": 3000,
                "recipientcountry_codename": "USA",
                "Sector": "Infraestructura"
            }
        ]

        # Filtrar por Sector
        if sector_filtrado != "Todos":
            data = [d for d in data if d["Sector"] == sector_filtrado]

        df = pd.DataFrame(data)
        # Separar lat/long
        lat_vals, lon_vals = [], []
        for pos in df["point_pos"]:
            lat_str, lon_str = pos.split(",")
            lat_vals.append(float(lat_str))
            lon_vals.append(float(lon_str))
        df["lat"] = lat_vals
        df["lon"] = lon_vals

        # Mapa de puntos Plotly
        fig_map = px.scatter_geo(
            df,
            lat="lat",
            lon="lon",
            color="Sector",
            size="value_usd",
            hover_name="recipientcountry_codename",
            projection="natural earth",
            title="Mapa de Puntos (Plotly)",
        )
        fig_map.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})
        fig_map_html = fig_map.to_html(full_html=False)

        # Gráfico de barras horizontal Plotly
        agg_data = df.groupby("recipientcountry_codename")["value_usd"].sum().reset_index()
        fig_bar = px.bar(
            agg_data,
            x="value_usd",
            y="recipientcountry_codename",
            orientation="h",
            color="recipientcountry_codename",
            title="Gráfico de Barras Horizontal (Plotly)",
        )
        fig_bar.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})
        fig_bar_html = fig_bar.to_html(full_html=False)

        with elements("montos"):
            # Mapa de Puntos
            with mui.Box(sx={"padding": "16px", "marginTop": "16px", "border": "1px solid #ccc", "borderRadius": "8px"}):
                mui.Typography("Mapa de Puntos con Plotly", variant="h6")
                # scripts=True para que se ejecute el JS en el HTML de Plotly
                html.html(fig_map_html, scripts=True, height="400px")

            # Barras Horizontal
            with mui.Box(sx={"padding": "16px", "marginTop": "16px", "border": "1px solid #ccc", "borderRadius": "8px"}):
                mui.Typography("Gráfico de Barras Horizontal con Plotly", variant="h6")
                html.html(fig_bar_html, scripts=True, height="400px")


def app_flujos():
    st.title("Flujos Agregados")
    st.write("Aquí se mostrarán los datos de flujos agregados.")

    with elements("flujos"):
        with mui.Box(sx={"padding": "16px", "marginTop": "16px", "border": "1px solid #ccc", "borderRadius": "8px"}):
            mui.Typography("Contenido específico para Flujos Agregados", variant="body1")


def main():
    st.set_page_config(page_title="Monitoreo Multilaterales", layout="wide")
    st.sidebar.title("Navegación")
    opcion = st.sidebar.selectbox(
        "Selecciona una sección:",
        ("Monitoreo Multilaterales", "GeoData", "Flujos Agregados")
    )

    if opcion == "Monitoreo Multilaterales":
        app_monitoreo()
    elif opcion == "GeoData":
        app_geodata()
    elif opcion == "Flujos Agregados":
        app_flujos()


if __name__ == "__main__":
    main()
