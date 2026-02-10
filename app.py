# app.py

import streamlit as st
import pandas as pd
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

from preprocess import run_preprocessing


st.set_page_config(page_title="Weekly Report Generator", layout="centered")

st.title("Weekly Report Generator")

st.write("Upload the fixed master file and the weekly file to generate the final PDF.")

# -----------------------------
# Upload fixed file (large file)
# -----------------------------
fixed_file = st.file_uploader(
    "Upload fixed master file (upload only when it changes)",
    type=["xlsx", "csv"],
    key="fixed"
)

# -----------------------------
# Upload weekly file
# -----------------------------
weekly_file = st.file_uploader(
    "Upload weekly file",
    type=["xlsx", "csv"],
    key="weekly"
)

generate = st.button("Generate PDF")


if generate:

    if fixed_file is None:
        st.error("Please upload the fixed master file")
        st.stop()

    if weekly_file is None:
        st.error("Please upload the weekly file")
        st.stop()

    # -----------------------------
    # Read fixed file
    # -----------------------------
    try:
        if fixed_file.name.lower().endswith(".csv"):
            fixed_df = pd.read_csv(fixed_file)
        else:
            fixed_df = pd.read_excel(fixed_file)
    except Exception as e:
        st.error("Unable to read fixed master file")
        st.exception(e)
        st.stop()

    # -----------------------------
    # Read weekly file
    # -----------------------------
    try:
        if weekly_file.name.lower().endswith(".csv"):
            weekly_df = pd.read_csv(weekly_file)
        else:
            weekly_df = pd.read_excel(weekly_file)
    except Exception as e:
        st.error("Unable to read weekly file")
        st.exception(e)
        st.stop()

    # -----------------------------
    # Preprocessing
    # -----------------------------
    try:
        table1_df, table2_df = run_preprocessing(fixed_df, weekly_df)
    except Exception as e:
        st.error("Error during preprocessing")
        st.exception(e)
        st.stop()

    # -----------------------------
    # Empty check
    # -----------------------------
    if table1_df is None or table1_df.empty:
        st.warning("Table 1 is empty. No PDF generated.")
        st.stop()

    if table2_df is None or table2_df.empty:
        st.warning("Table 2 is empty. No PDF generated.")
        st.stop()

    # -----------------------------
    # Build PDF
    # -----------------------------
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    # -----------------------------
    # Centered title
    # -----------------------------
    center_title_style = ParagraphStyle(
        name="CenterTitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER
    )

    title = Paragraph(
        "Analysis of members registered in MyTDP App",
        center_title_style
    )

    elements.append(title)
    elements.append(Spacer(1, 12))

    # =========================================================
    # SUMMARY BLOCKS (as in your image)
    # =========================================================

    # Total members registered (weekly rows)
    total_members_registered = len(weekly_df)

    # Registered users with no MID
    registered_no_mid = weekly_df["mid"].isna().sum()

    # Registered users with MID mapped
    registered_with_mid_mapped = int(
        table1_df.loc[
            table1_df["Committees"] == "Total CUBS_COMMITTEE",
            "Registered"
        ].values[0]
    )

    # Normalize weekly MID exactly same as preprocessing
    def _norm_mid_local(x):
        if pd.isna(x):
            return None

        if isinstance(x, float):
            x = str(int(x))
        else:
            x = str(x).strip()

        if x.startswith("#"):
            x = x[1:]

        x = "".join(c for c in x if c.isdigit())

        if len(x) == 0:
            return None

        if len(x) < 8:
            x = x.zfill(8)

        return "#" + x

    weekly_mid_norm = set(
        weekly_df["mid"].apply(_norm_mid_local).dropna()
    )

    tmp_fixed = fixed_df.copy()
    tmp_fixed["MIMD"] = tmp_fixed["MIMD"].astype(str).str.strip()

    tmp_fixed["is_registered"] = tmp_fixed["MIMD"].isin(weekly_mid_norm)

    # Party Functionaries / General Users
    party_functionaries = tmp_fixed.loc[
        (tmp_fixed["is_registered"]) &
        (tmp_fixed["CMTYPE"].astype(str).str.strip().str.lower() == "party functionaries")
    ].shape[0]

    general_users = tmp_fixed.loc[
        (tmp_fixed["is_registered"]) &
        (tmp_fixed["CMTYPE"].astype(str).str.strip().str.lower() != "party functionaries")
    ].shape[0]

    # ---- first small box ----
    summary1_data = [
        ["Total Members Registered", f"{total_members_registered}"],
        ["Registered Users with no MID", f"{registered_no_mid}"],
    ]

    summary1 = Table(summary1_data, colWidths=[260, 120])

    summary1.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(summary1)
    elements.append(Spacer(1, 18))

    # ---- second small box ----
    summary2_data = [
        [f"Registered Users with MID Mapped - {registered_with_mid_mapped}", ""],
        ["Party Functionaries", f"{party_functionaries}"],
        ["General Users", f"{general_users}"],
    ]

    summary2 = Table(summary2_data, colWidths=[260, 120])

    summary2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("SPAN", (0, 0), (-1, 0)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(summary2)
    elements.append(Spacer(1, 22))

    # ==================================================
    # TABLE 1
    # ==================================================
    elements.append(Paragraph(
        "Committees – Total Strength",
        styles["Heading3"]
    ))
    elements.append(Spacer(1, 8))

    table1_data = [list(table1_df.columns)] + table1_df.astype(str).values.tolist()

    table1 = Table(table1_data, repeatRows=1)

    table1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1c232")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(table1)

    # new page
    elements.append(PageBreak())

    # ==================================================
    # TABLE 2
    # ==================================================
    elements.append(Paragraph(
        "CM LEVEL ROLE – Total Cadre Members",
        styles["Heading3"]
    ))
    elements.append(Spacer(1, 8))

    table2_data = [list(table2_df.columns)] + table2_df.astype(str).values.tolist()

    table2 = Table(table2_data, repeatRows=1)

    table2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1c232")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(table2)

    doc.build(elements)

    buffer.seek(0)

    st.success("PDF generated successfully")

    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name="weekly_report.pdf",
        mime="application/pdf"
    )
