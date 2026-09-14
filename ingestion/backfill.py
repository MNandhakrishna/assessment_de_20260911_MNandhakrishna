import time
from datetime import date, timedelta

from ingestion.extract import extract_weather
from ingestion.load import load_weather


def backfill_weather(start_date, end_date):
    current_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)

    while current_date <= end_date:
        logical_date = current_date.isoformat()

        data = extract_weather(logical_date)
        load_weather(data)

        print(f"Loaded {logical_date}")

        current_date += timedelta(days=1)
        time.sleep(1)