# 1. The Warehouse
resource "snowflake_warehouse" "elt_warehouse" {
  name                = "COMPUTE_WH_PROD"
  warehouse_size      = "x-small"
  auto_suspend        = 60
  initially_suspended = true
}

# 2. The Database
resource "snowflake_database" "raw_lake" {
  name = "RAW_LAKE"
}

# 3. The Schema
resource "snowflake_schema" "landing_zone" {
  database = snowflake_database.raw_lake.name
  name     = "LANDING"
}

# 4. The Table (Columns now in UPPERCASE to match dbt)
resource "snowflake_table" "customers" {
  database = snowflake_database.raw_lake.name
  schema   = snowflake_schema.landing_zone.name
  name     = "CUSTOMERS"

  column {
    name = "CUSTOMER_ID"
    type = "VARCHAR(16777216)"
  }
  column {
    name = "FIRST_NAME"
    type = "VARCHAR(16777216)"
  }
  column {
    name = "LAST_NAME"
    type = "VARCHAR(16777216)"
  }
  column {
    name = "EMAIL"
    type = "VARCHAR(16777216)"
  }
  column {
    name = "STATE"
    type = "VARCHAR(16777216)"
  }
  column {
    name = "SIGNUP_DATE"
    type = "VARCHAR(16777216)"
  }
}

# 5. The Internal Stage
resource "snowflake_stage" "my_stage" {
  name     = "MY_INTERNAL_STAGE"
  database = snowflake_database.raw_lake.name
  schema   = snowflake_schema.landing_zone.name
}
