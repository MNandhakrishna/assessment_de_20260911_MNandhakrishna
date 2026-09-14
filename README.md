# Weather Data Engineering Assessment

A small end-to-end weather data pipeline that extracts daily weather data from the Open-Meteo historical API, loads it into PostgreSQL, transforms it with dbt, and orchestrates the workflow with Apache Airflow.

## Architecture

```text
Open-Meteo Historical API
          |
          v
     Airflow DAG
          |
          v
   Python Extraction
          |
          v
   PostgreSQL RAW
   raw.weather_daily
          |
          v
       dbt
     /      \
Staging     Mart
   |          |
   v          v
stg_weather  fct_city_daily
          |
          v
      Data Quality
          |
          v
     Airflow Tests
```

### Components

* **Open-Meteo** — historical weather API
* **Python** — extraction and loading
* **PostgreSQL** — local warehouse
* **dbt Core** — transformation and data quality tests
* **Apache Airflow** — orchestration
* **Jupyter** — reproducible walkthrough
* **Docker Compose** — local reproducible environment

## Project Structure

```text
.
├── config/
│   └── cities.yml
├── dags/
│   └── weather_pipeline.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── macros/
│   └── models/
│       ├── marts/
│       └── staging/
├── ingestion/
│   ├── extract.py
│   ├── load.py
│   └── backfill.py
├── notebooks/
│   └── walkthrough.ipynb
├── sql/
│   └── init/
├── docker/
│   └── airflow.Dockerfile
├── docker-compose.yml
├── Makefile
├── NOTES.md
└── README.md
```

## Prerequisites

* Docker Desktop
* Docker Compose
* Git
* `make` for the documented commands

On Windows, the equivalent `docker compose` commands can be run directly from PowerShell if `make` is not installed.

## Setup

Clone the repository and enter the project directory.

Create the environment file:

```bash
cp .env.example .env
```

Start the services:

```bash
make up
```

The main services are:

* Airflow: `http://localhost:8080`
* JupyterLab: `http://localhost:8888`
* PostgreSQL: `localhost:5432`

Airflow credentials for the local environment are:

```text
Username: admin
Password: admin
```

## Pipeline

The pipeline processes one logical date at a time.

The Airflow DAG follows:

```text
extract → load → dbt_run → dbt_test
```

The DAG is scheduled daily at 06:00 UTC and uses the Airflow logical date rather than the current system date.

The configured cities are maintained in:

```text
config/cities.yml
```

## Extraction

The extraction layer calls the Open-Meteo historical weather API for each configured city.

The following daily API fields are loaded:

* `temperature_2m_max`
* `temperature_2m_min`
* `precipitation_sum`

HTTP requests use:

* 30-second timeout
* retry handling for request failures
* exponential backoff
* handling for empty or invalid JSON responses

## Loading and Idempotency

Raw data is stored in:

```text
raw.weather_daily
```

The table uses:

```text
PRIMARY KEY (city, date)
```

Loads use PostgreSQL `ON CONFLICT DO UPDATE`, making the load idempotent.

Rerunning the same logical date therefore does not create duplicate rows.

## Backfill

Historical dates can be loaded using the backfill helper:

```bash
docker compose exec airflow python -c "from ingestion.backfill import backfill_weather; backfill_weather('2026-08-13', '2026-09-11')"
```

The helper processes each date independently while using the same extraction and loading functions as the Airflow DAG.

The assessment verification run covers:

```text
3 cities × 30 dates = 90 rows
```

## dbt

The dbt project contains:

### Source

```text
raw.weather_daily
```

### Staging

```text
staging.stg_weather
```

The staging model cleans and explicitly types the raw fields.

### Mart

```text
marts.fct_city_daily
```

The mart provides daily weather metrics by city for analytics and reporting.

Run dbt manually with:

```bash
make dbt
```

Run data quality tests:

```bash
make dbt-test
```

The project includes:

* not-null tests
* duplicate key regression test for `(city, date)`
* temperature range validation
* precipitation range validation

## Airflow

The DAG is:

```text
weather_pipeline
```

It runs:

```text
extract
   ↓
load
   ↓
dbt_run
   ↓
dbt_test
```

The DAG uses:

* daily scheduling
* logical dates
* catchup/backfill support
* task retries
* execution timeouts
* idempotent loading

## Walkthrough Notebook

The notebook is:

```text
notebooks/walkthrough.ipynb
```

It uses the same Python extraction and loading functions as the Airflow pipeline rather than reimplementing the pipeline logic.

The walkthrough demonstrates:

1. Configuration
2. Extraction
3. Raw loading
4. Row counts and sample data
5. Same-date rerun and idempotency
6. dbt transformation
7. dbt tests
8. Querying the final mart

To reproduce the notebook:

```bash
make reproduce
```

## Verification

Check the raw table:

```bash
make psql
```

Then:

```sql
SELECT
    MIN(date),
    MAX(date),
    COUNT(*),
    COUNT(DISTINCT city),
    COUNT(DISTINCT date)
FROM raw.weather_daily;
```

For the assessment backfill, the expected result is:

```text
90 rows
3 cities
30 dates
```

Check the mart:

```sql
SELECT
    MIN(date),
    MAX(date),
    COUNT(*),
    COUNT(DISTINCT city),
    COUNT(DISTINCT date)
FROM marts.fct_city_daily;
```

Run all dbt tests:

```bash
make dbt-test
```

## Useful Commands

Start services:

```bash
make up
```

Stop services:

```bash
make down
```

View Airflow logs:

```bash
make logs
```

Run dbt:

```bash
make dbt
```

Run dbt tests:

```bash
make dbt-test
```

Open the database:

```bash
make psql
```

Reproduce the notebook:

```bash
make reproduce
```

## Reproducibility

A clean environment can be started with:

```bash
cp .env.example .env
make up
make reproduce
```

The pipeline, dbt models, tests, Airflow DAG, and walkthrough are contained in the repository and run using Docker Compose.

## Notes

See [`NOTES.md`](NOTES.md) for time spent, known limitations, and AI-tool usage.
