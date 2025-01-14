import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, mui

st.set_page_config(layout="wide")

# Layout con un solo panel
layout = [
    # i="panel_1", (x=0, y=0, w=6, h=4) => Draggable y resizable
    dashboard.Item("panel_1", 0, 0, 6, 4, isDraggable=True, isResizable=True)
]

with elements("demo_dashboard"):
    # Habilita arrastre SOLO desde .drag-handle
    with dashboard.Grid(layout, draggableHandle=".drag-handle"):
        # Panel con key="panel_1"
        with mui.Paper(key="panel_1", sx={"padding": "10px", "backgroundColor": "#303030"}):
            st.markdown(
                """
                <div class="drag-handle"
                     style="cursor: move; 
                            background-color: #444444; 
                            color: white;
                            padding: 8px; 
                            margin-bottom: 10px; 
                            text-align: center;
                            z-index:9999;">
                    Arrastra aquí
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("Contenido del panel")
