select *
from {{ ref('fct_city_daily') }}
where temperature_2m_min > temperature_2m_max
   or precipitation_sum < 0