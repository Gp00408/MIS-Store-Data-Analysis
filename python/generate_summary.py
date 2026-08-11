import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================
# 1. Round 4에서 만든 분석 요약 JSON 불러오기
# ============================================================
with open("data/processed/analysis_summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

# ============================================================
# 2. GPT에게 보낼 프롬프트 구성
#    핵심: GPT는 "계산"을 하는 게 아니라, 이미 계산된 숫자를 "글로 풀어쓰기"만 함
# ============================================================
prompt = f"""
당신은 회사의 데이터 분석가입니다. 아래는 통계 분석을 통해 이미 계산된 결과입니다.
이 숫자들을 바탕으로 경영진에게 보고할 Executive Summary를 작성해주세요.

[분석 데이터]
- 분석 대상 개월 수: {summary['total_months']}개월
- 최근 달: {summary['latest_month']}
- 최근 달 전월 대비 매출 성장률: {summary['latest_mom_growth_pct']}%
- 최근 달 전년 동월 대비 매출 성장률: {summary['latest_yoy_growth_pct']}%
- 매출 이상치로 감지된 달: {summary['outlier_months_sales']}
- 이익 이상치로 감지된 달: {summary['outlier_months_profit']}
- 손해가 가장 컸던 주문 TOP 3: {summary['top_10_worst_orders'][:3]}

[작성 규칙]
1. 3~4개 문단으로 작성
2. 첫 문단: 전반적인 매출/이익 트렌드 요약
3. 둘째 문단: 이상치가 발견된 달과 그 의미에 대한 해석
4. 셋째 문단: 손해가 컸던 거래의 공통점 (할인율 등)에 대한 분석
5. 마지막 문단: 경영진에게 제안할 만한 실행 가능한 인사이트 1~2개
6. 숫자를 새로 만들어내지 말고, 주어진 데이터만 사용할 것
"""

# ============================================================
# 3. GPT API 호출
# ============================================================
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 정확하고 간결한 비즈니스 분석 보고서를 작성하는 전문가입니다."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3,  # 낮을수록 더 일관되고 사실 기반의 답변
)

executive_summary = response.choices[0].message.content

# ============================================================
# 4. 결과 출력 & 파일로 저장
# ============================================================
print("=== Executive Summary ===\n")
print(executive_summary)

os.makedirs("docs", exist_ok=True)
with open("docs/executive_summary.md", "w", encoding="utf-8") as f:
    f.write("# Executive Summary\n\n")
    f.write(executive_summary)

print("\n\n저장 완료: docs/executive_summary.md")