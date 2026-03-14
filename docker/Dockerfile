# 1. Base Image
FROM apache/airflow:2.8.1

USER root
# 2. Install System Dependencies
RUN apt-get update && \
    apt-get install -y git wget unzip && \
    # FIX: Full path to the ARM64 zip file
    wget https://releases.hashicorp.com && \
    unzip terraform_1.7.0_linux_arm64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_1.7.0_linux_arm64.zip

# 3. Switch back to airflow user
USER airflow

# 4. Install Python dependencies
COPY docker/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# 5. Copy dbt project
COPY --chown=airflow:root dbt_project /opt/airflow/dbt_project
