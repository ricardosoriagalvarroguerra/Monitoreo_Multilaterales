import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

st.set_page_config(layout="wide")

with elements("demo"):
    # Layout de ejemplo
    layout = [
        dashboard.Item(i="pie_chart", x=0, y=0, w=4, h=4, isDraggable=True, isResizable=True),
    ]

    with dashboard.Grid(layout, draggableHandle=".drag-handle"):
        # Tarjeta que contendrá el gráfico
        with mui.Card(key="pie_chart", sx={"backgroundColor": "#333", "borderRadius": "10px"}):
            
            # “Manija” para arrastrar
            st.markdown(
                """
                <div class="drag-handle"
                     style="
                         cursor: move;
                         background-color: #444;
                         color: white;
                         padding: 10px;
                         margin: 0 0 10px 0;
                         border-radius: 10px 10px 0 0;
                         text-align: center;
                         font-weight: bold;
                     ">
                    Arrastra aquí
                </div>
                """,
                unsafe_allow_html=True
            )

            # Contenedor con altura fija para el chart
            with mui.Box(sx={"height": 400, "padding": "10px"}):
                nivo.Pie(
                    data=[
                        {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
                        {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
                        {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
                        {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
                        {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
                    ],
                    margin={"top": 40, "right": 80, "bottom": 80, "left": 80},
                    innerRadius=0.5,
                    padAngle=1,
                    cornerRadius=5,
                    activeOuterRadiusOffset=8,
                    borderWidth=1,
                    borderColor={"from": "color", "modifiers": [["darker", 0.2]]},
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsTextColor="#FFF",
                    arcLinkLabelsThickness=2,
                    arcLinkLabelsColor={"from": "color"},
                    arcLabelsSkipAngle=10,
                    arcLabelsTextColor={"from": "color", "modifiers": [["darker", 2]]},
                    theme={
                        "background": "#333333",
                        "textColor": "#FFFFFF",
                        "tooltip": {
                            "container": {
                                "background": "#444444",
                                "color": "#FFFFFF",
                            }
                        }
                    }
                )
