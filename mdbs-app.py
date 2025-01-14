import streamlit as st
from streamlit_elements import elements, dashboard, mui

st.set_page_config(layout="wide")
st.title("Ejemplo Básico: Draggable y Resizable Dashboard")

# Construimos el layout inicial para cada 'item' del dashboard.
layout = [
    # dashboard.Item(identificador, x, y, width, height, ...)
    dashboard.Item("first_item", 0, 0, 2, 2),  # Draggable y resizable por defecto
    dashboard.Item("second_item", 2, 0, 2, 2, isDraggable=False, moved=False),
    dashboard.Item("third_item", 0, 2, 1, 1, isResizable=False),
]

# Creamos un frame para los elementos de streamlit-elements
with elements("dashboard_example"):

    # Creamos el Grid pasando el layout definido arriba
    with dashboard.Grid(layout):
        # Para enlazar cada panel con el layout, usamos key="..."
        mui.Paper("First item", key="first_item")
        mui.Paper("Second item (cannot drag)", key="second_item")
        mui.Paper("Third item (cannot resize)", key="third_item")
