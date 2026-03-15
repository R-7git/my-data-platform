# 1. Base Image
FROM apache/airflow:2.8.1

USER root

# 2. Install System Dependencies (Git, Terraform, and Utilities)
RUN apt-get update && \
    apt-get install -y git wget unzip lsb-release && \
    wget https://releases.hashicorp.com && \
    unzip terraform_1.7.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_1.7.0_linux_amd64.zip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Switch back to airflow user
USER airflow

# 4. Install Python dependencies
# Context is set to project root in docker-compose, so path is docker/requirements.txt
COPY docker/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# 5. Copy dbt project into the image
COPY --chown=airflow:root dbt_project /opt/airflow/dbt_project
