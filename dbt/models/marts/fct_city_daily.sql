select
    city,
    date,
    temperature_2m_max,
    temperature_2m_min,
    precipitation_sum
from {{ ref('stg_weather') }}