from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

output_path = "/sessions/laughing-gifted-shannon/mnt/Job Assist/applications/waymo/bi-analyst-2026-04/cover-letter.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    topMargin=1*inch,
    bottomMargin=1*inch,
    leftMargin=1*inch,
    rightMargin=1*inch,
)

styles = getSampleStyleSheet()

header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=4, textColor=HexColor('#333333'))
date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=20, textColor=HexColor('#333333'))
greeting_style = ParagraphStyle('Greeting', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=12, textColor=HexColor('#1a1a1a'))
body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=12, textColor=HexColor('#1a1a1a'))
signature_style = ParagraphStyle('Signature', parent=styles['Normal'], fontSize=11, leading=16, spaceBefore=24, spaceAfter=0, textColor=HexColor('#1a1a1a'))
name_style = ParagraphStyle('Name', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=0, textColor=HexColor('#1a1a1a'))

story = []

# Contact header
story.append(Paragraph("Milan Sharma", ParagraphStyle('NameHeader', parent=header_style, fontSize=12, fontName='Helvetica-Bold')))
story.append(Paragraph("msharm406@gmail.com | linkedin.com/in/msharm/ | github.com/sharmingmilan", header_style))
story.append(Spacer(1, 12))
story.append(Paragraph("April 8, 2026", date_style))

# Greeting
story.append(Paragraph("Dear Hiring Team,", greeting_style))

# Body paragraphs
p1 = (
    'I\'m applying for the Business Intelligence Analyst role on the Product Data Science team. '
    'What drew me to this posting is the "design, define, and govern KPIs" language. That\'s not '
    'a standard BI analyst ask, and it describes the work I find most valuable. At Apple, I built '
    'KPI governance for procurement reporting from scratch: clarifying metric definitions, documenting '
    'them in Confluence, and maintaining a centralized data dictionary so multiple business lines could '
    'trust the same numbers. Waymo\'s measurement challenges are harder and the stakes are higher, '
    'which is exactly why I want to work on them.'
)

p2 = (
    'My career has centered on two things: building the measurement infrastructure that teams rely '
    'on to make decisions, and translating between technical and non-technical stakeholders so the '
    'right insights actually drive action. At Apple, that means owning a weekly ETL pipeline that '
    '12 people depend on while serving as primary BI liaison to executives. At Wells Fargo, I connected '
    'call center logs to SLA data in Redshift, enabling non-technical stakeholders to see exactly where '
    'customers dropped off the self-service funnel, reducing help desk call volume by 20%. At Disney, '
    'I proactively backfilled two years of missing vendor-reported sales data that later became the '
    'organization\'s only pre-pandemic baseline for measuring trends during COVID.'
)

p3 = (
    'The thread connecting these experiences is a bias toward getting the measurement right, even when '
    'there\'s pressure to ship a quick fix. At Apple, I pushed back when budget managers wanted to '
    'hardcode around a field mapping error, traced the root cause to an upstream naming change, and '
    'drove correction at the source. At Waymo, that instinct maps directly to a domain where measurement '
    'rigor isn\'t just good practice; it determines whether the car is driving safely. With Waymo tripling '
    'ride volume, expanding to 20+ cities, and building out reporting infrastructure in real time, I\'d '
    'welcome the chance to help shape that foundation.'
)

story.append(Paragraph(p1, body_style))
story.append(Paragraph(p2, body_style))
story.append(Paragraph(p3, body_style))

# Signature
story.append(Paragraph("Sincerely,", signature_style))
story.append(Paragraph("Milan", name_style))

doc.build(story)
print("Cover letter PDF generated successfully")
