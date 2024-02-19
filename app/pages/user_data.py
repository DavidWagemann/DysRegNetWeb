import dash
from dash import html

from pages.components.user_input import get_input_layout

dash.register_page(__name__, path="/user_data")

# TODO: replace result caching by session_id caching
layout = html.Div([
        html.Div(
            [
                get_input_layout(),
            ],
            id="user-main",
            style={"margin": "5px", "padding": "0px"},
        ),
        dash.dcc.Store(id="session_id", storage_type="memory"),
    ])

