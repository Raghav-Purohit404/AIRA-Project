"""Dependency-free PDF generation layer for resumes."""

from __future__ import annotations


class PDFService:
    """Generate minimal PDF bytes from text content.

    This layer can later be replaced with WeasyPrint or another renderer
    without changing route contracts.
    """

    def generate_pdf(self, html: str) -> dict[str, object]:
        """Return a minimal valid PDF payload containing resume text metadata."""
        text = " ".join(html.replace("<", " <").split())
        safe_text = text[:1200].replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 10 Tf 40 760 Td ({safe_text}) Tj ET"
        objects = [
            "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
            "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
            "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
            "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
            f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj",
        ]
        content = "%PDF-1.4\n" + "\n".join(objects) + "\n%%EOF"
        return {
            "success": True,
            "content_type": "application/pdf",
            "pdf_bytes": content.encode("latin-1"),
            "html_length": len(html),
        }
