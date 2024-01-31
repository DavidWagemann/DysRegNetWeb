import collections

import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import callback, clientside_callback, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State

import pages.components.neo4j2csv as neo4j2csv
import pages.components.neo4j2Store as neo4j2Store
from pages.components.db import NetworkDB
from pages.components.detail import detail, edge_detail, node_detail
from pages.components.graph import graph
from pages.components.plots import (
    dysregulation_heatmap,
    methylation_heatmap,
    mutation_bar,
)
from pages.components.popovers import get_cancer_map, get_popovers
from pages.components.settings import get_settings
from pages.components.tabs import tabs

dash.register_page(__name__, path="/")

db = NetworkDB()
cyto.load_extra_layouts()

layout = html.Div(
    [
        dbc.Alert(
            "Database is unavailable",
            color="danger",
            is_open=False,
            id="db_unavailable",
            style={"marginTop": "10px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Spinner(
                            dcc.Dropdown(
                                multi=False,
                                placeholder="Select cancer type",
                                id="cancer_id_input",
                            ),
                            color="primary",
                        ),
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=3,
                    xl=3,
                    xxl=2,
                ),
                dbc.Col(
                    [
                        dbc.Spinner(
                            dcc.Dropdown(
                                multi=True,
                                placeholder="Select query genes",
                                id="gene_id_input",
                            ),
                            color="primary",
                        ),
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=9,
                    xl=9,
                    xxl=10,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(get_settings(), xs=12, sm=12, md=12, lg=3, xl=3, xxl=2),
                dbc.Col([graph], xs=12, sm=12, md=12, lg=9, xl=9, xxl=5),
                dbc.Col([detail, tabs], xs=12, sm=12, md=12, lg=12, xl=12, xxl=5),
            ],
            style={"marginTop": "15px", "marginBottom": "10px", "height": "85vh"},
        ),
        dcc.Store(id="store_graph", storage_type="memory", data={}),
        dcc.Store(
            id="store_selection",
            storage_type="memory",
            data={"gene_ids": [], "cancer_id": "", "compare_id": None},
        ),
        dcc.Store(id="store_compare", storage_type="memory", data=False),
        dcc.Store(id="dummy", storage_type="memory"),
    ]
    + get_popovers(),
)


@callback(
    Output(component_id="gene_id_input", component_property="options"),
    Output(component_id="cancer_id_input", component_property="options"),
    Output(component_id="compare_cancer", component_property="options"),
    Output(component_id="db_unavailable", component_property="is_open"),
    Input(component_id="dummy", component_property="data"),
)
def init_data(dummy):
    gene_ids = db.get_gene_ids("THCA")
    cancer_ids = db.get_cancer_ids()
    cancer_map = get_cancer_map()
    gene_options = [{"label": gene_id, "value": gene_id} for gene_id in gene_ids]
    cancer_options = [
        {"label": cancer_id, "value": cancer_id, "title": cancer_map.get(cancer_id)}
        for cancer_id in cancer_ids
    ]
    is_open = len(gene_ids) == 0
    return gene_options, cancer_options, cancer_options, is_open


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="update_graph"),
    Output(component_id="graph", component_property="elements"),
    Output(component_id="graph", component_property="layout"),
    Output(component_id="displayed_targets", component_property="children"),
    Output(component_id="displayed_sources", component_property="children"),
    Output(component_id="store_compare", component_property="data"),
    Input(component_id="diameter_type", component_property="value"),
    Input(component_id="display_nodes", component_property="value"),
    Input(component_id="min_fraction_slider", component_property="value"),
    Input(component_id="max_regulations_slider", component_property="value"),
    Input(component_id="store_graph", component_property="data"),
    Input(component_id="compare_switch", component_property="value"),
    Input(component_id="patient_switch", component_property="value"),
    State(component_id="store_selection", component_property="data"),
)


@callback(
    Output(component_id="store_selection", component_property="data"),
    Output(component_id="displayed_cancer", component_property="children"),
    Output(component_id="displayed_genes", component_property="children"),
    Input(component_id="gene_id_input", component_property="value"),
    Input(component_id="cancer_id_input", component_property="value"),
    State(component_id="store_selection", component_property="data"),
)
def update_selection_data(selected_gene_ids, cancer_id, selection_data):
    if selected_gene_ids is not None and cancer_id is not None:
        if (
            collections.Counter(selected_gene_ids)
            != collections.Counter(selection_data["gene_ids"])
            or cancer_id != selection_data["cancer_id"]
        ):
            displayed_cancer = f"{cancer_id} ({get_cancer_map().get(cancer_id)})"
            return (
                {"gene_ids": selected_gene_ids, "cancer_id": cancer_id},
                displayed_cancer,
                len(selected_gene_ids),
            )
    raise dash.exceptions.PreventUpdate

@callback(
    Output(component_id="patient_specific", component_property="options"),
    Output(component_id="patient_specific", component_property="value"),
    Input(component_id="cancer_id_input", component_property="value"),
)
def update_patient_specific_options(selected_cancer_id):
    dropdown_options = db.get_all_patient_ids(selected_cancer_id)
    default_value = dropdown_options[0]["value"] if dropdown_options else None
    return dropdown_options, default_value

@callback(
    Output(component_id="store_graph", component_property="data"),
    Output(component_id="total_targets", component_property="children"),
    Output(component_id="total_sources", component_property="children"),
    Input(component_id="store_selection", component_property="data"),
    Input(component_id="compare_cancer", component_property="value"),
    Input(component_id="patient_specific", component_property="value"),
    Input(component_id="cancer_id_input", component_property="value"),
)
def update_graph_data(selection_data, compare_cancer, patient_specific, cancer_id_input):
    if len(selection_data["gene_ids"]) != 0 and selection_data["cancer_id"] != "":
        graph_data = db.get_neighborhood_multi(
            selection_data["gene_ids"], selection_data["cancer_id"]
        )
        store_graph, total_regulations = neo4j2Store.get_neighborhood(graph_data)
        if patient_specific is not None:
            patient_data = db.get_dysregulation_patient_specific(
                [
                    regulation[0]["data"]["regulation_id"]
                    for regulation in store_graph["regulations"]
                ],
                cancer_id_input,
                patient_specific,
            )
            if len(patient_data) >= 1: print("PATIENT DATA", patient_data)
            store_graph["patient"] = patient_data

        if compare_cancer is not None:
            compare_data = db.get_fraction_map(
                [
                    regulation[0]["data"]["regulation_id"]
                    for regulation in store_graph["regulations"]
                ],
                compare_cancer,
            )
            store_graph["compare"] = compare_data
        return (
            store_graph,
            total_regulations["total_targets"],
            total_regulations["total_sources"],
        )
    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="detail", component_property="children"),
    Output(component_id="graph", component_property="tapNodeData"),
    Output(component_id="graph", component_property="tapEdgeData"),
    Input(component_id="graph", component_property="tapNodeData"),
    Input(component_id="graph", component_property="tapEdgeData"),
    State(component_id="store_selection", component_property="data"),
    State(component_id="store_compare", component_property="data"),
    State(component_id="compare_cancer", component_property="value"),
)
def update_detail(node, edge, selection_data, compare, compare_cancer):
    if selection_data is not None:
        if node is not None:
            is_center = node["id"] in selection_data["gene_ids"]
            return node_detail(node, selection_data["cancer_id"], is_center), None, None
        elif edge is not None:
            return (
                edge_detail(edge, selection_data["cancer_id"], compare, compare_cancer),
                None,
                None,
            )
    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="gene_id_input", component_property="value"),
    Output(component_id="center_add_button", component_property="children"),
    Output(component_id="center_add_button", component_property="value"),
    Output(component_id="center_add_button", component_property="color"),
    Input(component_id="center_button", component_property="value"),
    Input(component_id="center_button", component_property="n_clicks"),
    Input(component_id="center_add_button", component_property="n_clicks"),
    State(component_id="center_add_button", component_property="value"),
    State(component_id="store_selection", component_property="data"),
    prevent_initial_call=True,
)
def update_gene_button(new_gene_id, new_clicks, add_clicks, add_remove, selection_data):
    if new_clicks > 0 or add_clicks > 0:
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]

        if changed_id == "center_button.n_clicks":
            return (
                [new_gene_id],
                [html.I(className="fa fa-minus mr-1"), " Remove from query"],
                "remove",
                "danger",
            )

        elif changed_id == "center_add_button.n_clicks":
            if add_remove == "add":
                if new_gene_id not in selection_data["gene_ids"]:
                    return (
                        selection_data["gene_ids"] + [new_gene_id],
                        [html.I(className="fa fa-minus mr-1"), " Remove from query"],
                        "remove",
                        "danger",
                    )
                else:
                    return (
                        dash.no_update,
                        [html.I(className="fa fa-minus mr-1"), " Remove from query"],
                        "remove",
                        "danger",
                    )
            elif add_remove == "remove":
                if new_gene_id in selection_data["gene_ids"]:
                    selection_data["gene_ids"].remove(new_gene_id)
                    return (
                        selection_data["gene_ids"],
                        [html.I(className="fa fa-plus mr-1"), " Add to query"],
                        "add",
                        "success",
                    )
                else:
                    return (
                        dash.no_update,
                        [html.I(className="fa fa-plus mr-1"), " Add to query"],
                        "add",
                        "success",
                    )

    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="download_graph_full", component_property="data"),
    Input(component_id="btn_download_graph_full", component_property="n_clicks"),
    State(component_id="store_selection", component_property="data"),
    prevent_initial_call=True,
)
def download_graph_full(n_clicks, selection_data):
    if (
        n_clicks > 0
        and len(selection_data["gene_ids"]) != 0
        and selection_data["cancer_id"] != ""
    ):
        graph_data = db.get_neighborhood_multi(
            selection_data["gene_ids"], selection_data["cancer_id"]
        )
        return dict(content=neo4j2csv.get_csv(graph_data), filename="full_graph.csv")
    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="download_graph_displayed", component_property="data"),
    Input(component_id="btn_download_graph_displayed", component_property="n_clicks"),
    State(component_id="graph", component_property="elements"),
    prevent_initial_call=True,
)
def download_graph_displayed(n_clicks, elements):
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
    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="graph", component_property="generateImage"),
    Input(component_id="btn_download_graph_png", component_property="n_clicks"),
    prevent_initial_call=True,
)
def download_graph_png(n_clicks):
    if n_clicks > 0:
        return {"type": "png", "action": "download"}
    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="mutation_plot", component_property="figure"),
    Input(component_id="graph", component_property="elements"),
    prevent_initial_call=True,
)
def update_mutation_plot(elements):
    if elements is not None:
        return mutation_bar(elements)
    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="methylation_plot", component_property="figure"),
    Output(component_id="refresh_methylation_button", component_property="children"),
    Input(component_id="refresh_methylation_button", component_property="n_clicks"),
    State(component_id="store_selection", component_property="data"),
    prevent_initial_call=True,
)
def update_methylation_plot(n_clicks, selection_data):
    if (
        n_clicks > 0
        and len(selection_data["gene_ids"]) != 0
        and selection_data["cancer_id"] != ""
    ):
        data = db.get_methylation(
            list(selection_data["gene_ids"]), selection_data["cancer_id"]
        )
        if len(data) > 0:
            return methylation_heatmap(data), [
                html.I(className="fa fa-refresh mr-1"),
                " Refresh",
            ]

    raise dash.exceptions.PreventUpdate


@callback(
    Output(component_id="dysregulation_plot", component_property="figure"),
    Output(component_id="refresh_dysregulation_button", component_property="children"),
    Input(component_id="refresh_dysregulation_button", component_property="n_clicks"),
    State(component_id="graph", component_property="elements"),
    State(component_id="store_selection", component_property="data"),
    prevent_initial_call=True,
)
def update_dysregulation_plot(n_clicks, elements, selection_data):
    if (
        n_clicks > 0
        and elements is not None
        and len(selection_data["gene_ids"]) != 0
        and selection_data["cancer_id"] != ""
    ):
        regulation_ids = [
            element["data"]["regulation_id"]
            for element in elements
            if "regulation_id" in element["data"]
        ]
        data = db.get_dysregulation(regulation_ids, selection_data["cancer_id"])
        if len(data) > 0:
            return dysregulation_heatmap(data), [
                html.I(className="fa fa-refresh mr-1"),
                " Refresh",
            ]

    raise dash.exceptions.PreventUpdate
