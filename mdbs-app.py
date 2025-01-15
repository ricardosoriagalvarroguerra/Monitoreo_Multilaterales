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
                    # Barra superior en color negro
                    "backgroundColor": "#000000",
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
# 2. HORIZONTAL BAR CHART (con Montos en Millones, Orden Ascendente)
###############################################################################
class HorizontalBar(Dashboard.Item):
    """
    Gráfico de barras horizontal usando Nivo, mostrando:
      - Eje Y: recipientcountry_codename
      - Eje X: value_usd (en millones)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definimos temas para modo oscuro / claro
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
        """
        data_dict: Lista de diccionarios, p.ej:
            [
                {
                    "recipientcountry_codename": "País A",
                    "value_usd": 123.45  # en millones
                },
                ...
            ]
        """
        with mui.Paper(
            key=self._key,
            sx={
                "display": "flex",
                "flexDirection": "column",
                "borderRadius": 3,
                "overflow": "hidden",
                # Borde negro para todo el contenedor
                "border": "2px solid #000000",
            },
            elevation=1
        ):
            # Barra de título (manija) -> color #000000 (definido en title_bar)
            with self.title_bar():
                mui.icon.BarChart()
                mui.Typography("Horizontal Bar (Millones, Asc)", sx={"flex": 1})

            with mui.Box(sx={"flex": 1, "minHeight": 0, "padding": "10px"}):
                # Gráfico de barras horizontal
                # 'keys=["value_usd"]' indica la columna con los valores
                # 'indexBy="recipientcountry_codename"' para la categoría
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
                    axisLeft={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legend": "País",
                        "legendPosition": "middle",
                        "legendOffset": -100
                    },
                    axisBottom={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legend": "Monto (Millones USD)",
                        "legendPosition": "middle",
                        "legendOffset": 40
                    },
                    enableLabel=True,
                    labelSkipWidth=12,
                    labelSkipHeight=12,
                    labelTextColor={"from": "color", "modifiers": [["darker", 1.6]]},
                    legends=[
                        {
                            "dataFrom": "keys",
                            "anchor": "bottom-right",
                            "direction": "column",
                            "justify": False,
                            "translateX": 120,
                            "translateY": 0,
                            "itemsSpacing": 2,
                            "itemWidth": 100,
                            "itemHeight": 20,
                            "symbolSize": 20,
                            "effects": [
                                {
                                    "on": "hover",
                                    "style": {
                                        "itemOpacity": 1
                                    }
                                }
                            ]
                        }
                    ]
                )

###############################################################################
# 3. MAIN
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("Horizontal Bar Chart: Montos a Millones, Orden Ascendente")

    # 1) Cargar dataset
    df = pd.read_parquet("unique_locations.parquet")

    # 2) Filtro de Sector
    sector_list = df["Sector"].dropna().unique().tolist()
    selected_sectors = st.multiselect(
        "Filtrar por Sector:",
        sector_list,
        default=sector_list
    )

    # 3) Filtrar DataFrame
    df_filtered = df[df["Sector"].isin(selected_sectors)]

    # 4) Agrupar por País, sumar value_usd
    df_grouped = df_filtered.groupby("recipientcountry_codename", as_index=False)["value_usd"].sum()

    # 5) Convertir value_usd a millones
    df_grouped["value_usd"] = df_grouped["value_usd"] / 1_000_000

    # 6) Orden ascendente por value_usd
    df_grouped = df_grouped.sort_values("value_usd", ascending=True)

    # 7) Pasar a diccionario
    bar_data = df_grouped.to_dict(orient="records")

    # 8) Dashboard + Render
    board = Dashboard()
    bar_item = HorizontalBar(board, x=0, y=0, w=6, h=5, isDraggable=True, isResizable=True)

    with elements("demo_dashboard"):
        with board():
            bar_item(bar_data)

    # Estilo para el cursor "move"
    st.markdown("""
        <style>
        .draggable {
            cursor: move;
        }
        </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
