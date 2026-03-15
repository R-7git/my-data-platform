{{ config({"severity":"Warn","tags":[]}) }}
{{ test_accepted_values(column_name="state", model=get_where_subquery(ref('stg_customers')), values=["NY","CA","TX","FL"]) }}