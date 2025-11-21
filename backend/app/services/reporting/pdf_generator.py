"""
PDF Report Generator
Generates professional PDF reports for scan results
"""
import io
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.models.scan import Scan
from app.core.config import settings


class PDFReportGenerator:
    """Generates PDF reports for CodeRenew scans"""

    def __init__(self, scan: Scan):
        self.scan = scan
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Initialize custom styles"""
        self.styles.add(ParagraphStyle(
            name='Header1',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#1E3A8A')  # Dark Blue
        ))
        self.styles.add(ParagraphStyle(
            name='Header2',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#2563EB')  # Blue
        ))
        self.styles.add(ParagraphStyle(
            name='Normal_Small',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11
        ))

    def generate(self) -> bytes:
        """Generate the PDF report"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []

        # Title Page
        story.append(Paragraph(f"CodeRenew Compatibility Report", self.styles['Header1']))
        story.append(Spacer(1, 12))
        
        # Scan Info
        data = [
            ["Site URL:", self.scan.site.url if self.scan.site else "N/A"],
            ["Scan Date:", self.scan.created_at.strftime("%Y-%m-%d %H:%M")],
            ["WordPress Version:", f"{self.scan.wordpress_version_from} -> {self.scan.wordpress_version_to}"],
            ["Risk Level:", self.scan.risk_level.value.upper() if self.scan.risk_level else "UNKNOWN"],
            ["Total Issues:", str(len(self.scan.results))]
        ]
        
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#4B5563')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 30))

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['Header2']))
        summary_text = f"""
        This report analyzes the compatibility of your WordPress site when upgrading from version 
        {self.scan.wordpress_version_from} to {self.scan.wordpress_version_to}. 
        We found {len(self.scan.results)} issues that require attention.
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Issues List
        story.append(Paragraph("Detailed Findings", self.styles['Header2']))
        
        if not self.scan.results:
            story.append(Paragraph("No issues found! Your site appears to be compatible.", self.styles['Normal']))
        else:
            # Group by severity
            issues_data = [["Severity", "Type", "File", "Description"]]
            
            for result in self.scan.results:
                # Color code severity
                severity = result.severity.value if hasattr(result.severity, 'value') else str(result.severity)
                
                issues_data.append([
                    severity.upper(),
                    result.issue_type.replace('_', ' ').title(),
                    result.file_path.split('/')[-1] if result.file_path else "Unknown",
                    Paragraph(result.description, self.styles['Normal_Small'])
                ])

            t_issues = Table(issues_data, colWidths=[0.8*inch, 1.2*inch, 1.5*inch, 3*inch])
            t_issues.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E5E7EB')),
            ]))
            story.append(t_issues)

        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated by CodeRenew", self.styles['Normal_Small']))

        doc.build(story)
        self.buffer.seek(0)
        return self.buffer.getvalue()
