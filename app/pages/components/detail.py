import dash_bootstrap_components as dbc
from dash import html

from pages.components.popovers import (
    get_gene_popover,
    get_regulation_popover,
    heading_with_info,
)

detail = html.Div(
    dbc.Card(
        dbc.CardBody(
            [
                html.H5("Nothing selected", className="card-title"),
                html.Label("Click on a gene or regulation to display details."),
            ]
        ),
        className="mb-3",
    ),
    id="detail",
)


def node_detail(node, cancer_id, is_center):
    if is_center:
        children = [html.I(className="fa fa-minus mr-1"), " Remove from query"]
        color = "danger"
        value = "remove"
    else:
        children = [html.I(className="fa fa-plus mr-1"), " Add to query"]
        color = "success"
        value = "add"

    if node["methylation"] is None:
        meth_opacity = 0.3
        meth_label = "No data"
    else:
        meth_opacity = 1
        meth_label = node["methylation"]

    detail_card = dbc.Card(
        dbc.CardBody(
            [
                heading_with_info("Gene", "gene_info"),
                get_gene_popover(),
                dbc.Row(html.Label(f"Cancer: {cancer_id}")),
                dbc.Row(html.Label(f"Gene: {node['id']}")),
                dbc.Row(
                    html.Div(
                        [
                            html.Label(
                                "Promoter methylation:", style={"marginRight": "10px"}
                            ),
                            html.Label(meth_label, style={"opacity": meth_opacity}),
                        ],
                        style={"display": "flex"},
                    )
                ),
                dbc.Row(html.Label(f"Mutation frequency: {node['mutation']}")),
                html.Div(
                    [
                        dbc.Button(
                            [
                                html.I(className="fa fa-crosshairs mr-1"),
                                " Choose as query",
                            ],
                            outline=True,
                            color="primary",
                            className="me-1",
                            value=node["id"],
                            id="center_button",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            children,
                            outline=True,
                            color=color,
                            className="me-1",
                            value=value,
                            id="center_add_button",
                            n_clicks=0,
                        ),
                    ],
                    className="d-grid gap-2 d-md-flex",
                    style={"marginTop": "10px"},
                ),
            ]
        ),
        className="mb-3",
    )

    return detail_card


def edge_detail(edge, cancer_id, compare, compare_cancer):
    compare_info = dbc.Row()

    if compare and compare_cancer is not None:
        compare_color = "black"
        sign = ""

        diff = edge["diff"]

        if diff > 0:
            sign = "+"
            compare_color = "orange"
        elif diff < 0:
            compare_color = "green"

        compare_info.children = html.Div(
            [
                html.Label(
                    f"Dysregulation compared to {compare_cancer}:",
                    style={"marginRight": "10px"},
                ),
                html.Label(sign + str("%.5f" % diff), style={"color": compare_color}),
            ],
            style={"display": "flex"},
        )

    detail_card = dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    heading_with_info(
                        f'Regulation ({"Activation" if edge["classes"] == "a" else "Repression"})',
                        "regulation_info",
                    )
                ),
                get_regulation_popover(),
                dbc.Row(html.Label(f"Cancer: {cancer_id}")),
                dbc.Row(html.Label(f"Source: {edge['source']}")),
                dbc.Row(html.Label(f"Target: {edge['target']}")),
                dbc.Row(
                    html.Div(
                        [
                            html.Label(
                                f"Fraction of dysregulated patients:",
                                style={"marginRight": "10px"},
                            ),
                            html.Label(edge["fraction"], style={"color": "red"}),
                        ],
                        style={"display": "flex"},
                    )
                ),
                compare_info,
            ]
        ),
        className="mb-3",
    )
    return detail_card
