import streamlit as st
from streamlit_elements import elements, dashboard, mui

st.set_page_config(layout="wide")
st.title("Ejemplo Avanzado: Draggable y Resizable Dashboard con callback")

# Creamos el layout inicial con tres items
layout = [
    dashboard.Item("first_item",  0, 0, 2, 2),
    dashboard.Item("second_item", 2, 0, 2, 2, isDraggable=False, moved=False),
    dashboard.Item("third_item",  0, 2, 1, 1, isResizable=False),
]

# Definimos una función callback para manejar
# los cambios de layout (al arrastrar o redimensionar).
def handle_layout_change(updated_layout):
    """
    Esta función se llamará cada vez que un item
    cambie de posición o tamaño. 'updated_layout'
    es la nueva lista con la configuración (x, y, w, h).
    """
    print("¡Layout actualizado!")
    print(updated_layout)
    # Aquí podrías guardarlo en una base de datos, archivo JSON, etc.

with elements("dashboard_example"):

    # 1) Primer dashboard.Grid sin callback:
    #    Se mostrará con el layout inicial, pero no capturará cambios.
    with dashboard.Grid(layout):
        mui.Paper("First item", key="first_item")
        mui.Paper("Second item (cannot drag)", key="second_item")
        mui.Paper("Third item (cannot resize)", key="third_item")

    # 2) Segundo dashboard.Grid con callback onLayoutChange:
    #    Si arrastras o cambias de tamaño algún item, se disparará 'handle_layout_change'.
    #    Observa que usamos el MISMO layout, pero esta vez sí “escuchamos” los cambios.
    with dashboard.Grid(layout, onLayoutChange=handle_layout_change):
        mui.Paper("First item", key="first_item")
        mui.Paper("Second item (cannot drag)", key="second_item")
        mui.Paper("Third item (cannot resize)", key="third_item")
