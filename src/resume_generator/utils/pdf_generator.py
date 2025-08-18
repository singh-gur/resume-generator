"""PDF generation utilities for cover letters and resumes."""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer

from resume_generator.models.schemas import GeneratedCoverLetter


class CoverLetterPDFGenerator:
    """Generate professional PDF cover letters."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF."""
        # Header style for name
        self.styles.add(
            ParagraphStyle(
                name="HeaderName",
                parent=self.styles["Heading1"],
                fontSize=18,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=6,
                alignment=0,  # Left align
            )
        )

        # Contact info style
        self.styles.add(
            ParagraphStyle(
                name="ContactInfo",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=12,
                alignment=0,
            )
        )

        # Job info style
        self.styles.add(
            ParagraphStyle(
                name="JobInfo",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=12,
                spaceBefore=12,
                alignment=0,
            )
        )

        # Date style
        self.styles.add(
            ParagraphStyle(
                name="DateStyle",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#7F8C8D"),
                spaceAfter=18,
                alignment=2,  # Right align
            )
        )

        # Body text style
        self.styles.add(
            ParagraphStyle(
                name="BodyText",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=12,
                spaceBefore=6,
                leading=16,
                alignment=4,  # Justify
            )
        )

        # Signature style
        self.styles.add(
            ParagraphStyle(
                name="Signature",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=6,
                spaceBefore=24,
                alignment=0,
            )
        )

    def generate_pdf(self, cover_letter: GeneratedCoverLetter, output_path: str) -> str:
        """Generate a PDF cover letter and return the output path."""
        doc = BaseDocTemplate(
            str(output_path),
            pagesize=letter,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )

        # Create frame for content
        frame = Frame(
            1 * inch,  # left margin
            0.75 * inch,  # bottom margin
            6.5 * inch,  # width
            9.5 * inch,  # height
            topPadding=0,
            bottomPadding=0,
            leftPadding=0,
            rightPadding=0,
        )

        # Create page template
        template = PageTemplate(id="normal", frames=[frame])
        doc.addPageTemplates([template])

        # Build content
        story = self._build_story(cover_letter)

        # Generate PDF
        doc.build(story)
        return str(output_path)

    def _build_story(self, cover_letter: GeneratedCoverLetter) -> list:
        """Build the story (content) for the PDF."""
        story = []
        user_profile = cover_letter.user_profile
        job_desc = cover_letter.job_description

        # Add header section
        story.extend(self._build_header_section(user_profile))

        # Add date and job info
        story.extend(self._build_job_section(job_desc))

        # Add cover letter body
        story.extend(self._build_body_section(cover_letter))

        # Add signature and footer
        story.extend(self._build_footer_section(user_profile, cover_letter))

        return story

    def _build_header_section(self, user_profile) -> list:
        """Build the header section with name and contact info."""
        elements = []

        # Header with name
        elements.append(Paragraph(user_profile.full_name, self.styles["HeaderName"]))

        # Contact information
        contact_parts = []
        if user_profile.contact_info.email:
            contact_parts.append(user_profile.contact_info.email)
        if user_profile.contact_info.phone:
            contact_parts.append(user_profile.contact_info.phone)
        if user_profile.contact_info.location:
            contact_parts.append(user_profile.contact_info.location)

        if contact_parts:
            contact_text = " | ".join(contact_parts)
            elements.append(Paragraph(contact_text, self.styles["ContactInfo"]))

        # LinkedIn and portfolio on second line if available
        online_parts = []
        if user_profile.contact_info.linkedin:
            online_parts.append(f"LinkedIn: {user_profile.contact_info.linkedin}")
        if user_profile.contact_info.portfolio:
            online_parts.append(f"Portfolio: {user_profile.contact_info.portfolio}")
        if user_profile.contact_info.github:
            online_parts.append(f"GitHub: {user_profile.contact_info.github}")

        if online_parts:
            online_text = " | ".join(online_parts)
            elements.append(Paragraph(online_text, self.styles["ContactInfo"]))

        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def _build_job_section(self, job_desc) -> list:
        """Build the job information section."""
        elements = []

        # Date
        current_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(current_date, self.styles["DateStyle"]))

        # Job information
        job_title = f"Re: {job_desc.title}"
        if job_desc.company:
            job_title += f" at {job_desc.company}"
        elements.append(Paragraph(job_title, self.styles["JobInfo"]))

        return elements

    def _build_body_section(self, cover_letter) -> list:
        """Build the cover letter body section."""
        elements = []

        # Cover letter body - split into paragraphs
        cover_letter_text = cover_letter.cover_letter_content.strip()
        paragraphs = [p.strip() for p in cover_letter_text.split("\n\n") if p.strip()]

        for paragraph in paragraphs:
            if paragraph:
                elements.append(Paragraph(paragraph, self.styles["BodyText"]))

        return elements

    def _build_footer_section(self, user_profile, cover_letter) -> list:
        """Build the signature and footer section."""
        elements = []

        # Signature
        elements.append(Paragraph("Sincerely,", self.styles["Signature"]))
        elements.append(Paragraph(user_profile.full_name, self.styles["Signature"]))

        # Add match percentage as a footer note (small and subtle)
        elements.append(Spacer(1, 0.3 * inch))
        match_text = f"<font size='8' color='#95A5A6'>Job Match: {cover_letter.match_percentage:.1f}%</font>"
        elements.append(Paragraph(match_text, self.styles["Normal"]))

        return elements


def generate_cover_letter_pdf(cover_letter: GeneratedCoverLetter, output_path: str | Path) -> str:
    """
    Generate a well-formatted PDF cover letter.

    Args:
        cover_letter: GeneratedCoverLetter object containing the data
        output_path: Path where the PDF should be saved

    Returns:
        str: Path to the generated PDF file
    """
    generator = CoverLetterPDFGenerator()
    return generator.generate_pdf(cover_letter, str(output_path))
