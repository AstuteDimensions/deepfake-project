from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from xml.sax.saxutils import escape

from datetime import datetime
import os
import uuid
pdfmetrics.registerFont(
    TTFont("NotoSans", "fonts/NotoSans-Regular.ttf")
)

def generate_report(
    filename,
    is_fake,
    confidence,
    details,
    reverse_search=None
):

    # =====================================
    # REPORT FOLDER
    # =====================================

    report_folder = "assets/reports"

    os.makedirs(
        report_folder,
        exist_ok=True
    )

    report_path = os.path.join(
        report_folder,
        "DeepGuard_Analysis_Report.pdf"
    )


    # =====================================
    # REPORT INFORMATION
    # =====================================

    report_id = str(
        uuid.uuid4()
    )[:8].upper()

    generated_time = datetime.now().strftime(
        "%d %B %Y, %I:%M:%S %p"
    )


    # =====================================
    # REVERSE SEARCH DATA
    # =====================================

    if reverse_search is None:

        reverse_search = {
            "matches_found": 0,
            "digital_footprint": "UNAVAILABLE",
            "sources": []
        }


    matches_found = reverse_search.get(
        "matches_found",
        0
    )

    digital_footprint = reverse_search.get(
        "digital_footprint",
        "UNAVAILABLE"
    )

    sources = reverse_search.get(
        "sources",
        []
    )


    # =====================================
    # DOCUMENT
    # =====================================

    document = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )


    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "NotoSans"
    styles["Title"].fontName = "NotoSans"
    styles["Heading2"].fontName = "NotoSans"

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="NotoSans",
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=10
    )


    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontName="NotoSans",
        fontSize=13,
        alignment=TA_CENTER,
        spaceAfter=25
    )


    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName="NotoSans",
        fontSize=15,
        spaceBefore=15,
        spaceAfter=10
    )


    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="NotoSans",
        fontSize=10,
        leading=15
    )


    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontName="NotoSans",
        fontSize=8,
        leading=11
    )


    story = []


    # =====================================
    # TITLE
    # =====================================

    story.append(
        Paragraph(
            "DeepGuard AI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Deepfake Analysis Report",
            subtitle_style
        )
    )


    # =====================================
    # REPORT INFORMATION
    # =====================================

    story.append(
        Paragraph(
            "1. Report Information",
            heading_style
        )
    )


    report_info = [

        ["Report ID", report_id],

        ["Generated", generated_time],

        ["File Name", filename],

        ["Media Type", "Image"],

    ]


    table = Table(
        report_info,
        colWidths=[
            1.6 * inch,
            4.8 * inch
        ]
    )


    table.setStyle(
        TableStyle([

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND", (0, 0), (0, -1),
             colors.lightgrey),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            ("FONTNAME", (0, 0), (0, -1),
             "Helvetica-Bold"),

            ("FONTNAME", (1, 0), (1, -1),
             "Helvetica"),

            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("TOPPADDING", (0, 0), (-1, -1), 7),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),

        ])
    )


    story.append(table)

    story.append(
        Spacer(1, 15)
    )


    # =====================================
    # AI ANALYSIS
    # =====================================

    story.append(
        Paragraph(
            "2. AI Deepfake Analysis",
            heading_style
        )
    )


    status = (
        "DEEPFAKE DETECTED"
        if is_fake
        else
        "AUTHENTIC IMAGE"
    )


    analysis_info = [

        ["Analysis Result", status],

        ["Confidence", str(confidence)],

        ["AI Model", "EfficientNet-B0"],

        ["Face Detection / Preprocessing",
         "MTCNN"],

    ]


    table = Table(
        analysis_info,
        colWidths=[
            2.5 * inch,
            3.9 * inch
        ]
    )


    table.setStyle(
        TableStyle([

            ("GRID", (0, 0), (-1, -1),
             0.5, colors.grey),

            ("BACKGROUND", (0, 0), (0, -1),
             colors.lightgrey),

            ("FONTNAME", (0, 0), (0, -1),
             "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("VALIGN", (0, 0), (-1, -1),
             "TOP"),

            ("TOPPADDING", (0, 0), (-1, -1), 7),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),

        ])
    )


    story.append(table)

    story.append(
        Spacer(1, 15)
    )


    # =====================================
    # MODEL DETAILS
    # =====================================

    story.append(
        Paragraph(
            "3. Analysis Details",
            heading_style
        )
    )


    story.append(
        Paragraph(
            str(details),
            normal_style
        )
    )


    # =====================================
    # REVERSE IMAGE SEARCH
    # =====================================

    story.append(
        Paragraph(
            "4. Reverse Image Search",
            heading_style
        )
    )


    reverse_info = [

        ["Matches Found",
         str(matches_found)],

        ["Digital Footprint",
         str(digital_footprint)],

    ]


    table = Table(
        reverse_info,
        colWidths=[
            2.5 * inch,
            3.9 * inch
        ]
    )


    table.setStyle(
        TableStyle([

            ("GRID", (0, 0), (-1, -1),
             0.5, colors.grey),

            ("BACKGROUND", (0, 0), (0, -1),
             colors.lightgrey),

            ("FONTNAME", (0, 0), (0, -1),
             "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("TOPPADDING", (0, 0), (-1, -1), 7),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),

        ])
    )


    story.append(table)

    story.append(
        Spacer(1, 15)
    )


    # =====================================
    # ONLINE SOURCES
    # =====================================

    story.append(
        Paragraph(
            "5. Online Sources",
            heading_style
        )
    )


    if sources:

        for index, source in enumerate(
            sources,
            start=1
        ):

            title = source.get(
                "title",
                "Unknown"
            )

            source_name = source.get(
                "source",
                "Unknown"
            )

            link = source.get(
                "link",
                ""
            )


            story.append(
                Paragraph(
                    f"<b>{index}. {title}</b>",
                    normal_style
                )
            )


            story.append(
                Paragraph(
                    f"Source: {source_name}",
                    small_style
                )
            )


            if link:

                story.append(
                    Paragraph(
                        f'<link href="{link}" color="blue">'
                        f'{link}'
                        f'</link>',
                        small_style
                    )
                )


            story.append(
                Spacer(1, 10)
            )


    else:

        story.append(
            Paragraph(
                "No matching online sources were found.",
                normal_style
            )
        )


    # =====================================
    # INTERPRETATION
    # =====================================

    story.append(
        Paragraph(
            "6. Interpretation",
            heading_style
        )
    )


    if is_fake:

        interpretation = (
            "The AI model classified the submitted image "
            "as potentially manipulated or synthetically generated. "
            "The confidence value represents the model's prediction "
            "for the analyzed image."
        )

    else:

        interpretation = (
            "The AI model classified the submitted image "
            "as authentic based on the visual characteristics "
            "identified during analysis."
        )


    story.append(
        Paragraph(
            interpretation,
            normal_style
        )
    )


    story.append(
        Spacer(1, 15)
    )


    # =====================================
    # LIMITATIONS
    # =====================================

    story.append(
        Paragraph(
            "7. Limitations",
            heading_style
        )
    )


    limitation = (
        "AI-based deepfake detection is probabilistic and "
        "should not be treated as absolute proof of authenticity "
        "or manipulation. Reverse image search results indicate "
        "online pages containing matching or visually similar "
        "images; they do not by themselves establish the original "
        "source or ownership of an image."
    )


    story.append(
        Paragraph(
            limitation,
            normal_style
        )
    )


    # =====================================
    # FOOTER
    # =====================================

    story.append(
        Spacer(1, 25)
    )


    story.append(
        Paragraph(
            "Generated by DeepGuard AI Deepfake Detection Platform",
            small_style
        )
    )


    # =====================================
    # BUILD PDF
    # =====================================

    document.build(
        story
    )


    return report_path