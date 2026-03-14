from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import boto3

# --- IMPORT THE ALERT ---
# This will fail if you didn't rename alerts.py.py -> alerts.py
from utils.alerts import notify_slack_on_failure
from scripts.generate_data import generate_and_upload_customers

# --- CONFIGURATION ---
default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # THE SAFETY NET: If *any* task fails, this function runs automatically
    'on_failure_callback': notify_slack_on_failure
}

@dag(
    dag_id='2_enterprise_elt_pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args, # <--- Activates the alert system
    tags=['snowflake', 'elt', 'minio', 'dbt']
)
def enterprise_elt():

    # 1. EXTRACT: Generate Data & Land in MinIO
    @task
    def extract_to_minio():
        file_name = generate_and_upload_customers(num_records=1000)
        return file_name

    # 2. LOAD: Push from MinIO to Snowflake Stage
    @task
    def load_to_snowflake_stage(file_name: str):
        # A. Connect to MinIO
        s3 = boto3.client('s3', 
                          endpoint_url='http://minio:9000',
                          aws_access_key_id='minioadmin', 
                          aws_secret_access_key='minioadmin')
        
        local_path = f"/tmp/{file_name.split('/')[-1]}"
        s3.download_file('raw-data-lake', file_name, local_path)
        
        # B. Connect to Snowflake
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        print(f"Uploading {local_path} to Snowflake Stage...")
        hook.run(f"PUT file://{local_path} @RAW_LAKE.LANDING.MY_INTERNAL_STAGE AUTO_COMPRESS=TRUE")
        
        os.remove(local_path)
        return file_name.split('/')[-1]

    # 3. REGISTER: Copy into Table
    @task
    def copy_into_table(file_name: str):
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        sql = f"""
            COPY INTO RAW_LAKE.LANDING.CUSTOMERS 
            FROM @RAW_LAKE.LANDING.MY_INTERNAL_STAGE/{file_name}.gz
            FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1);
        """
        hook.run(sql)

    # 4. TRANSFORM: Run dbt
    transform_data = BashOperator(
        task_id='dbt_transform',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # Define the Flow
    csv_file = extract_to_minio()
    staged_file = load_to_snowflake_stage(csv_file)
    copy_task = copy_into_table(staged_file)

    # Dependency: Transform waits for Copy
    copy_task >> transform_data

# Init
dag = enterprise_elt()
