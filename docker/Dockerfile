# Base Image: Official Airflow
FROM apache/airflow:2.8.1

USER root
# Install Git and Terraform for Jenkins/CI usage
RUN apt-get update && \
    apt-get install -y git wget unzip && \
    # FIX: Added the full direct link for Terraform 1.7.0
    wget https://releases.hashicorp.com && \
    unzip terraform_1.7.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_1.7.0_linux_amd64.zip

USER airflow

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy dbt project into the image so it's ready for production
COPY --chown=airflow:root dbt_project /opt/airflow/dbt_project
