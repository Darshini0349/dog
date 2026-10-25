"""
Project 3 (APIs/Automation): PDF Generator
Generates a professional PDF invoice from structured data — fully real,
no network needed. Produces an actual .pdf file you can open.

Run: pip install reportlab
     python 03_pdf_generator.py

Concepts practiced: programmatic document generation with reportlab
(tables, styles, computed totals), turning structured Python data into a
polished business document — a very common automation task.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from datetime import date


INVOICE = {
    "invoice_no": "INV-2026-0042",
    "date": str(date.today()),
    "from": {"name": "Darshini N — Freelance Dev", "email": "hello@example.com"},
    "to": {"name": "Acme Corp", "address": "12 Business Park, Bengaluru"},
    "items": [
        {"desc": "Backend API development (40 hrs)", "qty": 40, "rate": 1500},
        {"desc": "Database design & optimization", "qty": 10, "rate": 1800},
        {"desc": "Deployment & CI setup", "qty": 8, "rate": 1600},
    ],
    "tax_rate": 0.18,  # 18% GST
}


def build_invoice(data, path):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            topMargin=25 * mm, bottomMargin=25 * mm,
                            leftMargin=20 * mm, rightMargin=20 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=24, spaceAfter=6)
    elements = []

    # Header
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Paragraph(f"#{data['invoice_no']} &nbsp;&nbsp;|&nbsp;&nbsp; {data['date']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # From / To
    elements.append(Paragraph(f"<b>From:</b> {data['from']['name']} ({data['from']['email']})", styles["Normal"]))
    elements.append(Paragraph(f"<b>To:</b> {data['to']['name']}, {data['to']['address']}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Line items table
    table_data = [["Description", "Qty", "Rate", "Amount"]]
    subtotal = 0
    for item in data["items"]:
        amount = item["qty"] * item["rate"]
        subtotal += amount
        table_data.append([
            item["desc"], str(item["qty"]),
            f"Rs {item['rate']:,}", f"Rs {amount:,}"
        ])

    tax = subtotal * data["tax_rate"]
    total = subtotal + tax
    table_data.append(["", "", "Subtotal", f"Rs {subtotal:,.0f}"])
    table_data.append(["", "", f"Tax ({data['tax_rate']*100:.0f}%)", f"Rs {tax:,.0f}"])
    table_data.append(["", "", "TOTAL", f"Rs {total:,.0f}"])

    table = Table(table_data, colWidths=[85 * mm, 20 * mm, 30 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -4), 0.5, colors.grey),
        ("LINEABOVE", (2, -1), (-1, -1), 1, colors.black),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -4), [colors.white, colors.HexColor("#f5f6fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("<i>Thank you for your business!</i>", styles["Normal"]))

    doc.build(elements)
    return subtotal, tax, total


def main():
    print("=== PDF Invoice Generator ===")
    path = "invoice.pdf"
    subtotal, tax, total = build_invoice(INVOICE, path)
    print(f"Invoice {INVOICE['invoice_no']} generated:")
    print(f"  Subtotal: Rs {subtotal:,.0f}")
    print(f"  Tax:      Rs {tax:,.0f}")
    print(f"  Total:    Rs {total:,.0f}")
    print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()