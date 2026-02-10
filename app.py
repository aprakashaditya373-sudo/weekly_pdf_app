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
    # Centered title  (ONLY CHANGE)
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
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1c232")),   # header bg
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),           # header text
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
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1c232")),   # header bg
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),           # header text
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
