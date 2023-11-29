import os

import dash_bootstrap_components as dbc
from dash import html

from pages.components.popovers import heading_with_info

display_info = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(heading_with_info("Display info", "display_info_info")),
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src=f'{os.getenv("SUBDOMAIN", "")}/assets/legend_arial.png'
                        ),
                        style={"marginBottom": "15px"},
                        width="auto",
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    html.B(
                                        "Selected cancer type:",
                                        style={"marginRight": "10px"},
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    html.Label("None", id="displayed_cancer"),
                                ]
                            ),
                            dbc.Row(
                                [
                                    html.B(
                                        "Number of query genes:",
                                        style={"marginRight": "10px"},
                                    ),
                                    html.Label(0, id="displayed_genes"),
                                ]
                            ),
                            dbc.Row(
                                [
                                    html.B(
                                        "Target regulations: ",
                                        style={"marginRight": "10px"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(0, id="displayed_targets"),
                                            html.Label("/"),
                                            html.Label(0, id="total_targets"),
                                        ],
                                        style={"display": "flex"},
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    html.B(
                                        "Source regulations: ",
                                        style={"marginRight": "10px"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(0, id="displayed_sources"),
                                            html.Label("/"),
                                            html.Label(0, id="total_sources"),
                                        ],
                                        style={"display": "flex"},
                                    ),
                                ]
                            ),
                        ],
                        style={"marginBottom": "15px"},
                        width="auto",
                    ),
                ],
                justify="evenly",
            ),
        ]
    ),
    className="mt-3",
)
