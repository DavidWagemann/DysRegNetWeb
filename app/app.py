import collections
import os

import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from flask import Flask

FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)


server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    title="DysRegNet",
    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
    # requests_pathname_prefix=os.getenv("SUBDOMAIN", "/"),
    use_pages=True,
)

app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
                for page in dash.page_registry.values()
            ],
            brand="DysRegNet",
            brand_href="#",
            className="navbar navbar-light bg-light mx-0",
            style={"margin-top": "10px", "border-radius": "10px"},
        ),
        dash.page_container,
    ],
    fluid=True,
)


if __name__ == "__main__":
    debug = os.getenv("DEBUG", "True") == "True"
    app.run_server(debug=debug)
