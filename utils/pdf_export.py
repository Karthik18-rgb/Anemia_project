from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import red, orange, green, black
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Image, Paragraph
from reportlab.lib.units import cm
import pandas as pd
from io import BytesIO
from datetime import datetime

def risk_color(value):
    try:
        v = float(value)
        if v >= 80:
            return red
        elif v >= 60:
            return orange
        else:
            return green
    except:
        return black  

def generate_pdf(results_df: pd.DataFrame, patient_id = None, chart_path=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Anemia Risk Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))

    if patient_id is not None:
        story.append(Paragraph(f"Patient ID: {patient_id}", styles["Normal"]))
    story.append(Spacer(1, 12))

    data = [list(results_df.columns)]
    for _, row in results_df.iterrows():
        data.append([str(x) for x in row.values])

    table = Table(data, repeatRows=1)

    style = TableStyle([
        ("BACKGROUND", (0,0), (-1, 0), "#DDDDDD"),
        ("GRID", (0,0), (len(data[0])-1, len(data)-1),1,black),
        ("ALIGN", (0,0), (-1, 0), "CENTER"),
        ("VALIGN", (0,0), (-1, -1), "MIDDLE"),
    ])    

    if "Risk Probability (%)" in results_df.columns:
        risk_col_index = results_df.columns.get_loc("Risk Probability (%)")
        for row_idx in range(1, len(data)):
            value = data[row_idx][risk_col_index]
            style.add(
                "TEXTCOLOR",
                (risk_col_index, row_idx),
                (risk_col_index, row_idx),
                risk_color(value)
            )

    table.setStyle(style)
    story.append(table)

    story.append(Spacer(1, 12))

    if chart_path:
        story.append(Paragraph("Risk Trend Chart", styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Image(chart_path, width=16*cm, height=9*cm))
    doc.build(story)        
    
    buffer.seek(0)
    return buffer