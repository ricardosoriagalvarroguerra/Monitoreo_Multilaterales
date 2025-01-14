import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo

# Para usar la pantalla ancha (opcional)
st.set_page_config(layout="wide")

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

# Definir el layout inicial del dashboard, con dimensiones más grandes.
# w=8, h=5 son un punto de partida; ajústalo a tu gusto.
layout = [
    dashboard.Item(
        item_id="bar_chart",
        x=0,          # posición inicial columna
        y=0,          # posición inicial fila
        w=8,          # ancho en "columnas" del grid
        h=6,          # alto en "filas" del grid
        isDraggable=True,
        isResizable=True
    )
]

st.title("GeoData Dashboard")

# Uso de 'elements' para tu grid interactivo.
with elements("GeoData"):
    # Añadimos la clase .drag-handle para hacer "arrastrable" el elemento por esa zona
    with dashboard.Grid(layout, draggableHandle=".drag-handle"):
        
        # Esta zona servirá como "manija" para arrastrar
        # (puedes darle estilos CSS a tu gusto)
        st.markdown(
            """
            <div class="drag-handle" 
                 style="cursor: move; 
                        background-color: #444444; 
                        color: white;
                        padding: 8px; 
                        margin-bottom: 5px; 
                        width: 100%;
                        text-align: center;">
                Arrastra aquí
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Tu gráfico
        nivo.Bar(
            data=country_data.to_dict("records"),
            keys=["value_usd"],
            indexBy="recipientcountry_codename",
            margin={"top": 30, "right": 100, "bottom": 100, "left": 150},
            padding=0.3,
            layout="horizontal",
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
                    "translateX": 120,
                    "itemWidth": 100,
                    "itemHeight": 20,
                    "symbolSize": 20,
                }
            ],
            theme={
                "textColor": "#FFFFFF",
                "tooltip": {
                    "container": {
                        "background": "#333333",
                        "color": "#FFFFFF",
                    }
                }
            },
            sortByValue=True,  # Ordenar descendente
        )
