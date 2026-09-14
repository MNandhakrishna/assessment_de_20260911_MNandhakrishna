import os

import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.environ["WAREHOUSE_HOST"],
        port=os.environ["WAREHOUSE_PORT"],
        dbname=os.environ["WAREHOUSE_DB"],
        user=os.environ["WAREHOUSE_USER"],
        password=os.environ["WAREHOUSE_PASSWORD"],
    )


def load_weather(data):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE SCHEMA IF NOT EXISTS raw;

                CREATE TABLE IF NOT EXISTS raw.weather_daily (
                    city TEXT NOT NULL,
                    latitude DOUBLE PRECISION NOT NULL,
                    longitude DOUBLE PRECISION NOT NULL,
                    date DATE NOT NULL,
                    temperature_2m_max DOUBLE PRECISION,
                    temperature_2m_min DOUBLE PRECISION,
                    precipitation_sum DOUBLE PRECISION,
                    PRIMARY KEY (city, date)
                );
            """)

            for record in data:
                daily = record["response"]["daily"]

                for i, date in enumerate(daily["time"]):
                    cursor.execute(
                        """
                        INSERT INTO raw.weather_daily (
                            city,
                            latitude,
                            longitude,
                            date,
                            temperature_2m_max,
                            temperature_2m_min,
                            precipitation_sum
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (city, date)
                        DO UPDATE SET
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            temperature_2m_max = EXCLUDED.temperature_2m_max,
                            temperature_2m_min = EXCLUDED.temperature_2m_min,
                            precipitation_sum = EXCLUDED.precipitation_sum
                        """,
                        (
                            record["city"],
                            record["latitude"],
                            record["longitude"],
                            date,
                            daily["temperature_2m_max"][i],
                            daily["temperature_2m_min"][i],
                            daily["precipitation_sum"][i],
                        ),
                    )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
