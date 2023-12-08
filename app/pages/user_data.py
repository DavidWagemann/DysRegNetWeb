import base64
import io
from contextlib import redirect_stderr
from typing import Any, Dict, List, Literal, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, html
from dash._callback import NoUpdate
from dash.dependencies import Input, Output, State
from pages.components.dysregnet_progress import DysregnetProgress
from pages.components.run_dysregnet import get_results
from pages.components.user_input import get_input_layout
from pages.components.user_output import get_output_layout

dash.register_page(__name__, path="/user_data")

layout = html.Div(
    [get_input_layout()],
    id="user-main",
    style={"margin": "10px", "padding": "0px"},
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
    Output("condition", "options"),
    Output("cat-cov", "options"),
    Output("con-cov", "options"),
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
    Output("select-cols", "style"),
    Output("loading-options-output", "children"),
    Input("expression", "contents"),
    Input("meta", "contents"),
    Input("network", "contents"),
    prevent_initial_call=True,
)
def show_dropdown_options(
    expression: Union[str, None], meta: Union[str, None], network: Union[str, None]
) -> Tuple[
    Union[List[str], List[Dict[str, str]]],
    Union[List[str], List[Dict[str, str]]],
    Union[List[str], List[Dict[str, str]]],
    Union[NoUpdate, str],
    Dict[str, str],
    Dict[str, str],
    Union[NoUpdate, Literal[""]],
]:
    """
    Generate dropdown options based on the provided expression, meta, and network data.
    Stores expression, meta, and network dataframes in global variables for use in the dysregnet run callback.

    Args:
        expression (str): Base64 encoded expression data.
        meta (str): Base64 encoded meta data.
        network (str): Base64 encoded network data.

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
    if expression is not None and meta is not None and network is not None:
        try:
            global expression_df
            expression_df = pd.read_csv(
                io.StringIO(
                    base64.b64decode(expression.split(",")[1] + "===").decode("utf-8")
                ),
            )
            global meta_df
            meta_df = pd.read_csv(
                io.StringIO(
                    base64.b64decode(meta.split(",")[1] + "===").decode("utf-8")
                ),
            )
            global network_df
            network_df = pd.read_csv(
                io.StringIO(
                    base64.b64decode(network.split(",")[1] + "===").decode("utf-8")
                )
            )

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

            if len(network_df.columns) != 2:
                return (
                    [],
                    [],
                    [],
                    "Error: Network file must have exactly two columns",
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
        except Exception as e:
            return (
                [],
                [],
                [],
                f"Error: Something went wrong ({e})",
                {"display": "block"},
                {"display": "None"},
                dash.no_update,
            )

    return (
        [],
        [],
        [],
        dash.no_update,
        {"display": "None"},
        {"display": "None"},
        dash.no_update,
    )


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


@callback(
    Output("user-main", "children"),
    Output("errorbox", "children", allow_duplicate=True),
    Output("errorbox", "style", allow_duplicate=True),
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
) -> Union[
    Tuple[dbc.Container, Literal[""], Dict[str, str]],
    Tuple[NoUpdate, str, Dict[str, str]],
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
        global expression_df
        global meta_df
        global network_df
        try:
            with DysregnetProgress() as f:
                f.set_max(max=len(network_df))
                f.set_progress = set_progress
                with redirect_stderr(new_target=f):
                    results = get_results(
                        expression_df,
                        meta_df,
                        network_df,
                        condition,
                        [] if cat_cov is None else cat_cov,
                        [] if con_cov is None else con_cov,
                        zscoring,
                        1e-2 if bonferroni is None else bonferroni,
                        normaltest,
                        1e-3 if normaltest_alpha is None else normaltest_alpha,
                        r2,
                        condition_direction,
                    )

            return get_output_layout(results), "", {"display": "None"}
        except Exception as e:
            print(e)
            return (
                dash.no_update,
                f"Error: Something went wrong ({e})",
                {"display": "block"},
            )

    return dash.no_update, "", {"display": "None"}
