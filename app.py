import streamlit as st

st.set_page_config(
    page_title="사교육 상업화 분석 보고서",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-banner">
        <h1>📚 사교육 상업화 분석 보고서</h1>
        <p>2016 – 2025 통계청 데이터로 보는 한국 사교육 산업화의 실태</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("👈 왼쪽 사이드바에서 페이지를 선택하세요.")
st.markdown("---")
st.caption("데이터 출처: 통계청 사교육비조사 (2016~2025) | 제작: 당곡고등학교")
