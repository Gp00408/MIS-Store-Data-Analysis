# MIS Store Data Analysis

End-to-end analysis pipeline for the Superstore sales dataset: SQL schema → Python ETL → SQL analytics → Python statistical analysis → Power BI dashboard → GPT-generated executive summary.

## Team

- **Hamin** — schema design, CSV-to-DB loader, statistical analysis, GPT executive summary generation
- **Gyutae** — SQL analysis queries, Power BI dashboard, documentation

## Pipeline

| Step | Owner | Output |
|---|---|---|
| 1. SQL schema design + DB table creation | Hamin | [sql/schema.sql](sql/schema.sql) |
| 2. Load CSV into DB | Hamin | [python/load_data.py](python/load_data.py) |
| 3. SQL analysis queries (monthly sales, category margins, regional performance, ...) | Gyutae | [sql/analysis_queries.sql](sql/analysis_queries.sql) |
| 4. Statistical analysis (z-score outliers, MoM/YoY growth) | Hamin | [python/analysis.py](python/analysis.py) |
| 5. Power BI dashboard | Gyutae | [powerbi/dashboard.pbix](powerbi/dashboard.pbix) |
| 6. GPT-generated executive summary | Hamin | [python/generate_summary.py](python/generate_summary.py) |
| 7. Docs | Gyutae | this file, [docs/architecture.md](docs/architecture.md) |

See [docs/architecture.md](docs/architecture.md) for a diagram of how these pieces connect.

## Setup

1. `pip install -r requirements.txt`
2. Create `python/.env` with:
   ```
   DB_USER=...
   DB_PASSWORD=...
   DB_HOST=...
   DB_PORT=...
   DB_NAME=...
   OPENAI_API_KEY=...
   ```
3. Run [sql/schema.sql](sql/schema.sql) against your Postgres database
4. `python python/load_data.py`
5. Run [sql/analysis_queries.sql](sql/analysis_queries.sql) as needed (also used as the Power BI data source)
6. `python python/analysis.py`
7. `python python/generate_summary.py`

## Notes / gotchas from building this

- `.env` accidentally got created as a folder at one point instead of a file — worth double-checking.
- CSV filename mismatches between scripts and the actual file in `data/`.
- CSV is read with `utf-8-sig` encoding to handle a BOM in the source file.
- DB passwords with special characters need URL-encoding (`quote_plus`) before being used in the SQLAlchemy connection string.
