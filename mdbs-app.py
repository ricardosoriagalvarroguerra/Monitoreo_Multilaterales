import streamlit as st
import pandas as pd
import json
from uuid import uuid4
from abc import ABC, abstractmethod
from contextlib import contextmanager

# streamlit-elements
from streamlit_elements import elements, dashboard, mui, nivo, event

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
        # Zona de arrastre = .draggable
        props["draggableHandle"] = f".{Dashboard.DRAGGABLE_CLASS}"
        with dashboard.Grid(self._layout, **props):
            yield

    class Item(ABC):
        def __init__(self, board, x, y, w, h, **item_props):
            self._key = str(uuid4())
            self._draggable_class = Dashboard.DRAGGABLE_CLASS
            self._dark_mode = True

            board._register(
                dashboard.Item(self._key, x, y, w, h, **item_props)
            )

        def _switch_theme(self):
            self._dark_mode = not self._dark_mode

        @contextmanager
        def title_bar(self, padding="5px 15px 5px 15px", dark_switcher=True):
            """
            Barra horizontal arrastrable (Stack) con clase .draggable.
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
# 2. HORIZONTAL BAR (con Montos en Millones, Orden Ascendente)
###############################################################################
class HorizontalBar(Dashboard.Item):
    """
    Gráfico de barras horizontal usando Nivo.
      - Eje Y: recipientcountry_codename
      - Eje X: value_usd (millones)
    """

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
                "overflow": "hidden",
            },
            elevation=1
        ):
            with self.title_bar():
                mui.icon.BarChart()
                mui.Typography("GeoData: Horizontal Bar", sx={"flex": 1})

            with mui.Box(sx={"flex": 1, "minHeight": 0, "padding": "10px"}):
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

    # Definir PÁGINAS disponibles
    pages = ["GeoData", "OtraPágina"]

    # Inicializar st.session_state para 'page' y 'sector' si no existen
    if "page" not in st.session_state:
        st.session_state.page = "GeoData"  # Página inicial
    if "sector" not in st.session_state:
        st.session_state.sector = None

    # Leer dataset
    df = pd.read_parquet("unique_locations.parquet")
    sector_list = df["Sector"].dropna().unique().tolist()

    # --- Callbacks para actualizar st.session_state desde la UI con event.Select ---
    def handle_page_change(new_page):
        st.session_state.page = new_page

    def handle_sector_change(new_sector):
        st.session_state.sector = new_sector

    # Crear la barra de MENÚ superior (AppBar) con:
    #   - Un desplegable para la página.
    #   - Un desplegable para el sector.
    with elements("top_bar"):
        with mui.AppBar(position="static"):
            with mui.Toolbar:
                mui.Typography("Mi App", variant="h6", sx={"flex": 1})

                # Menu desplegable de "Páginas"
                with mui.Select(
                    st.session_state.page,
                    event.Select(
                        events=["onChange"],
                        args_schema=["value"],  # "value" es lo que viene del JS
                        # Llamamos a la función handle_page_change(value)
                        on_event=lambda args: handle_page_change(args["value"]),
                    ),
                    sx={"color": "#fff"},  # texto blanco sobre la AppBar
                ):
                    for pg in pages:
                        mui.MenuItem(pg, value=pg)

                # Menu desplegable para "Sector"
                with mui.Select(
                    st.session_state.sector if st.session_state.sector else "",  # valor actual
                    event.Select(
                        events=["onChange"],
                        args_schema=["value"],
                        on_event=lambda args: handle_sector_change(args["value"]),
                    ),
                    sx={"color": "#fff"},
                    displayEmpty=True  # Para mostrar un placeholder si no se ha elegido nada
                ):
                    # Placeholder ("Elige un Sector") si st.session_state.sector es None
                    mui.MenuItem("Elige un Sector", value="", disabled=True)

                    # Para un solo sector a la vez, no hay multiselect: con MUI es normal
                    for sec in sector_list:
                        mui.MenuItem(sec, value=sec)

    # --- Lógica para renderizar la página seleccionada ---
    if st.session_state.page == "GeoData":
        # Aplica Filtro de Sector si se eligió alguno
        if st.session_state.sector:
            df_filtered = df[df["Sector"] == st.session_state.sector]
        else:
            # Si no se eligió sector, mostramos todos
            df_filtered = df

        # Agrupar, convertir a millones, ordenar
        df_grouped = (
            df_filtered
            .groupby("recipientcountry_codename", as_index=False)["value_usd"]
            .sum()
        )
        df_grouped["value_usd"] = df_grouped["value_usd"] / 1_000_000
        df_grouped = df_grouped.sort_values("value_usd", ascending=True)

        bar_data = df_grouped.to_dict(orient="records")

        # Renderizamos el dashboard con el gráfico
        board = Dashboard()
        bar_item = HorizontalBar(board, x=0, y=0, w=6, h=5, isDraggable=True, isResizable=True)

        with elements("geo_data"):
            with board():
                bar_item(bar_data)

        st.markdown("""
            <style>
            .draggable {
                cursor: move;
            }
            </style>
        """, unsafe_allow_html=True)

    else:
        # Cualquier otra página
        st.write("Esta es la página 'OtraPágina'. Aquí iría otro contenido.")


if __name__ == "__main__":
    main()
