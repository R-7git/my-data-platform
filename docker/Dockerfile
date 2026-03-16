# 1. Base Image
FROM apache/airflow:2.8.1

USER root

# 2. Install System Dependencies
RUN apt-get update && \
    apt-get install -y git wget unzip lsb-release && \
    
    # Install Terraform
    TERRAFORM_VERSION=1.7.0 && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then TARGET=amd64; else TARGET=arm64; fi && \
    
    wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${TARGET}.zip -O /tmp/terraform.zip && \
    unzip /tmp/terraform.zip -d /usr/local/bin/ && \
    rm /tmp/terraform.zip && \
    
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Switch back to airflow user
USER airflow

# 4. Install Python dependencies
COPY docker/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# 5. Copy dbt project
COPY --chown=airflow:root dbt_project /opt/airflow/dbt_project