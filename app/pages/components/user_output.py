import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table


def get_output_layout(results: pd.DataFrame) -> dbc.Container:
    """
    Generate the layout for displaying the output results.

    Args:
        results (pandas.DataFrame): The results to be displayed.

    Returns:
        dbc.Container: The layout containing the results.
    """
    results.columns = [str(x) for x in results.columns]
    results = results.iloc[
        :10, :5
    ]  # Temporary, will be replaced with visualisations later
    output_layout = dbc.Container(dash_table.DataTable(results.to_dict("records")))
    return output_layout
