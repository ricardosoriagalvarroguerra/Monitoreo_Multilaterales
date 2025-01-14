import streamlit as st
from streamlit_elements import elements, dashboard, mui, nivo

# Ejemplo de datos para un gráfico de pastel Nivo
SAMPLE_DATA = [
    {"id": "java",   "label": "java",   "value": 465, "color": "hsl(104, 70%, 50%)"},
    {"id": "rust",   "label": "rust",   "value": 140, "color": "hsl(204, 70%, 50%)"},
    {"id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(304, 70%, 50%)"},
    {"id": "scala",  "label": "scala",  "value":  40, "color": "hsl(51, 70%, 50%)"},
    {"id": "elixir", "label": "elixir", "value": 366, "color": "hsl(11, 70%, 50%)"},
]

###############################################################################
# CLASE CARD
###############################################################################
class Card:
    """
    Clase que representa una tarjeta (mui.Card) dentro del dashboard,
    con encabezado arrastrable gracias a CardHeader (className="drag-handle").
    """
    def __init__(self, i, x, y, w, h, title="Mi Chart", minW=None, minH=None):
        """
        :param i: Identificador único de la tarjeta (coincide con dashboard.Item).
        :param x, y: Posición inicial en la cuadrícula.
        :param w, h: Tamaño en celdas de la cuadrícula.
        :param title: Título que aparece en la cabecera de la tarjeta.
        :param minW, minH: Tamaños mínimos, si deseas restringir el resizing.
        """
        self.i = i
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.minW = minW
        self.minH = minH

    def render(self, data):
        """
        Renderiza la tarjeta y su contenido:
          - Un encabezado (CardHeader) con className="drag-handle".
          - Un contenido (CardContent) que muestra un Pie chart de Nivo.
        :param data: datos a pasarle al Pie chart (SAMPLE_DATA, por ejemplo).
        """
        # Definimos la Card con el MISMO key que self.i
        with mui.Card(
            key=self.i,
            sx={
                "backgroundColor": "#333333",
                "borderRadius": "10px",
                "color": "#fff",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "overflow": "hidden"
            }
        ):
            # Cabecera arrastrable
            with mui.CardHeader(
                title=self.title,
                className="drag-handle",  # permite arrastrar desde aquí
                sx={
                    "cursor": "move",
                    "backgroundColor": "#444444",
                    "padding": "10px"
                },
                # Si tu versión de streamlit-elements soporta mui.icons.material:
                # action=mui.IconButton(mui.icons.material.DarkMode, sx={"color": "#fff"})
                #
                # Si da error con ".material", usa solo mui.icons.DarkMode o elimina el ícono:
                action=None
            ):
                pass

            # Contenido principal
            with mui.CardContent(sx={"backgroundColor": "#333", "flex": 1}):
                with mui.Box(sx={"height": "100%", "padding": "10px"}):
                    # Aquí definimos el gráfico de Pastel con Nivo
                    nivo.Pie(
                        data=data,
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

###############################################################################
# FUNCIÓN PRINCIPAL
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("Ejemplo todo-en-uno: Card con encabezado arrastrable y Pie Chart")

    # Definimos el layout del dashboard:
    # - Un único item (identificador="pie_card") arrastrable y redimensionable
    layout = [
        dashboard.Item(
            i="pie_card",
            x=0, y=0,
            w=4, h=4,
            isDraggable=True,
            isResizable=True,
            minW=3,
            minH=3
        )
    ]

    # Instanciamos nuestra Card con los parámetros del layout
    # (para no duplicar, reutilizamos "pie_card" como id)
    my_card = Card(
        i="pie_card",  # debe coincidir con i= en dashboard.Item
        x=0, y=0,      # lo mismo que en layout (opcional si no la mueves dinámicamente)
        w=4, h=4,
        title="Mi Pie Chart",  # Título que se verá en el encabezado
        minW=3, minH=3
    )

    # Renderizamos con streamlit-elements
    with elements("demo_dashboard"):
        # Creamos el grid, indicando que .drag-handle es la zona arrastrable
        with dashboard.Grid(layout, draggableHandle=".drag-handle", style={"backgroundColor": "#1e1e1e"}):
            # Aquí llamamos la Card y le pasamos los datos del gráfico
            my_card.render(SAMPLE_DATA)

    # Estilos para asegurar que el cursor "move" aparezca en la cabecera
    st.markdown("""
        <style>
        .drag-handle {
            cursor: move;
        }
        </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
