from typing import List, Union, Dict

import dysregnet
import pandas as pd
from pages.components.dysregnet_cache import cache

def get_results(session_id: str, *args) -> pd.DataFrame:
    """
    This is a workaround for using the cached dysregnet call.
    Due to the limits of flask_caching, particularly the deprecated hash backend,
    retrieving entries by session_id from the redis cache proved unfeasable.
    Thus, all args except session_id are ignored for caching.
    TODO: Please improve on this with some other caching library than flask.
    """

    @cache.memoize(
        args_to_ignore=[
            "expression", "meta", "network", "condition", "cat_cov", "con_cov",
            "zscoring", "bonferroni", "normaltest", "normaltest_alpha", "r2",
            "condition_direction"
        ]
    )
    def run_dysregnet(session_id: str, *args) -> pd.DataFrame:
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

        # TODO kwargs parsing or assertion of correct type
        # expression: Dict[str, Dict[str, str]],
        # meta: Dict[str, Dict[str, str]],
        # network: Dict[str, Dict[str, str]],
        # condition: str,
        # cat_cov: List[str],
        # con_cov: List[str],
        # zscoring: bool,
        # bonferroni: float,
        # normaltest: bool,
        # normaltest_alpha: float,
        # r2: Union[float, None],
        # condition_direction: bool,

        result = dysregnet.run(
            expression_data=pd.DataFrame(args[0]),
            meta=pd.DataFrame(args[1]),
            GRN=pd.DataFrame(args[2]),
            conCol=args[3],
            CatCov=args[4],
            ConCov=args[5],
            zscoring=args[6],
            bonferroni_alpha=args[7],  # = 1e-2
            R2_threshold=args[10],  # None
            normaltest=args[8],  # False
            normaltest_alpha=args[9],  # = 1e-3
            direction_condition=args[11],
        )

        # convert result to Dict[str, str]
        results = result.run_dysregnet()
        results.columns = [",".join(c) for c in results.columns]
        results = results.to_dict()

        return results

    # depending on usecase: if args for dysregnet.run() provided, run DysRegNet
    # otherwise return cached version
    if len(args) > 0:
        return run_dysregnet(session_id, *args)
    else:
        return run_dysregnet(session_id = session_id)
