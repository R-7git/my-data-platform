# 1. Base Image (This was missing!)
FROM apache/airflow:2.8.1

USER root
# 2. Install System Dependencies
RUN apt-get update && \
    apt-get install -y git wget unzip && \
    wget https://releases.hashicorp.com && \
    unzip terraform_1.7.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_1.7.0_linux_amd64.zip

# 3. Switch back to airflow user
USER airflow

# 4. Install Python dependencies (Using the docker/ prefix)
COPY docker/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# 5. Copy dbt project
COPY --chown=airflow:root dbt_project /opt/airflow/dbt_project
