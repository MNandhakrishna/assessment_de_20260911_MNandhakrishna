import sys
from datetime import timedelta

import pendulum
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.python import get_current_context

sys.path.insert(0, "/opt/airflow")

from ingestion.extract import extract_weather
from ingestion.load import load_weather


@dag(
    dag_id="weather_pipeline",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2026, 9, 1, tz="UTC"),
    catchup=True,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "execution_timeout": timedelta(minutes=10),
    },
    description="Daily weather extraction, loading, transformation and testing",
    tags=["weather", "data-engineering"],
)
def weather_pipeline():

    @task
    def extract():
        context = get_current_context()
        logical_date = context["ds"]

        return extract_weather(logical_date)

    @task
    def load(data):
        load_weather(data)

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run",
        execution_timeout=timedelta(minutes=10),
        retries=2,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test",
        execution_timeout=timedelta(minutes=10),
        retries=2,
    )

    extracted_data = extract()
    loaded_data = load(extracted_data)

    loaded_data >> dbt_run >> dbt_test


weather_pipeline()