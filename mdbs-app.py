import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo, mui

# Configura la página en modo ancho
st.set_page_config(layout="wide")
st.title("Barras Horizontales Drag & Resize")

# --- Carga de datos ---
@st.cache_data
def load_data():
    return pd.read_parquet("unique_location.parquet")

df = load_data()

# --- Agrupación y suma ---
country_data = (
    df.groupby("recipientcountry_codename")["value_usd"]
    .sum()
    .reset_index()
    .sort_values(by="value_usd", ascending=False)
)

# Convertimos a millones de USD
country_data["value_usd"] = country_data["value_usd"] / 1e6

# --- Definición del dashboard ---
# Un solo item: bar_chart. Ponemos isDraggable y isResizable en True.
layout = [
    dashboard.Item(
        i="bar_chart",
        x=0, y=0,
        w=6, h=5,
        isDraggable=True,
        isResizable=True
    )
]

# --- Creamos el frame para streamlit-elements ---
with elements("my_dashboard"):

    # Creamos el Grid, habilitando el arrastre solo en .drag-handle
    # y un color de fondo oscuro (opcional).
    with dashboard.Grid(layout, draggableHandle=".drag-handle", style={"backgroundColor": "#212121"}):

        # Enlazamos el layout con key="bar_chart".
        with mui.Paper(key="bar_chart", sx={"padding": "10px", "backgroundColor": "#303030"}):
            
            # "Manija" para arrastrar
            st.markdown(
                """
                <div class="drag-handle"
                     style="cursor: move; 
                            background-color: #444444; 
                            color: white;
                            padding: 8px; 
                            margin-bottom: 10px; 
                            text-align: center;">
                    Arrastra aquí
                </div>
                """,
                unsafe_allow_html=True
            )

            # Gráfico de barras horizontal con Nivo
            nivo.Bar(
                data=country_data.to_dict("records"),
                keys=["value_usd"],  # Columna con valores
                indexBy="recipientcountry_codename",
                margin={"top": 30, "right": 80, "bottom": 80, "left": 150},
                padding=0.3,
                layout="horizontal",  # Barras horizontales
                colors={"scheme": "nivo"},
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": 45,
                    "legend": "Valor Acumulado (Millones USD)",
                    "legendPosition": "middle",
                    "legendOffset": 50,
                    "tickColor": "#FFFFFF",  
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": 0,
                    "legend": "País",
                    "legendPosition": "middle",
                    "legendOffset": -70,
                    "tickColor": "#FFFFFF",
                },
                enableLabel=True,
                labelSkipWidth=12,
                labelSkipHeight=12,
                legends=[
                    {
                        "dataFrom": "keys",
                        "anchor": "bottom-right",
                        "direction": "column",
                        "translateX": 110,
                        "itemWidth": 100,
                        "itemHeight": 20,
                        "symbolSize": 20,
                        "symbolShape": "circle"
                    }
                ],
                theme={
                    "background": "#303030",
                    "textColor": "#FFFFFF",
                    "tooltip": {
                        "container": {
                            "background": "#333333",
                            "color": "#FFFFFF",
                        }
                    }
                },
                sortByValue=True,  # Orden descendente
            )
