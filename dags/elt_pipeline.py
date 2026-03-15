from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import boto3
from utils.alerts import notify_slack_on_failure
from scripts.generate_data import generate_and_upload_customers

default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': notify_slack_on_failure
}

@dag(
    dag_id='2_enterprise_elt_pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=['snowflake', 'elt', 'minio', 'dbt']
)
def enterprise_elt():

    @task
    def extract_to_minio():
        file_name = generate_and_upload_customers(num_records=1000)
        return file_name

    @task
    def load_to_snowflake_stage(file_name: str):
        # --- UPDATED ENDPOINT ---
        s3 = boto3.client('s3', 
                          endpoint_url='http://host.docker.internal:9002',
                          aws_access_key_id='minioadmin', 
                          aws_secret_access_key='minioadmin')
        
        local_path = f"/tmp/{file_name.split('/')[-1]}"
        s3.download_file('raw-data-lake', file_name, local_path)
        
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        hook.run(f"PUT file://{local_path} @RAW_LAKE.LANDING.MY_INTERNAL_STAGE AUTO_COMPRESS=TRUE")
        
        os.remove(local_path)
        return file_name.split('/')[-1]

    @task
    def copy_into_table(file_name: str):
        hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
        sql = f"""
            COPY INTO RAW_LAKE.LANDING.CUSTOMERS 
            FROM @RAW_LAKE.LANDING.MY_INTERNAL_STAGE/{file_name}.gz
            FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1);
        """
        hook.run(sql)

    transform_data = BashOperator(
        task_id='dbt_transform',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    csv_file = extract_to_minio()
    staged_file = load_to_snowflake_stage(csv_file)
    copy_task = copy_into_table(staged_file)

    copy_task >> transform_data

dag = enterprise_elt()
