import csv
import io
import logging
from datetime import datetime
from faker import Faker
import boto3
from botocore.client import Config

# 1. Configuration (Matches your docker-compose MinIO settings)
MINIO_URL = 'http://minio:9000'  # Inside Docker, we talk to 'minio' hostname
ACCESS_KEY = 'minioadmin'
SECRET_KEY = 'minioadmin'
BUCKET_NAME = 'raw-data-lake'

def generate_and_upload_customers(num_records=100):
    """
    Simulates an extraction from a CRM system.
    """
    # --- THE TIME BOMB ---
    # This is valid Python, but it causes a "Runtime Error" when executed.
    # This allows the DAG to start, fail, and THEN send the Slack Alert.
    #raise ValueError("🚨 THIS IS A DRILL: SIMULATED PIPELINE FAILURE 🚨")

    # ... (Rest of your code below is fine, but it won't run because of the line above)
    fake = Faker()
    # ...

    
    # 2. In-Memory Buffer (Acting as a temporary file)
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # 3. Define Schema (The "Source" Contract)
    headers = ['customer_id', 'first_name', 'last_name', 'email', 'state', 'signup_date']
    writer.writerow(headers)
    
    # 4. Generate Fake Rows
    logging.info(f"Generating {num_records} fake customer records...")
    for _ in range(num_records):
        writer.writerow([
            fake.uuid4(),
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.state_abbr(),
            fake.date_between(start_date='-1y', end_date='today').isoformat()
        ])
    
    # 5. Connect to Local Data Lake (MinIO)
    # We use boto3, the standard AWS SDK for Python
    s3_client = boto3.client('s3',
                             endpoint_url=MINIO_URL,
                             aws_access_key_id=ACCESS_KEY,
                             aws_secret_access_key=SECRET_KEY,
                             config=Config(signature_version='s3v4'),
                             region_name='us-east-1')
    
    # 6. Ensure Bucket Exists (Idempotency)
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass

    # 7. Upload the file
    file_name = f"customers/extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=csv_buffer.getvalue())
    
    logging.info(f"SUCCESS: Uploaded {file_name} to MinIO bucket '{BUCKET_NAME}'")
    return file_name

# Allow local testing (only runs if you execute this script directly)
if __name__ == "__main__":
    # Note: If running locally (outside Docker), change MINIO_URL to 'http://localhost:9000'
    generate_and_upload_customers()
