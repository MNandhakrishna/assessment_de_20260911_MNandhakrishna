from pathlib import Path

import requests
import yaml
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

API_URL = "https://archive-api.open-meteo.com/v1/archive"

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "cities.yml"


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def get_weather(latitude, longitude, logical_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": logical_date,
        "end_date": logical_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def extract_weather(logical_date):
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    cities = config["cities"]

    results = []

    for city in cities:
        response = get_weather(
            city["latitude"],
            city["longitude"],
            logical_date,
        )

        results.append({
            "city": city["name"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "logical_date": logical_date,
            "response": response,
        })

    return results
