import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo, mui

# Configuración de página en modo ancho
st.set_page_config(layout="wide")
st.title("Ejemplo: Barras Horizontales Drag/Resize")

# 1) Cargar datos desde unique_location.parquet
@st.cache_data
def load_data():
    return pd.read_parquet("unique_location.parquet")

df = load_data()

# 2) Agrupar por recipientcountry_codename y sumar value_usd
country_data = (
    df.groupby("recipientcountry_codename")["value_usd"]
    .sum()
    .reset_index()
    .sort_values(by="value_usd", ascending=False)
)

# Convertir a millones
country_data["value_usd"] = country_data["value_usd"] / 1e6

# 3) Definir layout del dashboard con un solo panel (bar_chart).
#    (Puedes agregar más Items en la lista si quieres múltiples paneles.)
layout = [
    dashboard.Item(
        i="bar_chart", 
        x=0, y=0,   # posición inicial
        w=6, h=5,   # ancho y alto en celdas del grid
        isDraggable=True,
        isResizable=True
    )
]

# 4) Crear frame para streamlit-elements
with elements("my_dashboard"):
    
    # dashboard.Grid() con draggableHandle para mover arrastrando .drag-handle
    with dashboard.Grid(layout, draggableHandle=".drag-handle", style={"backgroundColor": "#212121"}):
        
        # Panel contenedor: usamos key="bar_chart" para enlazar con el layout
        with mui.Paper(key="bar_chart", sx={"padding": "10px", "backgroundColor": "#303030"}):
            
            # Manija de arrastre
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

            # 5) Gráfico de barras horizontal con Nivo
            #    Se basa en country_data, con layout horizontal.
            nivo.Bar(
                data=country_data.to_dict("records"),
                keys=["value_usd"],
                indexBy="recipientcountry_codename",
                margin={"top": 30, "right": 80, "bottom": 80, "left": 150},
                padding=0.3,
                layout="horizontal",  # Barras horizontales
                colors={"scheme": "nivo"},
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": 45,
                    "legend": "Valor (Millones USD)",
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
