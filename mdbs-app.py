import streamlit as st
import json
from uuid import uuid4
from abc import ABC, abstractmethod
from contextlib import contextmanager

# Importaciones de streamlit-elements
from streamlit_elements import elements, dashboard, mui, nivo


###############################################################################
# 1. DASHBOARD
###############################################################################
class Dashboard:
    """
    Dashboard principal para manejar el layout de items arrastrables.
    Usa la clase interna 'Item' como base para elementos concretos (Card, Pie, etc.).
    """

    DRAGGABLE_CLASS = "draggable"  # Clase CSS para el handle de arrastre

    def __init__(self):
        self._layout = []  # Guarda el layout de cada item

    def _register(self, item):
        """
        Registra cada item (Card, Pie, etc.) en el layout.
        """
        self._layout.append(item)

    @contextmanager
    def __call__(self, **props):
        """
        Permite usar 'with board(...)' para crear un dashboard.Grid
        con las propiedades deseadas.
        """
        # Indicamos que la clase arrastrable será .draggable
        props["draggableHandle"] = f".{Dashboard.DRAGGABLE_CLASS}"

        with dashboard.Grid(self._layout, **props):
            yield

    # -------------------------------------------------------------------------
    # Clase interna 'Item' que servirá como base para Card, Pie, etc.
    # -------------------------------------------------------------------------
    class Item(ABC):
        def __init__(self, board, x, y, w, h, **item_props):
            """
            :param board: Instancia de Dashboard.
            :param x, y: Posición inicial en el Grid (en celdas).
            :param w, h: Tamaño en celdas.
            :param item_props: Extras (isDraggable, isResizable, etc.).
            """
            # Identificador único para el item
            self._key = str(uuid4())
            # Clase CSS para arrastre
            self._draggable_class = Dashboard.DRAGGABLE_CLASS
            # Modo oscuro o claro
            self._dark_mode = True

            # Registramos este item en el Dashboard
            board._register(
                dashboard.Item(self._key, x, y, w, h, **item_props)
            )

        def _switch_theme(self):
            """
            Cambia de modo oscuro a claro, o viceversa.
            """
            self._dark_mode = not self._dark_mode

        @contextmanager
        def title_bar(self, padding="5px 15px 5px 15px", dark_switcher=True):
            """
            Crea una barra horizontal (Stack) que sirve como zona arrastrable
            si incluye la clase self._draggable_class.
            """
            with mui.Stack(
                className=self._draggable_class,
                alignItems="center",
                direction="row",
                spacing=1,
                sx={
                    "padding": padding,
                    "borderBottom": 1,
                    "borderColor": "divider",
                },
            ):
                # Contenido que añada el desarrollador
                yield

                # Botón para alternar modo oscuro/claro
                if dark_switcher:
                    if self._dark_mode:
                        mui.IconButton(mui.icon.DarkMode, onClick=self._switch_theme)
                    else:
                        mui.IconButton(mui.icon.LightMode, sx={"color": "#ffc107"}, onClick=self._switch_theme)

        @abstractmethod
        def __call__(self, *args, **kwargs):
            """
            Método que debe implementar cada subclase para renderizarse.
            """
            raise NotImplementedError


###############################################################################
# 2. CARD
###############################################################################
class Card(Dashboard.Item):
    """
    Ejemplo de tarjeta con header, imagen, contenido y acciones.
    """

    DEFAULT_CONTENT = (
        "This impressive paella is a perfect party dish and a fun meal to cook "
        "together with your guests. Add 1 cup of frozen peas along with the mussels, "
        "if you like."
    )

    def __call__(self, content):
        """
        Renderiza la tarjeta con:
          - CardHeader
          - CardMedia (imagen)
          - CardContent (texto)
          - CardActions (íconos de acción)
        """
        if not content:
            content = self.DEFAULT_CONTENT

        with mui.Card(
            key=self._key,
            sx={
                "display": "flex",
                "flexDirection": "column",
                "borderRadius": 3,
                "overflow": "hidden"
            },
            elevation=1
        ):
            # Encabezado de la tarjeta con subheader e ícono
            mui.CardHeader(
                title="Shrimp and Chorizo Paella",
                subheader="September 14, 2016",
                avatar=mui.Avatar("R", sx={"bgcolor": "red"}),
                action=mui.IconButton(mui.icon.MoreVert),
                # className define la zona arrastrable
                className=self._draggable_class
            )

            # Imagen
            mui.CardMedia(
                component="img",
                height=194,
                image="https://mui.com/static/images/cards/paella.jpg",
                alt="Paella dish"
            )

            # Contenido
            with mui.CardContent(sx={"flex": 1}):
                mui.Typography(content)

            # Acciones (iconos)
            with mui.CardActions(disableSpacing=True):
                mui.IconButton(mui.icon.Favorite)
                mui.IconButton(mui.icon.Share)


###############################################################################
# 3. PIE CHART
###############################################################################
class Pie(Dashboard.Item):
    """
    Gráfico de pastel (Pie chart) usando Nivo, con soporte para modo oscuro/claro.
    """

    DEFAULT_DATA = [
        { "id": "java",   "label": "java",   "value": 465, "color": "hsl(128, 70%, 50%)" },
        { "id": "rust",   "label": "rust",   "value": 140, "color": "hsl(178, 70%, 50%)" },
        { "id": "scala",  "label": "scala",  "value":  40, "color": "hsl(322, 70%, 50%)" },
        { "id": "ruby",   "label": "ruby",   "value": 439, "color": "hsl(117, 70%, 50%)" },
        { "id": "elixir", "label": "elixir", "value": 366, "color": "hsl(286, 70%, 50%)" }
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definimos temas para modo oscuro y claro
        self._theme = {
            "dark": {
                "background": "#252526",
                "textColor": "#FAFAFA",
                "tooltip": {
                    "container": {
                        "background": "#3F3F3F",
                        "color": "#FAFAFA",
                    }
                }
            },
            "light": {
                "background": "#FFFFFF",
                "textColor": "#31333F",
                "tooltip": {
                    "container": {
                        "background": "#FFFFFF",
                        "color": "#31333F",
                    }
                }
            }
        }

    def __call__(self, json_data):
        """
        Recibe un string JSON y lo parsea para renderizar el Pie chart.
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            data = self.DEFAULT_DATA

        # Paper: contenedor con fondo y borde redondeado
        with mui.Paper(
            key=self._key,
            sx={
                "display": "flex",
                "flexDirection": "column",
                "borderRadius": 3,
                "overflow": "hidden"
            },
            elevation=1
        ):
            # Usamos la barra de título para tener la clase arrastrable
            with self.title_bar():
                mui.icon.PieChart()
                mui.Typography("Pie chart", sx={"flex": 1})

            # Contenedor principal para el gráfico
            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Pie(
                    data=data,
                    theme=self._theme["dark" if self._dark_mode else "light"],
                    margin={"top": 40, "right": 80, "bottom": 80, "left": 80},
                    innerRadius=0.5,
                    padAngle=0.7,
                    cornerRadius=3,
                    activeOuterRadiusOffset=8,
                    borderWidth=1,
                    borderColor={
                        "from": "color",
                        "modifiers": [["darker", 0.2]]
                    },
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsTextColor="grey",
                    arcLinkLabelsThickness=2,
                    arcLinkLabelsColor={ "from": "color" },
                    arcLabelsSkipAngle=10,
                    arcLabelsTextColor={
                        "from": "color",
                        "modifiers": [["darker", 2]]
                    },
                    defs=[
                        {
                            "id": "dots",
                            "type": "patternDots",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "size": 4,
                            "padding": 1,
                            "stagger": True
                        },
                        {
                            "id": "lines",
                            "type": "patternLines",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "rotation": -45,
                            "lineWidth": 6,
                            "spacing": 10
                        }
                    ],
                    fill=[
                        { "match": { "id": "ruby" },   "id": "dots" },
                        { "match": { "id": "c" },      "id": "dots" },
                        { "match": { "id": "go" },     "id": "dots" },
                        { "match": { "id": "python" }, "id": "dots" },
                        { "match": { "id": "scala" },  "id": "lines" },
                        { "match": { "id": "lisp" },   "id": "lines" },
                        { "match": { "id": "elixir" }, "id": "lines" },
                        { "match": { "id": "javascript" }, "id": "lines" }
                    ],
                    legends=[
                        {
                            "anchor": "bottom",
                            "direction": "row",
                            "justify": False,
                            "translateX": 0,
                            "translateY": 56,
                            "itemsSpacing": 0,
                            "itemWidth": 100,
                            "itemHeight": 18,
                            "itemTextColor": "#999",
                            "itemDirection": "left-to-right",
                            "itemOpacity": 1,
                            "symbolSize": 18,
                            "symbolShape": "circle",
                            "effects": [
                                {
                                    "on": "hover",
                                    "style": {
                                        "itemTextColor": "#000"
                                    }
                                }
                            ]
                        }
                    ]
                )


###############################################################################
# 4. MAIN APP
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("Ejemplo unificado: Dashboard, Card y Pie Chart en un solo archivo")

    # 1) Creamos el dashboard
    board = Dashboard()

    # 2) Instanciamos un Card y un Pie chart
    card_item = Card(board, x=0, y=0, w=4, h=5, isDraggable=True, isResizable=True)
    pie_item = Pie(board, x=4, y=0, w=4, h=5, isDraggable=True, isResizable=True)

    # 3) Renderizamos con elements
    with elements("demo"):
        # Abrimos el dashboard (Grid), el "with board()" usa la clase .draggable
        with board():
            # Mostramos la Card con algún contenido
            card_item("¡Hola! Este es el contenido de mi Card.")

            # Mostramos el Pie con datos por defecto (convertidos a JSON)
            data_json = json.dumps(pie_item.DEFAULT_DATA)
            pie_item(data_json)


if __name__ == "__main__":
    main()
