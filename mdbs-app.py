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

# Crear el layout para el dashboard
layout = [dashboard.Item("bar_chart", 0, 0, 12, 8)]  # Ajustar el tamaño aquí

# Página principal
st.title("GeoData Dashboard")

with elements("GeoData"):
    # Aplicar estilos para un contenedor más grande
    with mui.Box(
        sx={
            "width": "100%",
            "height": 500,  # Altura personalizada
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
        }
    ):
        nivo.Bar(
            data=country_data.to_dict("records"),
            keys=["value_usd"],
            indexBy="recipientcountry_codename",
            margin={"top": 50, "right": 150, "bottom": 150, "left": 200},  # Márgenes ajustados
            padding=0.3,
            layout="horizontal",
            colors={"scheme": "nivo"},
            axisBottom={
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 45,
                "legend": "Valor Acumulado (USD)",
                "legendPosition": "middle",
                "legendOffset": 80,
            },
            axisLeft={
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 0,
                "legend": "País",
                "legendPosition": "middle",
                "legendOffset": -100,
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
                "background": "#1e1e1e",
                "textColor": "#FFFFFF",
                "tooltip": {
                    "container": {
                        "background": "#333333",
                        "color": "#FFFFFF",
                    }
                }
            },
        )
