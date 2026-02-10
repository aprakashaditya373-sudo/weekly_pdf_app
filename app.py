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

st.write("Upload the weekly file and generate the final PDF.")

# -----------------------------------
# Fixed file path
# -----------------------------------
FIXED_FILE_PATH = "fixed_file.xlsx"

# -----------------------------------
# Upload weekly file
# -----------------------------------
weekly_file = st.file_uploader(
    "Upload weekly file",
    type=["xlsx", "csv"]
)

generate = st.button("Generate PDF")

if generate:

    if weekly_file is None:
        st.error("Please upload weekly file")
        st.stop()

    # -----------------------------------
    # Load both files
    # -----------------------------------
    fixed_df = pd.read_excel(FIXED_FILE_PATH)

    if weekly_file.name.endswith(".csv"):
        weekly_df = pd.read_csv(weekly_file)
    else:
        weekly_df = pd.read_excel(weekly_file)

    # -----------------------------------
    # Your preprocessing
    # -----------------------------------
    final_df = run_preprocessing(fixed_df, weekly_df)

    # -----------------------------------
    # Build PDF
    # -----------------------------------
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("Analysis of members registered in MyTDP App", styles["Heading2"])
    elements.append(title)
    elements.append(Spacer(1, 10))

    table_data = [final_df.columns.tolist()] + final_df.values.tolist()

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
