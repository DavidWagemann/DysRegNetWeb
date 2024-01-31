from typing import List, Union

import dysregnet
import pandas as pd

# TODO cache function call using celery and redis
def get_results(
    expression: pd.DataFrame,
    meta: pd.DataFrame,
    network: pd.DataFrame,
    condition: str,
    cat_cov: List[str],
    con_cov: List[str],
    zscoring: bool,
    bonferroni: float,
    normaltest: bool,
    normaltest_alpha: float,
    r2: Union[float, None],
    condition_direction: bool,
) -> pd.DataFrame:
    """
    Runs the DysRegNet analysis and returns the results.

    Args:
        expression (pd.DataFrame): The expression data.
        meta (pd.DataFrame): The metadata.
        network (pd.DataFrame): The gene regulatory network.
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
        expression_data=expression,
        meta=meta,
        GRN=network,
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

    return result.get_results()
