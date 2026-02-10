# preprocess.py

import pandas as pd


def run_preprocessing(fixed_df: pd.DataFrame,
                       weekly_df: pd.DataFrame):

    if "CMLEVEL" not in fixed_df.columns:
        raise ValueError("CMLEVEL column not found in fixed file")

    if "ROLE" not in fixed_df.columns:
        raise ValueError("ROLE column not found in fixed file")

    if "MIMD" not in fixed_df.columns:
        raise ValueError("MIMD column not found in fixed file")

    if "mid" not in weekly_df.columns:
        raise ValueError("mid column not found in weekly file")

    # ------------------------------------------------
    # Normalize ONLY weekly mid
    # ------------------------------------------------
    def normalize_weekly_mid(x):

        if pd.isna(x):
            return None

        # important fix for float mids
        if isinstance(x, float):
            x = str(int(x))
        else:
            x = str(x).strip()

        if x.startswith("#"):
            x = x[1:]

        x = "".join(c for c in x if c.isdigit())

        if len(x) == 0:
            return None

        # MIMD format is # + 8 digits
        if len(x) < 8:
            x = x.zfill(8)

        return "#" + x

    # ------------------------------------------------
    # Prepare fixed file (MIMD as-is)
    # ------------------------------------------------
    df = fixed_df.copy()

    df["CMLEVEL"] = df["CMLEVEL"].astype(str).str.strip()
    df["ROLE"] = df["ROLE"].astype(str).str.strip()
    df["MIMD"] = df["MIMD"].astype(str).str.strip()

    # ------------------------------------------------
    # Prepare weekly file
    # ------------------------------------------------
    weekly = weekly_df.copy()
    weekly["mid_norm"] = weekly["mid"].apply(normalize_weekly_mid)

    registered_mids = set(weekly["mid_norm"].dropna())

    # ------------------------------------------------
    # Registered flag
    # ------------------------------------------------
    df["is_registered"] = df["MIMD"].isin(registered_mids)

    # ==========================================================
    # TABLE 1 – Committees
    # ==========================================================

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

    counts = df["CMLEVEL"].value_counts().to_dict()

    registered_counts_1 = (
        df[df["is_registered"]]
        .groupby("CMLEVEL")
        .size()
        .to_dict()
    )

    rows_1 = []
    total_strength_sum = 0
    total_registered_sum = 0

    for committee in committee_order:

        total_strength = counts.get(committee, 0)
        registered_cnt = registered_counts_1.get(committee, 0)

        total_strength_sum += total_strength
        total_registered_sum += registered_cnt

        if total_strength > 0:
            pct = f"{(registered_cnt / total_strength) * 100:.1f}%"
        else:
            pct = "0.0%"

        rows_1.append({
            "Committees": committee,
            "Total Strength": total_strength,
            "Registered": registered_cnt,
            "%": pct
        })

    if total_strength_sum > 0:
        total_pct = f"{(total_registered_sum / total_strength_sum) * 100:.1f}%"
    else:
        total_pct = "0.0%"

    rows_1.append({
        "Committees": "Total CUBS_COMMITTEE",
        "Total Strength": total_strength_sum,
        "Registered": total_registered_sum,
        "%": total_pct
    })

    table_1 = pd.DataFrame(
        rows_1,
        columns=["Committees", "Total Strength", "Registered", "%"]
    )

    # ==========================================================
    # TABLE 2 – CM LEVEL ROLE
    # ==========================================================

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
        ("Parliament", "Media  Coordinator"),
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

    registered_counts_2 = (
        df[df["is_registered"]]
        .groupby(["CMLEVEL", "ROLE"])
        .size()
        .to_dict()
    )

    rows_2 = []

    for cmlevel, role in ordered_rows:

        total_members = grouped_counts.get((cmlevel, role), 0)
        registered_members = registered_counts_2.get((cmlevel, role), 0)

        if total_members > 0:
            pct = f"{(registered_members / total_members) * 100:.1f}%"
        else:
            pct = "0.0%"

        rows_2.append({
            "CM LEVEL": cmlevel,
            "ROLE": role,
            "Total Cadre Members": total_members,
            "Registered": registered_members,
            "% Registered": pct
        })

    table_2 = pd.DataFrame(
        rows_2,
        columns=[
            "CM LEVEL",
            "ROLE",
            "Total Cadre Members",
            "Registered",
            "% Registered"
        ]
    )

    return table_1, table_2
