import io
import re
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate

from app.schemas.destination import PrepItemOut

TITLE_STYLE = ParagraphStyle("Title", fontName="Times-Bold", fontSize=22, leading=26, spaceAfter=4)
COUNTRY_STYLE = ParagraphStyle("Country", fontName="Times-Italic", fontSize=11, textColor="#555555", spaceAfter=16)
SECTION_STYLE = ParagraphStyle("Section", fontName="Times-Bold", fontSize=14, spaceBefore=12, spaceAfter=8)
RELEASE_STYLE = ParagraphStyle("Release", fontName="Times-Bold", fontSize=12, spaceAfter=6)
ITEM_STYLE = ParagraphStyle("Item", fontName="Times-Roman", fontSize=10.5, leading=14, spaceAfter=10)

SECTION_TITLES = {
    "general": "Documents & Bureaucracy",
    "specific": "Specific to This Permit",
    "good_to_know": "Good to Know",
    "custom": "My Own Notes",
}
SECTION_ORDER = ["general", "specific", "good_to_know", "custom"]


def safe_filename(name: str) -> str:
    """Content-Disposition filenames need to be ASCII-safe (or RFC 5987
    encoded) - simplest to just slugify rather than deal with encoding a
    destination name that might contain non-ASCII characters."""
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    return safe or "destination"


def build_checklist_pdf(
    *,
    name: str,
    country: str,
    next_known_release: datetime | None,
    items: list[PrepItemOut],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title=f"{name} checklist - SlotScout")
    # reportlab's Paragraph parses a small XML-like markup subset (<b>, <br/>,
    # etc.) - escape every dynamic string first, since one section (a user's
    # own custom checklist items) is arbitrary user-submitted text, and an
    # unescaped "<" or "&" in it would either break the markup parser or let
    # it inject formatting tags.
    story = [Paragraph(escape(name), TITLE_STYLE), Paragraph(escape(country), COUNTRY_STYLE)]

    if next_known_release:
        story.append(Paragraph(f"Next known release: {next_known_release.strftime('%B %d, %Y')}", RELEASE_STYLE))

    by_section: dict[str, list[PrepItemOut]] = {}
    for item in items:
        by_section.setdefault(item.section, []).append(item)

    for section_key in SECTION_ORDER:
        section_items = by_section.get(section_key)
        if not section_items:
            continue
        story.append(Paragraph(SECTION_TITLES[section_key], SECTION_STYLE))
        bullets = []
        for item in sorted(section_items, key=lambda i: i.order_index):
            marker = "[Required]" if item.is_required else "[Optional]"
            line = f"{marker} {escape(item.text)}"
            if item.link_url:
                line += f" &mdash; {escape(item.link_url)}"
            bullets.append(ListItem(Paragraph(line, ITEM_STYLE)))
        story.append(ListFlowable(bullets, bulletType="bullet"))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
