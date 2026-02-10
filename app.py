# app.py

import streamlit as st
import pandas as pd
import os
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from preprocess import run_preprocessing


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Weekly Report Generator", layout="centered")

st.title("Weekly Report Generator")
st.write("Upload the weekly file and generate the final PDF.")


# -----------------------------
# Fixed file path (cloud safe)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXED_FILE_PATH = os.path.join(BASE_DIR, "fixed_file.xlsx")


# -----------------------------
# Upload weekly file
# -----------------------------
weekly_file = st.file_uploader(
    "Upload weekly file",
    type=["xlsx", "csv"]
)

generate = st.button("Generate PDF")


if generate:

    if weekly_file is None:
        st.error("Please upload weekly file")
        st.stop()

    # -----------------------------
    # Load fixed file
    # -----------------------------
    try:
        fixed_df = pd.read_excel(FIXED_FILE_PATH)
    except Exception as e:
        st.error("Unable to read fixed_file.xlsx")
        st.exception(e)
        st.stop()

    # -----------------------------
    # Load weekly file
    # -----------------------------
    try:
        if weekly_file.name.lower().endswith(".csv"):
            weekly_df = pd.read_csv(weekly_file)
        else:
            weekly_df = pd.read_excel(weekly_file)
    except Exception as e:
        st.error("Unable to read uploaded file")
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
