import streamlit as st
import pandas as pd
import json
from uuid import uuid4
from abc import ABC, abstractmethod
from contextlib import contextmanager

# streamlit-elements
from streamlit_elements import elements, dashboard, mui, nivo


###############################################################################
# DASHBOARD
###############################################################################
class Dashboard:
    """
    Maneja un grid arrastrable y redimensionable. Cada elemento (Item) se registra
    en un layout que se pasa a dashboard.Grid().
    """

    DRAGGABLE_CLASS = "draggable"

    def __init__(self):
        self._layout = []

    def _register(self, item):
        self._layout.append(item)

    @contextmanager
    def __call__(self, **props):
        # Le decimos a dashboard.Grid que .draggable es nuestra "manija" de arrastre.
        props["draggableHandle"] = f".{Dashboard.DRAGGABLE_CLASS}"
        with dashboard.Grid(self._layout, **props):
            yield

    class Item(ABC):
        """
        Clase base para cada elemento (gráfico, tarjeta, etc.) dentro del Dashboard.
        """
        def __init__(self, board, x, y, w, h, **item_props):
            self._key = str(uuid4())               # Identificador único
            self._draggable_class = Dashboard.DRAGGABLE_CLASS
            self._dark_mode = True                # Bandera para modo oscuro/claro

            # Registra este item en el tablero
            board._register(
                dashboard.Item(self._key, x, y, w, h, **item_props)
            )

        def _switch_theme(self):
            """ Alterna modo oscuro / claro. """
            self._dark_mode = not self._dark_mode

        @contextmanager
        def title_bar(self, padding="5px 15px 5px 15px", dark_switcher=True):
            """
            Crea un encabezado (Stack) que sirve de "barra" arrastrable si
            asignamos la clase self._draggable_class.
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
                # Aquí puede ir texto, iconos, etc.
                yield

                # Icono para alternar tema (opcional)
                if dark_switcher:
                    if self._dark_mode:
                        mui.IconButton(mui.icon.DarkMode, onClick=self._switch_theme)
                    else:
                        mui.IconButton(mui.icon.LightMode, sx={"color": "#ffc107"}, onClick=self._switch_theme)

        @abstractmethod
        def __call__(self, *args, **kwargs):
            """ Cada subclase define cómo se renderiza. """
            raise NotImplementedError


###############################################################################
# HORIZONTAL BAR CHART
###############################################################################
class HorizontalBar(Dashboard.Item):
    """
    Genera un gráfico de barras horizontal usando Nivo. Filtra por 'Sector' en Streamlit
    y agrupa por 'recipientcountry_codename', sumando 'value_usd'.
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
        :param data_dict: Lista de diccionarios con campos:
            { "recipientcountry_codename": "...", "value_usd": ... }
        """
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
            # Barra de título arrastrable
            with self.title_bar():
                mui.icon.BarChart()
                mui.Typography("Horizontal Bar Chart", sx={"flex": 1})

            # Contenedor principal para el gráfico
            with mui.Box(sx={"flex": 1, "minHeight": 0, "padding": "10px"}):
                # Renderizamos la gráfica con Nivo
                # - 'layout="horizontal"' para barras horizontales
                # - 'keys=["value_usd"]' define la(s) serie(s) a graficar
                # - 'indexBy="recipientcountry_codename"' define la categoría (Y axis)
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
                        "legend": "recipientcountry_codename",
                        "legendPosition": "middle",
                        "legendOffset": -100
                    },
                    axisBottom={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legend": "value_usd",
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
# MAIN
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("Horizontal Bar Chart con Filtro de 'Sector'")

    # 1) Cargar dataset
    df = pd.read_parquet("unique_locations.parquet")

    # 2) Crear un filtro de Sector
    sector_list = df["Sector"].dropna().unique().tolist()
    selected_sectors = st.multiselect("Filtrar por Sector:", sector_list, default=sector_list)

    # 3) Filtrar el DataFrame
    df_filtered = df[df["Sector"].isin(selected_sectors)]

    # 4) Agrupar por país y sumar value_usd
    df_grouped = df_filtered.groupby("recipientcountry_codename", as_index=False)["value_usd"].sum()

    # 5) Convertir a lista de diccionarios (para nivo.Bar)
    bar_data = df_grouped.to_dict(orient="records")

    # 6) Crear el dashboard
    board = Dashboard()

    # 7) Instanciar nuestro HorizontalBar
    bar_item = HorizontalBar(board, x=0, y=0, w=6, h=5, isDraggable=True, isResizable=True)

    # 8) Renderizar con streamlit_elements
    with elements("demo_dashboard"):
        # Abrimos el Dashboard
        with board():
            bar_item(bar_data)

    # 9) CSS para ver el cursor de arrastre
    st.markdown("""
        <style>
        .draggable {
            cursor: move;
        }
        </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
