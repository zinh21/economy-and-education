import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="상업화 구조 분석", page_icon="🟠", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
    }
    [data-testid="stSidebar"] * { color:#e0e0e0 !important; }
    .hero-banner {
        background:linear-gradient(135deg,#0f3460 0%,#f4a261 100%);
        color:white; padding:2.5rem 2rem; border-radius:20px;
        text-align:center; margin-bottom:2rem;
    }
    .hero-banner h1 { font-size:2.4rem; font-weight:900; margin:0; }
    .hero-banner p  { font-size:1rem; opacity:.9; margin-top:.5rem; }
    .section-title {
        font-size:1.4rem; font-weight:700; color:#1a1a2e;
        border-bottom:3px solid #f4a261;
        padding-bottom:.4rem; margin:2.2rem 0 1rem 0;
    }
    .quote-box {
        background:#fff8f0; border-left:4px solid #f4a261;
        padding:1rem 1.5rem; border-radius:0 8px 8px 0;
        font-style:italic; color:#333; margin:1rem 0;
    }
    .mkt-card {
        background:white; border-radius:12px; padding:1.2rem 1.4rem;
        box-shadow:0 3px 12px rgba(0,0,0,0.09);
        border-top:4px solid #e63946; margin:.5rem 0;
    }
    .mkt-card h4 { color:#e63946; margin:0 0 .5rem 0; font-size:1rem; }
    .stat-highlight {
        background:linear-gradient(135deg,#0f3460,#457b9d);
        color:white; border-radius:10px; padding:1rem 1.2rem; margin:.5rem 0;
    }
    .stat-highlight .val { font-size:1.7rem; font-weight:900; }
    .stat-highlight .lbl { font-size:.82rem; opacity:.85; }
    .anxiety-box {
        background:linear-gradient(135deg,#1a1a2e,#e63946);
        color:white; border-radius:16px; padding:1.8rem;
        margin:1rem 0;
    }
    .anxiety-box h3 { font-size:1.3rem; margin:0 0 1rem 0; }
    .pattern-card {
        background:#f8f9fc; border-radius:10px; padding:1rem 1.2rem;
        border-left:4px solid #f4a261; margin:.6rem 0;
    }
    .premium-card {
        background:linear-gradient(135deg,#f8f9fc,#fff3e0);
        border:1px solid #f4a261; border-radius:12px;
        padding:1.2rem; margin:.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data
def load_cost():
    df = pd.read_csv(
        "data/학교급별_사교육비_총액.csv",
        header=None,
        encoding="utf-8-sig",
    )
    years = df.iloc[0, 1:].tolist()
    items = df.iloc[1, 1:].tolist()
    cols  = ["특성별"] + [f"{y}_{i}" for y, i in zip(years, items)]
    df.columns = cols
    df = df.iloc[2:].reset_index(drop=True).replace("-", np.nan)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data
def load_rate():
    df = pd.read_csv(
        "data/학생_성적_구간별_사교육_참여율.csv",
        header=None,
        encoding="utf-8-sig",
    )
    years = df.iloc[0, 1:].tolist()
    items = df.iloc[1, 1:].tolist()
    cols  = ["과목 및 유형"] + [f"{y}_{i}" for y, i in zip(years, items)]
    df.columns = cols
    df = df.iloc[2:].reset_index(drop=True).replace("-", np.nan)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


cost_df = load_cost()
rate_df = load_rate()

YEARS     = list(range(2016, 2026))
COLOR_ORG = "#f4a261"
COLOR_RED = "#e63946"
COLOR_BLU = "#457b9d"
COLOR_DRK = "#1a1a2e"
COLOR_GRN = "#2a9d8f"


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


def extract_rate_series(row_label, col_keyword):
    row = rate_df[rate_df["과목 및 유형"] == row_label]
    if row.empty:
        return pd.Series(dtype=float)
    vals = {}
    for y in YEARS:
        matched = [c for c in rate_df.columns if c.startswith(str(y)) and col_keyword in c]
        if matched:
            vals[y] = row.iloc[0][matched[0]]
    return pd.Series(vals)


# ── 일반교과 유형 구간 인덱스 ─────────────────────────────────────────────────
idx_start = cost_df[cost_df["특성별"] == "유형: 일반교과 사교육"].index
idx_end   = cost_df[cost_df["특성별"] == "유형: 예체능, 취미·교양 사교육"].index


def get_type_row(key):
    """일반교과 유형 구간 안에서 row 추출"""
    candidates = cost_df[cost_df["특성별"] == key]
    if candidates.empty:
        return pd.DataFrame()
    if len(idx_start) and len(idx_end):
        in_range = candidates[
            (candidates.index > idx_start[0]) &
            (candidates.index < idx_end[0])
        ]
        return in_range if not in_range.empty else candidates.iloc[[0]]
    return candidates.iloc[[0]]


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero-banner">
        <h1>🟠 교육이 어떻게 '돈벌이'가 되는가?</h1>
        <p>사교육 상업화의 구체적 구조 — 과목별 지출, 유형별 시장, 불안 마케팅 패턴</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 · 과목별 사교육비 포트폴리오
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">① 과목별 사교육비 포트폴리오 변화</div>',
    unsafe_allow_html=True,
)

subjects_kw = {
    "국어":            "국어",
    "영어":            "영어",
    "수학":            "수학",
    "사회·과학":       "사회, 과학",
    "논술":            "논술",
    "예체능·취미교양": "과목: 예체능, 취미·교양 사교육",
}

subj_data = []
for label, row_key in subjects_kw.items():
    row = cost_df[cost_df["특성별"] == row_key]
    if row.empty:
        continue
    for y in YEARS:
        matched = [c for c in cost_df.columns
                   if c.startswith(str(y)) and "전체 (억원)" in c]
        if matched:
            v = row.iloc[0][matched[0]]
            if not np.isnan(float(v)) if v is not None else True:
                subj_data.append({"연도": y, "과목": label, "억원": v})

subj_df = pd.DataFrame(subj_data).dropna()

# 100% 누적 면적 차트
fig1 = px.area(
    subj_df, x="연도", y="억원", color="과목",
    groupnorm="fraction",
    color_discrete_sequence=px.colors.qualitative.Bold,
    title="과목별 사교육비 구성 비율 변화 (100% 기준)",
)
fig1.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    yaxis_tickformat=".0%",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    xaxis=dict(dtick=1),
)
st.plotly_chart(fig1, use_container_width=True)

# 절대 금액 라인 차트
fig1b = px.line(
    subj_df, x="연도", y="억원", color="과목",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Bold,
    title="과목별 사교육비 절대 금액 추이 (억원)",
)
fig1b.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    xaxis=dict(dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig1b, use_container_width=True)

# 2024년 과목별 비중 도넛 차트
pie_2024 = subj_df[subj_df["연도"] == 2024]
fig1c = px.pie(
    pie_2024, values="억원", names="과목",
    title="2024년 과목별 사교육비 비중",
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Bold,
)
fig1c.update_layout(font=dict(family="Noto Sans KR"))
st.plotly_chart(fig1c, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 <strong>수학·영어가 전체 일반교과 사교육비의 약 70%를 차지</strong>합니다.
    입시 핵심 과목 중심의 과점 구조가 형성되어 있으며,
    이는 학원·인강 업체들이 수학·영어에 집중 투자하는 경제적 유인이 됩니다.
    특히 <strong>수학 사교육비는 2016년 5.4조 → 2024년 8.3조</strong>로
    10년간 53% 성장했습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 · 사교육 유형별 시장 구조
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">② 사교육 유형별 시장 구조 변화</div>',
    unsafe_allow_html=True,
)

type_labels_ordered = [
    ("학원수강",         "학원수강"),
    ("개인과외",         "개인과외"),
    ("그룹과외",         "그룹과외"),
    ("방문학습지",       "방문학습지"),
    ("유료인터넷·통신강좌", "유료인터넷 및 통신강좌 등"),
]

type_data = []
for t_label, t_key in type_labels_ordered:
    row = get_type_row(t_key)
    if row.empty:
        continue
    for y in YEARS:
        matched = [c for c in cost_df.columns
                   if c.startswith(str(y)) and "전체 (억원)" in c]
        if matched:
            v = row.iloc[0][matched[0]]
            if pd.notna(v):
                type_data.append({"연도": y, "유형": t_label, "억원": float(v)})

type_df = pd.DataFrame(type_data)

fig2 = px.bar(
    type_df, x="연도", y="억원", color="유형",
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title="일반교과 사교육 유형별 시장 규모 추이 (억원)",
)
fig2.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    xaxis=dict(dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig2, use_container_width=True)

# 유료인터넷 성장률 KPI
internet_s = extract_series(cost_df, "유료인터넷 및 통신강좌 등", "전체 (억원)")
v16 = internet_s.get(2016, np.nan)
v24 = internet_s.get(2024, np.nan)
growth_net = (v24 - v16) / v16 * 100 if not (np.isnan(v16) or np.isnan(v24)) else np.nan

hakwon_row = get_type_row("학원수강")
hv16, hv24 = np.nan, np.nan
for y, attr in [(2016, "hv16"), (2024, "hv24")]:
    m = [c for c in cost_df.columns if c.startswith(str(y)) and "전체 (억원)" in c]
    if m and not hakwon_row.empty:
        val = hakwon_row.iloc[0][m[0]]
        if y == 2016:
            hv16 = float(val) if pd.notna(val) else np.nan
        else:
            hv24 = float(val) if pd.notna(val) else np.nan

hakwon_growth = (hv24 - hv16) / hv16 * 100 if not (np.isnan(hv16) or np.isnan(hv24)) else np.nan

c1, c2, c3 = st.columns(3)
stats = [
    (f"+{growth_net:.0f}%",   "유료인터넷 강좌 10년 성장률 (2016→2024)"),
    (f"+{hakwon_growth:.0f}%", "학원수강 10년 성장률 (2016→2024)"),
    (f"{growth_net/hakwon_growth:.1f}배", "인터넷강좌 성장속도 / 학원 성장속도"),
]
for col, (val, lbl) in zip([c1, c2, c3], stats):
    col.markdown(
        f'<div class="stat-highlight">'
        f'<div class="val">{val}</div>'
        f'<div class="lbl">{lbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="quote-box">
    💡 <strong>유료인터넷·통신강좌 시장이 학원보다 훨씬 빠른 속도로 성장</strong>하고 있습니다.
    에듀테크 플랫폼이 구독 모델, 알고리즘 기반 맞춤 추천, 스트리밍 강의로
    사교육을 <strong>24시간 상시 소비재</strong>로 전환시키고 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 · 학원 vs 에듀테크 성장 지수 비교
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">③ 학원 vs 에듀테크(인터넷강좌) 성장 지수 비교</div>',
    unsafe_allow_html=True,
)

compare_data = []
for y in YEARS:
    m = [c for c in cost_df.columns if c.startswith(str(y)) and "전체 (억원)" in c]
    if m:
        if not hakwon_row.empty:
            hv = hakwon_row.iloc[0][m[0]]
            if pd.notna(hv):
                compare_data.append({"연도": y, "유형": "학원수강", "억원": float(hv)})
        iv = internet_s.get(y, np.nan)
        if not np.isnan(iv):
            compare_data.append({"연도": y, "유형": "유료인터넷·통신강좌", "억원": iv})

compare_df = pd.DataFrame(compare_data)

# 2016 기준 지수화
base_map = compare_df[compare_df["연도"] == 2016].set_index("유형")["억원"].to_dict()
compare_df["지수(2016=100)"] = compare_df.apply(
    lambda r: r["억원"] / base_map[r["유형"]] * 100
    if r["유형"] in base_map else np.nan,
    axis=1,
)

fig3 = px.line(
    compare_df, x="연도", y="지수(2016=100)", color="유형",
    markers=True,
    color_discrete_map={
        "학원수강":            COLOR_BLU,
        "유료인터넷·통신강좌": COLOR_RED,
    },
    title="학원 vs 에듀테크 성장 지수 (2016=100 기준)",
)
fig3.add_hline(y=100, line_dash="dash", line_color="gray",
               annotation_text="기준선(2016)")
fig3.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    xaxis=dict(dtick=1),
    yaxis_title="성장 지수 (2016=100)",
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 2020년 코로나 팬데믹이 에듀테크의 폭발적 성장을 촉발했습니다.
    <strong>비대면 학습이 일상화되면서 인터넷 강좌는 '대체재'에서
    '필수재'로 전환</strong>되었고, 팬데믹 이후에도 성장세가 꺾이지 않았습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 · 예체능·취미교양 팽창 — 수요 다각화 전략
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">④ 예체능·취미교양 사교육 팽창 — 수요 다각화 전략</div>',
    unsafe_allow_html=True,
)

art_subjects = {
    "음악":     "음악",
    "미술":     "미술",
    "체육":     "체육",
    "취미·교양": "취미·교양",
}

art_data = []
for label, row_key in art_subjects.items():
    row = cost_df[cost_df["특성별"] == row_key]
    if row.empty:
        continue
    for y in YEARS:
        matched = [c for c in cost_df.columns
                   if c.startswith(str(y)) and "전체 (억원)" in c]
        if matched:
            v = row.iloc[0][matched[0]]
            if pd.notna(v):
                art_data.append({"연도": y, "종류": label, "억원": float(v)})

art_df = pd.DataFrame(art_data)

col_left, col_right = st.columns(2)

with col_left:
    fig4a = px.line(
        art_df, x="연도", y="억원", color="종류",
        markers=True,
        color_discrete_sequence=[COLOR_RED, COLOR_ORG, COLOR_GRN, COLOR_BLU],
        title="예체능·취미교양 세부 사교육비 추이",
    )
    fig4a.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Noto Sans KR"),
        xaxis=dict(dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig4a, use_container_width=True)

with col_right:
    # 2016, 2024 비교 bar
    art_compare = art_df[art_df["연도"].isin([2016, 2024])]
    fig4b = px.bar(
        art_compare, x="종류", y="억원", color="연도",
        barmode="group",
        color_discrete_map={2016: "#adb5bd", 2024: COLOR_RED},
        title="2016 vs 2024 예체능·취미교양 비교",
    )
    fig4b.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Noto Sans KR"),
    )
    st.plotly_chart(fig4b, use_container_width=True)

# 체육 성장률
sport_s = extract_series(cost_df, "체육", "전체 (억원)")
sp16 = sport_s.get(2016, np.nan)
sp24 = sport_s.get(2024, np.nan)
sport_growth = (sp24 - sp16) / sp16 * 100 if not (np.isnan(sp16) or np.isnan(sp24)) else np.nan

hobby_s = extract_series(cost_df, "취미·교양", "전체 (억원)")
hb16 = hobby_s.get(2016, np.nan)
hb24 = hobby_s.get(2024, np.nan)
hobby_growth = (hb24 - hb16) / hb16 * 100 if not (np.isnan(hb16) or np.isnan(hb24)) else np.nan

c1, c2 = st.columns(2)
c1.markdown(
    f'<div class="stat-highlight"><div class="val">+{sport_growth:.0f}%</div>'
    f'<div class="lbl">체육 사교육비 10년 성장률</div></div>',
    unsafe_allow_html=True,
)
c2.markdown(
    f'<div class="stat-highlight"><div class="val">+{hobby_growth:.0f}%</div>'
    f'<div class="lbl">취미·교양 사교육비 10년 성장률</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="quote-box">
    💡 <strong>"스펙이 되는 취미"</strong> 담론이 확산되며 체육·예술 사교육이
    입시 도구로 편입되고 있습니다. 산업은 불안감을 "입시 스펙"으로 연결해
    소비를 확장합니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 · 불안 마케팅의 데이터 근거
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">⑤ 불안 마케팅의 효과 — "잘하는 학생도 더 한다"</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="anxiety-box">
        <h3>🎯 불안 마케팅(Anxiety Marketing)이란?</h3>
        <p>학원·에듀테크 업체가 <strong>"지금 안 하면 뒤처진다"</strong>,
        <strong>"상위권도 다 다닌다"</strong>,
        <strong>"이 강좌 없이는 SKY 불가"</strong> 같은 메시지로
        학생·학부모의 불안감을 자극해 수요를 창출하는 마케팅 전략입니다.<br><br>
        아래 데이터는 이 전략이 <b>실제로 효과가 있음</b>을 통계로 보여줍니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 성적 상위 10% 참여율 추이
top10_subjects = {
    "전체 사교육": "사교육 참여",
    "수학":        "수학",
    "영어":        "영어",
    "국어":        "국어",
}

top10_data = []
for label, key in top10_subjects.items():
    s = extract_rate_series(key, "상위10% 이내")
    for y, v in s.items():
        if pd.notna(v):
            top10_data.append({"연도": y, "과목": label, "상위10% 참여율(%)": float(v)})

top10_df = pd.DataFrame(top10_data)

fig5 = px.line(
    top10_df, x="연도", y="상위10% 참여율(%)", color="과목",
    markers=True,
    color_discrete_sequence=[COLOR_RED, COLOR_ORG, COLOR_BLU, COLOR_GRN],
    title="성적 상위 10% 학생의 과목별 사교육 참여율 추이",
)
fig5.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    xaxis=dict(dtick=1),
    yaxis_title="참여율 (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 성적 <strong>상위 10% 학생들의 사교육 참여율이 꾸준히 상승</strong>하고 있습니다.
    이미 잘하는 학생들도 "더 잘하기 위해" 사교육을 받는 구조가 정착됐으며,
    이는 사교육 업체의 <strong>"최상위권 마케팅"이 효과적임을 입증</strong>합니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# 상·하위 격차 히트맵
st.subheader("과목별 × 연도별 성적 상위 10% 참여율 히트맵")

heatmap_subjects = ["사교육 참여", "수학", "영어", "국어", "사회, 과학", "논술"]
heatmap_rows, heatmap_cols = [], []
heat_data = {}

for subj in heatmap_subjects:
    s = extract_rate_series(subj, "상위10% 이내")
    heat_data[subj] = [float(s.get(y, np.nan)) for y in YEARS]

heat_df = pd.DataFrame(heat_data, index=YEARS).T

fig5b = px.imshow(
    heat_df,
    color_continuous_scale="Reds",
    title="과목별 × 연도별 성적 상위 10% 사교육 참여율 히트맵 (%)",
    aspect="auto",
    text_auto=".1f",
)
fig5b.update_layout(
    font=dict(family="Noto Sans KR"),
    xaxis_title="연도",
    yaxis_title="과목",
)
st.plotly_chart(fig5b, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 · 상업화 패턴 분석 — 구조적 메커니즘
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">⑥ 사교육 상업화의 구조적 메커니즘</div>',
    unsafe_allow_html=True,
)

st.markdown("#### 📌 데이터로 확인된 3가지 상업화 패턴")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="mkt-card">
            <h4>🔴 패턴 1 · 불안 마케팅</h4>
            <p><strong>"지금 안 하면 뒤처진다"</strong></p>
            <ul>
                <li>성적 상위권도 참여율 지속 상승</li>
                <li>수학·영어 독과점 구조 심화</li>
                <li>코로나 이후 급반등</li>
            </ul>
            <p><b>근거:</b> 상위 10% 수학 참여율
            2016년 52% → 2024년 64%</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="mkt-card">
            <h4>🟠 패턴 2 · 프리미엄화·고가화</h4>
            <p><strong>"더 비싼 게 더 좋다"</strong></p>
            <ul>
                <li>개인과외 단가 지속 상승</li>
                <li>1:1 맞춤 컨설팅 시장 확대</li>
                <li>진로·진학 상담 시장 신설</li>
            </ul>
            <p><b>근거:</b> 진로·진학 상담 사교육비
            2017년 신설 → 2024년 1,006억원</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="mkt-card">
            <h4>🟡 패턴 3 · 디지털 구독화</h4>
            <p><strong>"끊을 수 없게 만든다"</strong></p>
            <ul>
                <li>인터넷·통신강좌 3배 성장</li>
                <li>알고리즘 맞춤 추천</li>
                <li>구독형 월정액 모델 확산</li>
            </ul>
            <p><b>근거:</b> 유료인터넷강좌
            2016년 3,042억 → 2024년 9,658억</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 · 진로·진학 상담 시장 — 신(新)사교육 영역
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">⑦ 신(新)사교육 영역 — 진로·진학 상담의 상업화</div>',
    unsafe_allow_html=True,
)

consult_s = extract_series(cost_df, "과목: 진로·진학 학습상담", "전체 (억원)")
consult_data = [
    {"연도": y, "억원": float(v)}
    for y, v in consult_s.items() if pd.notna(v)
]
consult_df = pd.DataFrame(consult_data)

consult_rate_s = extract_rate_series("과목: 진로·진학 학습상담", "평  균")
consult_rate_top = extract_rate_series("과목: 진로·진학 학습상담", "상위10% 이내")
consult_rate_bot = extract_rate_series("과목: 진로·진학 학습상담", "81 ~ 100%")

rate_compare = []
for y in YEARS:
    avg_v = consult_rate_s.get(y, np.nan)
    top_v = consult_rate_top.get(y, np.nan)
    bot_v = consult_rate_bot.get(y, np.nan)
    if pd.notna(avg_v):
        rate_compare.append({"연도": y, "구분": "전체 평균",  "참여율(%)": float(avg_v)})
    if pd.notna(top_v):
        rate_compare.append({"연도": y, "구분": "상위 10%",  "참여율(%)": float(top_v)})
    if pd.notna(bot_v):
        rate_compare.append({"연도": y, "구분": "하위 20%",  "참여율(%)": float(bot_v)})

rate_compare_df = pd.DataFrame(rate_compare)

col_l, col_r = st.columns(2)

with col_l:
    fig6a = px.bar(
        consult_df, x="연도", y="억원",
        color_discrete_sequence=[COLOR_ORG],
        title="진로·진학 학습상담 사교육비 총액 (억원)",
    )
    fig6a.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Noto Sans KR"),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig6a, use_container_width=True)

with col_r:
    fig6b = px.line(
        rate_compare_df, x="연도", y="참여율(%)", color="구분",
        markers=True,
        color_discrete_map={
            "전체 평균": COLOR_ORG,
            "상위 10%":  COLOR_RED,
            "하위 20%":  "#adb5bd",
        },
        title="진로·진학 상담 사교육 참여율 격차",
    )
    fig6b.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Noto Sans KR"),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig6b, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 2017년 통계에 처음 등장한 <strong>진로·진학 상담 사교육</strong>은
    2024년 1,007억원 규모로 성장했습니다.
    특히 <strong>상위 10% 학생의 참여율이 하위 20%의 약 3~4배</strong>에 달해,
    고가의 입시 컨설팅이 고소득층 중심의 "프리미엄 사교육"으로 자리잡고 있음을 보여줍니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 · 방문학습지 → 디지털 전환 사례
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">⑧ 아날로그 → 디지털 전환: 방문학습지의 몰락과 인터넷강좌의 부상</div>',
    unsafe_allow_html=True,
)

# 방문학습지 vs 인터넷 강좌 비교
visit_row = get_type_row("방문학습지")
digital_comparison = []

for y in YEARS:
    m = [c for c in cost_df.columns if c.startswith(str(y)) and "전체 (억원)" in c]
    if m:
        if not visit_row.empty:
            vv = visit_row.iloc[0][m[0]]
            if pd.notna(vv):
                digital_comparison.append(
                    {"연도": y, "유형": "방문학습지", "억원": float(vv)}
                )
        iv = internet_s.get(y, np.nan)
        if not np.isnan(iv):
            digital_comparison.append(
                {"연도": y, "유형": "유료인터넷·통신강좌", "억원": iv}
            )

digital_df = pd.DataFrame(digital_comparison)

fig7 = go.Figure()

for유형, color, dash in [
    ("방문학습지",       "#adb5bd", "dash"),
    ("유료인터넷·통신강좌", COLOR_RED, "solid"),
]:
    sub = digital_df[digital_df["유형"] == 유형]
    fig7.add_trace(go.Scatter(
        x=sub["연도"], y=sub["억원"],
        name=유형,
        mode="lines+markers",
        line=dict(color=color, dash=dash, width=3),
        marker=dict(size=8),
    ))

# 교차점 표시
fig7.add_annotation(
    x=2018, y=3865,
    text="교차점:<br>인터넷강좌 > 방문학습지",
    showarrow=True, arrowhead=2,
    ax=60, ay=-50,
    font=dict(color=COLOR_RED, size=11),
)
fig7.update_layout(
    title="방문학습지 vs 유료인터넷강좌 시장 규모 추이 (억원)",
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    xaxis=dict(dtick=1, title="연도"),
    yaxis=dict(title="억원"),
    legend=dict(orientation="h"),
)
st.plotly_chart(fig7, use_container_width=True)

st.markdown(
    """
    <div class="quote-box">
    💡 한때 사교육의 상징이었던 <strong>방문학습지는 2018년 이후 지속 하락</strong>하는 반면,
    유료인터넷강좌는 역전에 성공하며 <strong>디지털 사교육 시대</strong>를 열었습니다.
    에듀테크 기업들은 이 전환을 주도하며 사교육을 플랫폼 경제로 편입시키고 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 · 상업화 구조 종합 요약
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">⑨ 사교육 상업화 구조 종합 요약</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="premium-card">
    <h4>📋 사교육 산업화의 4단계 메커니즘</h4>
    </div>
    """,
    unsafe_allow_html=True,
)

steps = [
    (
        "1단계 · 불안 조성",
        "입시 경쟁 심화 → '안 하면 뒤처진다' 공포 마케팅 → 수요 창출",
        "상위 10%도 참여율 77%로 상승 (2024)",
    ),
    (
        "2단계 · 과목 과점화",
        "수학·영어 중심 독과점 → 규모의 경제 → 스타강사 브랜드화",
        "수학+영어 = 전체 일반교과비의 약 70%",
    ),
    (
        "3단계 · 프리미엄화",
        "상위권 맞춤 고가 컨설팅 → 진로·진학 상담 시장 창출",
        "진로상담 사교육: 2017년 신설 → 2024년 1,007억원",
    ),
    (
        "4단계 · 플랫폼 구독화",
        "에듀테크 구독 모델 → 알고리즘 추천 → 이탈 방지 설계",
        "인터넷강좌 2016→2024년 217% 성장",
    ),
]

for title, desc, data in steps:
    st.markdown(
        f"""
        <div class="pattern-card">
            <strong>{title}</strong><br>
            {desc}<br>
            <span style="color:{COLOR_RED}; font-weight:700;">📊 데이터: {data}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 최종 종합 차트 — 전체 사교육비 + 유형별 비중 변화
st.subheader("📊 종합: 사교육비 총액과 유형별 구성 변화 (2016–2025)")

# 전체 총액 라인 + 유형별 비중 콤보
fig9 = make_subplots(
    rows=2, cols=1,
    subplot_titles=("전체 사교육비 총액 (조원)", "유형별 비중 변화 (%)"),
    vertical_spacing=0.15,
)

total_s = extract_series(cost_df, "전체", "전체 (억원)")
total_years = [y for y in YEARS if y in total_s and pd.notna(total_s[y])]
total_vals  = [total_s[y] / 10000 for y in total_years]  # 억원 → 조원

fig9.add_trace(
    go.Bar(
        x=total_years, y=total_vals,
        name="총액(조원)", marker_color=COLOR_RED,
        text=[f"{v:.1f}조" for v in total_vals],
        textposition="outside",
    ),
    row=1, col=1,
)

# 유형별 비중
type_pivot = type_df.pivot(index="연도", columns="유형", values="억원").fillna(0)
type_pivot["합계"] = type_pivot.sum(axis=1)
colors_type = [COLOR_RED, COLOR_ORG, COLOR_BLU, COLOR_GRN, "#9b5de5"]
for i, col_name in enumerate(
    ["학원수강", "개인과외", "그룹과외", "방문학습지", "유료인터넷·통신강좌"]
):
    if col_name in type_pivot.columns:
        pct = type_pivot[col_name] / type_pivot["합계"] * 100
        fig9.add_trace(
            go.Scatter(
                x=pct.index.tolist(),
                y=pct.values.tolist(),
                name=col_name,
                mode="lines+markers",
                line=dict(color=colors_type[i], width=2),
                marker=dict(size=6),
            ),
            row=2, col=1,
        )

fig9.update_layout(
    height=700,
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Noto Sans KR"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    showlegend=True,
)
fig9.update_xaxes(dtick=1)
st.plotly_chart(fig9, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#888; font-size:.85rem; padding:1rem 0;">
        📊 데이터 출처: 통계청 사교육비조사 (2016–2025)<br>
        🏫 제작: 당곡고등학교 | 주제: 사교육 상업화 분석 보고서
    </div>
    """,
    unsafe_allow_html=True,
)
