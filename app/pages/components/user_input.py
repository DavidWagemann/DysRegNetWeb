import dash_bootstrap_components as dbc
from dash import dcc, html
from pandas import wide_to_long


def get_input_layout() -> dbc.Container:
    """
    Returns the layout for the user input section.

    This function creates a layout using the Dash Bootstrap Components (dbc) and Dash Core Components (dcc)
    to allow users to upload files and select options for their input data.

    Returns:
        dbc.Container: The layout container containing all the input components.
    """
    return dbc.Container(
        [
            dbc.Alert(
                [
                    "Something went wrong",
                ],
                id="errorbox",
                color="danger",
                style={"display": "None"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Center(html.H4("Expression Data")),
                            dcc.Upload(
                                id="expression",
                                children="Drag and Drop or Select Files",
                                accept=".csv",
                                style={
                                    "width": "100%",
                                    "height": "60px",
                                    "lineHeight": "60px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "margin": "10px",
                                    "cursor": "pointer",
                                },
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Center(html.H4("Metadata")),
                            dcc.Upload(
                                id="meta",
                                children="Drag and Drop or Select Files",
                                accept=".csv",
                                style={
                                    "width": "100%",
                                    "height": "60px",
                                    "lineHeight": "60px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "margin": "10px",
                                    "cursor": "pointer",
                                },
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Center(html.H4("Gene Regulatory Network")),
                            dcc.Upload(
                                id="network",
                                children="Drag and Drop or Select Files",
                                accept=".csv",
                                style={
                                    "width": "100%",
                                    "height": "60px",
                                    "lineHeight": "60px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "margin": "10px",
                                    "cursor": "pointer",
                                },
                            ),
                        ]
                    ),
                ]
            ),
            html.Br(),
            dcc.Loading(
                id="loading-options",
                type="default",
                children=html.Div(id="loading-options-output"),
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Center(html.H4("Condition")),
                            dcc.Dropdown(
                                id="condition",
                                options=[],
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Center(html.H4("Categorical Covariates")),
                            dcc.Dropdown(
                                id="cat-cov",
                                options=[],
                                multi=True,
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Center(html.H4("Continuous Covariates")),
                            dcc.Dropdown(
                                id="con-cov",
                                options=[],
                                multi=True,
                            ),
                        ]
                    ),
                    html.Br(),
                ],
                id="select-cols",
                style={"display": "None"},
            ),
            dbc.Container(
                [
                    html.Center(html.H3("Options")),
                    html.Center(
                        [
                            dbc.Row(
                                [
                                    dbc.Container(
                                        [
                                            dbc.Label(
                                                "Use zscoring of expression data: ",
                                                style={"margin-right": "10px"},
                                            ),
                                            dbc.Switch(
                                                id="zscore",
                                                value=False,
                                            ),
                                        ],
                                        id="styled-numeric-input",
                                        style={
                                            "display": "flex",
                                            "justify-content": "start",
                                            "width": "50%",
                                        },
                                    ),
                                ],
                                justify="center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Container(
                                        [
                                            html.P(
                                                "Bonferroni α: ",
                                                style={"margin-right": "10px"},
                                            ),
                                            dbc.Input(
                                                id="bonferroni",
                                                type="number",
                                                min=0,
                                                max=1,
                                                step=0.01,
                                                style={
                                                    "width": "100px",
                                                    "height": "30px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "justify-content": "start",
                                            "width": "50%",
                                            "text-align": "left",
                                        },
                                    ),
                                ],
                                justify="center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Container(
                                        [
                                            dbc.Label(
                                                "Run a normality test: ",
                                                style={"margin-right": "10px"},
                                            ),
                                            dbc.Switch(
                                                id="normality",
                                                value=False,
                                            ),
                                        ],
                                        id="styled-numeric-input",
                                        style={
                                            "display": "flex",
                                            "justify-content": "start",
                                            "width": "50%",
                                        },
                                    ),
                                ],
                                justify="center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Container(
                                        [
                                            html.P(
                                                "Normaltest α: ",
                                                style={"margin-right": "10px"},
                                            ),
                                            dbc.Input(
                                                id="normaltest-alpha",
                                                type="number",
                                                min=0,
                                                max=1,
                                                step=0.01,
                                                style={
                                                    "width": "100px",
                                                    "height": "30px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "justify-content": "start",
                                            "width": "50%",
                                            "text-align": "left",
                                        },
                                    ),
                                ],
                                justify="center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Container(
                                        [
                                            html.P(
                                                "R² Threshold",
                                                style={"margin-right": "10px"},
                                            ),
                                            dbc.Input(
                                                id="r2",
                                                type="number",
                                                min=0,
                                                max=1,
                                                step=0.01,
                                                style={
                                                    "width": "100px",
                                                    "height": "30px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "justify-content": "start",
                                            "width": "50%",
                                            "text-align": "left",
                                        },
                                    ),
                                ],
                                justify="center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Container(
                                        [
                                            dbc.Label(
                                                "Condition direction: ",
                                                style={"margin-right": "10px"},
                                            ),
                                            dbc.Switch(
                                                id="condition-direction",
                                                value=False,
                                            ),
                                        ],
                                        id="styled-numeric-input",
                                        style={
                                            "display": "flex",
                                            "justify-content": "start",
                                            "width": "50%",
                                        },
                                    ),
                                ],
                                justify="center",
                            ),
                            html.Br(),
                        ],
                    ),
                ],
                id="options",
                style={"display": "None"},
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Button(
                        "Run DysRegNet",
                        id="run",
                        color="success",
                        className="mr-1",
                        outline=True,
                        disabled=True,
                        style={"width": "30%"},
                    )
                ],
                justify="center",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Running DysRegNet"), close_button=False
                    ),
                    dbc.ModalBody([html.Center([dbc.Progress(id="progress")])]),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Cancel",
                            id="cancel-run",
                            color="danger",
                            className="mr-1",
                            outline=True,
                        ),
                    ),
                ],
                id="modal",
                is_open=False,
                backdrop="static",
                centered=True,
            ),
        ],
        id="input_layout",
    )
