
    
    

with all_values as (

    select
        state as value_field,
        count(*) as n_records

    from RAW_LAKE.ANALYTICS.stg_customers
    group by state

)

select *
from all_values
where value_field not in (
    'NY','CA','TX','FL'
)


