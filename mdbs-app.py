import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

st.set_page_config(layout="wide")
st.title("Ejemplo: Drag & Resize dentro de un Card")

# Datos de ejemplo para un Nivo Pie chart (podrías cambiarlo a Bar, Radar, etc.)
sample_data = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

# Creamos un layout de dashboard con un único panel (panel "pie_chart").
layout = [
    dashboard.Item(
        i="pie_chart",
        x=0, y=0,    # posición inicial en la cuadrícula
        w=4, h=4,    # ancho y alto en celdas del grid
        isDraggable=True,
        isResizable=True
    )
]

with elements("drag_resize_demo"):
    
    # Creamos el dashboard.Grid pasándole el layout.
    # "draggableHandle" se refiere a la clase CSS ".drag-handle".
    with dashboard.Grid(layout, draggableHandle=".drag-handle", style={"backgroundColor": "#222222"}):
        
        # Enlazamos el layout con key="pie_chart".
        # En lugar de Paper, usamos un Card (de MUI) para dar estilo de "card".
        with mui.Card(key="pie_chart", sx={"backgroundColor": "#333333", "borderRadius": "10px"}):
            
            # Aquí añadimos la "manija" con clase .drag-handle
            st.markdown(
                """
                <div class="drag-handle"
                     style="
                         cursor: move; 
                         background-color: #444444;
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
            
            # Agregamos un contenedor BOX de MUI para el chart
            # con un alto fijo (puedes ajustarlo o hacerlo dinámico).
            with mui.Box(sx={"height": 400, "padding": "10px"}):
                
                # Un Pie chart sencillo de Nivo.
                # ¡Puedes usar nivo.Bar, nivo.Sunburst, Radar, etc.!
                nivo.Pie(
                    data=sample_data,
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
                )  # Paréntesis de cierre agregado aquí
