import dash
import dash_cytoscape as cyto
from dash import html

app = dash.Dash(__name__)

style_sheet = [
                {
                    'selector': 'edge',
                    'style': {
                        'curve-style': 'bezier',
                        'line-fill': 'linear-gradient',
                        'line-gradient-stop-colors': 'data(colors)',
                        'line-gradient-stop-positions': "data(divide)",
                        'width': 8,
                        'target-arrow-color': 'grey',
                    }
                },
                {
                    'selector': '.a',
                    'style': {
                        'target-arrow-shape': 'triangle',
                    }
                },
                {
                    'selector': '.r',
                    'style': {
                        'target-arrow-shape': 'tee',
                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(label)',
                        'width': 'data(diameter)',
                        'height': 'data(diameter)',
                        'text-halign': 'right',
                        'text-valign': 'center',
                        'background-color': 'grey',
                    }
                },
                {
                    'selector': '.center',
                    'style': {
                        'border-width': 2,
                        'border-color': "black",
                        'background-color': "red",
                    }
                },
                {
                    'selector': '.invis',
                    'style': {
                        'opacity': 0,
                    }
                },
            ]

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '700px'},
        elements=[
            {'data': {'id': 'query', 'label': ''}, 'classes': 'center', 'position': {'x': 55, 'y': 75}},

            {'data': {'id': 'source_target', 'label': ''}, 'classes': 's', 'position': {'x': 55, 'y': 125}},


            {'data': {'id': 'a_one', 'label': ''}, 'classes': 'invis', 'position': {'x': 10, 'y': 175}},
            {'data': {'id': 'a_two', 'label': ''}, 'classes': 'invis', 'position': {'x': 110, 'y': 175}},
            {'data': {'source': 'a_one', 'target': 'a_two', 'divide': '0% 0% 0% 100%', 'colors': 'red red grey grey'}, 'classes': 'a'},

            {'data': {'id': 'r_one', 'label': ''}, 'classes': 'invis', 'position': {'x': 10, 'y': 225}},
            {'data': {'id': 'r_two', 'label': ''}, 'classes': 'invis', 'position': {'x': 110, 'y': 225}},
            {'data': {'source': 'r_one', 'target': 'r_two', 'divide': '0% 0% 0% 100%', 'colors': 'red red grey grey'}, 'classes': 'r'},

            {'data': {'id': 'f_one', 'label': ''}, 'classes': 'invis', 'position': {'x': 10, 'y': 275}},
            {'data': {'id': 'f_two', 'label': ''}, 'classes': 'invis', 'position': {'x': 110, 'y': 275}},
            {'data': {'source': 'f_one', 'target': 'f_two', 'divide': '0% 40% 40% 100%', 'colors': 'red red grey grey'}},

            {'data': {'id': 'l_one', 'label': ''}, 'classes': 'invis', 'position': {'x': 10, 'y': 325}},
            {'data': {'id': 'l_two', 'label': ''}, 'classes': 'invis', 'position': {'x': 110, 'y': 325}},
            {'data': {'source': 'l_one', 'target': 'l_two', 'divide': '0% 60% 60% 100%',
                      'colors': 'green green grey grey'}},

            {'data': {'id': 'h_one', 'label': ''}, 'classes': 'invis', 'position': {'x': 10, 'y': 375}},
            {'data': {'id': 'h_two', 'label': ''}, 'classes': 'invis', 'position': {'x': 110, 'y': 375}},
            {'data': {'source': 'h_one', 'target': 'h_two', 'divide': '0% 35% 35% 100%',
                      'colors': 'orange orange grey grey'}},

        ],
        stylesheet=style_sheet
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)