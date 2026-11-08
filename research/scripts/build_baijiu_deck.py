#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""白酒竞争格局分析 PPTX 生成脚本（2026-10-09）"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# ---------- palette / design tokens ----------
NAVY = RGBColor(0x1F, 0x38, 0x64)
RED = RGBColor(0xC0, 0x00, 0x00)
GRAY = RGBColor(0x59, 0x59, 0x59)
LGRAY = RGBColor(0xED, 0xED, 0xED)
MGRAY = RGBColor(0xD9, 0xD9, 0xD9)
GOLD = RGBColor(0xBF, 0x90, 0x00)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

# ---------- helpers ----------
def new_slide():
    return prs.slides.add_slide(BLANK)

def tb(slide, x, y, w, h, text, size=14, bold=False, color=GRAY,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, wrap=True, italic=False):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = FONT
    return box

def bullets(slide, x, y, w, h, items, size=14, color=GRAY, gap=6):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        if isinstance(it, tuple):
            txt, b, c = (it + (color,))[:3]
        else:
            txt, b, c = it, False, color
        r = p.add_run()
        r.text = txt
        r.font.size = Pt(size)
        r.font.bold = b
        r.font.color.rgb = c
        r.font.name = FONT
    return box

def rect(slide, x, y, w, h, fill=NAVY, line=None, shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp

def footer(slide, idx, source):
    tb(slide, Inches(0.4), Inches(7.1), Inches(11.6), Inches(0.3),
       source, size=9, color=GRAY)
    tb(slide, Inches(12.5), Inches(7.1), Inches(0.5), Inches(0.3),
       str(idx), size=9, color=GRAY, align=PP_ALIGN.RIGHT)

def content_slide(title, source):
    s = new_slide()
    rect(s, 0, 0, Inches(13.333), Inches(0.88), NAVY)
    tb(s, Inches(0.4), Inches(0.1), Inches(12.5), Inches(0.68), title,
       size=28, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    return s

def style_cell(cell, text, size=12, bold=False, color=GRAY, fill=None,
               align=PP_ALIGN.LEFT):
    cell.text = ""
    p = cell.text_frame.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = FONT
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.05)
    cell.margin_right = Inches(0.05)
    cell.margin_top = Inches(0.02)
    cell.margin_bottom = Inches(0.02)
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill

# ---------- data ----------
# (name, code, rev亿, rev_yoy, profit亿, profit_yoy, gross, pe, pb,
#  mcap亿, div, payout, tier, price_note, inv_note, strength, weakness, strategy)
D = [
 ("贵州茅台", "600519.SH", 907.0, 1.5, 445.2, -2.0, 89.6, 19.4, 6.29, 15828, 3.77, 79.0,
  "超高端", "批价 1715（节后回落，此前 1730+）", "库存不足两周，全行业最健康",
  ["品牌无可替代，批价锚定全行业", "渠道库存 <2 周，动销最稳", "分红率 79%，股息 3.77%"],
  ["上市以来净利罕见同比 -2.0%", "批价自高位一路下行，i茅台提价对冲有限", "绝对市值大，弹性弱于次高端"],
  "i茅台零售价上调至 1639 元；回购注销 + 系列酒放量"),
 ("五粮液", "000858.SZ", 284.2, 20.9, 87.5, 89.3, 80.3, 20.8, 2.30, 2726, 4.87, 223.5,
  "高端", "八代批价 770+，流速明显加快", "库存低位，动销正增长",
  ["八代流速加快，逆势抢回份额", "2026H1 营收 +20.9%，七家唯一高增", "股息率 4.87%（含特别分红）"],
  ["净利 +89.3% 含低基数因素，勿线性外推", "批价 770 仍低于茅台体系的势能", "千元价格带受 1573 与酱酒双向挤压"],
  "挺价控量 + 经销商激励 + 国际化"),
 ("泸州老窖", "000568.SZ", 104.7, -36.4, 43.4, -43.4, 85.3, 12.2, 2.32, 1058, 4.97, 78.5,
  "高端", "国窖 1573 批价坚挺但动销偏弱", "渠道库存约 3 个月",
  ["股息率 4.97%，七家最高", "毛利率 85.3%，高端结构扎实", "PB 2.32 处历史低位"],
  ["营收 -36.4% 为七家最深", "国窖动销弱于茅五，份额承压", "去库存进度滞后于五粮液"],
  "收缩投放稳价 + 去库存 + 保利润"),
 ("山西汾酒", "600809.SH", 210.4, -12.2, 64.4, -24.3, 75.4, 13.8, 3.70, 1409, 3.82, 65.3,
  "次高端", "低度产品首次降价", "渠道库存约 4 个月，七家最深",
  ["清香型唯一龙头，赛道独占", "PE-TTM 13.8，估值七家最低", "2025-27 分红率承诺 65%"],
  ["库存 4 个月为七家最深", "低度产品首次降价，价盘松动", "Q2 单季净利 -43%，出清未完成"],
  "控货去库存 + 玻汾/青20 结构升级 + 省外扩张"),
 ("洋河股份", "002304.SZ", 105.4, -28.8, 26.0, -40.1, 73.4, 67.6, 1.39, 558, 2.42, 100.4,
  "次高端", "梦三水晶版批价较春节 +20 元", "库存低位，去库存阶段",
  ["库存低位，梦三批价企稳回升", "分红率 100%+ 承诺，PB 仅 1.39", "估值已充分反映悲观预期"],
  ["PE-TTM 67.6 倍——净利暴跌被动冲高", "营收 -28.8%，品牌老化问题", "股息率 2.42% 七家最低"],
  "去库存 + 梦之蓝手工班换代 + ≥100% 分红承诺"),
 ("古井贡酒", "000596.SZ", 101.3, -27.0, 21.6, -40.9, 80.3, 17.7, 1.92, 436, 3.32, 65.5,
  "区域龙头", "价盘稳定，古 16 动销正增长", "去库存阶段，价盘最稳",
  ["价盘稳定，古 16 动销正增长", "毛利率 80.3%，徽酒绝对龙头", "PE 17.7 / PB 1.92 估值不高"],
  ["营收 -27.0%、净利 -40.9% 双降", "省外扩张受阻，全国化遇瓶颈", "规模体量在七家中最小档"],
  "稳价盘 + 聚焦古16/古20 + 省内深耕"),
 ("今世缘", "603369.SH", 64.4, -7.4, 20.8, -6.6, 74.1, 15.9, 2.08, 344, 3.45, 57.5,
  "区域龙头", "淡雅大流通流速快、价盘波动", "库存正常，动销正增长",
  ["整体动销正增长，营收降幅最小（-7.4%）", "江苏大本营渠道稳固", "净利 -6.6%，出清压力最小"],
  ["淡雅价盘波动，控价能力受考验", "分红率 57.5% 七家最低", "规模最小，全国化尚早"],
  "主动压货提市占 + 淡雅/单开/对开大单品矩阵"),
]

# ---------- slide 1: cover ----------
s = new_slide()
rect(s, 0, 0, Inches(13.333), Inches(7.5), NAVY)
rect(s, 0, Inches(4.9), Inches(13.333), Inches(0.06), GOLD)
tb(s, Inches(0.9), Inches(2.1), Inches(11.5), Inches(1.4),
   "白酒竞争格局：深度调整第五年的分化与出清", size=40, bold=True,
   color=WHITE, align=PP_ALIGN.CENTER)
tb(s, Inches(0.9), Inches(3.55), Inches(11.5), Inches(0.6),
   "贵州茅台 · 五粮液 · 泸州老窖 · 山西汾酒 · 洋河股份 · 古井贡酒 · 今世缘",
   size=18, color=GOLD, align=PP_ALIGN.CENTER)
tb(s, Inches(0.9), Inches(5.2), Inches(11.5), Inches(0.9),
   "估值底已现 · 盈利底未确认 ｜ 批价锚定龙头 · 五粮液逆势抢份额 · 次高端最受伤\n2026-10-09 · 数据：同花顺问财 / 本地温度计 / csindex",
   size=14, color=MGRAY, align=PP_ALIGN.CENTER)

# ---------- slide 2: executive summary ----------
s = content_slide("执行摘要：估值底已现，盈利底未确认，头部集中加速",
                  "数据来源：同花顺问财（2026-10-09 行情 / 2026H1 中报）；白酒指数 881273")
cards = [
    ("10y PE 分位 7.2%", "行业温度计 buy 区，已连续 703 天；CAPE 20.9 处样本 1.6% 分位"),
    ("白酒指数 YTD -27.7%", "2021 高点以来最大回撤 -72.2%，本轮为历史最深调整"),
    ("七家净利 2026H1 平均 -21%", "茅台 -2%、五粮液 +89%（低基数）、老窖 -43%、汾酒 -24%"),
]
x = Inches(0.4)
for t, d in cards:
    rect(s, x, Inches(1.15), Inches(4.05), Inches(1.75), LGRAY)
    tb(s, x + Inches(0.15), Inches(1.3), Inches(3.8), Inches(0.6), t,
       size=18, bold=True, color=NAVY)
    tb(s, x + Inches(0.15), Inches(1.95), Inches(3.8), Inches(0.85), d,
       size=12, color=GRAY)
    x += Inches(4.25)
bullets(s, Inches(0.4), Inches(3.25), Inches(12.5), Inches(3.6), [
    ("结论一｜头部集中加速：", True, NAVY),
    "茅台批价 1715 仍是全行业锚，库存不足两周；五粮液八代流速加快、动销正增长，是唯一逆势放量的高端酒；",
    "长尾品牌动销暴跌 30-60%，份额向强动销单品（八代、古16、淡雅、青20/玻汾）集中。",
    ("结论二｜次高端与区域酒仍在出清：", True, NAVY),
    "老窖营收 -36% 最深、汾酒库存 4 个月最深、洋河净利 -40% 致 PE 被动冲高至 68 倍；古井/今世缘相对最稳。",
    ("结论三｜估值底已现，盈利底未确认：", True, NAVY),
    "板块 10y PE 分位 7.2%（buy 区）+ 股息率 2.4-5.0%，下行保护厚；但七家净利平均 -21%，",
    "PE 分位便宜可与盈利下滑长期并存——左侧高赔率，右侧信号未现。",
], size=14, gap=4)
footer(s, 2, "数据来源：同花顺问财 hithink-industry-query；本地温度计 2026-09-28")

# ---------- slide 3: market context ----------
s = content_slide("市场语境：动销平淡、批价下行，2026 中报七家营收增速罕见齐降",
                  "数据来源：同花顺问财；2026H1 中报；批价数据来自 2026-09-30 经销商调研")
tb(s, Inches(0.4), Inches(1.05), Inches(7.6), Inches(0.4),
   "2026 中秋国庆动销：终端烟酒店普遍下滑 20%-40%", size=18, bold=True, color=NAVY)
bullets(s, Inches(0.4), Inches(1.55), Inches(7.6), Inches(2.0), [
    "茅台批价节后回落至 1715 元，五粮液 770 元左右",
    "汾酒低度首次降价；国窖 1573 批价坚挺但动销偏弱",
    "长尾品牌动销暴跌 30-60%，行业加速洗牌",
    "渠道库存：汾酒约 4 个月、老窖约 3 个月（历史偏高）",
], size=13, gap=3)
# native bar chart: 2026H1 revenue yoy
chart_data = CategoryChartData()
names = [d[0][:2] for d in D]
yoy = [d[3] for d in D]
chart_data.categories = names
chart_data.add_series("2026H1 营收同比 %", yoy)
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                        Inches(0.4), Inches(3.6), Inches(7.6), Inches(3.2),
                        chart_data)
ch = gf.chart
ch.has_legend = False
plot = ch.plots[0]
plot.has_data_labels = True
plot.data_labels.font.size = Pt(10)
plot.data_labels.number_format = '0.0'
plot.data_labels.number_format_is_linked = False
ser = plot.series[0]
ser.format.fill.solid()
ser.format.fill.fore_color.rgb = NAVY
ch.category_axis.tick_labels.font.size = Pt(11)
ch.value_axis.tick_labels.font.size = Pt(10)
ch.value_axis.has_major_gridlines = True
tb(s, Inches(8.2), Inches(1.05), Inches(4.7), Inches(5.6),
   "市场规模与结构\n\n"
   "· 白酒板块总市值约 2.3 万亿元（七家合计），占食品饮料行业利润大头\n"
   "· 价格带金字塔：超高端（茅台）→ 高端（五粮液/国窖）→ 次高端（汾酒/洋河）→ 区域（古井/今世缘）\n"
   "· 2026H1 七家营收增速：仅五粮液 +20.9%（含低基数）与茅台 +1.5% 为正，其余五家 -7%~-36%\n"
   "· 政策：2026-08-31 商务部等 7 部门《关于推动商品消费扩容升级的实施意见》，促食品饮料消费品质提升\n"
   "· 机构持仓与估值双处近十年低位，高股息（龙头 3.3-5.0%）提供安全垫",
   size=13, color=GRAY)
footer(s, 3, "数据来源：同花顺问财；news-search 2026-09-20~09-30")

# ---------- slide 4: industry economics ----------
s = content_slide("行业经济学：价格带金字塔与库存周期——白酒是品牌与渠道的双重生意",
                  "数据来源：同花顺问财；渠道调研")
# pyramid
levels = [
    ("超高端｜茅台", "批价 1715 · 库存 <2 周", NAVY, 4.0),
    ("高端｜五粮液 / 国窖 1573", "批价 770+ / 坚挺 · 动销分化", RGBColor(0x2E, 0x4A, 0x8A), 6.0),
    ("次高端｜汾酒 / 洋河", "库存 4 个月 / 低位 · 出清中", RGBColor(0x3D, 0x5A, 0xA0), 8.0),
    ("区域龙头｜古井 / 今世缘", "价盘稳 / 动销正增长", RGBColor(0x6B, 0x82, 0xC0), 10.0),
]
y = Inches(1.15)
for i, (t, sub, c, w) in enumerate(levels):
    w_in = Inches(w)
    rect(s, (Inches(13.333) - w_in) / 2, y, w_in, Inches(0.95), c)
    tb(s, Inches(1.2), y + Inches(0.1), Inches(6.0), Inches(0.4), t,
       size=15, bold=True, color=WHITE if i < 3 else NAVY)
    tb(s, Inches(6.2), y + Inches(0.1), Inches(6.8), Inches(0.4), sub,
       size=12, color=WHITE if i < 3 else NAVY)
    y += Inches(1.05)
tb(s, Inches(0.4), Inches(5.5), Inches(12.5), Inches(0.4),
   "价值链利润分配：品牌方（吨价 x 毛利 73-90%）> 渠道（经销商返利与差价）> 终端",
   size=14, bold=True, color=NAVY)
bullets(s, Inches(0.4), Inches(5.95), Inches(12.5), Inches(1.0), [
    "库存周期定位：2021 年渠道加库存见顶 → 2024-2026 主动去库存；当前汾酒/老窖库存仍高，行业处于出清后段而非尾声",
    "竞争本质：价格带卡位（谁守住批价谁保住品牌）+ 渠道动销（谁流速快谁抢份额）——批价与库存是先行指标",
], size=13, gap=3)
footer(s, 4, "数据来源：同花顺问财；2026-09-30 经销商调研")

# ---------- slide 5: unified metrics ----------
s = content_slide("统一对比口径：白酒赛道六项关键指标",
                  "本页口径适用于 deck 全部跨公司对比")
metrics = [
    ("批价（元/瓶）", "渠道实际成交价，品牌力的即时标尺；下行=需求疲弱，上行=供需逆转"),
    ("渠道库存（月）", "经销商库存周转月数；>3 个月为高压区，<2 个月为健康区"),
    ("2026H1 营收增速", "动销与报表的综合结果；五粮液 +20.9% 含低基数，需结合批价看"),
    ("毛利率", "价格带卡位的财务体现：超高端 89%+，区域 74% 左右"),
    ("股息率 / 分红率", "下行保护厚度；行业 2025 年度普遍 57-224% 分红率"),
    ("PE-TTM 与历史分位", "注意洋河式陷阱：净利暴跌会把 PE 被动推高，分位才有意义"),
]
x = Inches(0.4)
y = Inches(1.3)
for i, (t, d) in enumerate(metrics):
    col = i % 2
    row = i // 2
    cx = x + col * Inches(6.35)
    cy = y + row * Inches(1.85)
    rect(s, cx, cy, Inches(6.1), Inches(1.7), LGRAY)
    tb(s, cx + Inches(0.15), cy + Inches(0.1), Inches(5.8), Inches(0.4), t,
       size=16, bold=True, color=NAVY)
    tb(s, cx + Inches(0.15), cy + Inches(0.55), Inches(5.8), Inches(1.05), d,
       size=12, color=GRAY)
footer(s, 5, "口径统一说明：财务为 2026 中报；批价/库存为 2026-09-30 渠道调研")

# ---------- slide 6: competitor mapping ----------
s = content_slide("竞对映射：七家分属四个价格带阵营",
                  "数据来源：同花顺问财")
groups = [
    ("超高端", NAVY, ["贵州茅台：行业批价锚，库存最健康"]),
    ("高端", RGBColor(0x2E, 0x4A, 0x8A), ["五粮液：八代流速加快，逆势抢份额", "泸州老窖：国窖动销偏弱，去库存中"]),
    ("次高端", RGBColor(0x3D, 0x5A, 0xA0), ["山西汾酒：库存最深，出清后段", "洋河股份：去库存+产品换代"]),
    ("区域龙头", RGBColor(0x6B, 0x82, 0xC0), ["古井贡酒：价盘最稳，古16正增长", "今世缘：动销正增长，营收降幅最小"]),
]
x = Inches(0.4)
w = Inches(3.05)
for i, (t, c, items) in enumerate(groups):
    rect(s, x + i * (w + Inches(0.1)), Inches(1.2), w, Inches(4.6), LGRAY)
    rect(s, x + i * (w + Inches(0.1)), Inches(1.2), w, Inches(0.55), c)
    tb(s, x + i * (w + Inches(0.1)), Inches(1.28), w, Inches(0.45), t,
       size=17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    bl = []
    for it in items:
        bl.append((it, True, NAVY))
    bullets(s, x + i * (w + Inches(0.1)) + Inches(0.12), Inches(1.9), w - Inches(0.24), Inches(3.8),
            bl, size=12, gap=8)
tb(s, Inches(0.4), Inches(6.0), Inches(12.5), Inches(0.8),
   "阵营间竞争：五粮液 vs 国窖 1573 抢高端份额；次高端是挤压最狠价格带（酒鬼/舍得/水井坊不在本 deck 范围内，但承压最深）；区域龙头靠省内精耕守住基本盘。",
   size=13, color=GRAY, bold=False)
footer(s, 6, "数据来源：同花顺问财")

# ---------- slide 7: 2x2 matrix ----------
s = content_slide("定位矩阵：价格带卡位 × 动销势能——右上角赢家明确",
                  "动销势能 = 批价趋势 + 库存健康度 + 2026H1 动销调研综合")
plot_x, plot_y, plot_w, plot_h = Inches(2.2), Inches(1.35), Inches(10.0), Inches(4.9)
rect(s, plot_x, plot_y, plot_w, plot_h, WHITE, line=GRAY)
# quadrant labels
tb(s, Inches(2.35), Inches(1.45), Inches(4.7), Inches(0.35), "高端承压（批价坚挺但动销弱）", size=11, color=GRAY, italic=True)
tb(s, Inches(7.3), Inches(1.45), Inches(4.7), Inches(0.35), "高端强势（流速加快抢份额）", size=11, color=GREEN, bold=True)
tb(s, Inches(2.35), Inches(5.6), Inches(4.7), Inches(0.35), "区域出清（价盘/动销双弱）", size=11, color=GRAY, italic=True)
tb(s, Inches(7.3), Inches(5.6), Inches(4.7), Inches(0.35), "区域稳健（动销正增长）", size=11, color=GREEN, bold=True)
# axis titles
tb(s, Inches(7.0), Inches(6.4), Inches(2.0), Inches(0.35), "价格带卡位 →", size=12, bold=True, color=NAVY)
tb(s, Inches(0.5), Inches(3.6), Inches(1.6), Inches(0.6), "动销势能 →", size=12, bold=True, color=NAVY)
# positions: (name, tier_x 0-10, momentum_y 0-10, color)
pts = [
    ("贵州茅台", 10.0, 5.6, NAVY),
    ("五粮液", 8.2, 9.2, GREEN),
    ("泸州老窖", 7.8, 2.6, RED),
    ("山西汾酒", 6.6, 2.9, RED),
    ("洋河股份", 5.4, 1.8, RED),
    ("古井贡酒", 4.6, 6.8, GOLD),
    ("今世缘", 3.8, 6.0, GOLD),
]
for name, tx, ty, c in pts:
    cx = plot_x + plot_w * tx / 10.0
    cy = plot_y + plot_h * (1 - ty / 10.0)
    oval = rect(s, cx - Inches(0.09), cy - Inches(0.09), Inches(0.18), Inches(0.18), c, shape=MSO_SHAPE.OVAL)
    tb(s, cx - Inches(0.85), cy + Inches(0.12), Inches(1.7), Inches(0.3), name,
       size=11, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
footer(s, 7, "定位基于 2026-09-30 渠道调研与 2026H1 中报综合")

# ---------- slides 8-14: company deep-dives ----------
titles = [
    "贵州茅台：唯一的批价锚——最稳，但净利罕见转负",
    "五粮液：批价流速双强，本轮唯一逆势放量的高端酒",
    "泸州老窖：国窖动销偏弱，营收降幅七家最深",
    "山西汾酒：库存四个月 + 低度降价，出清最深的清香龙头",
    "洋河股份：净利暴跌致 PE 被动冲高至 68 倍",
    "古井贡酒：价盘最稳的徽酒龙头，古 16 仍正增长",
    "今世缘：动销正增长的区域黑马，价盘有波动",
]
for idx, (name, code, rev, rev_yoy, profit, profit_yoy, gross, pe, pb,
          mcap, div, payout, tier, price_note, inv_note,
          strength, weakness, strategy) in enumerate(D):
    s = content_slide(titles[idx], f"数据来源：同花顺问财（2026H1 中报 / 2026-10-09 行情）｜{code}")
    # left metrics table
    rows = [
        ("2026H1 营收", f"{rev:.1f} 亿（同比 {rev_yoy:+.1f}%）"),
        ("2026H1 归母净利", f"{profit:.1f} 亿（同比 {profit_yoy:+.1f}%）"),
        ("销售毛利率", f"{gross:.1f}%"),
        ("PE-TTM / PB", f"{pe:.1f} / {pb:.2f}"),
        ("总市值", f"{mcap:,} 亿"),
        ("股息率（2025年度）", f"{div:.2f}%"),
        ("分红率（2025年度）", f"{payout:.1f}%"),
        ("批价动态", price_note),
        ("渠道库存", inv_note),
    ]
    tbl = s.shapes.add_table(len(rows), 2, Inches(0.4), Inches(1.2), Inches(5.9), Inches(4.9)).table
    tbl.columns[0].width = Inches(2.0)
    tbl.columns[1].width = Inches(3.9)
    for r, (k, v) in enumerate(rows):
        style_cell(tbl.cell(r, 0), k, size=12, bold=True, color=WHITE, fill=NAVY)
        style_cell(tbl.cell(r, 1), v, size=12, color=GRAY, fill=LGRAY if r % 2 == 0 else WHITE)
    # right qualitative boxes
    boxes = [
        ("优势", GREEN, strength),
        ("劣势", RED, weakness),
        ("战略", NAVY, [strategy]),
    ]
    y = Inches(1.2)
    for t, c, items in boxes:
        rect(s, Inches(6.6), y, Inches(6.3), Inches(1.6), LGRAY)
        rect(s, Inches(6.6), y, Inches(6.3), Inches(0.4), c)
        tb(s, Inches(6.75), y + Inches(0.03), Inches(6.0), Inches(0.35), t,
           size=14, bold=True, color=WHITE)
        bullets(s, Inches(6.75), y + Inches(0.45), Inches(6.0), Inches(1.1), items,
                size=11, gap=2)
        y += Inches(1.7)
    footer(s, 8 + idx, f"数据来源：同花顺问财；{code} 2026 中报；批价/库存 2026-09-30 渠道调研")

# ---------- slide 15: comparative matrix ----------
s = content_slide("七维对比矩阵：赢家（五粮液）与输家（洋河/老窖）分化清晰",
                  "评级 ●●● 强 / ●●○ 中 / ●○○ 弱 / ○○○ 极弱 ｜数据来源：同花顺问财")
comp_header = ["维度"] + [d[0] for d in D]
comp_rows = [
    ("规模（总市值）", "●●● 15,828亿", "●●○ 2,726亿", "●●○ 1,058亿", "●●○ 1,409亿", "●○○ 558亿", "●○○ 436亿", "●○○ 344亿"),
    ("2026H1 营收增速", "●○○ +1.5%", "●●● +20.9%", "○○○ -36.4%", "●○○ -12.2%", "○○○ -28.8%", "○○○ -27.0%", "●●○ -7.4%"),
    ("毛利率", "●●● 89.6%", "●●○ 80.3%", "●●● 85.3%", "●●○ 75.4%", "●●○ 73.4%", "●●○ 80.3%", "●●○ 74.1%"),
    ("渠道库存", "●●● <2周", "●●● 低位", "●○○ ~3个月", "○○○ ~4个月", "●●○ 低位", "●●○ 价盘稳", "●●○ 正常"),
    ("批价势能", "●●○ 1715回落", "●●● 流速加快", "●○○ 动销弱", "●○○ 低度首降", "●●○ 梦三+20", "●●○ 稳定", "●●○ 淡雅波动"),
    ("股息率", "●●○ 3.77%", "●●● 4.87%", "●●● 4.97%", "●●○ 3.82%", "●○○ 2.42%", "●●○ 3.32%", "●●○ 3.45%"),
    ("估值 PE-TTM", "●●○ 19.4x", "●●○ 20.8x", "●●● 12.2x", "●●● 13.8x", "○○○ 67.6x*", "●●○ 17.7x", "●●● 15.9x"),
]
tbl = s.shapes.add_table(len(comp_rows) + 1, len(comp_header), Inches(0.4), Inches(1.2), Inches(12.5), Inches(4.8)).table
tbl.columns[0].width = Inches(1.9)
for c in range(1, 8):
    tbl.columns[c].width = Inches(1.51)
for c, h in enumerate(comp_header):
    style_cell(tbl.cell(0, c), h, size=12, bold=True, color=WHITE, fill=NAVY, align=PP_ALIGN.CENTER)
for r, row in enumerate(comp_rows, start=1):
    for c, v in enumerate(row):
        fill = LGRAY if r % 2 == 0 else WHITE
        style_cell(tbl.cell(r, c), v, size=10.5, bold=(c == 0), color=NAVY if c == 0 else GRAY, fill=fill, align=PP_ALIGN.CENTER if c > 0 else PP_ALIGN.LEFT)
bullets(s, Inches(0.4), Inches(6.15), Inches(12.5), Inches(0.85), [
    "* 洋河 PE-TTM 67.6x 为净利暴跌被动抬升，非市场给予溢价，解读须结合历史分位",
    "读表方法：五粮液在增速/批价/股息三列全 ●●●，是当前格局赢家；老窖与洋河在增速/库存列最弱，仍处出清",
], size=11, gap=2)
footer(s, 15, "数据来源：同花顺问财（2026H1 中报 / 2026-10-09 行情 / 2025 年度分红）")

# ---------- slide 16: moat ----------
s = content_slide("护城河评级：茅台四维全强，区域酒护城河=省内渠道深度",
                  "评级：强 / 中 / 弱 ｜数据来源：公开财报与渠道调研综合")
moat_header = ["公司", "品牌无形资产", "渠道/转换成本", "规模经济", "产区/工艺稀缺性"]
moat_rows = [
    ("贵州茅台", "强", "强", "强", "强"),
    ("五粮液", "强", "强", "中", "中"),
    ("泸州老窖", "强", "中", "中", "中"),
    ("山西汾酒", "强", "中", "中", "中"),
    ("洋河股份", "中", "中", "中", "弱"),
    ("古井贡酒", "中", "中", "弱", "弱"),
    ("今世缘", "中", "中", "弱", "弱"),
]
RATE_COLOR = {"强": GREEN, "中": GOLD, "弱": RED}
tbl = s.shapes.add_table(len(moat_rows) + 1, 5, Inches(0.4), Inches(1.2), Inches(12.5), Inches(3.3)).table
tbl.columns[0].width = Inches(2.2)
for c in range(1, 5):
    tbl.columns[c].width = Inches(2.575)
for c, h in enumerate(moat_header):
    style_cell(tbl.cell(0, c), h, size=13, bold=True, color=WHITE, fill=NAVY, align=PP_ALIGN.CENTER)
for r, row in enumerate(moat_rows, start=1):
    fill = LGRAY if r % 2 == 0 else WHITE
    style_cell(tbl.cell(r, 0), row[0], size=12.5, bold=True, color=NAVY, fill=fill)
    for c in range(1, 5):
        style_cell(tbl.cell(r, c), row[c], size=12.5, bold=(row[c] == "强"), color=RATE_COLOR[row[c]], fill=fill, align=PP_ALIGN.CENTER)
bullets(s, Inches(0.4), Inches(4.7), Inches(12.5), Inches(2.2), [
    ("持久优势（难复制）：", True, NAVY),
    "茅台的批价锚地位 + 库存极低——本轮下行中唯一不伤筋动骨的品牌；",
    "五粮液的渠道流速与高端卡位——逆周期抢份额的能力；古井/今世缘的省内渠道深度。",
    ("结构性脆弱（难修复）：", True, NAVY),
    "老窖对国窖 1573 单品的依赖（动销弱即全盘弱）；汾酒渠道库存 4 个月的去化之难；",
    "洋河品牌老化 + 净利暴跌后的 PE 失真，修复需产品换代与渠道重建同步完成。",
], size=13, gap=3)
footer(s, 16, "评级为定性综合判断（品牌力/渠道/成本/稀缺性四维），仅供研究参考")

# ---------- slide 17: scenarios & signposts ----------
s = content_slide("情景与信号：Base 磨底概率最大，右侧信号未现",
                  "概率为主观判断 ｜数据来源：同花顺问财、本地温度计")
scen = [
    ("Bull ｜ 25%", GREEN, "政策加码 + 批价企稳回升 + 去库存完成", "估值修复至 25x PE（约 +25% 空间）；驱动：茅台批价站稳 1800+、春节动销超预期、龙头单季营收回正"),
    ("Base ｜ 50%", NAVY, "磨底延续：批价低位横盘，盈利再降 0~10%", "估值在 7-15% 分位震荡，股息 3.3-5.0% 提供持有收益；驱动：去库存缓慢推进，动销未见起色"),
    ("Bear ｜ 25%", RED, "批价破位：茅台 <1600，库存去化失败", "2027 年盈利再下修 20%+，PE 分位越跌越贵；驱动：消费力持续疲弱、渠道信心崩溃"),
]
y = Inches(1.2)
for t, c, sub, d in scen:
    rect(s, Inches(0.4), y, Inches(12.5), Inches(1.15), LGRAY)
    rect(s, Inches(0.4), y, Inches(0.12), Inches(1.15), c)
    tb(s, Inches(0.7), y + Inches(0.08), Inches(2.6), Inches(0.4), t, size=16, bold=True, color=c)
    tb(s, Inches(0.7), y + Inches(0.48), Inches(3.3), Inches(0.6), sub, size=11.5, bold=True, color=NAVY)
    tb(s, Inches(4.1), y + Inches(0.08), Inches(8.6), Inches(1.0), d, size=11.5, color=GRAY)
    y += Inches(1.3)
tb(s, Inches(0.4), y + Inches(0.05), Inches(12.5), Inches(0.4), "跟踪信号（Signposts）——出现 ≥2 项则右侧确认",
   size=16, bold=True, color=NAVY)
bullets(s, Inches(0.4), y + Inches(0.5), Inches(12.5), Inches(1.6), [
    "① 茅台批价站稳 1800+ 且不再阴跌（当前 1715）　② 汾酒/老窖渠道库存降至 2 个月以内",
    "③ 任一龙头单季营收增速回正　④ 2027 年春节动销超预期（2027-02）　⑤ 消费刺激政策加码落地　⑥ 龙头回购/特别分红加码",
], size=13, gap=4)
footer(s, 17, "概率与信号为分析框架，非预测承诺")

# ---------- slide 18: sources ----------
s = content_slide("附：数据来源与口径说明", "")
bullets(s, Inches(0.4), Inches(1.2), Inches(12.5), Inches(5.4), [
    ("行情 / 财务 / 股息数据：", True, NAVY),
    "同花顺问财 hithink-industry-query，2026-10-09 查询；财务口径为 2026 年中报，股息为 2025 年度分红。",
    ("批价 / 库存 / 动销：", True, NAVY),
    "同花顺问财 news-search（2026-09-20 ~ 09-30 经销商调研与券商研报资讯）。",
    ("估值分位：", True, NAVY),
    "本地温度计 tactical/signals/temperature.json（2026-09-28 快照，10y PE 分位 7.16%）；CAPE 20.9 为 csindex 自建测算（2026-10-08，样本 61 个月，分位 1.6%）。",
    ("口径注意：", True, NAVY),
    "① 五粮液 2026H1 净利 +89.3% 含低基数/一次性因素，勿线性外推；",
    "② 洋河 PE-TTM 67.6x 为净利暴跌被动抬升，解读须结合历史分位；",
    "③ 白酒指数 2021 高点以来最大回撤 -72.2%（csindex，截至 2026-09-15）。",
    ("声明：", True, RED),
    "本 deck 为个人投资研究用途，不构成任何投资建议。",
], size=13, gap=5)
footer(s, 18, "生成时间 2026-10-09")

# ---------- save ----------
out = "/home/work/workspace01/bmc/xuleihs/study/saa/tactical/analysis/2026-10-09-baijiu-competitive-landscape.pptx"
prs.save(out)
print("saved:", out)
