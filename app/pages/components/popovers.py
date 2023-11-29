import dash_bootstrap_components as dbc
from dash import dcc, html

cancer_map = {
    "LUAD": "Lung adenocarcinoma",
    "BRCA": "Breast invasive carcinoma",
    "COAD": "Colon adenocarcinoma",
    "HNSC": "Head and Neck squamous cell carcinoma",
    "KIRC": "Kidney renal clear cell carcinoma",
    "KIRP": "Kidney renal papillary cell carcinoma",
    "LIHC": "Liver hepatocellular carcinoma",
    "LUSC": "Lung squamous cell carcinoma",
    "PRAD": "Prostate adenocarcinoma",
    "STAD": "Stomach adenocarcinoma",
    "THCA": "Thyroid carcinoma",
}


def get_popovers():
    popovers = [
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Display options
                **Minimum dysregulation fraction:**
                Allows to filter the displayed regulations by the fraction of patients they are dysregulated in.
                Only edges with an equal to or larger fraction of dysregulated patients will be displayed in the network
                graph.
                
                **Maximum regulations displayed:** 
                Sets a cutoff for the maximum number of regulations displayed in 
                the network graph. Therefore, regulations get sorted by their fraction of dysregulated patients. 
                Regulations, which are disregulated in only few patients, will be dropped first. Due to the upper 
                limit, it is only possible to graphically inspect the 200 topmost dysregulated edges. 
                
                **Scale node size by:**
                Scale the size of displayed genes/nodes by the fraction of patients they are
                mutated in or their mean promoter methylation across patients. Nodes with missing data are displayed
                with reduced opacity.
                 
                **Display nodes:**
                Filter the nodes/genes, so that either only target or only source nodes of the query genes are
                displayed.
                """,
            ),
            target="display_options_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Compare options
                **Compare to cancer type:**
                Compare the dysregulation fractions of currently displayed regulations to the corresponding ones in a
                different cancer type.
                
                **Display dysregulation difference:**
                Toggles, whether the difference between the dysregulation fractions should be visualized as 
                colored bars on the edges. A orange bar means, that the primary selected cancer type has a higher
                dysregulation fraction than the type compared to. A green bar means a lower dysregulation fraction.
                Even if the feature is toggled off, the exact differences can still be inspected by clicking directly on
                a regulation.
                
                NOTE: Any filtering of the regulations will still be based on the dysregulation fraction of the primary
                selected cancer type, not on its difference to the compared type.

                """,
            ),
            target="compare_options_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Downloads 
                **Download full graph:**
                Downloads the queried network as a CSV file. All regulations are included, even those
                exceeding the maximum display limit of 200. 
                
                **Download displayed graph:**
                Downloads the displayed network as a CSV file. Filtered out regulations aren't included.
                
                **Download graph image:**
                Downloads the displayed network graph as a PNG image.
                
                """,
            ),
            target="downloads_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Display info
                **Selected cancer type:**
                Displays the currently selected TCGA study. A full list of the abbreviations can be found 
                [here](https://gdc.cancer.gov/resources-tcga-users/tcga-code-tables/tcga-study-abbreviations).
                
                **Target/Source regulations:**
                A query genes outgoing edges are considered target regulations, incoming edges source regulations. 
                For both types the first number corresponds to the amount of currently displayed edges, the second to 
                the total number including edges which were removed by filtering or by exceeding the maximum number of
                displayable edges. 
                
                NOTE: The combined values of both categories (source/target regulations) won't necessarily sum up to the
                total number of edges, since a connection between two query genes is included in both.
    
                """,
            ),
            target="display_info_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Mutation info
                The bar chart shows mutation frequencies for query and source/target genes. Click on the name in the
                legend to exclude one of the categories. The mutation frequency of a gene is defined as the fraction of
                patients in which the gene possesses at least one mutation.
                """,
            ),
            target="mutation_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Methylation info
                Load a heatmap to visualize patient-specific promoter methylation. Each row corresponds to a
                patient, each column to a query gene. The value of a cell is the average beta-value across all 
                methylation sites of a genes promoter region in an individual patient. Hover over a cell to inspect the
                exact value.
                
                NOTE: The heatmap will not update automatically after changing the gene query and has to be
                refreshed manually.
                
                NOTE: The number of columns can be lower than the number of query genes since methylation data isn't
                available for every gene.
                """,
            ),
            target="methylation_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
        dbc.Popover(
            dcc.Markdown(
                """
                ##### Dysregulation info
                Load a heatmap to visualize patient-specific dysregulation. Each row corresponds to a
                patient, each column to a regulation in the currently displayed network graph. The value of a cell is
                an absolute z-value, which was used to categorize a regulation in a patient as dysregulated. The higher
                the value, the more significant is the dysregulation. Hovering over a cell will yield the exact z-value.
                Cells with missing z-values are considered conventionally regulated. For the clustering they are treated as 
                zeros, even though in reality their z-values are just below a threshold.

                NOTE: The heatmap will not update automatically after changing the network graph and has to be
                refreshed manually.
                """,
            ),
            target="dysregulation_info",
            body=True,
            trigger="legacy",
            placement="auto",
        ),
    ]
    return popovers


def get_gene_popover():
    gene_popover = dbc.Popover(
        dcc.Markdown(
            """
            ##### Gene detail information
            **Promoter methylation:** 
            Indicates the promoter methylation averaged across patients with available methylation data. The patient 
            specific methylation values themselves are averaged beta-values across all methylation sites of their
            promoter region. Navigate to the *Methylation* tab to inspect patient specific promoter methylation
            values.
            
            **Mutation frequency:**
            Displays the fraction of patients, where this gene is mutated at least once.
            
            **Choose as query:**
            Replaces the current selection of query genes with only this gene.
            
            **Add/Remove:**
            Adds the gene to the query, if it is not yet part of it. Else it removes the gene from the query.
            
            """,
        ),
        target="gene_info",
        body=True,
        trigger="legacy",
        placement="auto",
    )

    return gene_popover


def get_regulation_popover():
    regulation_popover = dbc.Popover(
        dcc.Markdown(
            """
            ##### Regulation detail information
            **Fraction of dysregulated patients:**
            Displays the fraction of patients with a dysregulation regarding this edge. The value matches the 
            corresponding red bar in the network graph.
            """,
        ),
        target="regulation_info",
        body=True,
        trigger="legacy",
        placement="auto",
    )

    return regulation_popover


def info_button(popover_id):
    info_button = dbc.Button(
        html.I(className="fa fa-question"),
        id=popover_id,
        outline=True,
        color="primary",
        size="sm",
    )
    return info_button


def heading_with_info(text, popover_id):
    return html.Div(
        [html.H5(text), html.Div(info_button(popover_id))],
        className="d-grid gap-2 mb-2 d-md-flex justify-content-md-between",
    )


def get_cancer_map():
    return cancer_map


def map_cancer(cancer):
    return cancer_map.get(cancer)
