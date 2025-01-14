import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Ejemplo: Dashboard con Drag & Resize y Gráfico de Nivo")

# Datos de ejemplo para un gráfico de pastel (Nivo Pie Chart)
sample_data = [
    {"id": "java",   "label": "Java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "Rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "Ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "Scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "Elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

# Definición del layout del dashboard
layout = [
    # Elemento 1: Gráfico de Pastel
    dashboard.Item(
        i="pie_chart",  # Identificador único
        x=0, y=0,        # Posición inicial
        w=4, h=4,        # Tamaño en celdas
        isDraggable=True,
        isResizable=True
    ),
    # Elemento 2: Segundo Elemento (Ejemplo)
    dashboard.Item(
        i="second_item",
        x=4, y=0,
        w=4, h=4,
        isDraggable=True,
        isResizable=True
    ),
    # Elemento 3: Tercer Elemento (Ejemplo)
    dashboard.Item(
        i="third_item",
        x=0, y=4,
        w=2, h=2,
        isDraggable=True,
        isResizable=True
    ),
]

# Función para manejar cambios en el layout
def handle_layout_change(updated_layout):
    # Aquí puedes manejar el layout actualizado, por ejemplo, guardarlo en una base de datos o archivo
    st.write("Layout Actualizado:", updated_layout)

# Iniciamos los elementos de streamlit_elements
with elements("dashboard"):
    # Definimos el Grid del dashboard
    with dashboard.Grid(
        layout, 
        draggableHandle=".drag-handle",  # Clase CSS para el manejador de arrastre
        style={"backgroundColor": "#222222"},  # Estilo de fondo del grid
        onLayoutChange=handle_layout_change  # Callback para cambios en el layout
    ):
        # Elemento 1: Gráfico de Pastel dentro de una Card
        with mui.Card(
            key="pie_chart",  # Debe coincidir con el identificador en el layout
            sx={
                "backgroundColor": "#333333",
                "borderRadius": "10px",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%"  # Asegura que el Card ocupe todo el espacio asignado
            }
        ):
            # Manejador de arrastre (drag handle)
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
            
            # Contenedor para el gráfico con Box de Material-UI
            with mui.Box(
                sx={
                    "flex": 1,  # Permite que el Box ocupe el espacio restante en el Card
                    "padding": "10px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }
            ):
                # Gráfico de Pastel de Nivo
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
                )
        
        # Elemento 2: Segundo Elemento (Ejemplo) dentro de una Card
        with mui.Card(
            key="second_item",
            sx={
                "backgroundColor": "#555555",
                "borderRadius": "10px",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%"
            }
        ):
            st.markdown(
                """
                <div class="drag-handle"
                     style="
                         cursor: move; 
                         background-color: #666666;
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
            with mui.Box(
                sx={
                    "flex": 1,
                    "padding": "10px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }
            ):
                st.write("Contenido del Segundo Elemento")
        
        # Elemento 3: Tercer Elemento (Ejemplo) dentro de una Card
        with mui.Card(
            key="third_item",
            sx={
                "backgroundColor": "#777777",
                "borderRadius": "10px",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%"
            }
        ):
            st.markdown(
                """
                <div class="drag-handle"
                     style="
                         cursor: move; 
                         background-color: #888888;
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
            with mui.Box(
                sx={
                    "flex": 1,
                    "padding": "10px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }
            ):
                st.write("Contenido del Tercer Elemento")
    
    # Estilos personalizados para mejorar la experiencia de arrastre y redimensionamiento
    st.markdown(
        """
        <style>
        /* Asegura que el cursor de arrastre aparezca correctamente */
        .drag-handle {
            cursor: move;
        }

        /* Ajustes para el Box que contiene el gráfico */
        .streamlit-container {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
