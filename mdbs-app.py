import streamlit as st
import pandas as pd
from streamlit_elements import elements, dashboard, nivo, mui

# Ejemplo de datos para un pastel (pie chart)
pie_data = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

# Ejemplo de datos para la tabla
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

# 1) Definimos un layout para el dashboard con los items que queremos.
#    Cada dashboard.Item() lleva los 4 argumentos obligatorios: x, y, w, h
dashboard_layout = [
    dashboard.Item("pie_chart",  0, 0, 4, 4, isDraggable=True, isResizable=True),
    dashboard.Item("data_grid",  4, 0, 4, 4, isDraggable=True, isResizable=True),
]

# Ajustamos la página en modo ancho
st.set_page_config(layout="wide")
st.title("Ejemplo de Dashboard (Primera opción con layout)")

# 2) Creamos el frame de streamlit-elements
with elements("mi_dashboard"):

    # 3) Creamos el dashboard Grid usando nuestro layout.
    #    - draggableHandle=".drag-handle" hará que solo se arrastre
    #      pulsando en la zona con esa clase CSS.
    #    - style={"backgroundColor": "#212121"} para fondo oscuro (opcional).
    with dashboard.Grid(layout=dashboard_layout,
                        draggableHandle=".drag-handle",
                        style={"backgroundColor": "#212121"}):
        
        # -------------------------- ITEM "pie_chart" --------------------------
        # Usamos key="pie_chart" en lugar de "with dashboard.Item(...)"
        # para respetar el layout. Así evitamos errores de x, y, w, h.
        with mui.Paper(key="pie_chart", sx={"backgroundColor": "#303030"}):
            
            # Manija de arrastre
            st.markdown(
                """
                <div class="drag-handle"
                     style="cursor: move; 
                            background-color: #333333;
                            color: white;
                            padding: 8px; 
                            margin: 0 0 5px 0; 
                            text-align: center;">
                    Pie chart
                </div>
                """,
                unsafe_allow_html=True
            )

            # Gráfico de pastel con Nivo
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

        # -------------------------- ITEM "data_grid" --------------------------
        # Se referencia igual que en layout, con key="data_grid".
        with mui.Paper(key="data_grid", sx={"backgroundColor": "#303030"}):
            
            # Manija de arrastre
            st.markdown(
                """
                <div class="drag-handle"
                     style="cursor: move; 
                            background-color: #333333;
                            color: white;
                            padding: 8px; 
                            margin: 0 0 5px 0; 
                            text-align: center;">
                    Data grid
                </div>
                """,
                unsafe_allow_html=True
            )

            # Creamos una tabla MUI manualmente
            with mui.TableContainer:
                with mui.Table:
                    # Cabecera
                    with mui.TableHead:
                        with mui.TableRow:
                            for col in df.columns:
                                mui.TableCell(col, sx={"color": "white", "fontWeight": "bold"})
                    
                    # Cuerpo
                    with mui.TableBody:
                        for _, row in df.iterrows():
                            with mui.TableRow:
                                for value in row:
                                    mui.TableCell(str(value), sx={"color": "white"})
