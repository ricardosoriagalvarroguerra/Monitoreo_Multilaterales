rom streamlit_elements import mui, html, sync
import json

class Card:
    DEFAULT_CONTENT = "Hello from your card!"

    def __init__(self, board, x, y, w, h, minW=None, minH=None):
        """Inicializa los parámetros de posicionamiento en el dashboard."""
        self.board = board
        self.item_id = "my_card"  # Identificador único
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.minW = minW
        self.minH = minH

    def __call__(self, content=None):
        """
        Al llamar a la instancia como función, se renderiza la Card 
        en la posición especificada del Dashboard.
        """
        # Si no se provee contenido, usar contenido por defecto
        if content is None:
            content = self.DEFAULT_CONTENT

        with self.board(item_id=self.item_id, x=self.x, y=self.y, w=self.w, h=self.h,
                        minW=self.minW, minH=self.minH):
            # Construimos la tarjeta con MUI
            with mui.Card(key=self.item_id, sx={
                "backgroundColor": "#333333",
                "borderRadius": "10px",
                "color": "#fff",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "overflow": "hidden"
            }):

                # Encabezado arrastrable con mui.CardHeader
                with mui.CardHeader(
                    title="Mi Card Title",               # Texto a la izquierda
                    className="drag-handle",             # Zona draggable
                    sx={
                        "cursor": "move",
                        "backgroundColor": "#444444",
                        "padding": "10px"
                    },
                    action=mui.IconButton(
                        # Si tu versión soporta mui.icons.material:
                        # mui.icons.material.DarkMode,
                        #
                        # Si no, prueba solo mui.icons.DarkMode o sin icono.
                        mui.icons.DarkMode,
                        sx={"color": "#fff"}
                    )
                ):
                    pass

                # Contenido de la tarjeta
                with mui.CardContent(sx={"backgroundColor": "#333", "flex": 1}):
                    # Aquí pones lo que quieras renderizar. Ejemplo: texto o HTML
                    html.div(content, style={"padding": "10px"})
