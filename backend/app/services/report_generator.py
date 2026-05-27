from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.models.scan import Scan
from app.services.risk_engine import risk_label

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def generate_pdf_report(scan: Scan) -> str:
    path = REPORT_DIR / f"{scan.id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=f"Sentinel AI report {scan.id}")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Sentinel AI Security Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Target: {scan.normalized_target}", styles["Normal"]),
        Paragraph(f"Risk score: {scan.score}/100 - {risk_label(scan.score)}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("AI xulosa", styles["Heading2"]),
        Paragraph(scan.summary or "Xulosa mavjud emas.", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Topilmalar", styles["Heading2"]),
    ]

    rows = [["Severity", "Category", "Title", "Recommendation"]]
    for finding in scan.findings:
        rows.append(
            [
                finding.severity.value,
                finding.category,
                finding.title,
                finding.recommendation or "",
            ]
        )

    table = Table(rows, colWidths=[65, 80, 155, 210], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#162033")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B8C1D1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return str(path)

