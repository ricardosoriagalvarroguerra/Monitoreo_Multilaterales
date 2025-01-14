import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

st.set_page_config(layout="wide")
st.title("Ejemplo: Card con encabezado arrastrable tipo 'título'")

# Datos de ejemplo
sample_data = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

# Layout para el Dashboard con un solo elemento ("pie_chart")
layout = [
    dashboard.Item(i="pie_chart", x=0, y=0, w=4, h=4, isDraggable=True, isResizable=True)
]

with elements("gallery_style"):
    # Grid principal, con la clase CSS .drag-handle como zona de arrastre
    with dashboard.Grid(layout, draggableHandle=".drag-handle", style={"backgroundColor": "#1e1e1e"}):
        
        # Tarjeta con key="pie_chart" que coincide con el i="pie_chart" del layout
        with mui.Card(
            key="pie_chart",
            sx={
                "width": "auto",
                "backgroundColor": "#333333",
                "borderRadius": "10px",
                "color": "#fff",          # Texto en blanco
                "overflow": "hidden"      # Para que los bordes se vean limpios
            }
        ):
            # Usamos mui.CardHeader como la cabecera (barra) de la tarjeta
            # className="drag-handle" le dice al dashboard que se arrastra desde aquí
            with mui.CardHeader(
                title="Pie chart",  # Título que aparece a la izquierda
                className="drag-handle",  # Indispensable para arrastrar
                # sx para darle estilo a la cabecera (fondo, cursor, etc.)
                sx={
                    "cursor": "move",
                    "backgroundColor": "#444444",
                    "padding": "10px"
                },
                # Puedes agregar íconos de ejemplo a la derecha, como un botón de "dark mode"
                action=mui.IconButton(
                    mui.icons.material.DarkMode,
                    sx={"color": "#fff"}
                )
            ):
                pass

            # Luego el contenido de la tarjeta (mui.CardContent),
            # dentro definimos el contenedor para el gráfico
            with mui.CardContent(sx={"backgroundColor": "#333333"}):
                with mui.Box(sx={"height": "400px", "padding": "10px"}):
                    # Aquí tu Nivo.Pie
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

# Opcional: estilo extra para asegurar el cursor "move" en la cabecera
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
