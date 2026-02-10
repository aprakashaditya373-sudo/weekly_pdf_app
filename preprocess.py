# preprocess.py

import pandas as pd


def run_preprocessing(fixed_df: pd.DataFrame,
                       weekly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace this logic with your real preprocessing steps.
    For now it simply returns the weekly data.
    """

    final_df = weekly_df.copy()

    return final_df
