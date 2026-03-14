-- back compat for old kwarg name
  
  begin;
    
        
            
            
        
    

    

    merge into RAW_LAKE.ANALYTICS.stg_customers as DBT_INTERNAL_DEST
        using RAW_LAKE.ANALYTICS.stg_customers__dbt_tmp as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.customer_id = DBT_INTERNAL_DEST.customer_id
            )

    
    when matched then update set
        "CUSTOMER_ID" = DBT_INTERNAL_SOURCE."CUSTOMER_ID","FIRST_NAME" = DBT_INTERNAL_SOURCE."FIRST_NAME","LAST_NAME" = DBT_INTERNAL_SOURCE."LAST_NAME","EMAIL" = DBT_INTERNAL_SOURCE."EMAIL","STATE" = DBT_INTERNAL_SOURCE."STATE","SIGNUP_DATE" = DBT_INTERNAL_SOURCE."SIGNUP_DATE"
    

    when not matched then insert
        ("CUSTOMER_ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "STATE", "SIGNUP_DATE")
    values
        ("CUSTOMER_ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "STATE", "SIGNUP_DATE")

;
    commit;