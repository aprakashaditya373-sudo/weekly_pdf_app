# app.py

import streamlit as st
import pandas as pd
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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
        final_df = run_preprocessing(fixed_df, weekly_df)
    except Exception as e:
        st.error("Error during preprocessing")
        st.exception(e)
        st.stop()

    if final_df is None or final_df.empty:
        st.warning("Final output is empty. No PDF generated.")
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

    title = Paragraph(
        "Analysis of members registered in MyTDP App",
        styles["Heading2"]
    )

    elements.append(title)
    elements.append(Spacer(1, 12))

    # convert everything to string for reportlab safety
    table_data = [list(final_df.columns)] + final_df.astype(str).values.tolist()

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    st.success("PDF generated successfully")

    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name="weekly_report.pdf",
        mime="application/pdf"
    )
