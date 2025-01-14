import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

st.set_page_config(layout="wide")
st.title("Ejemplo: Arrastrar el gráfico con la manija DENTRO de la tarjeta")

# Datos de ejemplo para tu Nivo Pie chart
sample_data = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

# Layout del dashboard: un solo Item arrastrable y redimensionable, con key "pie_chart"
layout = [
    dashboard.Item(
        i="pie_chart",
        x=0, y=0,
        w=4, h=4,
        isDraggable=True,
        isResizable=True
    )
]

# Iniciamos el contexto "elements"
with elements("demo_dashboard"):
    
    # Definimos el Grid del dashboard, usando `layout` y clase CSS .drag-handle
    with dashboard.Grid(layout, draggableHandle=".drag-handle"):
        
        # AQUÍ es donde definimos la Card con el MISMO key que "i" en el layout
        with mui.Card(
            key="pie_chart",
            sx={
                "backgroundColor": "#333333",
                "borderRadius": "10px",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%"
            }
        ):

            # Aquí mismo metemos la manija, con la clase .drag-handle
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
                    Arrastra aquí (manija dentro de la tarjeta)
                </div>
                """,
                unsafe_allow_html=True
            )

            # Ahora, en el MISMO with, definimos el contenedor Box para el gráfico
            with mui.Box(sx={"height": 400, "padding": "10px"}):
                # Añadimos el gráfico de Nivo
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

# Estilo para el cursor en la manija
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
