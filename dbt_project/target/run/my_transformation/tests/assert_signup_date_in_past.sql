select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      -- If this query returns results, the test fails.
-- We are looking for "Bad Data" (Future dates).

select
    customer_id,
    signup_date
from RAW_LAKE.ANALYTICS.stg_customers
where signup_date > current_date()
      
    ) dbt_internal_test