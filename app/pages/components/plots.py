import pandas as pd
import dash_bio as dashbio
import plotly.express as px
import plotly.graph_objects as go


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


def methylation_heatmap(data):
    methylation_data = pd.DataFrame(
        columns=['Gene id', 'Patient id', 'Methylation'],
        data=data,
    )
    methylation_data["Methylation"] = pd.to_numeric(methylation_data["Methylation"])
    methylation_data = methylation_data.pivot('Patient id', 'Gene id', 'Methylation')
    columns = list(methylation_data.columns.values)
    rows = list(methylation_data.index)
    cluster = 'all' if len(columns) > 1 else 'rows'
    fig = dashbio.Clustergram(
        data=methylation_data.loc[rows].values,
        column_labels=columns,
        row_labels=rows,
        hidden_labels='row',
        center_values=False,
        cluster=cluster,
        color_map=[
            [0.0, 'white'],
            [1.0, 'blue']
        ]
    )

    fig.for_each_trace(
        lambda t: t.update(hovertemplate="Gene id: %{x}<br>Patient id: %{y}<br>Methylation: %{z}<extra></extra>")
        if isinstance(t, go.Heatmap)
        else t
    )

    return fig


def dysregulation_heatmap(data):
    dysregulation_data = pd.DataFrame(
        columns=['Regulation', 'Patient id', 'z-value'],
        data=data,
    )
    dysregulation_data["z-value"] = pd.to_numeric(dysregulation_data["z-value"]).abs()
    dysregulation_data = dysregulation_data.pivot('Patient id', 'Regulation', 'z-value')
    columns = list(dysregulation_data.columns.values)
    rows = list(dysregulation_data.index)

    dysregulation_data = dysregulation_data.fillna(0)

    cluster = 'all' if len(columns) > 1 else 'rows'

    hidden_labels = []
    if len(columns) > 20:
        hidden_labels.append('col')
    if len(rows) > 20:
        hidden_labels.append('row')

    fig = dashbio.Clustergram(
        data=dysregulation_data.loc[rows].values,
        column_labels=columns,
        row_labels=rows,
        hidden_labels=hidden_labels,
        center_values=False,
        cluster=cluster,
        color_map=[
            [0.0, 'white'],
            [1.0, 'red']
        ],
    )
    for t in fig.data:
        if isinstance(t, go.Heatmap):
            z = [[ij if ij > 0 else '' for ij in i] for i in t['z']]

    fig.for_each_trace(
        lambda t: t.update(customdata=z)
        if isinstance(t, go.Heatmap)
        else t
    )

    fig.for_each_trace(
        lambda t: t.update(hovertemplate="Regulation: %{x}<br>Patient id: %{y}<br>Z-score: %{customdata}<extra></extra>")
        if isinstance(t, go.Heatmap)
        else t
    )

    return fig


def mutation_bar(elements):
    node_set = set()
    for element in elements:
        if 'mutation' in element['data']:
            color = 'Source/Target'
            if 'center' in element['classes']:
                color = 'Query gene'
            node_set.add((element['data']['id'], element['data']['mutation'], color))

    ids, mutations, colors = map(list, zip(*node_set))
    df = pd.DataFrame({'Gene id': ids, 'Fraction of patients with mutation': mutations, 'Type': colors, })
    fig = px.bar(df, x='Gene id', y='Fraction of patients with mutation',
                 color='Type', color_discrete_map={'Query gene': 'red', 'Source/Target': 'grey'},
                 category_orders={"Type": ["Query gene", "Source/Target"]},
                 template="simple_white")
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis={'categoryorder': 'total descending'},
    )
    fig.update_xaxes(type='category', tickmode='array', ticktext=df['Gene id'].tolist())
    return fig
