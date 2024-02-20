import base64
import io
import time
from contextlib import redirect_stderr
from typing import Any, Dict, List, Literal, Tuple, Union
from uuid import uuid4

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
from dash import callback, ctx, dcc, html
from dash._callback import NoUpdate
from dash.dependencies import Input, Output, State
from pages.components.control_data import ControlData
from pages.components.dysregnet_progress import DysregnetProgress
from pages.components.run_dysregnet import get_results
from pages.components.user_output import get_output_layout
from pandas.testing import assert_index_equal

control_data = ControlData()

app = dash.get_app()


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
                                        download="https://figshare.com/ndownloader/files/43544799",
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
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Center(
                                            [
                                                html.H4(
                                                    "Metadata",
                                                    id="metadata-title",
                                                    style={
                                                        "display": "inline",
                                                        "color": "black",
                                                    },
                                                ),
                                                help_component(
                                                    "metadata",
                                                    "A csv file containing meta data.",
                                                    "The first column should contain samples ids and other columns for the condition and the covariates.",
                                                    icon_size="1.3rem",
                                                    download="https://figshare.com/ndownloader/files/43544802",
                                                ),
                                            ]
                                        ),
                                        style={
                                            "display": "inline",
                                            "margin": "0",
                                            "padding": "0",
                                        },
                                        width={"size": 6, "offset": 0},
                                    ),
                                    dbc.Col(
                                        dbc.Container(
                                            [
                                                daq.BooleanSwitch(
                                                    id="meta-toggle-switch",
                                                    on=False,
                                                    color="#303030",
                                                    style={
                                                        "display": "inline",
                                                        "margin": "0",
                                                        "padding": "0",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "inline",
                                                "margin": "0",
                                                "padding": "0",
                                            },
                                        ),
                                    ),
                                    dbc.Col(
                                        html.Center(
                                            [
                                                html.H4(
                                                    "GTEx",
                                                    id="gtexdata-title",
                                                    style={
                                                        "display": "inline",
                                                        "color": "grey",
                                                    },
                                                ),
                                                help_component(
                                                    "gtex-data",
                                                    "Use GTex data as control data",
                                                    "The provided meta data will not be used if an option is chosen",
                                                    icon_size="1.3rem",
                                                    color="grey",
                                                ),
                                            ]
                                        ),
                                        style={
                                            "display": "inline",
                                            "margin": "0",
                                            "padding": "0",
                                        },
                                        width={"size": 3, "offset": 0},
                                    ),
                                ],
                                align="center",
                            ),
                            dcc.Upload(
                                id="meta",
                                children="Drag and Drop or Select Files",
                                accept=".csv",
                            ),
                            dcc.Dropdown(
                                id="control-option",
                                options=control_data.get_control_data_options(),
                            ),
                        ],
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
                                        download="https://figshare.com/ndownloader/files/43544805",
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
                                    html.H5("Condition", style={"display": "inline"}),
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
                                    html.H5(
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
                                    html.H5(
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
                                                        placeholder="0.01",
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
                                                        placeholder="0.001",
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
                                                        value=True,
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
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Missing genes in selected control data"),
                        close_button=False,
                    ),
                    # dbc.ModalBody("Some genes are missing"),
                    dbc.ModalBody(
                        id="missing_genes_list", style={"white-space": "pre-line"}
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="close_control_data_modal",
                            color="success",
                            className="mr-1",
                            outline=True,
                        ),
                    ),
                ],
                id="control_data_modal",
                is_open=False,
                backdrop="static",
                centered=True,
                scrollable=True,
            ),
            dash.dcc.Store(id="expression_data", storage_type="memory"),
            dash.dcc.Store(id="network_data", storage_type="memory"),
            dash.dcc.Store(id="meta_data", storage_type="memory"),
            dash.dcc.Store(id="meta_data_autogenerated", storage_type="memory"),
            dash.dcc.Store(id="expression_data_autogenerated", storage_type="memory"),
        ],
        id="input_layout",
    )


def help_component(target, *args, icon_size, color="black", download=None):
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
        html.I(className="fa fa-question-circle-o"),
        id=f"{target}-help",
        style={
            "display": "inline",
            "background-color": "transparent",
            "border": "none",
            "font-size": icon_size,
            "color": color,
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
        id=f"{target}-help-container",
        style={"display": "inline", "margin": "0", "padding": "0"},
    )

    return out


@callback(
    Output("metadata-title", "style"),
    Output("gtexdata-title", "style"),
    Output("metadata-help", "style"),
    Output("gtex-data-help", "style"),
    Output("meta", "style"),
    Output("control-option", "style"),
    Input("meta-toggle-switch", "on"),
)
def change_layout_toggle(value: bool):
    """
    Changes the layout to dispaly metadata uploading or control data options according to toggle state.

    Args:
        value (bool): If the toggle switch is toggled or not.

    Returns:
        tuple: A tuple containing the styles of metadata uploading and gtex control data components.
    """
    if value:
        return (
            {
                "color": "grey",
                "display": "inline",
            },
            {"color": "black", "display": "inline"},
            {
                "display": "inline",
                "background-color": "transparent",
                "border": "none",
                "font-size": "1.3rem",
                "color": "grey",
            },
            {
                "display": "inline",
                "background-color": "transparent",
                "border": "none",
                "font-size": "1.3rem",
                "color": "black",
            },
            {
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
                "cursor": "pointer",
                "display": "none",
            },
            {"margin-top": "20px", "display": "block"},
        )
    else:
        return (
            {"color": "black", "display": "inline"},
            {"color": "grey", "display": "inline"},
            {
                "display": "inline",
                "background-color": "transparent",
                "border": "none",
                "font-size": "1.3rem",
                "color": "black",
            },
            {
                "display": "inline",
                "background-color": "transparent",
                "border": "none",
                "font-size": "1.3rem",
                "color": "grey",
            },
            {
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
                "cursor": "pointer",
                "display": "block",
            },
            {"display": "none"},
        )


@callback(
    Output("expression", "children"),
    Output("meta", "children"),
    Output("network", "children"),
    Input("expression", "filename"),
    Input("meta", "filename"),
    Input("network", "filename"),
)
def upload_name_update(
    expression_name: Union[str, None],
    meta_name: Union[str, None],
    network_name: Union[str, None],
) -> Tuple[str, str, str]:
    """
    Updates the names of the uploaded files.

    Args:
        expression_name (str): The name of the expression file.
        meta_name (str): The name of the meta file.
        network_name (str): The name of the network file.

    Returns:
        tuple: A tuple containing the updated names of the expression, meta, and network files.
    """
    expression_name = (
        expression_name
        if expression_name is not None
        else "Drag and Drop or Select Files"
    )
    meta_name = meta_name if meta_name is not None else "Drag and Drop or Select Files"
    network_name = (
        network_name if network_name is not None else "Drag and Drop or Select Files"
    )

    return expression_name, meta_name, network_name


@callback(
    Output("control_data_modal", "is_open", allow_duplicate=True),
    Input("close_control_data_modal", "n_clicks"),
    State("control_data_modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(n: Union[int, None], is_open: bool) -> bool:
    """
    Turn off the modal.

    Args:
        n (int): The times that the close button is clicked.
        is_open (bool): If the modal is open or not.

    Returns:
        is_open (bool): New state of the modal
    """
    if n:
        return False
    return is_open


@callback(
    Output("loading-options-output", "children", allow_duplicate=True),
    Input("control-option", "value"),
    background=True,
    running=[
        (Output("condition", "disabled"), True, False),
        (Output("cat-cov", "disabled"), True, False),
        (Output("con-cov", "disabled"), True, False),
        (Output("run", "disabled"), True, True),
    ],
    prevent_initial_call=True,
)
def disable_button(control_option: Union[str, None]):
    if control_option:
        time.sleep(9.0)
        return ""


@callback(
    Output("missing_genes_list", "children"),
    Output("control_data_modal", "is_open", allow_duplicate=True),
    Output("expression_data_autogenerated", "data", allow_duplicate=True),
    Output("meta_data_autogenerated", "data", allow_duplicate=True),
    Output("loading-options-output", "children", allow_duplicate=True),
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    background=True,
    running=[
        (Output("condition", "disabled"), True, False),
        (Output("cat-cov", "disabled"), True, False),
        (Output("con-cov", "disabled"), True, False),
        (Output("run", "disabled"), True, True),
    ],
    inputs=[
        Input("control-option", "value"),
        Input("expression_data", "data"),
    ],
    prevent_initial_call=True,
)
def prepare_control_data(
    control_option: Union[str, None], expression: Dict[str, Dict[str, str]]
):
    """
    Generate dropdown options based on the provided (or generated) expression, meta, and network data.

    Args:
        control_optoin (str): Selected tissue type of which control data is going to be prepared.
        expression_data (Dict[str, Dict[str, str]]): User provided expression data.

    Returns:
        tuple: A tuple containing the following elements:
            - missing_genes_message (str): A message listing genes that are not found in the gtex control data set, if any.
            - open_modal (bool): Open the modal which shows the missing_genes_message.
            - expression_data_auto (Dict[str, Dict[str, str]]): Expression data generated from selected control data option.
            - meta_data_auto (Dict[str, Dict[str, str]]): Meta data generated from selected control data option.
            - output (dash.no_update): A special value indicating that the loading-options-output should not be updated.
            - error_message (str): An error message, if any.
            - error_style (dict): A dictionary representing the CSS style for displaying the error message.
    """

    if control_option is not None:

        control_data.load_control_data(control_option)

        expression_df = pd.DataFrame(expression)

        # Original control data is indexed using genes in user expressoin data
        # Genes in user data that do not exist in the control data are returned as a list,
        # which should be dropped from user expression data
        genes_not_exist = control_data.filter_control_data(expression_df.columns[1:])

        if control_data.control_data is not None:

            control_data.control_data.insert(
                0, expression_df.columns[0], control_data.control_data.index
            )
            expression_df.drop(columns=genes_not_exist, inplace=True)
            assert_index_equal(expression_df.columns, control_data.control_data.columns)

            new_meta = {
                "sample": expression_df.iloc[:, 0].to_list()
                + control_data.control_data.iloc[:, 0].to_list(),
                "condition": [1] * expression_df.shape[0]
                + [0] * control_data.control_data.shape[0],
            }

            # Update `condition`, `cat-cov`, `con-cov` dropdown list options
            # Using the same logic as in `show_dropdown_options` function
            meta_df = pd.DataFrame(new_meta)
            expression_df = pd.concat([expression_df, control_data.control_data])

            if set(meta_df.iloc[:, 0]) != set(expression_df.iloc[:, 0]):
                return (
                    "",
                    False,
                    dash.no_update,
                    dash.no_update,
                    "",
                    "Error: Gene names in expression and meta data do not match",
                    {"display": "block"},
                )

            # Display missing genes in dialog box
            if ~genes_not_exist.empty:
                return (
                    """The following genes are missing in the selected control data set 
                        (also dropped in the provided expression data):\n"""
                    + ",\n".join(genes_not_exist),
                    True,
                    expression_df.to_dict(),
                    new_meta,
                    "",
                    "",
                    {"display": "none"},
                )

            return (
                "",
                False,
                expression_df.to_dict(),
                new_meta,
                "",
                "",
                {"display": "none"},
            )

        else:
            assert_index_equal(pd.Index(genes_not_exist), expression_df.columns[1:])

            return (
                """The selected control data set cannot be used with the provided data:\n
                all genes do not exist in the control data""",
                True,
                dash.no_update,
                dash.no_update,
                "",
                "",
                {"display": "none"},
            )

    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    Output("expression_data", "data"),
    Input("expression", "contents"),
    prevent_initial_call=True,
)
def load_expression_data(expression: Union[str, None]):
    """
    Stores expression dataframes in global variables for generating dropdown options and use in the dysregnet run callback.

    Args:
        expression (str): Base64 encoded expression data.

    Returns:
        tuple: A tuple containing the following elements:
            - error_message (str): An error message, if any.
            - error_style (Dict): A dictionary representing the CSS style for displaying the error message.
            - expression_data (Dict[str, Dict[str, str]])
    """
    try:
        expression_df = pd.read_csv(
            io.StringIO(
                base64.b64decode(expression.split(",")[1] + "===").decode("utf-8")
            ),
        )
        return ("", {"display": "none"}, expression_df.to_dict())

    except Exception as e:
        return (
            f"Error: Something went wrong ({e})",
            {"display": "block"},
            {},
        )


@callback(
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    Output("meta_data", "data"),
    Input("meta", "contents"),
    prevent_initial_call=True,
)
def load_meta_data(meta: Union[str, None]):
    """
    Stores metadata dataframes in global variables for generating dropdown options and use in the dysregnet run callback.

    Args:
        metadata (str): Base64 encoded metadata data.

    Returns:
        tuple: A tuple containing the following elements:
            - error_message (str): An error message, if any.
            - error_style (Dict): A dictionary representing the CSS style for displaying the error message.
            - metadata_data (Dict[str, Dict[str, str]])
    """
    try:
        meta_df = pd.read_csv(
            io.StringIO(base64.b64decode(meta.split(",")[1] + "===").decode("utf-8")),
        )
        return ("", {"display": "none"}, meta_df.to_dict())

    except Exception as e:
        return (
            f"Error: Something went wrong ({e})",
            {"display": "block"},
            {},
        )


@callback(
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    Output("network_data", "data"),
    Input("network", "contents"),
    prevent_initial_call=True,
)
def load_network_data(network: Union[str, None]):
    """
    Stores network dataframes in global variables for generating dropdown options and use in the dysregnet run callback.

    Args:
        network (str): Base64 encoded network data.

    Returns:
        tuple: A tuple containing the following elements:
            - error_message (str): An error message, if any.
            - error_style (Dict): A dictionary representing the CSS style for displaying the error message.
            - network_data (Dict[str, Dict[str, str]])
    """
    try:
        network_df = pd.read_csv(
            io.StringIO(
                base64.b64decode(network.split(",")[1] + "===").decode("utf-8")
            ),
        )

        if len(network_df.columns) != 2:
            return (
                "Error: Network file must have exactly two columns",
                {"display": "block"},
                dash.no_update,
            )

        return ("", {"display": "none"}, network_df.to_dict())

    except Exception as e:
        return (
            f"Error: Something went wrong ({e})",
            {"display": "block"},
            {},
        )


@callback(
    Output("condition", "options"),
    Output("cat-cov", "options"),
    Output("con-cov", "options"),
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    Output("select-cols", "style"),
    Output("loading-options-output", "children"),
    Input("expression_data", "data"),
    Input("meta_data", "data"),
    Input("network_data", "data"),
    Input("expression_data_autogenerated", "data"),
    Input("meta_data_autogenerated", "data"),
    Input("meta-toggle-switch", "on"),
    prevent_initial_call=True,
)
def show_dropdown_options(
    expression_data: Dict[str, Dict[str, str]],
    meta_data: Dict[str, Dict[str, str]],
    network_data: Dict[str, Dict[str, str]],
    expression_data_auto: Dict[str, Dict[str, str]],
    meta_data_auto: Dict[str, Dict[str, str]],
    toggle: bool,
):
    """
    Generate dropdown options based on the provided (or generated) expression, meta, and network data.

    Args:
        expression_data (Dict[str, Dict[str, str]]): User provided expression data.
        meta_data (Dict[str, Dict[str, str]]): User provided meta data.
        network_data (Dict[str, Dict[str, str]]): User provided network data.
        expression_data_auto (Dict[str, Dict[str, str]]): Expression data generated from selected control data option.
        meta_data_auto (Dict[str, Dict[str, str]]): Meta data generated from selected control data option.

    Returns:
        tuple: A tuple containing the following elements:
            - conditions (list): A list of dictionaries representing the dropdown options for conditions.
            - covariates (list): A list of dictionaries representing the dropdown options for covariates.
            - covariates (list): A list of dictionaries representing the dropdown options for covariates.
            - error_message (str): An error message, if any.
            - error_style (dict): A dictionary representing the CSS style for displaying the error message.
            - loading_style (dict): A dictionary representing the CSS style for displaying the loading spinner.
            - output (dash.no_update): A special value indicating that the loading-options-output should not be updated.
    """
    if toggle:
        expression_df = pd.DataFrame(expression_data_auto)
        meta_df = pd.DataFrame(meta_data_auto)
    else:
        expression_df = pd.DataFrame(expression_data)
        meta_df = pd.DataFrame(meta_data)

    network_df = pd.DataFrame(network_data)
    # if set(meta_df.iloc[:, 0]) != set(expression_df.iloc[:, 0]):
    #     return (
    #         [],
    #         [],
    #         [],
    #         "Error: Sample names in expression and meta data do not match",
    #         {"display": "block"},
    #         {"display": "None"},
    #         dash.no_update,
    #         {},
    #         {},
    #         {},
    #     )

    if not expression_df.empty and not meta_df.empty and not network_df.empty:

        if set(meta_df.iloc[:, 0]) != set(expression_df.iloc[:, 0]):
            return (
                [],
                [],
                [],
                "Error: Gene names in expression and meta data do not match",
                {"display": "block"},
                {"display": "None"},
                dash.no_update,
            )

        # TODO: check for matching gene names in expression and network

        columns = list(meta_df.columns)[1:]

        conditions = [
            {"label": option, "value": option}
            for option in columns
            if set(meta_df[option]) == {0, 1}
        ]

        if len(conditions) == 0:
            return (
                [],
                [],
                [],
                "Error: No binary condition found in meta data",
                {"display": "block"},
                {"display": "None"},
                dash.no_update,
            )

        covariates = [{"label": option, "value": option} for option in columns]
        return (
            conditions,
            covariates,
            covariates,
            dash.no_update,
            {"display": "None"},
            {"display": "flex"},
            "",
        )

    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("options", "style"),
    Input("condition", "value"),
)
def show_options(condition: Union[str, None]) -> Dict[str, str]:
    """
    Determines whether to show the options based on whether a condition was selected.

    Args:
        condition (str): Name of the selected condition column, None if no condition has been selected.

    Returns:
        dict: A dictionary containing the display option, inline if the condition has been selected, otherwise None.
    """
    if condition is not None:
        return {"display": "inline"}
    return {"display": "None"}


@callback(
    Output("run", "disabled"),
    Output("run", "color"),
    Input("condition", "value"),
)
def enable_run_button(condition: Union[str, None]) -> Tuple[bool, str]:
    """
    Determines whether the run button should be enabled or disabled based on whether a condition has been selected.

    Args:
        condition (str): Name of the selected condition column, None if no condition has been selected.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean value indicating whether the run button should be enabled (True) or disabled (False),
        and a string indicating the button's color ("success" for enabled, "secondary" for disabled).
    """
    if condition is not None:
        return False, "success"
    return True, "secondary"


@app.callback(
    Output("user-main", "children"),
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    Output("session_id", "value"),
    # Output("session_id", "inputs"), # TODO return caching of DysRegnet parameters by session-id
    inputs=[
        Input("run", "n_clicks"),
        State("condition", "value"),
        State("cat-cov", "value"),
        State("con-cov", "value"),
        State("zscore", "value"),
        State("bonferroni", "value"),
        State("normality", "value"),
        State("normaltest-alpha", "value"),
        State("r2", "value"),
        State("condition-direction", "value"),
        State("expression_data", "data"),
        State("network_data", "data"),
        State("meta_data", "data"),
        State("expression_data_autogenerated", "data"),
        State("meta_data_autogenerated", "data"),
        State("control-option", "value"),
        State("meta-toggle-switch", "on"),
    ],
    cancel=[Input("cancel-run", "n_clicks")],
    background=True,
    running=[
        (Output("modal", "is_open"), True, False),
    ],
    progress=[
        Output("progress", "value"),
        Output("progress", "max"),
        Output("progress", "label"),
    ],
    interval=100,
    prevent_initial_call=True,
)
def run(
    set_progress: Any,
    n_clicks: Union[int, None],
    condition: str,
    cat_cov: Union[List[str], None],
    con_cov: Union[List[str], None],
    zscoring: bool,
    bonferroni: Union[float, None],
    normaltest: bool,
    normaltest_alpha: Union[float, None],
    r2: Union[float, None],
    condition_direction: bool,
    expression: Dict[str, Dict[str, str]],
    network: Dict[str, Dict[str, str]],
    meta: Dict[str, Dict[str, str]],
    expression_auto: Dict[str, Dict[str, str]],
    meta_auto: Dict[str, Dict[str, str]],
    control_option: Union[str, None],
    toggle: bool,
) -> Union[
    Tuple[dbc.Container, Literal[""], Dict[str, str]],
    Tuple[NoUpdate, str, Dict[str, str]],
    Tuple[str],
]:
    """
    Run the analysis based on the provided parameters.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        condition (str): The condition for the analysis.
        cat_cov (list): List of categorical covariates.
        con_cov (list): List of continuous covariates.
        zscoring (bool): Flag indicating whether to perform z-scoring.
        bonferroni (float): The Bonferroni correction threshold.
        normaltest (bool): Flag indicating whether to perform normality test.
        normaltest_alpha (float): The significance level for normality test.
        r2 (float): The R-squared threshold.
        condition_direction (str): Flag indicating whether to only include dysregulation that are relevant for the interactions.

    Returns:
        object: The output layout for the analysis results.
        str: An error message, if any.
        dict: A dictionary representing the CSS style for displaying the error message.
    """
    if n_clicks is not None:
        if toggle and control_option is not None:
            expression = expression_auto
            meta = meta_auto

        session_id = str(uuid4())
        try:
            with DysregnetProgress() as f:
                f.set_max(max=len(pd.DataFrame(network)))
                f.set_progress = set_progress

                with redirect_stderr(new_target=f):
                    results = get_results(
                        expression,
                        meta,
                        network,
                        condition,
                        [] if cat_cov is None else cat_cov,
                        [] if con_cov is None else con_cov,
                        zscoring,
                        1e-2 if bonferroni is None else bonferroni,
                        normaltest,
                        1e-3 if normaltest_alpha is None else normaltest_alpha,
                        r2,
                        condition_direction,
                        session_id,
                    )

            results_convert = pd.DataFrame(results)
            results_convert.columns = [
                tuple(c.split(",")) for c in results_convert.columns
            ]
            out_layout = (get_output_layout(results_convert),)
            return (
                out_layout,
                "",
                {"display": "None"},
                session_id,  # results
            )
        except Exception as e:
            return (
                dash.no_update,
                f"Error: Something went wrong ({e})",
                {"display": "block"},
                {},
            )

    return dash.no_update, "", {"display": "None"}, {}
