import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================
# 1. Load the analysis summary JSON produced in Round 4
# ============================================================
with open("data/processed/analysis_summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

# ============================================================
# 2. Build the prompt to send to GPT
#    Key point: GPT isn't doing "calculation" — it's just turning
#    numbers that are already calculated into prose.
# ============================================================
prompt = f"""
You are a data analyst at the company. Below are results that have already
been computed through statistical analysis. Based on these numbers, write an
Executive Summary to report to management.

[Analysis data]
- Number of months analyzed: {summary['total_months']}
- Most recent month: {summary['latest_month']}
- Most recent month's sales growth vs. prior month (MoM): {summary['latest_mom_growth_pct']}%
- Most recent month's sales growth vs. same month last year (YoY): {summary['latest_yoy_growth_pct']}%
- Months flagged as sales outliers: {summary['outlier_months_sales']}
- Months flagged as profit outliers: {summary['outlier_months_profit']}
- Top 3 worst-loss orders: {summary['top_10_worst_orders'][:3]}

[Writing rules]
1. Write 3-4 paragraphs
2. First paragraph: overall summary of sales/profit trends
3. Second paragraph: interpretation of which months were flagged as outliers and what that means
4. Third paragraph: analysis of what the highest-loss orders have in common (e.g. discount rate)
5. Final paragraph: 1-2 actionable insights to propose to management
6. Do not invent new numbers — use only the data given
"""

# ============================================================
# 3. Call the GPT API
# ============================================================
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert who writes accurate, concise business analysis reports."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3,  # lower = more consistent, fact-grounded answers
)

executive_summary = response.choices[0].message.content

# ============================================================
# 4. Print the result & save to file
# ============================================================
print("=== Executive Summary ===\n")
print(executive_summary)

os.makedirs("docs", exist_ok=True)
with open("docs/executive_summary.md", "w", encoding="utf-8") as f:
    f.write("# Executive Summary\n\n")
    f.write(executive_summary)

print("\n\nSaved: docs/executive_summary.md")