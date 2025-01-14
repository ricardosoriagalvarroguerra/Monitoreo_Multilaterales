import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Ejemplo: Drag & Resize de un Gráfico dentro de un Card")

# Datos de ejemplo para un gráfico de pastel (Nivo Pie Chart)
sample_data = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

# Definición del layout del dashboard
layout = [
    dashboard.Item(
        i="pie_chart",  # Identificador único para el elemento
        x=0, y=0,        # Posición inicial en la cuadrícula
        w=4, h=4,        # Ancho y alto en celdas del grid
        isDraggable=True,
        isResizable=True
    )
]

# Iniciamos los elementos de streamlit_elements
with elements("drag_resize_demo"):
    # Definimos el Grid del dashboard
    with dashboard.Grid(
        layout, 
        draggableHandle=".drag-handle",  # Clase CSS para el manejador de arrastre
        style={"backgroundColor": "#222222"}  # Estilo de fondo del grid
    ):
        # Definimos una tarjeta (Card) de Material-UI para contener el gráfico
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
                )  # Cierre de la función nivo.Pie

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
