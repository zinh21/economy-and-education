import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="문제의 심각성", page_icon="🔴", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
    }
    [data-testid="stSidebar"] * { color:#e0e0e0 !important; }
    .hero-banner {
        background: linear-gradient(135deg,#1a1a2e 0%,#e63946 100%);
        color:white; padding:2.5rem 2rem; border-radius:20px;
        text-align:center; margin-bottom:2rem;
    }
    .hero-banner h1 { font-size:2.4rem; font-weight:900; margin:0; }
    .hero-banner p  { font-size:1rem; opacity:.9; margin-top:.5rem; }
    .kpi-box {
        background:linear-gradient(135deg,#e63946,#c1121f);
        color:white; border-radius:12px; padding:1.2rem; text-align:center;
    }
    .kpi-box .kpi-value { font-size:1.9rem; font-weight:900; }
    .kpi-box .kpi-label { font-size:.82rem; opacity:.85; margin-top:4px; }
    .section-title {
        font-size:1.4rem; font-weight:700; color:#1a1a2e;
        border-bottom:3px solid #e63946;
        padding-bottom:.4rem; margin:2.2rem 0 1rem 0;
    }
    .quote-box {
        background:#fff3f3; border-left:4px solid #e63946;
        padding:1rem 1.5rem; border-radius:0 8px 8px 0;
        font-style:italic; color:#333; margin:1rem 0;
    }
    .insight-card {
        background:#fffdf0; border:1px solid #f4a261;
        border-radius:10px; padding:1rem 1.2rem; margin:.6rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 데이터 로드 & 전처리 ──────────────────────────────────────────────────────
@st.cache_data
def load_cost_data():
    path = DATA_DIR / "학교급별_사교육비_총액.csv"
    df = pd.read_csv(str(path), header=None, encoding="utf-8-sig")
    years = df.iloc[0, 1:].tolist()
    items = df.iloc[1, 1:].tolist()
    cols  = ["특성별"] + [f"{y}_{i}" for y, i in zip(years, items)]
    df.columns = cols
    df = df.iloc[2:].reset_index(drop=True).replace("-", np.nan)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data
def load_rate_data():
    path = DATA_DIR / "학생_성적_구간별_사교육_참여율.csv"
    df = pd.read_csv(str(path), header=None, encoding="utf-8-sig")
    years = df.iloc[0, 1:].tolist()
    items = df.iloc[1, 1:].tolist()
    cols  = ["과목 및 유형"] + [f"{y}_{i}" for y, i in zip(years, items)]
    df.columns = cols
    df = df.iloc[2:].reset_index(drop=True).replace("-", np.nan)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


cost_df = load_cost_data()
rate_df = load_rate_data()

YEARS     = list(range(2016, 2026))
COLOR_RED = "#e63946"
COLOR_ORG = "#f4a261"
COLOR_BLU = "#457b9d"


def extract_series(df, row_label, col_keyword, id_col="특성별"):
    row = df[df[id_col] == row_label]
    if row.empty:
        return pd.Series(dtype=float)
    vals = {}
    for y in YEARS:
        matched = [c for c in df.columns if c.startswith(str(y)) and col_keyword in c]
        if matched:
            vals[y] = row.iloc[0][matched[0]]
    return pd.Series(vals)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero-banner">
        <h1>🔴 사교육, 얼마나 심각한가?</h1>
        <p>2016–2025 통계청 사교육비 데이터로 보는 교육 불평등의 민낯</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 0 · KPI 요약
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 핵심 수치 요약</div>', unsafe_allow_html=True)

total_series = extract_series(cost_df, "전체", "전체 (억원)")
val_2016 = total_series.get(2016, np.nan)
val_2024 = total_series.get(2024, np.nan)
growth_rate = (val_2024 - val_2016) / val_2016 * 100 if not np.isnan(val_2016) else np.nan

rate_row = rate_df[rate_df["과목 및 유형"] == "사교육 참여"]
top_col = [c for c in rate_df.columns if c.startswith("2024") and "상위10%" in c]
bot_col = [c for c in rate_df.columns if c.startswith("2024") and "81 ~ 100%" in c]
top_rate = float(rate_row.iloc[0][top_col[0]]) if top_col else np.nan
bot_rate = float(rate_row.iloc[0][bot_col[0]]) if bot_col else np.nan
gap      = top_rate - bot_rate if not (np.isnan(top_rate) or np.isnan(bot_rate)) else np.nan

city_s  = extract_series(cost_df, "서울",     "전체 (억원)")
rural_s = extract_series(cost_df, "읍면지역", "전체 (억원)")
city_24  = city_s.get(2024,  np.nan)
rural_24 = rural_s.get(2024, np.nan)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (f"{val_2024/10000:.1f}조 원",          "2024년 사교육비 총액"),
    (f"+{growth_rate:.0f}%",                 "2016→2024 사교육비 증가율"),
    (f"{gap:.1f}%p",                         "성적 상위10% vs 하위20%\n참여율 격차 (2024)"),
    (f"{city_24/rural_24:.1f}배",            "서울 vs 읍면지역\n사교육비 규모 비율 (2024)"),
]
for col, (val, lbl) in zip([k1, k2, k3, k4], kpis):
    col.markdown(
        f'<div class="kpi-box">'
        f'<div class="kpi-value">{val}</div>'
        f'<div class="kpi-label">{lbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 · 사교육비 총액 추이
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">① 사교육비 총액 10년 추이 (2016–2025)</div>',
    unsafe_allow_html=True,
)

regions = {
    "전체 합계":  "전체",
    "서울":       "서울",
    "광역시":     "광역시",
    "중소도시":   "중소도시",
    "읍면지역":   "읍면지역",
}
trend_data = []
for label, row_key in regions.items():
    s = extract_series(cost_df, row_key, "전체 (억원)")
    for y, v in s.items():
        if pd.notna(v):
            trend_data.append({"연도": y, "구분": label, "사교육비(억원)": float(v)})

trend_df = pd.DataFrame(trend_data)

fig1 = px.line(
    trend_df,
    x="연도", y="사교육비(억원)", color="구분",
    markers=True,
    color_discrete_map={
        "전체 합계": COLOR_RED,
        "서울":      COLOR_ORG,
        "광역시":    COLOR_BLU,
        "중소도시":  "#2a9d8f",
        "읍면지역":  "#adb5bd",
    },
    title="지역별 연간 사교육비 총액 추이",
)
fig1.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis_title="사교육비 (억원)",
    xaxis=dict(dtick=1),
)
fig1.add_annotation(
    x=2021,
    y=float(total_series.get(2021, 0)),
    text="코로나 이후<br>급반등",
    showarrow=True, arrowhead=2, ax=50, ay=-40,
    font=dict(color=COLOR_RED, size=11),
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 <strong>2016년 약 18조 원 → 2024년 약 29조 원</strong>으로 10년 만에 61% 증가.
    코로나 팬데믹(2020)으로 일시 하락했으나 2021년부터 폭발적으로 반등하며
    사상 최고치를 경신했습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 · 학교급별 구성
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">② 학교급별 사교육비 구성 변화</div>',
    unsafe_allow_html=True,
)

col_a, col_b = st.columns(2)

grade_labels = {
    "초등학교": "초등학교 (억원)",
    "중학교":   "중학교 (억원)",
    "고등학교": "고등학교 (억원)",
}

bar_data = []
row_total = cost_df[cost_df["특성별"] == "전체"]
for y in YEARS:
    for grade, kw in grade_labels.items():
        matched = [c for c in cost_df.columns if c.startswith(str(y)) and kw in c]
        if matched:
            v = row_total.iloc[0][matched[0]]
            if pd.notna(v):
                bar_data.append({"연도": y, "학교급": grade, "억원": float(v)})

bar_df = pd.DataFrame(bar_data)

with col_a:
    fig2 = px.bar(
        bar_df, x="연도", y="억원", color="학교급",
        barmode="stack",
        color_discrete_map={
            "초등학교": COLOR_RED,
            "중학교":   COLOR_ORG,
            "고등학교": COLOR_BLU,
        },
        title="학교급별 사교육비 총액 (누적)",
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Noto Sans KR"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    pie_2024 = bar_df[bar_df["연도"] == 2024]
    fig3 = px.pie(
        pie_2024, values="억원", names="학교급",
        title="2024년 학교급별 사교육비 비중",
        color_discrete_sequence=[COLOR_RED, COLOR_ORG, COLOR_BLU],
        hole=0.4,
    )
    fig3.update_layout(font=dict(family="Noto Sans KR"))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 <strong>초등학생 사교육비가 전체의 약 45%</strong>를 차지하며 가장 많습니다.
    취학 전후부터 시작되는 조기 사교육이 이미 거대한 시장을 형성하고 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 · 지역 격차
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">③ 지역별 사교육비 격차</div>',
    unsafe_allow_html=True,
)

region_rows = {
    "서울":     "서울",
    "광역시":   "광역시",
    "중소도시": "중소도시",
    "읍면지역": "읍면지역",
}
gap_years = [2016, 2019, 2022, 2024]
gap_data  = []
for r_label, r_key in region_rows.items():
    s = extract_series(cost_df, r_key, "전체 (억원)")
    for y in gap_years:
        v = s.get(y, np.nan)
        if pd.notna(v):
            gap_data.append({"연도": str(y), "지역": r_label, "사교육비(억원)": float(v)})

gap_df = pd.DataFrame(gap_data)

fig4 = px.bar(
    gap_df, x="지역", y="사교육비(억원)", color="연도",
    barmode="group",
    color_discrete_sequence=["#adb5bd", COLOR_ORG, COLOR_BLU, COLOR_RED],
    title="지역별 사교육비 총액 비교 (선택 연도)",
)
fig4.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
)
st.plotly_chart(fig4, use_container_width=True)

# 서울/읍면 배율 추이
ratio_data = []
for y in YEARS:
    sv = city_s.get(y, np.nan)
    rv = rural_s.get(y, np.nan)
    if pd.notna(sv) and pd.notna(rv) and rv != 0:
        ratio_data.append({"연도": y, "서울/읍면 배율": float(sv) / float(rv)})

ratio_df = pd.DataFrame(ratio_data)

fig5 = px.line(
    ratio_df, x="연도", y="서울/읍면 배율",
    markers=True,
    title="서울 vs 읍면지역 사교육비 규모 배율",
    color_discrete_sequence=[COLOR_RED],
)
fig5.add_hline(y=2, line_dash="dash", line_color="gray",
               annotation_text="2배 기준선")
fig5.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    yaxis_title="배율 (서울 ÷ 읍면)",
    xaxis=dict(dtick=1),
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 서울의 사교육비는 읍면지역의 <strong>약 1.9~2.0배</strong> 수준입니다.
    도시-농촌 간 교육 기회 불균형이 구조적으로 고착화되고 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 · 성적 구간별 참여율
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">④ 성적 구간별 사교육 참여율 격차</div>',
    unsafe_allow_html=True,
)

grade_cols_map = {
    "상위 10%": "상위10% 이내",
    "11~30%":   "11 ~ 30%",
    "31~60%":   "31 ~ 60%",
    "61~80%":   "61 ~ 80%",
    "하위 20%": "81 ~ 100%",
}

participation_row = rate_df[rate_df["과목 및 유형"] == "사교육 참여"]
part_data = []
for y in YEARS:
    for g_label, g_kw in grade_cols_map.items():
        matched = [c for c in rate_df.columns if c.startswith(str(y)) and g_kw in c]
        if matched:
            v = participation_row.iloc[0][matched[0]]
            if pd.notna(v):
                part_data.append({"연도": y, "성적 구간": g_label, "참여율(%)": float(v)})

part_df = pd.DataFrame(part_data)

fig6 = px.line(
    part_df, x="연도", y="참여율(%)", color="성적 구간",
    markers=True,
    color_discrete_map={
        "상위 10%": COLOR_RED,
        "11~30%":   COLOR_ORG,
        "31~60%":   COLOR_BLU,
        "61~80%":   "#2a9d8f",
        "하위 20%": "#adb5bd",
    },
    title="성적 구간별 사교육 참여율 추이",
)
fig6.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    yaxis_title="참여율 (%)",
    xaxis=dict(dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig6, use_container_width=True)

# 레이더 차트 (2016 vs 2024)
st.subheader("2016 vs 2024 · 성적 구간별 참여율 비교")
categories = list(grade_cols_map.keys())
radar_data = {}
for y in [2016, 2024]:
    vals = []
    for g_kw in grade_cols_map.values():
        matched = [c for c in rate_df.columns if c.startswith(str(y)) and g_kw in c]
        if matched:
            v = participation_row.iloc[0][matched[0]]
            vals.append(float(v) if pd.notna(v) else 0.0)
        else:
            vals.append(0.0)
    radar_data[y] = vals

fig7 = go.Figure()
for y, color in zip([2016, 2024], ["#adb5bd", COLOR_RED]):
    fig7.add_trace(go.Scatterpolar(
        r=radar_data[y] + [radar_data[y][0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=str(y),
        line=dict(color=color),
        fillcolor=color,
        opacity=0.35,
    ))
fig7.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 90])),
    showlegend=True,
    font=dict(family="Noto Sans KR"),
    title="성적 구간별 사교육 참여율 레이더 차트",
    paper_bgcolor="white",
)
st.plotly_chart(fig7, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 성적 <strong>상위 10% 학생의 참여율(약 77%)이 하위 20%(약 56%)보다
    21%p 높습니다.</strong>
    사교육이 성적 불평등을 심화시키는 구조적 메커니즘으로 작동하고 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 · 과목별 성적 구간 참여율 격차
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">⑤ 과목별 성적 구간 참여율 격차 (2024)</div>',
    unsafe_allow_html=True,
)

subjects = ["국어", "영어", "수학", "사회, 과학", "논술"]
subject_gap = []

for subj in subjects:
    row = rate_df[rate_df["과목 및 유형"] == subj]
    if row.empty:
        continue
    top_c = [c for c in rate_df.columns if c.startswith("2024") and "상위10%" in c]
    bot_c = [c for c in rate_df.columns if c.startswith("2024") and "81 ~ 100%" in c]
    avg_c = [c for c in rate_df.columns if c.startswith("2024") and "평  균" in c]
    if top_c and bot_c and avg_c:
        t = row.iloc[0][top_c[0]]
        b = row.iloc[0][bot_c[0]]
        a = row.iloc[0][avg_c[0]]
        if pd.notna(t) and pd.notna(b):
            subject_gap.append({
                "과목": subj,
                "상위10%": float(t),
                "하위20%": float(b),
                "평균":    float(a) if pd.notna(a) else np.nan,
                "격차":    float(t) - float(b),
            })

gap_df2 = pd.DataFrame(subject_gap)

fig8 = go.Figure()
fig8.add_trace(go.Bar(
    x=gap_df2["과목"], y=gap_df2["상위10%"],
    name="상위 10%", marker_color=COLOR_RED,
))
fig8.add_trace(go.Bar(
    x=gap_df2["과목"], y=gap_df2["하위20%"],
    name="하위 20%", marker_color="#adb5bd",
))
fig8.add_trace(go.Scatter(
    x=gap_df2["과목"], y=gap_df2["격차"],
    name="격차(상위-하위)", mode="lines+markers",
    line=dict(color=COLOR_ORG, width=2, dash="dot"),
    yaxis="y2",
))
fig8.update_layout(
    barmode="group",
    yaxis=dict(title="참여율 (%)"),
    yaxis2=dict(title="격차 (%p)", overlaying="y", side="right"),
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    title="과목별 성적 상위/하위 사교육 참여율 격차 (2024)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig8, use_container_width=True)

for row_item in subject_gap:
    st.markdown(
        f'<div class="insight-card">'
        f'📌 <strong>{row_item["과목"]}</strong>: '
        f'상위 10% {row_item["상위10%"]:.1f}% vs 하위 20% {row_item["하위20%"]:.1f}% '
        f'→ <b>격차 {row_item["격차"]:.1f}%p</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption("데이터 출처: 통계청 사교육비조사 (2016–2025) | 당곡고등학교")
