select
    city::text as city,
    latitude::double precision as latitude,
    longitude::double precision as longitude,
    date::date as date,
    temperature_2m_max::double precision as temperature_2m_max,
    temperature_2m_min::double precision as temperature_2m_min,
    precipitation_sum::double precision as precipitation_sum
from {{ source('raw', 'weather_daily') }}