"""HTML template rendering for structured resumes."""

from __future__ import annotations

from html import escape
from typing import Any


def _render_list(items: list[str]) -> str:
    """Render a list of strings as HTML list items."""
    return "".join(f"<li>{escape(str(item))}</li>" for item in items)


SECTION_ORDER = {
    "ats": ["summary", "education", "skills", "projects", "internships", "achievements"],
    "modern": ["summary", "skills", "projects", "internships", "achievements", "education"],
    "academic": ["education", "achievements", "projects", "skills", "internships"],
}


def render_section(title: str, items: list[str]) -> str:
    """Render a resume section."""
    if not items:
        return ""
    return f"<section><h2>{escape(title)}</h2><ul>{_render_list(items)}</ul></section>"


def render_resume_html(
    resume: dict[str, Any],
    template: str = "ats",
    section_order: list[str] | None = None,
    custom_styles: str = "",
) -> str:
    """Render structured resume JSON into an HTML document."""
    candidate = resume.get("candidate", {})
    sections = resume.get("sections", {})
    ordered_sections = section_order or SECTION_ORDER.get(template, SECTION_ORDER["ats"])
    rendered_sections = "\n".join(
        render_section(section.replace("_", " ").title(), [str(item) for item in sections.get(section, [])])
        for section in ordered_sections
    )
    completeness = resume.get("profile_completeness", 0)
    base_styles = """
body{font-family:Arial,sans-serif;line-height:1.45;color:#1f2937;margin:32px;max-width:820px}
h1{font-size:28px;margin:0 0 4px} h2{font-size:16px;margin:22px 0 8px;border-bottom:1px solid #d1d5db}
p{margin:4px 0 12px} ul{margin-top:4px} li{margin-bottom:4px}
.meta{color:#4b5563}.completeness{font-size:12px;color:#6b7280}
"""
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>{escape(str(candidate.get("name", "Resume")))}</title><style>{base_styles}{custom_styles}</style></head>
<body>
  <h1>{escape(str(candidate.get("name", "")))}</h1>
  <p class="meta">{escape(str(candidate.get("email", "")))} | {escape(str(candidate.get("phone", "")))}</p>
  <p class="completeness">Profile completeness: {escape(str(completeness))}%</p>
  {rendered_sections}
</body>
</html>"""
