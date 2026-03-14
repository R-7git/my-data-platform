{{ config(
    materialized='incremental',
    unique_key='customer_id'
) }}

select
    customer_id,
    first_name,
    last_name,
    email,
    -- Standardize State to Uppercase
    upper(state) as state,
    -- Convert String to Real Date
    try_to_date(signup_date) as signup_date
from {{ source('landing_zone', 'customers') }}

{% if is_incremental() %}

  -- The Logic:
  -- 1. Look at "this" table (the one we are building).
  -- 2. Find the Maximum (latest) signup_date we already processed.
  -- 3. Only pull rows from the source that are NEWER than that date.
  
  where try_to_date(signup_date) > (select max(signup_date) from {{ this }})

{% endif %}
