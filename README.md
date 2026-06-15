# 📚 사교육 상업화 분석 보고서

> 데이터로 보는 한국 사교육 산업화의 실태

## 프로젝트 소개

이 프로젝트는 한국 사교육의 상업화 실태를 통계 데이터 기반으로 분석한
인터랙티브 보고서 웹사이트입니다.  
통계청 사교육비 조사 데이터(2016~2025)를 활용하여 사교육 시장 규모,
교육 격차, 상업화 구조를 시각적으로 제시합니다.

## 주요 기능

- **Page 1 – 문제의 심각성**: 사교육비 총액 추이, 학교급별 비중,
  성적 구간별 참여율 격차를 통한 교육 불평등 시각화
- **Page 2 – 상업화 구조 분석**: 과목별 지출 구조, 사교육 유형별 변화,
  불안 마케팅·프리미엄화 패턴 분석

## 데이터 출처

| 파일명 | 출처 | 기간 |
|--------|------|------|
| 학교급별_사교육비_총액.csv | 통계청 사교육비조사 | 2016~2025 |
| 학생_성적_구간별_사교육_참여율.csv | 통계청 사교육비조사 | 2016~2025 |

## 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/edu_commercialization.git
cd edu_commercialization

# 2. 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 데이터 파일 배치
# data/ 폴더에 CSV 파일 2개를 넣어주세요.

# 5. 앱 실행
streamlit run app.py
