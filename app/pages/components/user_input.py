import dash_bootstrap_components as dbc
from dash import dcc, html


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
                            html.Center(
                                [
                                    html.H4(
                                        "Expression Data", style={"display": "inline"}
                                    ),
                                    help_component(
                                        "expression",
                                        "A csv file containing a expression matrix with samples as rows and genes as columns.",
                                        "The first column should be sample names and the first row should be the gene names.",
                                        icon_size="1.3rem",
                                        download="https://drive.google.com/u/0/uc?id=1uV9P9D33mB9g5on5mPj68KLM6Ge-rFb9&export=download",
                                    ),
                                ],
                            ),
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
                            html.Center(
                                [
                                    html.H4("Metadata", style={"display": "inline"}),
                                    help_component(
                                        "metadata",
                                        "A csv file containing meta data.",
                                        "The first column should contain samples ids and other columns for the condition and the covariates.",
                                        icon_size="1.3rem",
                                        download="https://drive.google.com/u/0/uc?id=1dJKcyBrRQi-7-KgWhy4vAHo-x1MugOvR&export=download",
                                    ),
                                ]
                            ),
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
                            html.Center(
                                [
                                    html.H4(
                                        "Gene Regulatory Network",
                                        style={"display": "inline"},
                                    ),
                                    help_component(
                                        "regulatory-network",
                                        "A csv file containing a gene regulatory network.",
                                        "The file should contain exactly two columns in the following order: ['TF', 'target'].",
                                        icon_size="1.3rem",
                                        download="https://drive.google.com/u/0/uc?id=1KE1SLe7nc0f6w8rskWiMjtIjs3idSCqH&export=download",
                                    ),
                                ]
                            ),
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
                            html.Center(
                                [
                                    html.H4("Condition", style={"display": "inline"}),
                                    help_component(
                                        "condition",
                                        "Column name for the condition in the meta DataFrame.",
                                        "The columns should encode control samples as 0 and case samples as 1.",
                                        icon_size="1.3rem",
                                    ),
                                ]
                            ),
                            dcc.Dropdown(
                                id="condition",
                                options=[],
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Center(
                                [
                                    html.H4(
                                        "Categorical Covariates",
                                        style={"display": "inline"},
                                    ),
                                    help_component(
                                        "cat-cov",
                                        "List of categorical variable names.",
                                        "Only choose columns which contain categorical data.",
                                        icon_size="1.3rem",
                                    ),
                                ]
                            ),
                            dcc.Dropdown(
                                id="cat-cov",
                                options=[],
                                multi=True,
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Center(
                                [
                                    html.H4(
                                        "Continuous Covariates",
                                        style={"display": "inline"},
                                    ),
                                    help_component(
                                        "con-cov",
                                        "List of continuous variable names.",
                                        "Only choose columns which contain continuous data.",
                                        icon_size="1.3rem",
                                    ),
                                ]
                            ),
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
                            html.Table(
                                [
                                    html.Tr(
                                        [
                                            html.Td(
                                                [
                                                    dbc.Label(
                                                        "Use zscoring of expression data",
                                                    ),
                                                    help_component(
                                                        "zscore",
                                                        "If enabled, perform zscoring on the expression data.",
                                                        icon_size="1rem",
                                                    ),
                                                    dbc.Label(
                                                        ": ",
                                                        style={"margin-right": "10px"},
                                                    ),
                                                ]
                                            ),
                                            html.Td(
                                                [
                                                    dbc.Switch(
                                                        id="zscore",
                                                        value=False,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                [
                                                    dbc.Label(
                                                        "Bonferroni α",
                                                    ),
                                                    help_component(
                                                        "bonferroni",
                                                        "P-value threshold for multiple testing correction.",
                                                        "Default: 1e-2",
                                                        icon_size="1rem",
                                                    ),
                                                    dbc.Label(
                                                        ": ",
                                                        style={"margin-right": "10px"},
                                                    ),
                                                ]
                                            ),
                                            html.Td(
                                                [
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
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                [
                                                    dbc.Label(
                                                        "Run a normality test",
                                                    ),
                                                    help_component(
                                                        "normality",
                                                        "If enabled, run a normality test for residuals 'scipy.stats.normaltest'.",
                                                        "If residuals are not normal, the edge will not be considered in the analysis.",
                                                        icon_size="1rem",
                                                    ),
                                                    dbc.Label(
                                                        ": ",
                                                        style={"margin-right": "10px"},
                                                    ),
                                                ]
                                            ),
                                            html.Td(
                                                [
                                                    dbc.Switch(
                                                        id="normality",
                                                        value=False,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                [
                                                    dbc.Label(
                                                        "Normaltest α",
                                                    ),
                                                    help_component(
                                                        "normaltest-alpha",
                                                        "P-value threshold for normaltest.",
                                                        "Is only used if 'Run a normality test' is enabled.",
                                                        "Default: 1e-3.",
                                                        icon_size="1rem",
                                                    ),
                                                    dbc.Label(
                                                        ": ",
                                                        style={"margin-right": "10px"},
                                                    ),
                                                ]
                                            ),
                                            html.Td(
                                                [
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
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                [
                                                    dbc.Label(
                                                        "R² Threshold",
                                                    ),
                                                    help_component(
                                                        "r2",
                                                        "R² threshold from 0 to 1.",
                                                        "If the fit is weaker, the edge will not be considered in the analysis.",
                                                        "Only used if a value is provided.",
                                                        icon_size="1rem",
                                                    ),
                                                    dbc.Label(
                                                        ": ",
                                                        style={"margin-right": "10px"},
                                                    ),
                                                ]
                                            ),
                                            html.Td(
                                                [
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
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                [
                                                    dbc.Label(
                                                        "Condition direction",
                                                    ),
                                                    help_component(
                                                        "condition-direction",
                                                        "If enabled only include dysregulation that are relevant for the interactions (down-regulation of an activation or up-regulation of a supressions).",
                                                        "Please check the paper for more details.",
                                                        icon_size="1rem",
                                                    ),
                                                    dbc.Label(
                                                        ": ",
                                                        style={"margin-right": "10px"},
                                                    ),
                                                ]
                                            ),
                                            html.Td(
                                                [
                                                    dbc.Switch(
                                                        id="condition-direction",
                                                        value=False,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                ],
                            )
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


def help_component(target, *args, icon_size, download=None):
    children = [
        html.P(
            text,
            style={
                "text-align": "left",
                "margin-bottom": "0.1rem",
            },
        )
        for text in args
    ]
    if download is not None:
        children.append(
            html.B(
                html.A(
                    "Example file",
                    href=download,
                    download=download.split("/")[-1],
                    style={
                        "text-align": "left",
                        "color": "white",
                    },
                )
            )
        )

    button = html.Button(
        "🛈",
        id=f"{target}-help",
        style={
            "display": "inline",
            "background-color": "transparent",
            "border": "none",
            "font-size": icon_size,
        },
    )

    out = dbc.Container(
        [
            button,
            dbc.Tooltip(
                children,
                is_open=False,
                target=f"{target}-help",
                trigger="legacy",
            ),
        ],
        style={"display": "inline", "margin": "0", "padding": "0"},
    )

    return out
