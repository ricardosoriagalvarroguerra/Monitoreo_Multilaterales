import streamlit as st
import pandas as pd
import json
from uuid import uuid4
from abc import ABC, abstractmethod
from contextlib import contextmanager

# streamlit-elements
from streamlit_elements import elements, dashboard, mui, nivo

###############################################################################
# 1. DASHBOARD
###############################################################################
class Dashboard:
    DRAGGABLE_CLASS = "draggable"

    def __init__(self):
        self._layout = []

    def _register(self, item):
        self._layout.append(item)

    @contextmanager
    def __call__(self, **props):
        # Indicamos que .draggable será la zona de arrastre
        props["draggableHandle"] = f".{Dashboard.DRAGGABLE_CLASS}"
        with dashboard.Grid(self._layout, **props):
            yield

    class Item(ABC):
        def __init__(self, board, x, y, w, h, **item_props):
            self._key = str(uuid4())
            self._draggable_class = Dashboard.DRAGGABLE_CLASS
            self._dark_mode = True

            # Registramos este ítem en el Dashboard
            board._register(
                dashboard.Item(self._key, x, y, w, h, **item_props)
            )

        def _switch_theme(self):
            """Cambiar entre modo oscuro y claro."""
            self._dark_mode = not self._dark_mode

        @contextmanager
        def title_bar(self, padding="5px 15px 5px 15px", dark_switcher=True):
            """
            Barra horizontal arrastrable (Stack) con clase self._draggable_class.
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
                    # Si quisieras que la barra "title_bar" también sea negra:
                    # "backgroundColor": "#000000",
                },
            ):
                yield

                if dark_switcher:
                    if self._dark_mode:
                        mui.IconButton(mui.icon.DarkMode, onClick=self._switch_theme)
                    else:
                        mui.IconButton(mui.icon.LightMode, sx={"color": "#ffc107"}, onClick=self._switch_theme)

        @abstractmethod
        def __call__(self, *args, **kwargs):
            raise NotImplementedError

###############################################################################
# 2. CARD
#    Se cambia la barra (CardHeader) a color #000000
###############################################################################
class Card(Dashboard.Item):
    """
    Ejemplo de tarjeta con CardHeader (barra),
    donde cambiamos la barra a color negro.
    """

    DEFAULT_CONTENT = (
        "This impressive paella is a perfect party dish and a fun meal to cook "
        "together with your guests. Add 1 cup of frozen peas along with the mussels, "
        "if you like."
    )

    def __call__(self, content):
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
            # Encabezado de la tarjeta
            mui.CardHeader(
                title="Shrimp and Chorizo Paella",
                subheader="September 14, 2016",
                avatar=mui.Avatar("R", sx={"bgcolor": "red"}),
                action=mui.IconButton(mui.icon.MoreVert),
                className=self._draggable_class,
                # ¡Aquí cambiamos el color de fondo a negro!
                sx={"backgroundColor": "#000000"}
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

            # Acciones
            with mui.CardActions(disableSpacing=True):
                mui.IconButton(mui.icon.Favorite)
                mui.IconButton(mui.icon.Share)

###############################################################################
# 3. HORIZONTAL BAR CHART
#    (mantiene el mismo color por defecto; si deseas que también sea negro,
#     ajusta la propiedad 'backgroundColor' en self.title_bar() )
###############################################################################
class HorizontalBar(Dashboard.Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def __call__(self, data_dict):
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
            with self.title_bar():
                mui.icon.BarChart()
                mui.Typography("Horizontal Bar", sx={"flex": 1})

            with mui.Box(sx={"flex": 1, "minHeight": 0, "padding": "10px"}):
                # Ejemplo sin filtrar, solo para ilustrar
                nivo.Bar(
                    data=data_dict,
                    keys=["value_usd"],
                    indexBy="recipientcountry_codename",
                    layout="horizontal",
                    theme=self._theme["dark" if self._dark_mode else "light"],
                    margin={"top": 40, "right": 50, "bottom": 50, "left": 160},
                    padding=0.3,
                    valueScale={"type": "linear"},
                    indexScale={"type": "band", "round": True},
                    colors={"scheme": "nivo"},
                )

###############################################################################
# 4. MAIN
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("Ejemplo con barra de la Tarjeta en #000000")

    df = pd.DataFrame({
        "Sector": ["Agro", "Industria", "Comercio", "Agro", "Comercio"],
        "recipientcountry_codename": ["Pais1", "Pais2", "Pais3", "Pais1", "Pais3"],
        "value_usd": [1000000, 2000000, 1500000, 500000, 700000]
    })

    # (Opcional) Filtro
    sector_list = df["Sector"].dropna().unique().tolist()
    selected_sectors = st.multiselect(
        "Filtrar por Sector:",
        sector_list,
        default=sector_list
    )
    df_filtered = df[df["Sector"].isin(selected_sectors)]

    # Agrupamos y preparamos datos (a modo de ejemplo)
    df_grouped = df_filtered.groupby("recipientcountry_codename", as_index=False)["value_usd"].sum()
    df_grouped = df_grouped.sort_values("value_usd", ascending=True)

    bar_data = df_grouped.to_dict(orient="records")

    # Instanciamos el dashboard
    board = Dashboard()

    # Un Card (barra negra) y un HorizontalBar
    my_card = Card(board, x=0, y=0, w=3, h=4, isDraggable=True, isResizable=True)
    bar_item = HorizontalBar(board, x=3, y=0, w=5, h=4, isDraggable=True, isResizable=True)

    with elements("demo_dashboard"):
        with board():
            my_card("¡Contenido de la tarjeta!")  # Barra del Card = #000000
            bar_item(bar_data)

    # Cursor de arrastre
    st.markdown("""
    <style>
    .draggable {
        cursor: move;
    }
    </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
