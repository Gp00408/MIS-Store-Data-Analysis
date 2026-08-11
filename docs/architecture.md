# Architecture

```mermaid
flowchart LR
    CSV["Superstore.csv"] --> LOAD["load_data.py"]
    LOAD --> DB[("PostgreSQL\ndim_customers / dim_products / fact_orders")]
    SCHEMA["schema.sql"] -.defines.-> DB
    DB --> QUERIES["analysis_queries.sql"]
    QUERIES --> STATS["analysis.py\n(z-score outliers, MoM/YoY)"]
    QUERIES --> PBI["dashboard.pbix\n(Power BI)"]
    STATS --> JSON["analysis_summary.json"]
    JSON --> GPT["generate_summary.py\n(OpenAI API)"]
    GPT --> SUMMARY["executive_summary.md"]
```

1. `load_data.py` reads `data/Superstore.csv` and loads it into the Postgres tables defined in `schema.sql`.
2. `analysis_queries.sql` runs SQL-side analytics (monthly sales, category/segment/region profit margins, top customers, discount-vs-profit, ...) directly against the database. These queries also feed the Power BI dashboard.
3. `analysis.py` pulls query results into Python, runs z-score outlier detection and MoM/YoY growth calculations, and writes `data/processed/analysis_summary.json`.
4. `generate_summary.py` sends that JSON summary to the OpenAI API and writes the result to `docs/executive_summary.md`.
