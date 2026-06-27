from datetime import datetime
from io import BytesIO
from textwrap import wrap

import fitz

from app.core.database import PromptScan


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 46
LINE_HEIGHT = 14


def _risk_color(level: str) -> tuple[float, float, float]:
    colors = {
        "Critical": (0.86, 0.15, 0.15),
        "High": (0.92, 0.35, 0.08),
        "Medium": (0.82, 0.55, 0.05),
        "Low": (0.15, 0.39, 0.92),
        "Safe": (0.13, 0.65, 0.33),
    }
    return colors.get(level, (0.25, 0.29, 0.36))


def _new_page(doc: fitz.Document, title: str = "") -> tuple[fitz.Page, float]:
    page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    page.draw_rect(fitz.Rect(0, 0, PAGE_WIDTH, 72), color=(0.05, 0.08, 0.14), fill=(0.05, 0.08, 0.14))
    page.insert_text((MARGIN, 42), "ShadowAI Guardian", fontsize=18, color=(1, 1, 1), fontname="helv")
    if title:
        page.insert_text((MARGIN, 96), title, fontsize=17, color=(0.05, 0.08, 0.14), fontname="helv")
        return page, 122
    return page, 96


def _write_wrapped(doc: fitz.Document, page: fitz.Page, y: float, text: str, *, size: int = 10, color=(0.15, 0.18, 0.24), width: int = 88) -> tuple[fitz.Page, float]:
    for paragraph in str(text or "").splitlines() or [""]:
        lines = wrap(paragraph, width=width) or [""]
        for line in lines:
            if y > PAGE_HEIGHT - MARGIN:
                page, y = _new_page(doc)
            page.insert_text((MARGIN, y), line, fontsize=size, color=color, fontname="helv")
            y += LINE_HEIGHT
        y += 3
    return page, y


def _section(doc: fitz.Document, page: fitz.Page, y: float, heading: str) -> tuple[fitz.Page, float]:
    if y > PAGE_HEIGHT - 80:
        page, y = _new_page(doc)
    page.insert_text((MARGIN, y), heading, fontsize=13, color=(0.05, 0.08, 0.14), fontname="helv")
    return page, y + 20


def build_scan_pdf(scan: PromptScan) -> bytes:
    doc = fitz.open()
    page, y = _new_page(doc, "Detailed Privacy Risk Report")

    risk_color = _risk_color(scan.risk_level)
    page.draw_rect(fitz.Rect(MARGIN, y, PAGE_WIDTH - MARGIN, y + 84), color=(0.88, 0.91, 0.95), fill=(0.97, 0.98, 1))
    page.insert_text((MARGIN + 16, y + 28), f"Risk Level: {scan.risk_level}", fontsize=17, color=risk_color, fontname="helv")
    page.insert_text((MARGIN + 16, y + 54), f"Risk Score: {scan.risk_score}/100", fontsize=12, color=(0.12, 0.16, 0.22), fontname="helv")
    page.insert_text((MARGIN + 210, y + 54), f"Category: {scan.category}", fontsize=12, color=(0.12, 0.16, 0.22), fontname="helv")
    y += 112

    page, y = _section(doc, page, y, "Scan Metadata")
    metadata = [
        ("Report generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")),
        ("Scan time", scan.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")),
        ("Source", scan.source_type),
        ("Prompt injection detected", "Yes" if scan.injection_detected else "No"),
        ("ML confidence", f"{scan.ml_confidence:.2f}" if scan.ml_confidence is not None else "N/A"),
    ]
    for label, value in metadata:
        page.insert_text((MARGIN, y), f"{label}:", fontsize=10, color=(0.39, 0.45, 0.55), fontname="helv")
        page.insert_text((MARGIN + 155, y), value, fontsize=10, color=(0.08, 0.11, 0.16), fontname="helv")
        y += 18
    y += 10

    page, y = _section(doc, page, y, "Executive Summary")
    summary = scan.explanation or "No AI-generated explanation was stored for this scan."
    page, y = _write_wrapped(doc, page, y, summary, size=10)
    y += 8

    page, y = _section(doc, page, y, "Detected Entities")
    if scan.entities:
        page.insert_text((MARGIN, y), "Type", fontsize=10, color=(0.39, 0.45, 0.55), fontname="helv")
        page.insert_text((MARGIN + 125, y), "Severity", fontsize=10, color=(0.39, 0.45, 0.55), fontname="helv")
        page.insert_text((MARGIN + 220, y), "Confidence", fontsize=10, color=(0.39, 0.45, 0.55), fontname="helv")
        page.insert_text((MARGIN + 310, y), "Redacted Value", fontsize=10, color=(0.39, 0.45, 0.55), fontname="helv")
        y += 16
        for entity in scan.entities:
            if y > PAGE_HEIGHT - 80:
                page, y = _new_page(doc)
            page.draw_line((MARGIN, y - 7), (PAGE_WIDTH - MARGIN, y - 7), color=(0.88, 0.91, 0.95))
            page.insert_text((MARGIN, y), entity.entity_type, fontsize=9, color=(0.08, 0.11, 0.16), fontname="helv")
            page.insert_text((MARGIN + 125, y), entity.severity, fontsize=9, color=_risk_color(entity.severity.capitalize()), fontname="helv")
            page.insert_text((MARGIN + 220, y), f"{entity.confidence:.2f}", fontsize=9, color=(0.08, 0.11, 0.16), fontname="helv")
            page, y = _write_wrapped(doc, page, y, entity.redacted_value, size=8, width=38)
            y += 4
    else:
        page, y = _write_wrapped(doc, page, y, "No sensitive entities were detected.", size=10)
    y += 8

    page, y = _section(doc, page, y, "Original Text Preview")
    preview = scan.original_text[:1800]
    if len(scan.original_text) > len(preview):
        preview += "\n\n[Preview truncated in PDF. Full text remains in the local SQLite database.]"
    page, y = _write_wrapped(doc, page, y, preview, size=9, color=(0.20, 0.24, 0.31), width=96)
    y += 8

    if scan.safe_text:
        page, y = _section(doc, page, y, "Safe Rewritten Version")
        page, y = _write_wrapped(doc, page, y, scan.safe_text, size=9, color=(0.08, 0.32, 0.18), width=96)
        y += 8

    page, y = _section(doc, page, y, "Recommendations")
    recommendations = [
        "Use the safe rewritten version before submitting content to external AI tools.",
        "Rotate any exposed API keys, passwords, database URLs, or tokens immediately.",
        "Remove personal identifiers unless they are strictly required for the task.",
        "Treat prompt injection warnings as blockers until reviewed by a human.",
        "Keep this report local unless sharing is explicitly approved.",
    ]
    for item in recommendations:
        page, y = _write_wrapped(doc, page, y, f"- {item}", size=10)

    page_count = doc.page_count
    for index, footer_page in enumerate(doc, start=1):
        footer_page.draw_line((MARGIN, PAGE_HEIGHT - 34), (PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 34), color=(0.88, 0.91, 0.95))
        footer_page.insert_text((MARGIN, PAGE_HEIGHT - 18), "ShadowAI Guardian - Local Privacy Report", fontsize=8, color=(0.39, 0.45, 0.55), fontname="helv")
        footer_page.insert_text((PAGE_WIDTH - 96, PAGE_HEIGHT - 18), f"Page {index} of {page_count}", fontsize=8, color=(0.39, 0.45, 0.55), fontname="helv")

    output = BytesIO()
    doc.save(output)
    doc.close()
    return output.getvalue()
