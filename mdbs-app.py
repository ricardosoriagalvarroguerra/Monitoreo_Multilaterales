import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo
# Si tu versión no reconoce mui.icons.material, prueba descomentar:
# from streamlit_elements import mui_icons

st.set_page_config(layout="wide")

layout = [
    dashboard.Item("pie_chart", 0, 0, 4, 4, isDraggable=True, isResizable=True)
]

with elements("demo"):
    with dashboard.Grid(layout, draggableHandle=".drag-handle"):
        with mui.Card(key="pie_chart"):
            # -- Encabezado (manija):
            # Opción A: si tu versión soporta mui.icons.material
            header_action = mui.IconButton(mui.icons.material.DarkMode, sx={"color": "#fff"})

            # Opción B: si NO soporta .material, usa directamente mui.icons.DarkMode
            # header_action = mui.IconButton(mui.icons.DarkMode, sx={"color": "#fff"})

            # Opción C: si tampoco sirve, prueba con mui_icons
            # header_action = mui.IconButton(mui_icons.MdDarkMode, sx={"color": "#fff"})

            with mui.CardHeader(
                title="Pie chart",
                className="drag-handle",
                sx={"cursor": "move", "backgroundColor": "#444444", "padding": "10px"},
                action=header_action
            ):
                pass

            # -- Contenido (gráfico):
            with mui.CardContent(sx={"backgroundColor": "#333", "height": 400}):
                nivo.Pie(
                    data=[
                        {"id": "java", "label": "java", "value": 465},
                        {"id": "rust", "label": "rust", "value": 140},
                    ],
                    # etc...
                )

st.markdown(
    """
    <style>
    .drag-handle {
        cursor: move;
    }
    </style>
    """,
    unsafe_allow_html=True
)
