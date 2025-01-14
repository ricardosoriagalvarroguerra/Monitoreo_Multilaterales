import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo, mui

# --- Datos de ejemplo ---
pie_data = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

df = pd.DataFrame([
    {"ID": 1, "First name": "Jon",    "Last name": "Snow",      "Age": 35},
    {"ID": 2, "First name": "Cersei", "Last name": "Lannister", "Age": 42},
    {"ID": 3, "First name": "Jaime",  "Last name": "Lannister", "Age": 45},
    {"ID": 4, "First name": "Arya",   "Last name": "Stark",     "Age": 18},
    {"ID": 5, "First name": "Bran",   "Last name": "Stark",     "Age": 16},
    {"ID": 6, "First name": "Tyrion", "Last name": "Lannister", "Age": 39},
    {"ID": 7, "First name": "Sansa",  "Last name": "Stark",     "Age": 20},
    {"ID": 8, "First name": "Sam",    "Last name": "Tarly",     "Age": 32},
    {"ID": 9, "First name": "Theon",  "Last name": "Greyjoy",   "Age": 27},
])

# Layout inicial: dos items, uno para el Pie chart y otro para la tabla.
# x, y determinan la posición en la cuadrícula;
# w, h determinan el tamaño (en "celdas" del grid).
dashboard_layout = [
    dashboard.Item(
        i="pie_chart",
        x=2, y=3, w=4, h=4,  # Ajusta según te guste
        isDraggable=True,
        isResizable=True
    ),
    dashboard.Item(
        i="data_grid",
        x=4, y=1, w=4, h=4,  # Ajusta según te guste
        isDraggable=True,
        isResizable=True
    ),
]

# Configuración de la página de Streamlit en modo ancho.
st.set_page_config(layout="wide")
st.title("Ejemplo de dashboard con Pie chart y Data grid")

# Creamos el "frame" para los componentes de streamlit-elements.
with elements("my_dashboard"):

    # Creamos la grilla usando nuestro layout.
    # Añadimos style={"backgroundColor": "#212121"} para un fondo oscuro.
    # draggableHandle=".drag-handle" indica que para arrastrar hay que
    # hacer click en la zona que tenga esa clase CSS.
    with dashboard.Grid(dashboard_layout, draggableHandle=".drag-handle", style={"backgroundColor": "#212121"}):
        
        # --- PRIMER ITEM: Pie chart ---
        with dashboard.Item("pie_chart"):
            
            # Añadimos un div que será la "manija" para arrastrar (drag-handle).
            st.markdown(
                """
                <div class="drag-handle"
                     style="cursor: move; 
                            background-color: #333333;
                            color: white;
                            padding: 8px; 
                            margin-bottom: 5px; 
                            text-align: center;">
                    Pie chart
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Ahora, dentro de un Paper (fondo gris) mostramos el Nivo Pie chart
            with mui.Paper(sx={"backgroundColor": "#303030", "padding": "10px"}):
                nivo.Pie(
                    data=pie_data,
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
                        "background": "#303030",
                        "textColor": "#FFFFFF",
                        "tooltip": {
                            "container": {
                                "background": "#333333",
                                "color": "#FFFFFF",
                            }
                        }
                    }
                )

        # --- SEGUNDO ITEM: Tabla de datos ---
        with dashboard.Item("data_grid"):
            
            # De nuevo, nuestra zona de arrastre
            st.markdown(
                """
                <div class="drag-handle"
                     style="cursor: move; 
                            background-color: #333333;
                            color: white;
                            padding: 8px; 
                            margin-bottom: 5px; 
                            text-align: center;">
                    Data grid
                </div>
                """,
                unsafe_allow_html=True
            )

            # En este caso creamos una tabla manualmente con MUI
            with mui.Paper(sx={"backgroundColor": "#303030", "padding": "10px"}):
                
                with mui.TableContainer:
                    with mui.Table:
                        # Cabecera
                        with mui.TableHead:
                            with mui.TableRow:
                                for col in df.columns:
                                    # Color del texto en blanco
                                    mui.TableCell(col, sx={"color": "white", "fontWeight": "bold"})
                        
                        # Cuerpo
                        with mui.TableBody:
                            for _, row in df.iterrows():
                                with mui.TableRow:
                                    for value in row:
                                        mui.TableCell(str(value), sx={"color": "white"})
