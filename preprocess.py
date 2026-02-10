# preprocess.py

import pandas as pd


def run_preprocessing(fixed_df: pd.DataFrame,
                       weekly_df: pd.DataFrame) -> pd.DataFrame:

    # ------------------------------------------------
    # Validate columns
    # ------------------------------------------------
    if "CMLEVEL" not in fixed_df.columns:
        raise ValueError("CMLEVEL column not found in fixed file")

    if "ROLE" not in fixed_df.columns:
        raise ValueError("ROLE column not found in fixed file")

    df = fixed_df.copy()
    df["CMLEVEL"] = df["CMLEVEL"].astype(str).str.strip()
    df["ROLE"] = df["ROLE"].astype(str).str.strip()

    # ============================================================
    # 1) PAGE–1 : Committees table (only CMLEVEL)
    # ============================================================

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

    counts = (
        df["CMLEVEL"]
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

    rows.append({
        "Committees": "Total CUBS_COMMITTEE",
        "Total Strength": total_strength_sum,
        "Registered": "",
        "%": ""
    })

    # blank row between tables
    rows.append({
        "Committees": "",
        "Total Strength": "",
        "Registered": "",
        "%": ""
    })

    # ============================================================
    # 2) PAGE–2 & 3 : CMLEVEL + ROLE table
    # ============================================================

    ordered_rows = [
        ("Cluster", "Convenor"),
        ("Cluster", "Co-Convenor"),

        ("Unit", "Convenor"),
        ("Unit", "Co-Convenor"),

        ("Booth", "Convenor"),
        ("Booth", "Co-Convenor"),

        ("Mandal", "President"),
        ("Mandal", "Vice-President"),
        ("Mandal", "General Secretary"),
        ("Mandal", "Organizing Secretary"),
        ("Mandal", "Secretary"),
        ("Mandal", "Treasurer"),

        ("Village", "President"),
        ("Village", "General Secretary"),
        ("Village", "Secretary"),
        ("Village", "Vice-President"),
        ("Village", "Organizing Secretary"),
        ("Village", "Treasurer"),

        ("Town", "President"),
        ("Town", "Vice-President"),
        ("Town", "General Secretary"),
        ("Town", "Organizing Secretary"),
        ("Town", "Secretary"),
        ("Town", "Treasurer"),

        ("Ward", "President"),
        ("Ward", "Vice-President"),
        ("Ward", "General Secretary"),
        ("Ward", "Organizing Secretary"),
        ("Ward", "Secretary"),
        ("Ward", "Treasurer"),

        ("Division", "President"),
        ("Division", "Vice-President"),
        ("Division", "General Secretary"),
        ("Division", "Organizing Secretary"),
        ("Division", "Secretary"),
        ("Division", "Treasurer"),

        ("Parliament", "President"),
        ("Parliament", "Vice-President"),
        ("Parliament", "General Secretary"),
        ("Parliament", "Organizing Secretary"),
        ("Parliament", "Secretary"),
        ("Parliament", "Official Spokesperson"),
        ("Parliament", "Treasurer"),
        ("Parliament", "Office Secretary"),
        ("Parliament", "Media Coordinator"),
        ("Parliament", "Social Media Coordinator"),

        ("Assembly", "President"),
        ("Assembly", "Vice-President"),
        ("Assembly", "General Secretary"),
        ("Assembly", "Organizing Secretary"),
        ("Assembly", "Secretary"),
        ("Assembly", "Official Spokesperson"),
        ("Assembly", "Social Media Coordinator"),
    ]

    grouped_counts = (
        df
        .groupby(["CMLEVEL", "ROLE"])
        .size()
        .to_dict()
    )

    for cmlevel, role in ordered_rows:

        total_members = grouped_counts.get((cmlevel, role), 0)

        rows.append({
            "Committees": f"{cmlevel} {role}",
            "Total Strength": total_members,
            "Registered": "",
            "%": ""
        })

    final_df = pd.DataFrame(
        rows,
        columns=["Committees", "Total Strength", "Registered", "%"]
    )

    return final_df
