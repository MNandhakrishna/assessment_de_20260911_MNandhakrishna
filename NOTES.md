# Notes

## Time Spent

Approximately 8–10 hours were spent on the assessment, including environment setup, pipeline implementation, debugging, testing, and documentation.

## Known Gaps / Limitations

* The pipeline currently uses PostgreSQL as the local warehouse for reproducibility.
* The Open-Meteo archive API occasionally returned transient HTTP 500 responses during development. The extraction layer handles HTTP failures, timeouts, empty/invalid responses, and retries failed requests.
* The current pipeline is designed for the configured cities in `config/cities.yml`.
* The backfill helper processes one logical date at a time and is intended for historical backfills.
* Production-scale deployment, secrets management, and cloud infrastructure are outside the scope of this assessment.

## AI Tools Used

ChatGPT (GPT-5.6 Luna) was used during development for:

* Understanding and clarifying the assessment requirements.
* Reviewing the project structure and implementation approach.
* Debugging Docker Compose, dbt, Airflow, and Python errors.
* Explaining implementation patterns for incremental/idempotent loading, retries, dbt testing, and Airflow logical dates.
* Reviewing code and suggesting improvements for robustness and reproducibility.

The implementation was developed, tested, and verified locally. AI was used as a development and debugging aid rather than as a replacement for testing or verification.
