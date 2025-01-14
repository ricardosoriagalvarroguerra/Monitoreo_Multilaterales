import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo, mui

# Cargar los datos desde el archivo Parquet
@st.cache_data
def load_data():
    return pd.read_parquet("unique_locations.parquet")

data = load_data()

# Sidebar para el filtro de Sector
sector_filter = st.sidebar.selectbox(
    "Selecciona un Sector", 
    options=["Todos"] + sorted(data["Sector"].dropna().unique().tolist())
)

# Filtrar los datos según el sector seleccionado
if sector_filter != "Todos":
    filtered_data = data[data["Sector"] == sector_filter]
else:
    filtered_data = data

# Agrupar por país y calcular el acumulado
country_data = (
    filtered_data.groupby("recipientcountry_codename")["value_usd"]
    .sum()
    .reset_index()
    .sort_values(by="value_usd", ascending=False)
)

# Convertir valores a millones
country_data["value_usd"] = country_data["value_usd"] / 1e6

# Crear el layout para el dashboard
layout = [dashboard.Item("bar_chart", 0, 0, 6, 2)]  # Reducido en largo y ancho

# Página principal
st.title("GeoData Dashboard")

with elements("GeoData"):
    # Aplicar estilos para un contenedor más pequeño y con color blanco en los ejes
    with mui.Box(
        sx={
            "width": "50%",  # Reducir el ancho
            "height": 300,  # Reducir la altura
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
        }
    ):
        nivo.Bar(
            data=country_data.to_dict("records"),
            keys=["value_usd"],
            indexBy="recipientcountry_codename",
            margin={"top": 30, "right": 50, "bottom": 70, "left": 100},
            padding=0.3,
            layout="horizontal",
            colors={"scheme": "nivo"},
            axisBottom={
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 45,
                "legend": "Valor Acumulado (Millones USD)",
                "legendPosition": "middle",
                "legendOffset": 40,
                "tickColor": "#FFFFFF",  # Color blanco para los ticks
            },
            axisLeft={
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 0,
                "legend": "País",
                "legendPosition": "middle",
                "legendOffset": -70,
                "tickColor": "#FFFFFF",  # Color blanco para los ticks
            },
            enableLabel=True,
            labelSkipWidth=12,
            labelSkipHeight=12,
            legends=[
                {
                    "dataFrom": "keys",
                    "anchor": "bottom-right",
                    "direction": "column",
                    "translateX": 120,
                    "itemWidth": 100,
                    "itemHeight": 20,
                    "symbolSize": 20,
                }
            ],
            theme={
                "textColor": "#FFFFFF",  # Texto en color blanco
                "tooltip": {
                    "container": {
                        "background": "#333333",
                        "color": "#FFFFFF",  # Texto del tooltip en blanco
                    }
                }
            },
            sortByValue=True,  # Ordenar descendente
        )
