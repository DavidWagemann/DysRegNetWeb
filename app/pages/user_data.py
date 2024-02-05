import dash
from dash import html
import uuid

from pages.components.user_input import get_input_layout

dash.register_page(__name__, path="/user_data")

def serve_layout():
    session_id = str(uuid.uuid4())

    return html.Div([
        html.Div(
            [
                get_input_layout(),
            ],
            id="user-main",
            style={"margin": "5px", "padding": "0px"},
        ),
        dash.dcc.Store(id="results", storage_type="memory"),
    ])

layout = serve_layout()

