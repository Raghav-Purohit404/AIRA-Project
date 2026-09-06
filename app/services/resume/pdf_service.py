"""Machine-readable PDF rendering for the resume HTML intermediate and projection."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
from typing import Any

from app.services.resume.template_engine import SECTION_LABELS, SECTION_ORDER, layout_engine
from app.utils.file_manager import resolve_safe_path


class PDFService:
    """Render ATS-safe, selectable-text PDFs using ReportLab flowable layout."""

    def generate_pdf(self, html: str, resume: dict[str, Any] | None = None, output_path: str | Path | None = None) -> dict[str, object]:
        """Render the HTML intermediate's grounded projection to PDF bytes and optional artifact."""
        try:
            payload = self._render(resume or self._resume_from_html(html))
        except ImportError as exc:  # pragma: no cover - installation concern, not layout logic
            raise RuntimeError("PDF rendering requires the 'reportlab' package.") from exc
        artifact: Path | None = None
        if output_path is not None:
            target = Path(output_path)
            artifact = resolve_safe_path(target.parent, target.name)
            artifact.write_bytes(payload)
        return {"success": True, "content_type": "application/pdf", "pdf_bytes": payload, "pdf_path": str(artifact) if artifact else None, "html_length": len(html)}

    def _render(self, resume: dict[str, Any]) -> bytes:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_RIGHT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm, title=str(resume.get("candidate", {}).get("name", "Resume")))
        styles = getSampleStyleSheet()
        name_style = ParagraphStyle("ResumeName", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=21, leading=23, textColor=HexColor("#0f172a"), spaceAfter=4)
        contact_style = ParagraphStyle("Contact", parent=styles["Normal"], fontName="Helvetica", fontSize=8.7, leading=11, textColor=HexColor("#334155"), spaceAfter=7, wordWrap="CJK")
        section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=HexColor("#172033"), spaceBefore=8, spaceAfter=4, keepWithNext=True)
        title_style = ParagraphStyle("EntryTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=12)
        meta_style = ParagraphStyle("EntryMeta", parent=styles["Normal"], fontName="Helvetica", fontSize=8.7, leading=11, alignment=TA_RIGHT, wordWrap="CJK")
        body_style = ParagraphStyle("EntryBody", parent=styles["Normal"], fontName="Helvetica", fontSize=9.4, leading=12, leftIndent=9, firstLineIndent=-6, bulletIndent=0, wordWrap="CJK")
        normal_style = ParagraphStyle("ResumeNormal", parent=styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=12, wordWrap="CJK")
        link_style = ParagraphStyle("Link", parent=normal_style, fontSize=8.2, leading=10, textColor=HexColor("#1d4ed8"), wordWrap="CJK")
        story: list[Any] = []
        candidate = resume.get("candidate", {})
        story.append(Paragraph(self._escape(str(candidate.get("name", ""))), name_style))
        contacts = [str(candidate[key]) for key in ("email", "phone", "location", "linkedin", "github", "portfolio") if candidate.get(key)]
        if contacts:
            story.append(Paragraph(self._escape(" | ".join(contacts)), contact_style))
        for key in SECTION_ORDER["ats"]:
            data = resume.get("sections", {}).get(key)
            if not data:
                continue
            story.append(Paragraph(SECTION_LABELS[key], section_style))
            if key == "summary":
                story.append(Paragraph(self._escape(str(data)), normal_style))
                continue
            if key == "skills":
                story.append(self._skills_table(data, doc.width, normal_style, Paragraph, Table, TableStyle, HexColor))
                continue
            for entry in data:
                title = Paragraph(self._escape(str(entry.get("title", ""))), title_style)
                meta = Paragraph(self._escape(str(entry.get("meta", ""))), meta_style)
                widths = layout_engine.column_widths([str(entry.get("title", "")), str(entry.get("meta", ""))], doc.width, minimum=72)
                if len(widths) == 2:
                    widths = [min(max(doc.width * .48, widths[0]), doc.width * .72), 0]
                    widths[1] = doc.width - widths[0]
                heading = Table([[title, meta]], colWidths=widths or [doc.width], hAlign="LEFT")
                heading.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
                entry_flowables: list[Any] = [heading]
                for bullet in entry.get("bullets", []):
                    entry_flowables.append(Paragraph(self._escape(str(bullet)), body_style, bulletText="•"))
                for url in entry.get("links", []):
                    if str(url).startswith(("http://", "https://")):
                        safe = self._escape(str(url))
                        entry_flowables.append(Paragraph(f'<link href="{safe}">{safe}</link>', link_style))
                # Keep a heading with its first evidence line, but permit unusually long
                # evidence to flow naturally to later pages instead of clipping it.
                if len(entry_flowables) > 1:
                    story.append(KeepTogether(entry_flowables[:2]))
                    story.extend(entry_flowables[2:])
                else:
                    story.extend(entry_flowables)
                story.append(Spacer(1, 3))
        doc.build(story)
        return buffer.getvalue()

    def _skills_table(self, skills: dict[str, list[str]], available: float, style: Any, paragraph_type: Any, table_type: Any, table_style: Any, color: Any) -> Any:
        rows = [[paragraph_type(f"<b>{self._escape(category)}:</b>", style), paragraph_type(self._escape(", ".join(values)), style)] for category, values in skills.items() if values]
        left = max(85, min(available * .30, max((len(category) * 5.5 for category in skills), default=85)))
        table = table_type(rows, colWidths=[left, available - left], repeatRows=0, hAlign="LEFT")
        table.setStyle(table_style([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LINEBELOW", (0, -1), (-1, -1), .25, color("#dbe3ee"))]))
        return table

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

    @staticmethod
    def _resume_from_html(html: str) -> dict[str, Any]:
        """Compatibility fallback for legacy callers that only supply HTML."""
        text = re.sub(r"<[^>]+>", " ", html)
        text = " ".join(text.split())
        return {"candidate": {"name": "Resume"}, "sections": {"summary": text}}
