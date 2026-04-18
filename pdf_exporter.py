"""
PDF导出模块：生成审计重点提示函
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
import datetime
import os

# 注册中文字体
def register_fonts():
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("CJK", path))
                pdfmetrics.registerFont(TTFont("CJK-Bold", path))
                return "CJK"
            except Exception:
                continue
    return "Helvetica"  # fallback


RISK_COLORS = {
    "极高": colors.HexColor("#FF2D55"),
    "高":   colors.HexColor("#FF6B35"),
    "中":   colors.HexColor("#F5A623"),
    "低":   colors.HexColor("#34C759"),
}


def generate_pdf(analysis_result, company_name="星锰精密机械股份有限公司（脱敏）"):
    """生成审计重点提示函PDF，返回bytes"""
    font = register_fonts()
    bold_font = font  # 同一字体文件包含 bold

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    # 自定义样式
    title_style = ParagraphStyle("Title", fontName=font, fontSize=18, leading=26,
                                  alignment=TA_CENTER, spaceAfter=6, textColor=colors.HexColor("#1A1A2E"))
    subtitle_style = ParagraphStyle("Sub", fontName=font, fontSize=11, leading=16,
                                     alignment=TA_CENTER, spaceAfter=4, textColor=colors.HexColor("#666"))
    h2_style = ParagraphStyle("H2", fontName=font, fontSize=13, leading=20,
                               spaceBefore=16, spaceAfter=6, textColor=colors.HexColor("#1A1A2E"),
                               borderPad=4)
    body_style = ParagraphStyle("Body", fontName=font, fontSize=10, leading=16,
                                 spaceAfter=4, textColor=colors.HexColor("#333"))
    small_style = ParagraphStyle("Small", fontName=font, fontSize=9, leading=14,
                                  textColor=colors.HexColor("#666"))
    warning_style = ParagraphStyle("Warn", fontName=font, fontSize=9, leading=14,
                                    textColor=colors.HexColor("#999"), alignment=TA_CENTER)

    story = []
    now = datetime.datetime.now().strftime("%Y年%m月%d日")

    # ===== 封头 =====
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("AuditArc 审迹", ParagraphStyle("Brand", fontName=font, fontSize=11,
                             alignment=TA_CENTER, textColor=colors.HexColor("#0066CC"), spaceAfter=2)))
    story.append(Paragraph("AI 审计风险预警智能体", ParagraphStyle("BrandSub", fontName=font, fontSize=9,
                             alignment=TA_CENTER, textColor=colors.HexColor("#999"), spaceAfter=12)))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0066CC")))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("审计重点提示函", title_style))
    story.append(Paragraph(f"Audit Key Risk Alert Report", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDD")))
    story.append(Spacer(1, 0.4*cm))

    # 基本信息表
    info_data = [
        ["被审计单位", company_name, "报告日期", now],
        ["分析年度", "2023年度", "总体风险等级", analysis_result["overall_risk"]],
        ["识别风险项目", f"{len(analysis_result['risks'])} 项", "生成方式", "AI自动生成"],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 7.5*cm, 3*cm, 3.5*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F0F4FF")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#F0F4FF")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#DDD")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUND", (0,0), (-1,-1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # ===== AI免责声明 =====
    disclaimer = Table([[Paragraph(
        "⚠️  本报告由 AuditArc AI 智能体自动生成，仅供审计师参考，不构成最终审计意见。"
        "所有风险结论须经注册会计师专业判断复核确认后方可纳入工作底稿。",
        ParagraphStyle("D", fontName=font, fontSize=9, textColor=colors.HexColor("#8B4513"))
    )]], colWidths=[17*cm])
    disclaimer.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF8E1")),
        ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#F5A623")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(disclaimer)
    story.append(Spacer(1, 0.5*cm))

    # ===== 风险汇总 =====
    story.append(Paragraph("一、风险识别汇总", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#EEE")))
    story.append(Spacer(1, 0.2*cm))

    cnt = analysis_result["risk_count"]
    summary_data = [["风险等级", "数量", "说明"]]
    for level, desc in [
        ("极高", "需立即关注，优先安排审计资源"),
        ("高", "存在重大错报风险，需实施重点程序"),
        ("中", "存在一定风险，纳入常规审计范围"),
        ("低", "风险较小，关注即可"),
    ]:
        count = cnt.get(level, 0)
        if count > 0:
            summary_data.append([level, str(count), desc])

    sum_table = Table(summary_data, colWidths=[3*cm, 2*cm, 12*cm])
    sum_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1A1A2E")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#DDD")),
        ("ALIGN", (1,0), (1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    # 给风险等级行上色
    level_row_map = {"极高": colors.HexColor("#FFF0F3"), "高": colors.HexColor("#FFF4EF"),
                     "中": colors.HexColor("#FFFBF0"), "低": colors.HexColor("#F0FFF4")}
    for i, row in enumerate(summary_data[1:], 1):
        bg = level_row_map.get(row[0], colors.white)
        sum_table.setStyle(TableStyle([("BACKGROUND", (0,i), (-1,i), bg)]))
        text_color = RISK_COLORS.get(row[0], colors.black)
        sum_table.setStyle(TableStyle([("TEXTCOLOR", (0,i), (0,i), text_color)]))

    story.append(sum_table)
    story.append(Spacer(1, 0.5*cm))

    # ===== 各风险详情 =====
    story.append(Paragraph("二、风险详情与审计程序建议", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#EEE")))

    for i, risk in enumerate(analysis_result["risks"], 1):
        story.append(Spacer(1, 0.4*cm))
        level = risk["风险等级"]
        level_color = RISK_COLORS.get(level, colors.black)

        # 风险标题行
        title_data = [[
            Paragraph(f"风险 {i}：{risk['风险类型']}", ParagraphStyle(
                "RT", fontName=font, fontSize=11, textColor=colors.white)),
            Paragraph(f"【{level}风险】 {risk['最终评分']}分", ParagraphStyle(
                "RS", fontName=font, fontSize=10, textColor=colors.white, alignment=TA_RIGHT)),
        ]]
        title_t = Table(title_data, colWidths=[11*cm, 6*cm])
        title_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), level_color),
            ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (0,-1), 10), ("RIGHTPADDING", (-1,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(KeepTogether([title_t]))

        # 详情内容
        detail_rows = []
        detail_rows.append(["触发规则", risk.get("触发规则", "")])
        for k, v in risk.get("指标数据", {}).items():
            detail_rows.append([k, v])
        detail_rows.append(["业务合理性判断", risk.get("业务合理性判断", "")])
        detail_rows.append(["交叉验证结论", risk.get("交叉验证", "")])
        detail_rows.append(["准则依据", risk.get("准则依据", "")])

        detail_table = Table(
            [[Paragraph(r[0], ParagraphStyle("DK", fontName=font, fontSize=9, textColor=colors.HexColor("#555"))),
              Paragraph(r[1], body_style)] for r in detail_rows],
            colWidths=[3.5*cm, 13.5*cm]
        )
        detail_table.setStyle(TableStyle([
            ("FONTNAME", (0,0), (-1,-1), font),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#E0E0E0")),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F8F9FA")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(detail_table)

        # SHAP权重
        shap = risk.get("SHAP权重", {})
        if shap:
            shap_text = "  |  ".join([f"{k}：{v}%" for k, v in shap.items()])
            story.append(Paragraph(f"SHAP特征贡献：{shap_text}", small_style))

        # 建议程序
        procs = risk.get("建议审计程序", [])
        if procs:
            story.append(Spacer(1, 0.1*cm))
            story.append(Paragraph("建议审计程序：", ParagraphStyle(
                "PH", fontName=font, fontSize=9, textColor=colors.HexColor("#0066CC"), spaceBefore=4)))
            for j, p in enumerate(procs, 1):
                story.append(Paragraph(f"  {j}. {p}", small_style))

    # ===== 尾部 =====
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDD")))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "本提示函由 AuditArc 审迹 AI 系统自动生成 · 生成时间：" + now +
        " · 本结论由AI生成，需审计师复核确认后方可归档",
        warning_style
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
