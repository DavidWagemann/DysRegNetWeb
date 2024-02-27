import dash_bootstrap_components as dbc
from dash import dcc, html

from .detail import detail
from .display_info import display_info, user_display_info
from .plots import blank_fig
from .popovers import heading_with_info

tab_info = html.Div([display_info])
user_tab_info = html.Div([user_display_info])

tab_mutation = html.Div(
    [
        dbc.Row(
            heading_with_info(
                "Gene mutation frequency among patients", "mutation_info"
            ),
            className="me-1 ms-1",
        ),
        dcc.Graph(
            id="mutation_plot",
            config={"modeBarButtonsToRemove": ["lasso2d", "select2d"]},
            figure=blank_fig(),
        ),
    ],
    className="mt-3",
)

tab_methylation = html.Div(
    [
        dbc.Row(
            heading_with_info(
                "Patient-specific promoter methylation heatmap", "methylation_info"
            ),
            className="me-1 ms-1",
        ),
        dbc.Spinner(
            [
                dbc.Row(
                    dcc.Graph(
                        id="methylation_plot",
                        figure=blank_fig(),
                        style={"height": "500px"},
                        responsive=True,
                    ),
                ),
                dbc.Row(
                    html.Div(
                        dbc.Button(
                            "Load methylation heatmap",
                            outline=True,
                            color="primary",
                            className="me-1",
                            id="refresh_methylation_button",
                            n_clicks=0,
                        ),
                        className="d-grid gap-2 mx-auto",
                    )
                ),
            ],
            color="primary",
        ),
    ],
    className="mt-3",
)

tab_dysregulation = lambda name: html.Div(
    [
        dbc.Row(
            heading_with_info(
                "Patient-specific dysregulation heatmap", f"{name}dysregulation_info"
            ),
            className="me-1 ms-1",
        ),
        dbc.Spinner(
            [
                dbc.Row(
                    dcc.Graph(
                        id=f"{name}dysregulation_plot",
                        figure=blank_fig(),
                        style={"height": "500px"},
                        responsive=True,
                    ),
                ),
                dbc.Row(
                    html.Div(
                        dbc.Button(
                            "Load dysregulation heatmap",
                            outline=True,
                            color="primary",
                            className="me-1",
                            id=f"{name}refresh_dysregulation_button",
                            n_clicks=0,
                        ),
                        className="d-grid gap-2 mx-auto",
                    )
                ),
            ],
            color="danger",
        ),
    ],
    className="mt-3",
)


tabs = html.Div(
    [
        dbc.Tabs(
            id="tabs",
            active_tab="tab_info",
            children=[
                dbc.Tab(tab_info, label="Display info", tab_id="tab_info"),
                dbc.Tab(tab_mutation, label="Mutation", tab_id="tab_mutation"),
                dbc.Tab(tab_methylation, label="Methylation", tab_id="tab_methylation"),
                dbc.Tab(
                    tab_dysregulation(""),
                    label="Dysregulation",
                    tab_id="tab_dysregulation",
                ),
            ],
        ),
        html.Div(id="tab-content", style={"marginBottom": "10px"}),
    ]
)

user_data_tabs = html.Div(
    [
        dbc.Tabs(
            id="user_tabs",
            active_tab="user_tab_info",
            children=[
                dbc.Tab(user_tab_info, label="Display info", tab_id="user_tab_info"),
                # dbc.Tab(tab_mutation, label="Mutation", tab_id="tab_mutation"),
                # dbc.Tab(tab_methylation, label="Methylation", tab_id="tab_methylation"),
                dbc.Tab(
                    tab_dysregulation("user_"),
                    label="Dysregulation",
                    tab_id="user_tab_dysregulation",
                ),
            ],
        ),
        html.Div(id="user-tab-content", style={"marginBottom": "10px"}),
    ]
)
