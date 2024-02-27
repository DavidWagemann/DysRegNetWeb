from typing import List, Union, Dict

import dysregnet
import pandas as pd
from pages.components.dysregnet_cache import cache_data

def get_results(
    expression: Dict[str, Dict[str, str]],
    meta: Dict[str, Dict[str, str]],
    network: Dict[str, Dict[str, str]],
    condition: str,
    cat_cov: List[str],
    con_cov: List[str],
    zscoring: bool,
    bonferroni: float,
    normaltest: bool,
    normaltest_alpha: float,
    r2: Union[float, None],
    condition_direction: bool,
    session_id: str
) -> pd.DataFrame:
    """
    Runs the DysRegNet analysis and returns the results.

    Args:
        expression (Dict[str, Dict[str, str]]): The expression data.
        meta (Dict[str, Dict[str, str]]): The metadata.
        network (Dict[str, Dict[str, str]]): The gene regulatory network.
        condition (str): The condition column name.
        cat_cov (List[str]): The categorical covariates.
        con_cov (List[str]): The continuous covariates.
        zscoring (bool): Flag indicating whether to perform z-scoring.
        bonferroni (float): The Bonferroni alpha threshold.
        normaltest (bool): Flag indicating whether to perform normality test.
        normaltest_alpha (float): The normality test alpha threshold.
        r2 (float): The R2 threshold.
        condition_direction (bool): Flag indicating whether to consider condition direction.

    Returns:
        pd.DataFrame: The DysRegNet analysis results.
    """

    result = dysregnet.run(
        expression_data=pd.DataFrame(expression),
        meta=pd.DataFrame(meta),
        GRN=pd.DataFrame(network),
        conCol=condition,
        CatCov=cat_cov,
        ConCov=con_cov,
        zscoring=zscoring,
        bonferroni_alpha=bonferroni,  # = 1e-2
        R2_threshold=r2,  # None
        normaltest=normaltest,  # False
        normaltest_alpha=normaltest_alpha,  # = 1e-3
        direction_condition=condition_direction,
    )

    # get result DataFrame from DysRegNet run object
    results = result.get_results()

    # convert result to Dict[str, str]
    results.columns = [",".join(c) for c in results.columns]
    results = results.to_dict()

    # cache input data and results
    cache_data(session_id, results, 
        parameters = {
            "expression": expression,
            "meta": meta,
            "network": network,
            "condition": condition,
            "cat_cov": cat_cov,
            "con_cov": con_cov,
            "zscoring": zscoring,
            "bonferroni": bonferroni,
            "r2": r2,
            "normaltest": normaltest,
            "normaltest_alpha": normaltest_alpha,
            "condition_direction": condition_direction,
        }
    )

    return results
