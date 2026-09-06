"""ATS-safe HTML templates and content-aware layout helpers for resumes."""

from __future__ import annotations

from html import escape
from typing import Any

SECTION_ORDER = {
    "ats": ["summary", "skills", "education", "experience", "projects", "certifications", "achievements", "research", "leadership"],
    "modern": ["summary", "skills", "experience", "projects", "education", "certifications", "achievements", "research", "leadership"],
    "academic": ["education", "research", "projects", "skills", "experience", "certifications", "achievements", "leadership"],
}
SECTION_LABELS = {"summary": "Professional Summary", "skills": "Technical Skills", "education": "Education", "experience": "Experience", "projects": "Projects", "certifications": "Certifications", "achievements": "Achievements", "research": "Research & Publications", "leadership": "Leadership & Activities"}


class AdaptiveLayoutEngine:
    """Allocate table columns from measured text rather than fixed dimensions."""

    def column_widths(self, values: list[str], available: float, *, minimum: float = 90.0) -> list[float]:
        if not values:
            return []
        weights = [max(minimum, min(available * 0.72, 5.5 * max(len(value), 1))) for value in values]
        total = sum(weights)
        return weights if total <= available else [max(minimum, available * weight / total) for weight in weights]


layout_engine = AdaptiveLayoutEngine()


def _link(url: str) -> str:
    return f'<a href="{escape(url, quote=True)}">{escape(url)}</a>'


def _render_bullets(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items if item.strip())


def _render_section(key: str, data: Any) -> str:
    if not data:
        return ""
    heading = SECTION_LABELS[key]
    if key == "summary":
        return f"<section class='resume-section'><h2>{heading}</h2><p>{escape(str(data))}</p></section>"
    if key == "skills":
        rows = "".join(f"<tr><th>{escape(category)}:</th><td>{escape(', '.join(skills))}</td></tr>" for category, skills in data.items() if skills)
        return f"<section class='resume-section'><h2>{heading}</h2><table class='skills-table'>{rows}</table></section>" if rows else ""
    cards: list[str] = []
    for item in data:
        if not isinstance(item, dict):
            cards.append(f"<li>{escape(str(item))}</li>")
            continue
        title, meta = escape(str(item.get("title", ""))), escape(str(item.get("meta", "")))
        bullets = _render_bullets([str(value) for value in item.get("bullets", [])])
        links = " | ".join(_link(str(url)) for url in item.get("links", []) if str(url).startswith(("http://", "https://")))
        link_markup = f"<p class='links'>{links}</p>" if links else ""
        cards.append(f"<article class='entry'><div class='entry-heading'><strong>{title}</strong><span>{meta}</span></div><ul>{bullets}</ul>{link_markup}</article>")
    return f"<section class='resume-section'><h2>{heading}</h2>{''.join(cards)}</section>" if cards else ""


def render_resume_html(resume: dict[str, Any], template: str = "ats", section_order: list[str] | None = None, custom_styles: str = "") -> str:
    """Render a one-column, print-safe HTML intermediate representation."""
    candidate = resume.get("candidate", {})
    contacts = [candidate.get(key) for key in ("email", "phone", "location", "linkedin", "github", "portfolio") if candidate.get(key)]
    sections = resume.get("sections", {})
    order = section_order or SECTION_ORDER.get(template, SECTION_ORDER["ats"])
    rendered_sections = "\n".join(_render_section(key, sections.get(key)) for key in order)
    styles = """
@page{size:A4;margin:15mm 16mm}*{box-sizing:border-box}body{font-family:Helvetica,Arial,sans-serif;font-size:10pt;line-height:1.35;color:#172033;margin:0;max-width:178mm}h1{font-size:22pt;line-height:1.05;margin:0 0 5pt;color:#0f172a}.contact{font-size:9pt;overflow-wrap:anywhere;word-break:break-word}.resume-section{margin-top:12pt;break-inside:avoid-page}h2{font-size:12pt;text-transform:uppercase;letter-spacing:.35pt;margin:0 0 5pt;padding-bottom:2pt;border-bottom:1pt solid #334155;break-after:avoid-page}p{margin:0 0 4pt}.skills-table{width:100%;border-collapse:collapse;table-layout:auto}.skills-table th{width:22%;min-width:25mm;text-align:left;vertical-align:top;padding:1.5pt 6pt 1.5pt 0}.skills-table td{overflow-wrap:anywhere;word-break:break-word;padding:1.5pt 0}.entry{margin:0 0 7pt;break-inside:avoid-page}.entry-heading{display:flex;gap:8pt;justify-content:space-between;align-items:baseline}.entry-heading strong{font-size:10.2pt}.entry-heading span{font-size:9pt;text-align:right;overflow-wrap:anywhere}ul{margin:2pt 0 0 14pt;padding:0}li{margin:0 0 2pt;padding-left:1pt}.links{font-size:8.5pt;overflow-wrap:anywhere;word-break:break-word}@media print{.resume-section,.entry{break-inside:avoid}}
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(str(candidate.get('name') or 'Resume'))}</title><style>{styles}{custom_styles}</style></head><body><header><h1>{escape(str(candidate.get('name') or ''))}</h1><div class='contact'>{' | '.join(escape(str(value)) for value in contacts)}</div></header>{rendered_sections}</body></html>"
