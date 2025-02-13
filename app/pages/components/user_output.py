from typing import Any, Dict, List

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, clientside_callback, dcc, exceptions, html
from dash.dependencies import ClientsideFunction, Input, Output, State

from pages.components.detail import detail, user_edge_detail, user_node_detail
from pages.components.dysregnet_cache import cache, get_cached_results
from pages.components.dysregnet_results import (
    get_graph_data,
    get_num_regulation,
    get_sources,
    get_targets,
    graph_to_csv,
)
from pages.components.graph import get_graph
from pages.components.plots import blank_fig, dysregulation_heatmap
from pages.components.popovers import get_popovers
from pages.components.settings import get_user_settings
from pages.components.tabs import user_data_tabs


def get_output_layout(results: pd.DataFrame) -> dbc.Container:
    """
    Generate the layout for displaying the output results.

    Args:
        results (pandas.DataFrame): The results to be displayed.

    Returns:
        dbc.Container: The layout containing the results.
    """

    genes = results.columns.to_series().explode(ignore_index=True).unique()
    output_layout = html.Div(
        [
            dbc.Row(
                [
                    dcc.Dropdown(
                        multi=True,
                        placeholder="Select query genes",
                        id="user_gene_id_input",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        get_user_settings(), xs=12, sm=12, md=12, lg=3, xl=3, xxl=2
                    ),
                    dbc.Col(
                        [get_graph("user_graph")],
                        xs=12,
                        sm=12,
                        md=12,
                        lg=9,
                        xl=9,
                        xxl=5,
                    ),
                    dbc.Col(
                        [detail, user_data_tabs],
                        xs=12,
                        sm=12,
                        md=12,
                        lg=12,
                        xl=12,
                        xxl=5,
                    ),
                ],
                style={"marginTop": "15px", "marginBottom": "10px", "height": "85vh"},
            ),
            dcc.Store(id="user_store_graph", storage_type="memory", data={}),
            dcc.Store(
                id="user_store_selection",
                storage_type="memory",
                data={"gene_ids": []},
            ),
            dcc.Store(id="user_store_compare", storage_type="memory", data=False),
            dcc.Store(id="user_dummy", storage_type="memory"),
            dcc.Store(
                id="user_genes_store",
                storage_type="memory",
                data={"gene_ids": [{"label": gene, "value": gene} for gene in genes]},
            ),
        ]
        + get_popovers(),
    )

    return output_layout


@callback(
    Output("user_gene_id_input", "options"),
    Input("user_gene_id_input", "search_value"),
    State("user_gene_id_input", "value"),
    State("user_genes_store", "data"),
)
def update_gene_input(
    search_value: str, value: List[str], data: Dict[str, List[str]]
) -> List[str]:
    if not search_value:
        return data["gene_ids"]

    return [
        o
        for o in data["gene_ids"]
        if search_value.upper() in o["label"].upper() or o["value"] in (value or [])
    ]


@callback(
    Output(component_id="user_store_graph", component_property="data"),
    Output(
        component_id="user_total_targets",
        component_property="children",
    ),
    Output(
        component_id="user_total_sources",
        component_property="children",
    ),
    Input(component_id="user_gene_id_input", component_property="value"),
    Input(component_id="user_patient_specific", component_property="value"),
    State(component_id="session_id", component_property="value"),
    prevent_initial_call=True,
)
def update_graph_data(genes: List[str], patient_id: str, session_id: str):
    if len(genes) > 0:
        results = pd.DataFrame(get_cached_results(session_id))
        results.columns = [tuple(c.split(",")) for c in results.columns]

        patient_data = None
        if patient_id is not None:
            # filtered_results = results[:, results.columns.isin(genes)]
            filtered_results = results.loc[results.index.isin([patient_id])]
            filtered_results = filtered_results.loc[
                :, (filtered_results != 0).any(axis=0)
            ]
            patient_data = [
                [":".join(edge), patient_id, filtered_results[edge].iloc[0]]
                for edge in filtered_results.columns
            ]

        sources = get_sources(results, genes)
        targets = get_targets(results, genes)

        total_regulations = get_num_regulation(sources, targets)
        user_store_graph = get_graph_data(sources, targets, genes, patient_data)
        return (
            user_store_graph,
            total_regulations["total_targets"],
            total_regulations["total_sources"],
        )

    return {}, 0, 0


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="update_user_graph"),
    Output(component_id="user_graph", component_property="elements"),
    Output(component_id="user_graph", component_property="layout"),
    Output(component_id="user_displayed_targets", component_property="children"),
    Output(component_id="user_displayed_sources", component_property="children"),
    Input(component_id="display_nodes", component_property="value"),
    Input(component_id="min_fraction_slider", component_property="value"),
    Input(component_id="max_regulations_slider", component_property="value"),
    Input(component_id="user_store_graph", component_property="data"),
    Input(component_id="user_patient_switch", component_property="value"),
    State(component_id="user_gene_id_input", component_property="value"),
    prevent_initial_call=False,
)


@callback(
    Output(component_id="detail", component_property="children", allow_duplicate=True),
    Output(component_id="user_graph", component_property="tapNodeData"),
    Output(component_id="user_graph", component_property="tapEdgeData"),
    Input(component_id="user_graph", component_property="tapNodeData"),
    Input(component_id="user_graph", component_property="tapEdgeData"),
    State(component_id="user_gene_id_input", component_property="value"),
    prevent_initial_call=True,
)
def update_detail(node: Dict[str, Any], edge: Dict[str, Any], genes: List[str]):
    if node is not None:
        is_center = node["id"] in genes
        return user_node_detail(node, is_center), None, None
    elif edge is not None:
        return user_edge_detail(edge), None, None
    raise exceptions.PreventUpdate


@callback(
    Output(component_id="download_user_dysregnet", component_property="data"),
    Input(component_id="btn_download_dysregnet", component_property="n_clicks"),
    State(component_id="session_id", component_property="value"),
    prevent_initial_call=True,
)
def download_dysregnet_results(n_clicks: int, session_id):
    if n_clicks > 0:
        results = pd.DataFrame(get_cached_results(session_id))
        # results.columns = [tuple(c.split(",")) for c in results.columns]
        csv_str = results.to_csv()

        return dict(content=csv_str + "\n", filename="results.csv")

    raise exceptions.PreventUpdate


@callback(
    Output(component_id="download_user_graph_full", component_property="data"),
    Input(component_id="btn_download_user_graph_full", component_property="n_clicks"),
    State(component_id="session_id", component_property="value"),
    State(component_id="user_gene_id_input", component_property="value"),
    prevent_initial_call=True,
)
def download_graph_full(n_clicks: int, session_id: str, genes: List[str]):
    if n_clicks > 0 and len(genes) != 0:
        results = pd.DataFrame(get_cached_results(session_id))
        results.columns = [tuple(c.split(",")) for c in results.columns]

        sources = get_sources(results, genes)
        targets = get_targets(results, genes)

        graph_data = get_graph_data(sources, targets, genes, None)

        return graph_to_csv(graph_data)

    raise exceptions.PreventUpdate


@callback(
    Output(component_id="download_user_graph_displayed", component_property="data"),
    Input(
        component_id="btn_download_user_graph_displayed", component_property="n_clicks"
    ),
    State(component_id="user_graph", component_property="elements"),
    prevent_initial_call=True,
)
def download_graph_displayed(n_clicks: int, elements: List[Dict[str, Any]]):
    if n_clicks > 0 and elements is not None:
        rows = ["source,target,type,fraction"]
        for element in elements:
            if "regulation_id" in element["data"]:
                source = element["data"]["source"]
                target = element["data"]["target"]
                fraction = str(element["data"]["fraction"])
                regulation_type = (
                    "repression" if element["classes"] == "r" else "activation"
                )
                rows.append(",".join((source, target, regulation_type, fraction)))

        return dict(content="\n".join(rows) + "\n", filename="displayed_graph.csv")
    raise exceptions.PreventUpdate


@callback(
    Output(component_id="user_graph", component_property="generateImage"),
    Input(component_id="btn_download_user_graph_png", component_property="n_clicks"),
    prevent_initial_call=True,
)
def download_graph_png(n_clicks: int):
    if n_clicks > 0:
        return {"type": "png", "action": "download"}
    raise exceptions.PreventUpdate


@callback(
    Output("user_gene_id_input", "value", allow_duplicate=True),
    Input("user_center_button", "n_clicks"),
    State("detail_selected_gene", "children"),
    prevent_initial_call=True,
)
def select_query(n_clicks: int, gene: str):
    if n_clicks > 0:
        return [gene]

    raise exceptions.PreventUpdate


@callback(
    Output("user_gene_id_input", "value", allow_duplicate=True),
    Input("user_center_add_button", "n_clicks"),
    State("user_center_add_button", "children"),
    State("detail_selected_gene", "children"),
    State("user_gene_id_input", "value"),
    prevent_initial_call=True,
)
def add_query(n_clicks: int, change_type: List[str], gene: str, current: List[str]):
    if n_clicks > 0:
        if "Add" in change_type[1]:
            current.append(gene)
        else:
            current.remove(gene)

        return current

    raise exceptions.PreventUpdate


@callback(
    Output(component_id="user_dysregulation_plot", component_property="figure"),
    Output(
        component_id="user_refresh_dysregulation_button", component_property="children"
    ),
    Input(
        component_id="user_refresh_dysregulation_button", component_property="n_clicks"
    ),
    State(component_id="user_graph", component_property="elements"),
    State(component_id="user_gene_id_input", component_property="value"),
    State(component_id="session_id", component_property="value"),
    prevent_initial_call=True,
)
def update_dysregulation_plot(
    n_clicks: int, elements, genes: List[str], session_id: str
):
    if n_clicks > 0 and elements is not None:
        if len(genes) > 0:
            results = pd.DataFrame(get_cached_results(session_id))
            results.columns = [c.replace(",", ":") for c in results.columns]

            regulation_ids = [
                element["data"]["regulation_id"]
                for element in elements
                if "regulation_id" in element["data"]
            ]

            results = results.filter(items=regulation_ids)
            results = results.loc[(results != 0).any(axis=1)]

            rows = results.index.tolist()
            data = []
            for col in results.columns:
                rowindex = 0
                for value in results[col]:
                    if value != 0:
                        data.append([str(col), rows[rowindex], value])
                    rowindex += 1

            return dysregulation_heatmap(data), [
                html.I(className="fa fa-refresh mr-1"),
                " Refresh",
            ]

        else:
            return blank_fig(), [
                html.I(className="fa fa-refresh mr-1"),
                " Refresh",
            ]

    raise dash.exceptions.PreventUpdate


@callback(
    Output("session_id_label", "children"),
    Input("url", "href"),
    State(component_id="session_id", component_property="value"),
)
def show_session_id(url: str, session_id: str):
    url = "/".join(url.split("/")[:-1]) + "/user_data?" + session_id
    return [
        session_id,
        dcc.Clipboard(
            content=url, style={"marginLeft": "5px", "display": "inline-block"}
        ),
    ]


@callback(
    Output(component_id="user_patient_specific", component_property="options"),
    Input(component_id="session_id", component_property="value"),
)
def update_user_patient_specific_options(session_id):
    results = pd.DataFrame(get_cached_results(session_id))
    patient_ids = results.index.tolist()
    dropdown_options = [{"label": name, "value": name} for name in patient_ids]

    return dropdown_options
