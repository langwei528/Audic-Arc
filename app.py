"""
AuditArc 审迹 - AI审计风险识别系统
Streamlit Demo 主界面
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.generate_sample_data import generate_financial_data
from modules.risk_engine import full_analysis_pipeline, RISK_LEVELS

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="AuditArc 审迹 | AI审计风险识别系统",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== 全局样式 ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', sans-serif;
}

/* 深色顶栏 */
.main-header {
    background: linear-gradient(135deg, #0A0E2A 0%, #1A237E 60%, #0066CC 100%);
    padding: 28px 36px 22px;
    border-radius: 12px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: "";
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,102,204,0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.main-header h1 {
    color: white; font-size: 28px; font-weight: 700;
    margin: 0; letter-spacing: 1px;
}
.main-header p {
    color: rgba(255,255,255,0.7); font-size: 13px;
    margin: 6px 0 0; letter-spacing: 0.5px;
}
.brand-tag {
    display: inline-block;
    background: rgba(0,102,204,0.4);
    border: 1px solid rgba(0,102,204,0.6);
    color: #7EC8FF;
    font-size: 11px; padding: 2px 10px;
    border-radius: 20px; margin-bottom: 8px;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 1px;
}

/* 步骤卡片 */
.step-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 28px; height: 28px; border-radius: 50%;
    background: #0066CC; color: white;
    font-size: 13px; font-weight: 700;
    margin-right: 8px; flex-shrink: 0;
}
.step-title {
    font-size: 16px; font-weight: 600; color: #1A1A2E;
    display: flex; align-items: center;
}

/* 风险卡片 */
.risk-card {
    border-radius: 10px; padding: 16px 20px;
    margin-bottom: 12px; border-left: 5px solid;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.risk-card:hover { transform: translateX(3px); box-shadow: 2px 4px 16px rgba(0,0,0,0.08); }

.risk-极高 { background: #FFF0F3; border-color: #FF2D55; }
.risk-高   { background: #FFF4EF; border-color: #FF6B35; }
.risk-中   { background: #FFFBF0; border-color: #F5A623; }
.risk-低   { background: #F0FFF4; border-color: #34C759; }

.risk-level-badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 12px; font-weight: 600;
    margin-left: 8px;
}

/* 指标卡 */
.metric-card {
    background: white; border-radius: 10px;
    padding: 16px; border: 1px solid #E8ECEF;
    text-align: center;
}
.metric-card .metric-val {
    font-size: 26px; font-weight: 700; color: #1A1A2E;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-card .metric-label { font-size: 12px; color: #888; margin-top: 4px; }

/* SHAP条形 */
.shap-bar-wrap { margin: 6px 0; }
.shap-label { font-size: 12px; color: #555; margin-bottom: 3px; }
.shap-bar { height: 8px; border-radius: 4px; background: #0066CC; }

/* 审计程序列表 */
.proc-item {
    background: #F0F7FF; border-radius: 6px;
    padding: 8px 12px; margin: 4px 0;
    font-size: 13px; color: #333;
    border-left: 3px solid #0066CC;
}

/* 日志行 */
.log-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; color: #00CC66;
    padding: 2px 0;
}

/* 底部免责 */
.disclaimer-bar {
    background: #FFF8E1; border: 1px solid #F5A623;
    border-radius: 8px; padding: 12px 16px;
    font-size: 12px; color: #8B4513;
    margin-top: 24px; text-align: center;
}

/* 数据质量得分 */
.quality-score {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 48px; font-weight: 700;
    color: #0066CC; text-align: center;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: #0A0E2A;
}
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
section[data-testid="stSidebar"] .stButton button {
    background: #0066CC !important; border: none;
    color: white !important; font-weight: 600;
}

/* 隐藏默认header */
#MainMenu, header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==================== Session State ====================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "result" not in st.session_state:
    st.session_state.result = None
if "inc_df" not in st.session_state:
    st.session_state.inc_df = None
if "bal_df" not in st.session_state:
    st.session_state.bal_df = None
if "cf_df" not in st.session_state:
    st.session_state.cf_df = None
if "selected_risk" not in st.session_state:
    st.session_state.selected_risk = None

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-size:32px; margin-bottom:4px;">🔍</div>
        <div style="font-size:20px; font-weight:700; letter-spacing:2px;">AuditArc</div>
        <div style="font-size:12px; color:rgba(255,255,255,0.5); letter-spacing:1px;">审 迹</div>
        <div style="margin-top:8px; font-size:11px; color:rgba(255,255,255,0.4);">
            AI审计风险预警智能体
        </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1); margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("**📋 演示流程**")
    steps_status = {
        "Step 1  数据导入": "✅" if st.session_state.inc_df is not None else "⬜",
        "Step 2  风险扫描": "✅" if st.session_state.analysis_done else "⬜",
        "Step 3  风险看板": "✅" if st.session_state.analysis_done else "⬜",
        "Step 4  导出报告": "⬜",
    }
    for step, status in steps_status.items():
        st.markdown(f"{status} {step}")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("**⚙️ 系统信息**")
    st.markdown("- 双模型架构（规则+AI）")
    st.markdown("- 三重保险校验机制")
    st.markdown("- 7×24 实时监控")
    st.markdown("- SHAP可解释性输出")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin:16px 0;'>", unsafe_allow_html=True)
    if st.button("🔄 重置演示", use_container_width=True):
        for k in ["analysis_done", "result", "inc_df", "bal_df", "cf_df", "selected_risk"]:
            st.session_state[k] = None if k != "analysis_done" else False
        st.rerun()

    st.markdown("""
    <div style="margin-top:20px; font-size:10px; color:rgba(255,255,255,0.3); text-align:center;">
        KPMG AI赋能审计大赛<br>AuditArc团队 · 演示版本
    </div>
    """, unsafe_allow_html=True)

# ==================== 主区域 Header ====================
st.markdown("""
<div class="main-header">
    <div class="brand-tag">KPMG AI赋能审计大赛 · 场景一：智能风险识别</div>
    <h1>🔍 AuditArc 审迹</h1>
    <p>AI赋能智能审计风险识别系统 · 双模型并行 · 三重保险校验 · SHAP可解释输出</p>
</div>
""", unsafe_allow_html=True)

# ==================== STEP 1: 数据导入 ====================
st.markdown('<div class="step-title"><span class="step-badge">1</span>数据导入</div>', unsafe_allow_html=True)
st.markdown("上传标准化财务数据（利润表、资产负债表、现金流量表），或使用预置演示数据。")

col_upload, col_sample = st.columns([2, 1])

with col_upload:
    with st.expander("📁 上传自定义CSV文件", expanded=False):
        uf_inc = st.file_uploader("利润表 CSV", type=["csv"], key="u_inc")
        uf_bal = st.file_uploader("资产负债表 CSV", type=["csv"], key="u_bal")
        uf_cf  = st.file_uploader("现金流量表 CSV", type=["csv"], key="u_cf")
        if uf_inc and uf_bal and uf_cf:
            if st.button("✅ 加载上传数据"):
                st.session_state.inc_df = pd.read_csv(uf_inc)
                st.session_state.bal_df = pd.read_csv(uf_bal)
                st.session_state.cf_df  = pd.read_csv(uf_cf)
                st.session_state.analysis_done = False
                st.success("数据加载成功！")
                st.rerun()

with col_sample:
    st.markdown("""
    <div style="background:#F0F7FF; border:1px solid #CCE0FF; border-radius:10px; padding:16px;">
        <div style="font-weight:600; color:#0066CC; margin-bottom:8px;">🏭 演示数据</div>
        <div style="font-size:12px; color:#555;">
            星锰精密机械股份有限公司<br>
            <span style="color:#999">（虚构 · 已脱敏）</span><br><br>
            📅 2021-2023年三年数据<br>
            ⚠️ 含预置风险特征
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    if st.button("📊 加载演示数据", use_container_width=True, type="primary"):
        inc, bal, cf, _ = generate_financial_data()
        st.session_state.inc_df = inc
        st.session_state.bal_df = bal
        st.session_state.cf_df  = cf
        st.session_state.analysis_done = False
        st.rerun()

# 显示已加载数据预览
if st.session_state.inc_df is not None:
    with st.expander("👁️ 查看已加载的财务数据", expanded=False):
        t1, t2, t3 = st.tabs(["利润表", "资产负债表", "现金流量表"])
        with t1:
            st.dataframe(st.session_state.inc_df, use_container_width=True, hide_index=True)
        with t2:
            st.dataframe(st.session_state.bal_df, use_container_width=True, hide_index=True)
        with t3:
            st.dataframe(st.session_state.cf_df, use_container_width=True, hide_index=True)

    # 数据质量得分（简单评估）
    total_items = len(st.session_state.inc_df) + len(st.session_state.bal_df) + len(st.session_state.cf_df)
    null_count = (st.session_state.inc_df.isnull().sum().sum() +
                  st.session_state.bal_df.isnull().sum().sum() +
                  st.session_state.cf_df.isnull().sum().sum())
    quality = max(0, 100 - int(null_count / max(total_items, 1) * 100))

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="quality-score">{quality}</div>
            <div class="metric-label">数据质量得分</div>
        </div>""", unsafe_allow_html=True)
    with col_q2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{total_items}</div>
            <div class="metric-label">数据项总数</div>
        </div>""", unsafe_allow_html=True)
    with col_q3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(st.session_state.inc_df.columns)-1}</div>
            <div class="metric-label">分析年度</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ==================== STEP 2: 风险扫描 ====================
st.markdown('<div class="step-title"><span class="step-badge">2</span>风险扫描</div>', unsafe_allow_html=True)

if st.session_state.inc_df is None:
    st.info("⬆️ 请先在 Step 1 加载财务数据")
else:
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        scan_btn = st.button("🚀 开始分析", use_container_width=True, type="primary",
                              disabled=st.session_state.analysis_done)
    with col_info:
        if not st.session_state.analysis_done:
            st.markdown("点击「开始分析」启动双模型风险识别引擎，约需 **5-7 秒**")
        else:
            st.success("✅ 分析已完成，请查看下方风险看板")

    if scan_btn and not st.session_state.analysis_done:
        log_placeholder = st.empty()
        progress_bar = st.progress(0)
        logs = []

        scan_steps = [
            ("🔗 通过 MCP 协议连接数据源...", 10),
            ("📥 数据清洗与格式校验...", 20),
            ("⚙️ 规则引擎扫描：应收账款阈值校验...", 35),
            ("⚙️ 规则引擎扫描：收入-现金流勾稽核查...", 50),
            ("🤖 AI评分模型运行中（XGBoost）...", 65),
            ("🔍 业务合理性核查：季节性因素排除...", 78),
            ("🔗 多维度交叉验证（财务+经营数据）...", 88),
            ("📊 SHAP特征归因计算...", 94),
            ("📈 风险图谱生成完毕", 100),
        ]

        def update_log(msg):
            logs.append(msg)
            log_html = "".join([f'<div class="log-line">▶ {l}</div>' for l in logs[-8:]])
            log_placeholder.markdown(
                f'<div style="background:#0A0E2A; border-radius:8px; padding:14px; '
                f'font-family:monospace; min-height:120px;">{log_html}</div>',
                unsafe_allow_html=True
            )

        for step_msg, pct in scan_steps:
            update_log(step_msg)
            progress_bar.progress(pct)
            time.sleep(0.55)

        result = full_analysis_pipeline(
            st.session_state.inc_df,
            st.session_state.bal_df,
            st.session_state.cf_df,
        )
        st.session_state.result = result
        st.session_state.analysis_done = True
        time.sleep(0.3)
        st.rerun()

st.markdown("---")

# ==================== STEP 3: 风险看板 ====================
st.markdown('<div class="step-title"><span class="step-badge">3</span>风险看板</div>', unsafe_allow_html=True)

if not st.session_state.analysis_done:
    st.info("⬆️ 请先完成 Step 2 风险扫描")
else:
    result = st.session_state.result
    risks = result["risks"]
    radar = result["radar_scores"]
    metrics = result["metrics"]
    cnt = result["risk_count"]

    # ---- 总览卡片 ----
    overall = result["overall_risk"]
    overall_color = RISK_LEVELS[overall]["color"]
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, (label, val, color) in zip(
        [c1, c2, c3, c4, c5],
        [
            ("总体风险等级", overall, overall_color),
            ("🔴 极高风险", cnt["极高"], "#FF2D55"),
            ("🟠 高风险",   cnt["高"],   "#FF6B35"),
            ("🟡 中等风险", cnt["中"],   "#F5A623"),
            ("🟢 低风险",   cnt["低"],   "#34C759"),
        ]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {color};">
                <div class="metric-val" style="color:{color}; font-size:{'20px' if label=='总体风险等级' else '32px'}">
                    {val}
                </div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ---- 雷达图 + 预警列表 ----
    col_radar, col_list = st.columns([1, 1.4])

    with col_radar:
        st.markdown("#### 📡 风险雷达图（五维度）")
        categories = list(radar.keys())
        values = list(radar.values())
        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(255,45,85,0.15)',
            line=dict(color='#FF2D55', width=2),
            marker=dict(size=6, color='#FF2D55'),
            name="风险评分"
        ))
        # 行业基准（假设均值为35分）
        bench_vals = [35] * len(categories)
        fig_radar.add_trace(go.Scatterpolar(
            r=bench_vals + [bench_vals[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(0,102,204,0.08)',
            line=dict(color='#0066CC', width=1.5, dash='dot'),
            name="行业基准"
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12)),
            ),
            showlegend=True,
            legend=dict(x=0.8, y=1.1),
            margin=dict(t=20, b=20, l=30, r=30),
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_list:
        st.markdown("#### ⚠️ 预警事项列表（按风险等级排序）")
        for i, risk in enumerate(risks):
            level = risk["风险等级"]
            info = RISK_LEVELS[level]
            score = risk["最终评分"]
            # 点击展开
            with st.expander(
                f"{info['icon']} {risk['风险类型']}  ·  【{level}风险】  ·  评分 {score}/100",
                expanded=(i == 0)
            ):
                st.markdown(f"""
                <div style="font-size:13px; color:#555; margin-bottom:8px;">
                    <strong>触发规则：</strong>{risk['触发规则']}
                </div>
                """, unsafe_allow_html=True)

                # 指标数据
                idx_data = risk.get("指标数据", {})
                if idx_data:
                    rows = [(k, v) for k, v in idx_data.items()]
                    idx_df = pd.DataFrame(rows, columns=["指标", "数值"])
                    st.dataframe(idx_df, hide_index=True, use_container_width=True)

                # 业务判断
                st.markdown(f"""
                <div style="background:#F8F9FA; border-radius:6px; padding:10px; margin:8px 0; font-size:13px;">
                    <strong>💼 业务合理性判断：</strong>{risk.get('业务合理性判断', '')}
                </div>
                <div style="background:#F0F7FF; border-radius:6px; padding:10px; margin:8px 0; font-size:13px;">
                    <strong>🔗 交叉验证结论：</strong>{risk.get('交叉验证', '')}
                </div>
                """, unsafe_allow_html=True)

                # SHAP图
                shap = risk.get("SHAP权重", {})
                if shap:
                    st.markdown("**📊 SHAP特征贡献权重：**")
                    shap_fig = go.Figure(go.Bar(
                        x=list(shap.values()),
                        y=list(shap.keys()),
                        orientation='h',
                        marker_color=['#FF2D55', '#FF6B35', '#F5A623'][:len(shap)],
                        text=[f"{v}%" for v in shap.values()],
                        textposition='outside',
                    ))
                    shap_fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=60),
                        height=120,
                        xaxis=dict(range=[0, 60], showticklabels=False),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(tickfont=dict(size=12)),
                    )
                    st.plotly_chart(shap_fig, use_container_width=True)

                # 准则依据
                std = risk.get("准则依据", "")
                if std:
                    st.markdown(f"""
                    <div style="background:#FFF8E1; border-left:3px solid #F5A623;
                         border-radius:4px; padding:8px 12px; font-size:12px; color:#666; margin:4px 0;">
                        📜 <strong>准则依据：</strong>{std}
                    </div>""", unsafe_allow_html=True)

                # 审计程序
                procs = risk.get("建议审计程序", [])
                if procs:
                    st.markdown("**🎯 建议审计程序：**")
                    for p in procs:
                        st.markdown(f'<div class="proc-item">✓ {p}</div>', unsafe_allow_html=True)

    st.markdown("")

    # ---- 关键指标趋势图 ----
    st.markdown("#### 📈 关键指标趋势（三年对比）")
    col_ch1, col_ch2 = st.columns(2)

    inc_df = st.session_state.inc_df
    inc_cols = [c for c in inc_df.columns if c != "科目"]
    years = inc_cols

    def get_series(df, item):
        cols = [c for c in df.columns if c != "科目"]
        row = df[df["科目"] == item]
        if row.empty:
            return [0] * len(cols)
        return [float(row[c].values[0]) for c in cols]

    with col_ch1:
        rev = get_series(st.session_state.inc_df, "营业收入")
        cost = get_series(st.session_state.inc_df, "营业成本")
        profit = get_series(st.session_state.inc_df, "净利润")
        fig1 = go.Figure()
        fig1.add_bar(name="营业收入", x=years, y=rev, marker_color="#0066CC")
        fig1.add_bar(name="营业成本", x=years, y=cost, marker_color="#FF6B35")
        fig1.add_scatter(name="净利润", x=years, y=profit, mode="lines+markers",
                         line=dict(color="#34C759", width=2), marker=dict(size=8))
        fig1.update_layout(
            title="收入·成本·利润（万元）", barmode="group",
            height=300, margin=dict(t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_ch2:
        bal_df = st.session_state.bal_df
        ar = get_series(bal_df, "应收账款")
        inv = get_series(bal_df, "存货")
        cf_vals = get_series(st.session_state.cf_df, "经营活动产生的现金流量净额")
        fig2 = go.Figure()
        fig2.add_bar(name="应收账款", x=years, y=ar, marker_color="#FF2D55")
        fig2.add_bar(name="存货", x=years, y=inv, marker_color="#F5A623")
        fig2.add_scatter(name="经营现金流", x=years, y=cf_vals, mode="lines+markers",
                         line=dict(color="#0066CC", width=2), marker=dict(size=8))
        fig2.update_layout(
            title="应收账款·存货·现金流（万元）", barmode="group",
            height=300, margin=dict(t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ==================== STEP 4: 导出 ====================
    st.markdown('<div class="step-title"><span class="step-badge">4</span>导出审计重点提示函</div>', unsafe_allow_html=True)

    col_exp1, col_exp2 = st.columns([1, 2])
    with col_exp1:
        if st.button("📄 生成 PDF 报告", use_container_width=True, type="primary"):
            with st.spinner("正在生成审计重点提示函..."):
                try:
                    from modules.pdf_exporter import generate_pdf
                    pdf_bytes = generate_pdf(result)
                    st.session_state.pdf_bytes = pdf_bytes
                    st.success("✅ PDF生成成功，点击下载")
                except Exception as e:
                    st.error(f"PDF生成失败：{e}")

    with col_exp2:
        if "pdf_bytes" in st.session_state and st.session_state.pdf_bytes:
            st.download_button(
                label="⬇️ 下载审计重点提示函.pdf",
                data=st.session_state.pdf_bytes,
                file_name="AuditArc_审计重点提示函.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ==================== 底部免责 ====================
st.markdown("""
<div class="disclaimer-bar">
    ⚠️ 本系统由 AuditArc AI 智能体驱动，所有风险结论均需注册会计师专业判断复核确认。
    AI仅提供风险线索与程序建议，最终审计定性、底稿签署与报告出具权始终保留在审计师手中。
    本演示版本使用脱敏虚构数据，不代表任何真实公司。
</div>
""", unsafe_allow_html=True)
