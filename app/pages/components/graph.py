import dash_cytoscape as cyto
from dash import html

style_sheet = [
                {
                    'selector': 'edge',
                    'style': {
                        'curve-style': 'bezier',
                        'line-fill': 'linear-gradient',
                        'line-gradient-stop-colors': 'data(colors)',
                        'line-gradient-stop-positions': "data(divide)",
                        'width': 'data(weight)',
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
                    'selector': '.no_data',
                    'style': {
                        'opacity': 0.3,
                    }
                },
                {
                    'selector': 'node:selected',
                    'style': {
                        "background-color": "#106cfc",
                    }
                },
                {
                    'selector': 'edge:selected',
                    'style': {
                        'target-arrow-color': "#106cfc",
                        'border-color': "black",
                    }
                },
                {
                    'selector': ':selected',
                    'style': {
                        "z-index": "999999"
                    }
                },
            ]

styles = {
    'cytoscape': {
        'position': 'relative',
        'width': '100%',
        'height': '100%',
    }
}

graph = cyto.Cytoscape(
            id='graph',
            minZoom=0.1,
            maxZoom=2,
            layout={'name': 'klay'},
            style=styles['cytoscape'],
            stylesheet=style_sheet,
        )

