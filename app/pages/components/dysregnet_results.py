from typing import Any, Dict, List

import pandas as pd


def get_sources(results: pd.DataFrame, ids: List[str]):
    return results[[t for t in results.columns if t[0] in ids]]


def get_targets(results: pd.DataFrame, ids: List[str]):
    return results[[t for t in results.columns if t[1] in ids]]


def get_graph_data(
    sources: pd.DataFrame,
    targets: pd.DataFrame,
    ids: List[str],
    patient_data: List[List[str]],
):
    targets = targets[targets.columns.difference(sources.columns)]

    source_regulations = [
        [
            {
                "data": {
                    "source": col[0],
                    "target": col[1],
                    "regulation_id": f"{col[0]}:{col[1]}",
                    "fraction": float((sources[[col]] != 0).sum() / len(sources)),
                    "weight": float((sources[[col]] != 0).sum() / len(sources)) * 10
                    + 2,
                    "classes": (
                        "r" if sources[col].mean() < 0 else "a"
                    ),  # TODO: check if this is correct
                },
                "classes": "r" if sources[col].mean() < 0 else "a",
            },
            {
                "data": {
                    "id": col[1],
                    "label": col[1],
                    "methylation": None,
                    "mutation": None,
                },
                "classes": "t",
            },
        ]
        for col in sources
    ]

    target_regulations = [
        [
            {
                "data": {
                    "source": col[0],
                    "target": col[1],
                    "regulation_id": f"{col[0]}:{col[1]}",
                    "fraction": float((targets[[col]] != 0).sum() / len(targets)),
                    "weight": float((targets[[col]] != 0).sum() / len(targets)) * 10
                    + 2,
                    "classes": "r" if targets[col].mean() < 0 else "a",
                },
                "classes": "r" if targets[col].mean() < 0 else "a",
            },
            {
                "data": {
                    "id": col[0],
                    "label": col[0],
                    "methylation": None,
                    "mutation": None,
                },
                "classes": "s",
            },
        ]
        for col in targets
    ]
    return {
        "center": [
            {
                "data": {"id": id, "label": id, "methylation": None, "mutation": None},
                "classes": "center",
            }
            for id in ids
        ],
        "regulations": source_regulations + target_regulations,
        "patient": (
            {
                regulation[0]: regulation[2]
                for regulation in patient_data
                if (
                    regulation[0].split(":")[0] in ids
                    or regulation[0].split(":")[1] in ids
                )
            }
            if patient_data is not None
            else {}
        ),
    }


def get_num_regulation(sources: pd.DataFrame, targets: pd.DataFrame) -> Dict[str, int]:
    return {
        "total_targets": len(targets.columns),
        "total_sources": len(sources.columns),
    }


def graph_to_csv(graph_data: Dict[Any, Any]) -> Dict[str, str]:
    rows = ["source,target,type,fraction"]

    for row in graph_data["regulations"]:
        rows.append(
            f"{row[0]['data']['source']},{row[0]['data']['target']},{row[0]['data']['classes']},{row[0]['data']['fraction']}"
        )

    return dict(content="\n".join(rows) + "\n", filename="full_graph.csv")
