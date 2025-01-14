import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_parquet("unique_locations.parquet")

data = load_data()

sector_filter = st.sidebar.selectbox(
    "Selecciona un Sector",
    options=["Todos"] + sorted(data["Sector"].dropna().unique().tolist())
)

if sector_filter != "Todos":
    filtered_data = data[data["Sector"] == sector_filter]
else:
    filtered_data = data

country_data = (
    filtered_data.groupby("recipientcountry_codename")["value_usd"]
    .sum()
    .reset_index()
    .sort_values(by="value_usd", ascending=False)
)

country_data["value_usd"] = country_data["value_usd"] / 1e6

st.title("GeoData Dashboard")

with elements("GeoData"):
    # dashboard.Grid sin layout, y definimos los items "en línea"
    with dashboard.Grid(draggableHandle=".drag-handle"):

        st.markdown(
            """
            <div class="drag-handle" 
                 style="cursor: move; 
                        background-color: #444444; 
                        color: white;
                        padding: 8px; 
                        margin-bottom: 5px; 
                        text-align: center;">
                Arrastra aquí
            </div>
            """,
            unsafe_allow_html=True
        )

        # Definimos el item con todos sus parámetros directamente:
        with dashboard.Item(
            i="bar_chart",
            x=0, 
            y=0, 
            w=8, 
            h=6,
            isDraggable=True,
            isResizable=True
        ):
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
                sortByValue=True,
            )
