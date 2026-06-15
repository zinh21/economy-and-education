import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path

st.set_page_config(
    page_title="사교육 상업화 분석 보고서",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .main { background-color: #f8f9fc; }
    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #e63946 100%);
        color: white; padding: 3rem 2rem; border-radius: 20px;
        text-align: center; margin-bottom: 2rem;
    }
    .hero-banner h1 { font-size: 2.8rem; font-weight: 900; margin: 0; }
    .hero-banner p  { font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem; }
    .report-card {
        background: white; border-radius: 16px; padding: 2rem; margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #e63946;
    }
    .report-card h3 { color: #1a1a2e; margin-top: 0; }
    .kpi-box {
        background: linear-gradient(135deg, #e63946, #c1121f);
        color: white; border-radius: 12px; padding: 1.2rem;
        text-align: center; margin: 0.3rem 0;
    }
    .kpi-box .kpi-value { font-size: 1.8rem; font-weight: 900; }
    .kpi-box .kpi-label { font-size: 0.82rem; opacity: 0.85; margin-top: 4px; }
    .status-ok {
        background: #d4edda; border: 1px solid #28a745;
        border-radius: 8px; padding: 0.8rem 1rem; margin: 0.3rem 0;
        color: #155724; font-weight: 600;
    }
    .status-err {
        background: #f8d7da; border: 1px solid #e63946;
        border-radius: 8px; padding: 0.8rem 1rem; margin: 0.3rem 0;
        color: #721c24; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 경로 탐색 ─────────────────────────────────────────────────────────────────
def find_csv(candidates: list[str]) -> str | None:
    """
    여러 루트 경로 × 여러 파일명 조합을 탐색해서
    실제 존재하는 첫 번째 경로 문자열을 반환.
    없으면 None 반환.
    """
    roots = [
        Path(__file__).resolve().parent,                  # app.py 와 같은 위치
        Path(os.getcwd()),                                 # 현재 작업 디렉토리
        Path("/mount/src/economy-and-education"),          # Streamlit Cloud
        Path("/mount/src"),
    ]
    for root in roots:
        for name in candidates:
            for p in [root / "data" / name, root / name]:
                if p.exists():
                    return str(p)
    return None


# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data
def load_cost():
    path = find_csv([
        "cost_by_school.csv",
        "학교급별_사교육비_총액.csv",
        "학교급별_사교육비_총액_20260610132639.csv",
    ])
    if path is None:
        return None, None
    df = pd.read_csv(path, header=None, encoding="utf-8-sig")
    years = df.iloc[0, 1:].tolist()
    items = df.iloc[1, 1:].tolist()
    cols  = ["특성별"] + [f"{y}_{i}" for y, i in zip(years, items)]
    df.columns = cols
    df = df.iloc[2:].reset_index(drop=True).replace("-", np.nan)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, path


@st.cache_data
def load_rate():
    path = find_csv([
        "rate_by_grade.csv",
        "학생_성적_구간별_사교육_참여율.csv",
        "학생_성적_구간별_사교육_참여율_20260610133731.csv",
    ])
    if path is None:
        return None, None
    df = pd.read_csv(path, header=None, encoding="utf-8-sig")
    years = df.iloc[0, 1:].tolist()
    items = df.iloc[1, 1:].tolist()
    cols  = ["과목 및 유형"] + [f"{y}_{i}" for y, i in zip(years, items)]
    df.columns = cols
    df = df.iloc[2:].reset_index(drop=True).replace("-", np.nan)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, path


cost_df, cost_path = load_cost()
rate_df, rate_path = load_rate()

# ── 데이터 상태 확인 ──────────────────────────────────────────────────────────
data_ok = (cost_df is not None) and (rate_df is not None)

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-banner">
        <h1>📚 사교육 상업화 분석 보고서</h1>
        <p>2016 – 2025 통계청 데이터로 보는 한국 사교육 산업화의 실태</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 데이터 로드 상태 표시 ─────────────────────────────────────────────────────
with st.expander("🗂️ 데이터 로드 상태 확인", expanded=not data_ok):
    c1, c2 = st.columns(2)
    with c1:
        if cost_path:
            st.markdown(
                f'<div class="status-ok">✅ 사교육비 총액 데이터 로드 성공<br>'
                f'<small>{cost_path}</small></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-err">❌ 사교육비 총액 CSV 파일을 찾을 수 없음</div>',
                unsafe_allow_html=True,
            )
    with c2:
        if rate_path:
            st.markdown(
                f'<div class="status-ok">✅ 사교육 참여율 데이터 로드 성공<br>'
                f'<small>{rate_path}</small></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-err">❌ 사교육 참여율 CSV 파일을 찾을 수 없음</div>',
                unsafe_allow_html=True,
            )

    if not data_ok:
        st.error("CSV 파일이 없어 일부 기능이 작동하지 않습니다.")
        st.markdown(
            """
            **해결 방법:**
            1. 깃허브 저장소에 `data/` 폴더를 만드세요.
            2. 아래 파일 중 하나의 이름으로 CSV를 업로드하세요.

            | 데이터 | 파일명 후보 |
            |--------|------------|
            | 사교육비 총액 | `cost_by_school.csv` 또는 `학교급별_사교육비_총액.csv` |
            | 참여율 | `rate_by_grade.csv` 또는 `학생_성적_구간별_사교육_참여율.csv` |
            """
        )
        # 디버깅 정보
        st.markdown("**현재 경로 정보:**")
        debug_info = {
            "__file__ 위치": str(Path(__file__).resolve()),
            "작업 디렉토리": os.getcwd(),
            "data/ 폴더 존재": str((Path(__file__).resolve().parent / "data").exists()),
        }
        data_dir = Path(__file__).resolve().parent / "data"
        if data_dir.exists():
            debug_info["data/ 내 파일"] = str([f.name for f in data_dir.iterdir()])
        else:
            root = Path(__file__).resolve().parent
            if root.exists():
                debug_info["루트 파일 목록"] = str([f.name for f in root.iterdir()])
        st.json(debug_info)

# ── KPI 요약 (데이터 있을 때만) ───────────────────────────────────────────────
if data_ok:
    YEARS = list(range(2016, 2026))

    def get_val(df, row_label, year, id_col="특성별"):
        row = df[df[id_col] == row_label]
        if row.empty:
            return np.nan
        matched = [c for c in df.columns if c.startswith(str(year)) and "전체 (억원)" in c]
        return float(row.iloc[0][matched[0]]) if matched else np.nan

    total_16 = get_val(cost_df, "전체", 2016)
    total_24 = get_val(cost_df, "전체", 2024)
    growth   = (total_24 - total_16) / total_16 * 100 if not np.isnan(total_16) else np.nan

    seoul_24 = get_val(cost_df, "서울",    2024)
    rural_24 = get_val(cost_df, "읍면지역", 2024)
    ratio    = seoul_24 / rural_24 if not (np.isnan(seoul_24) or np.isnan(rural_24)) else np.nan

    rate_row = rate_df[rate_df["과목 및 유형"] == "사교육 참여"]
    top_c = [c for c in rate_df.columns if c.startswith("2024") and "상위10%" in c]
    bot_c = [c for c in rate_df.columns if c.startswith("2024") and "81 ~ 100%" in c]
    top_r = float(rate_row.iloc[0][top_c[0]]) if top_c and not rate_row.empty else np.nan
    bot_r = float(rate_row.iloc[0][bot_c[0]]) if bot_c and not rate_row.empty else np.nan
    gap   = top_r - bot_r if not (np.isnan(top_r) or np.isnan(bot_r)) else np.nan

    st.markdown("### 📊 핵심 수치 한눈에 보기")
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (f"{total_24/10000:.1f}조 원", "2024년 사교육비 총액"),
        (f"+{growth:.0f}%",            "2016→2024 증가율"),
        (f"{gap:.1f}%p",               "성적 상위10% vs 하위20%\n참여율 격차"),
        (f"{ratio:.1f}배",             "서울 vs 읍면지역\n사교육비 비율"),
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

# ── 페이지 소개 카드 ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="report-card">
            <h3>🔴 Page 1 · 문제의 심각성</h3>
            <p>사교육비 총액 10년 추이, 학교급별 시장 규모,
            성적 구간별 참여율 격차를 통해
            <strong>교육 불평등이 얼마나 심화되었는지</strong>
            데이터로 증명합니다.</p>
            <ul>
                <li>연간 사교육비 총액 변화</li>
                <li>지역별 사교육비 격차</li>
                <li>성적 상·하위 참여율 비교</li>
                <li>과목별 격차 분석</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="report-card">
            <h3>🟠 Page 2 · 상업화 구조 분석</h3>
            <p>과목별 지출 구조, 사교육 유형별 변화 흐름,
            프리미엄화·불안 마케팅 패턴을 분석하여
            <strong>교육이 어떻게 '산업'이 되는지</strong>
            규명합니다.</p>
            <ul>
                <li>과목별 사교육비 포트폴리오</li>
                <li>유형별(학원·과외·인강) 시장 변화</li>
                <li>불안 마케팅·고가화 구조 분석</li>
                <li>디지털 전환 트렌드</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("👈 왼쪽 사이드바에서 페이지를 선택하세요.")
st.markdown("---")
st.caption("데이터 출처: 통계청 사교육비조사 (2016~2025) | 제작: 당곡고등학교")
