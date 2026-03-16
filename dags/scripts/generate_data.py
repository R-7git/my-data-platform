import csv
import io
import logging
from datetime import datetime
from faker import Faker
import boto3
from botocore.client import Config

# --- UPDATED CONFIGURATION ---
# Use host.docker.internal to reach Docker Compose from K8s
# Port 9002 is the external port for MinIO in your docker-compose.yaml
MINIO_URL = 'http://minio-external:9002'  
ACCESS_KEY = 'minioadmin'
SECRET_KEY = 'minioadmin' 
BUCKET_NAME = 'raw-data-lake'

def generate_and_upload_customers(num_records=18000): 
    """
    Simulates an extraction from a CRM system.
    """
    # Time Bomb is commented out - ready for production run
    # raise ValueError("🚨 THIS IS A DRILL: SIMULATED PIPELINE FAILURE 🚨")

    fake = Faker()
    
    # 2. In-Memory Buffer
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # 3. Define Schema
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
    
    # 5. Connect to Local Data Lake
    s3_client = boto3.client('s3',
                             endpoint_url=MINIO_URL,
                             aws_access_key_id=ACCESS_KEY,
                             aws_secret_access_key=SECRET_KEY,
                             config=Config(signature_version='s3v4'),
                             region_name='us-east-1')
    
    # 6. Ensure Bucket Exists
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
    except Exception:
        pass

    # 7. Upload the file
    file_name = f"customers/extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=csv_buffer.getvalue())
    
    logging.info(f"SUCCESS: Uploaded {file_name} to MinIO")
    return file_name

if __name__ == "__main__":
    generate_and_upload_customers()

