# preprocess.py

import pandas as pd


def run_preprocessing(fixed_df: pd.DataFrame,
                       weekly_df: pd.DataFrame) -> pd.DataFrame:

    # ------------------------------------------------
    # We only use fixed file for this step
    # ------------------------------------------------

    if "CMLEVEL" not in fixed_df.columns:
        raise ValueError("CMLEVEL column not found in fixed file")

    # Required committee order as per report
    committee_order = [
        "Cluster",
        "Unit",
        "Booth",
        "Mandal",
        "Village",
        "Town",
        "Ward",
        "Division",
        "Parliament",
        "Assembly"
    ]

    # ------------------------------------------------
    # Count total strength from fixed file
    # ------------------------------------------------
    counts = (
        fixed_df["CMLEVEL"]
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    rows = []

    total_strength_sum = 0

    for committee in committee_order:

        total_strength = counts.get(committee, 0)
        total_strength_sum += total_strength

        rows.append({
            "Committees": committee,
            "Total Strength": total_strength,
            "Registered": "",
            "%": ""
        })

    # ------------------------------------------------
    # Total CUBS_COMMITTEE row
    # ------------------------------------------------
    rows.append({
        "Committees": "Total CUBS_COMMITTEE",
        "Total Strength": total_strength_sum,
        "Registered": "",
        "%": ""
    })

    final_df = pd.DataFrame(
        rows,
        columns=["Committees", "Total Strength", "Registered", "%"]
    )

    return final_df
