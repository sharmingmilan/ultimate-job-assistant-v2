from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT

output_path = "/sessions/laughing-gifted-shannon/mnt/Job Assist/applications/waymo/bi-analyst-2026-04/speaking-points.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    topMargin=0.7*inch,
    bottomMargin=0.7*inch,
    leftMargin=0.8*inch,
    rightMargin=0.8*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16, leading=20, spaceAfter=2, textColor=HexColor('#1a1a1a'))
subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9, leading=12, spaceAfter=12, textColor=HexColor('#666666'))
h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, leading=16, spaceBefore=16, spaceAfter=6, textColor=HexColor('#1a1a1a'))
body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6, textColor=HexColor('#222222'))
italic_style = ParagraphStyle('ItalicBody', parent=body_style, fontSize=9, leading=12, spaceAfter=2, textColor=HexColor('#555555'), leftIndent=12)
elevator_style = ParagraphStyle('Elevator', parent=body_style, fontSize=10, leading=15, spaceAfter=8, textColor=HexColor('#222222'), leftIndent=6, rightIndent=6)
point_body_style = ParagraphStyle('PointBody', parent=body_style, fontSize=10, leading=14, spaceAfter=3, leftIndent=6)

story = []

story.append(Paragraph("Waymo: Speaking Points", title_style))
story.append(Paragraph("Business Intelligence Analyst (Product Data Science) | Generated: 2026-04-08", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc'), spaceAfter=12))

story.append(Paragraph("Your Story in 30 Seconds", h2_style))
story.append(Paragraph(
    "I've spent 6+ years building the measurement infrastructure that teams depend on to make decisions, "
    "and translating between the technical and non-technical sides of the house so the right people trust "
    "the right numbers. At Apple, that meant defining KPIs across procurement, pushing back when field "
    "mappings broke downstream reporting, and building governance from scratch. At Waymo, the stakes are "
    "higher. Getting measurement right isn't just about better dashboards; it's about whether the car "
    "is driving safely. That's the version of this problem I want to work on.",
    elevator_style
))

story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e0e0e0'), spaceBefore=8, spaceAfter=8))

story.append(Paragraph("Speaking Points", h2_style))

points = [
    {
        "label": "Measurement rigor when it matters",
        "body": "At Apple, I discovered Spend FY/QTR fields weren't mapping correctly, cascading errors into LOB and function reporting. Budget managers wanted a hardcode fix. I pushed back, traced the root cause to an upstream naming change, and drove the correction at the source. At Waymo, that same instinct (fix the measurement, not the symptom) applies to safety-critical metrics where a shortcut could have real consequences.",
        "proof": "Apple data integrity pushback, upstream auditing initiative",
        "priority": 'Safety-first culture, "rigor over speed," transparency when data is ambiguous',
    },
    {
        "label": "KPI definition and governance, not just reporting",
        "body": "I don't just query existing metrics. I define them. At Apple, I clarified whether procurement KPIs should include all PRs generated vs. only finalized/pending, documented definitions in Confluence, and built a centralized data dictionary. Waymo's JD explicitly says \"design, define, and govern KPIs,\" and that's the work I've been doing.",
        "proof": "Apple KPI governance, Confluence documentation, Box data dictionary",
        "priority": '"Identify the right measurement for business performance," metric definition ownership',
    },
    {
        "label": "Bridging technical and non-technical worlds",
        "body": "Every role I've had involves translating between data and the people who use it. At Apple I serve as primary BI liaison to executives. At Wells Fargo I connected call center logs to SLA data so non-technical stakeholders could see exactly where customers dropped off. I present to leadership regularly and know how to frame a finding so it drives a decision, not just a conversation.",
        "proof": "Apple executive liaison, Wells Fargo self-service funnel analysis, Apple stakeholder redirection",
        "priority": '"Prepare content and communicate to Waymo leadership," cross-functional partnership',
    },
    {
        "label": "Building infrastructure, not just running reports",
        "body": "At Apple, I own a weekly ETL pipeline that 12 people depend on. At Pinterest, I designed pipelines centralizing real estate and people data into Snowflake. At Wells Fargo, I built pipeline architecture connecting call center data to SLA metrics. The Waymo JD says \"state of the art reporting infrastructure,\" which signals building something new. That's the kind of work I find most rewarding.",
        "proof": "Apple ETL ownership, Pinterest Snowflake pipelines, Wells Fargo Redshift architecture",
        "priority": '"Build and maintain state of the art reporting infrastructure to enable continuous decision making"',
    },
    {
        "label": "Proactive problem identification",
        "body": "At Disney, I noticed a gap in digital asset sales reporting. Vendors weren't reporting timely. I didn't wait for someone to ask. I backfilled 2+ years of missing data, and when COVID hit, that historical baseline became the only way the organization could measure trends against pre-pandemic performance. At Waymo, where the product is scaling to 20+ cities, I'd expect similar situations where the right measurement doesn't exist yet.",
        "proof": "Disney digital asset backfill, proactive gap identification",
        "priority": '"Data-driven, curious, open-minded," self-starters who identify needs before being asked',
    },
    {
        "label": "Analytical depth when the problem calls for it",
        "body": "I'm not just a pipeline builder. At Disney, I ran regression analysis using dimensional and relational modeling in Python to discover that digital assets sell better when bundled with a content release. That finding shifted how marketing planned campaigns. At Wells Fargo, funnel analysis on call center data reduced help desk volume 20%. I can do both: build the infrastructure and run the analysis.",
        "proof": "Disney regression analysis and bundling strategy, Wells Fargo funnel analysis (20% call reduction, 12% self-service increase)",
        "priority": '"Perform advanced analytical modelling as necessary to help drive the right decisions"',
    },
    {
        "label": "Establishing team practices and knowledge sharing",
        "body": "At both Apple and Wells Fargo, I partnered with directors to establish office hours and biweekly deep-dives on business processes. At Apple, I also built the team's GitHub, documented AI workflows, and lead training sessions. It's a pattern. I build the infrastructure for how the team works, not just the data infrastructure.",
        "proof": "Apple + Wells Fargo office hours, Apple AI initiative (GitHub, documentation, training)",
        "priority": 'Culture of intellectual curiosity, "open, curious, interdisciplinary, and critical minds"',
    },
]

for i, pt in enumerate(points, 1):
    story.append(Paragraph(f"<b>{i}. {pt['label']}</b>", point_body_style))
    story.append(Paragraph(pt['body'], point_body_style))
    story.append(Paragraph(f"<i>Your proof: {pt['proof']}</i>", italic_style))
    story.append(Paragraph(f"<i>Their priority: {pt['priority']}</i>", italic_style))
    story.append(Spacer(1, 6))

story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e0e0e0'), spaceBefore=8, spaceAfter=8))

story.append(Paragraph('If They Ask "Why Are You Leaving Your Current Role?"', h2_style))
story.append(Paragraph(
    "My Apple role is a contract that's ending soon. I've enjoyed the work, especially building KPI "
    "governance and leading the AI initiative, and now I'm looking for a permanent position where I can "
    "invest long-term in building out measurement infrastructure. Waymo is exactly that kind of opportunity.",
    body_style
))

story.append(Paragraph('If They Ask "Why Now?"', h2_style))
story.append(Paragraph(
    "Waymo is at an inflection point: tripling ride volume, expanding to 20+ cities, scaling from 3,000 "
    "vehicles. That means the data infrastructure needs to scale with it. The reporting and metrics that "
    "leadership depends on are being built right now, not maintained. I'd rather join when I can shape the "
    "foundation than after it's already set.",
    body_style
))

story.append(Paragraph('If They Ask "Why Waymo Specifically?"', h2_style))
story.append(Paragraph(
    "Every company says data quality matters. At Waymo, it's literal. The measurements your team builds "
    "determine whether the car is driving safely. I've spent my career caring about whether the right people "
    "trust the right numbers, from catching field mapping errors at Apple to backfilling missing baselines at "
    "Disney. The difference at Waymo is that the stakes match the level of rigor I naturally bring to the "
    "work. That's a rare alignment.",
    body_style
))

doc.build(story)
print("PDF generated successfully")
