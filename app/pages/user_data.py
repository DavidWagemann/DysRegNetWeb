import dash
from dash import html

dash.register_page(__name__, path="/user_data")

layout = html.Div(
    [
        html.H1("Upload your own data, please."),
    ]
)
