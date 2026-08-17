"""
Convert Markdown report to PDF with proper formatting and page numbers
"""
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
from html.parser import HTMLParser

class MarkdownHTMLParser(HTMLParser):
    """Parse HTML generated from markdown and convert to reportlab elements"""

    def __init__(self):
        super().__init__()
        self.story = []
        self.current_tag = []
        self.current_data = []
        self.table_data = []
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Times-Bold'
        ))

        # Heading styles
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=10,
            spaceBefore=20,
            fontName='Times-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=8,
            spaceBefore=16,
            fontName='Times-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Times-Bold'
        ))

        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName='Times-Roman'
        ))

        # Code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            backColor=colors.HexColor('#f5f5f5'),
            fontName='Courier'
        ))

    def handle_starttag(self, tag, attrs):
        self.current_tag.append(tag)

        if tag == 'table':
            self.in_table = True
            self.table_data = []
        elif tag == 'tr':
            self.in_row = True
            self.table_data.append([])
        elif tag in ('td', 'th'):
            self.in_cell = True
            self.current_data.append('')

    def handle_endtag(self, tag):
        if not self.current_tag:
            return

        self.current_tag.pop()

        if tag == 'table':
            self.in_table = False
            if self.table_data:
                self._add_table()
        elif tag == 'tr':
            self.in_row = False
        elif tag in ('td', 'th'):
            self.in_cell = False
            if self.current_data:
                cell_text = self.current_data.pop()
                if self.table_data:
                    self.table_data[-1].append(cell_text)
        elif tag in ('h1', 'h2', 'h3', 'h4'):
            text = ''.join(self.current_data)
            self.current_data = []
            if text.strip():
                if tag == 'h1':
                    self.story.append(Paragraph(text, self.styles['CustomTitle']))
                elif tag == 'h2':
                    self.story.append(Paragraph(text, self.styles['CustomHeading1']))
                elif tag == 'h3':
                    self.story.append(Paragraph(text, self.styles['CustomHeading2']))
                else:
                    self.story.append(Paragraph(text, self.styles['CustomHeading3']))
        elif tag == 'p':
            text = ''.join(self.current_data)
            self.current_data = []
            if text.strip():
                # Handle inline code
                text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="9">\1</font>', text)
                self.story.append(Paragraph(text, self.styles['CustomBody']))
        elif tag == 'code':
            if not self.in_cell:
                code_text = ''.join(self.current_data)
                self.current_data = []
                if code_text.strip():
                    self.story.append(Paragraph(code_text, self.styles['CustomCode']))

    def handle_data(self, data):
        if self.in_cell:
            if self.current_data:
                self.current_data[-1] += data
        else:
            self.current_data.append(data)

    def _add_table(self):
        """Add table to story"""
        if not self.table_data:
            return

        # Create table
        table = Table(self.table_data)

        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 12))

def convert_markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF"""

    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

    # Parse HTML and build story
    parser = MarkdownHTMLParser()
    parser.feed(html_content)
    story = parser.story

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    # Build PDF
    doc.build(story)

    print(f'PDF generated: {pdf_file}')

if __name__ == '__main__':
    convert_markdown_to_pdf(
        'TS Liu Xianpeng REPORT.md',
        'TS_Liu_Xianpeng_REPORT.pdf'
    )
