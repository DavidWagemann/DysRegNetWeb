from functools import reduce

import pages.components.parameters


def get_neighborhood(graph_map_list):
    center = [
        get_gene(graph_map["center"][0]["center"], "center")
        for graph_map in graph_map_list
    ]
    center_ids = set([gene["data"]["id"] for gene in center])

    targets = []
    sources = []
    for graph_map in graph_map_list:
        targets.extend(get_targets(graph_map["targets"], center_ids))
        sources.extend(get_sources(graph_map["sources"], center_ids))
    size_targets = len(targets)
    size_sources = len(sources)

    targets = sorted(targets, key=sort_by, reverse=True)
    if len(targets) > parameters.max_regulations:
        targets = targets[: parameters.max_regulations]

    sources = sorted(sources, key=sort_by, reverse=True)
    if len(sources) > parameters.max_regulations:
        sources = sources[: parameters.max_regulations]

    regulations = sorted(targets + sources, key=sort_by, reverse=True)
    regulations = remove_adjacent_duplicates(regulations)

    print(
        f"Sources: {len(sources)}/{size_sources}, Targets: {len(targets)}/{size_targets}, Total return: {len(regulations)}"
    )
    return {"center": center, "regulations": regulations}, {
        "total_sources": size_sources,
        "total_targets": size_targets,
    }


def get_gene(gene, classes):
    node = {
        "data": {"id": gene["gene_id"], "label": gene["gene_id"]},
        "classes": classes,
    }
    if "methylation" in gene.keys():
        node["data"]["methylation"] = gene["methylation"]
    else:
        node["data"]["methylation"] = None
    node["data"]["mutation"] = gene["mutation"]
    return node


def get_regulation(regulation):
    source, target = regulation["regulation_id"].split(":")
    fraction = regulation["fraction"]
    if regulation["direction"] == "+":
        classes = "a"
    elif regulation["direction"] == "-":
        classes = "r"

    return {
        "data": {
            "source": source,
            "target": target,
            "regulation_id": regulation["regulation_id"],
            "fraction": fraction,
            "weight": fraction * 10 + 2,
            "classes": classes,
        },
        "classes": classes,
    }


def get_targets(regulation_list, center_ids=set()):
    targets = []
    for r in regulation_list:
        regulation = get_regulation(r["regulation"])
        gene = (
            get_gene(r["target"], "t")
            if r["target"]["gene_id"] not in center_ids
            else {}
        )
        targets.append([regulation, gene])
    return targets


def get_sources(regulation_list, center_ids=set()):
    sources = []
    for r in regulation_list:
        regulation = get_regulation(r["regulation"])
        gene = (
            get_gene(r["source"], "s")
            if r["source"]["gene_id"] not in center_ids
            else {}
        )
        sources.append([regulation, gene])
    return sources


def sort_by(regulation):
    return regulation[0]["data"]["fraction"], regulation[0]["data"]["regulation_id"]


def remove_adjacent_duplicates(regulations):
    unique_regulations = []
    for i in range(len(regulations)):
        if i > 0:
            if (
                unique_regulations[-1][0]["data"]["regulation_id"]
                != regulations[i][0]["data"]["regulation_id"]
            ):
                unique_regulations.append(regulations[i])
        else:
            unique_regulations.append(regulations[i])

    return unique_regulations
