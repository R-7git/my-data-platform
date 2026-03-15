pipeline {
    agent any

    environment {
        // --- TOOL PATHS ---
        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"

        // --- DOCKER HUB CONFIG ---
        DOCKERHUB_CREDENTIALS = 'dockerhub-pass'
        DOCKER_USER = 'rs121093'
        IMAGE_NAME = 'my-data-platform-airflow'
        
        // --- JFROG CONFIG (BYPASSED) ---
        ARTIFACTORY_URL = 'devops-artifactory:8081' 
        JFROG_CREDS_ID  = 'jfrog-admin-creds'
        JFROG_REPO      = 'docker-local'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    sh 'terraform init'
                    sh 'terraform plan'
                }
            }
        }

        stage('Build Airflow Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:latest -f docker/Dockerfile ."
                    sh "docker tag ${IMAGE_NAME}:latest ${DOCKER_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('', "${DOCKERHUB_CREDENTIALS}") {
                        sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Configure Server (Ansible)') {
            steps {
                dir('ansible') {
                    sh "ansible-playbook -i inventory.ini setup_data_node.yml"
                }
            }
        }

        stage('Deploy to K8s & Auto-Trigger DAG') {
            steps {
                dir('k8s') {
                    // 1. Update Kubernetes manifests
                    sh "kubectl apply -f airflow-deployment.yaml"
                    sh "kubectl apply -f airflow-service.yaml"
                    
                    // 2. Restart and wait for the NEW pod to reach "Ready"
                    sh "kubectl rollout restart deployment/airflow-platform"
                    sh "kubectl rollout status deployment/airflow-platform --timeout=90s"
                    
                    // 3. FIXED: Cooldown and Reserialize
                    // We wait 45s to ensure Airflow's internal file-scanner finds the DAG
                    sh """
                    NEW_POD=\$(kubectl get pods -l app=airflow --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
                    
                    echo "Cooldown: Waiting 45s for Airflow to parse new DAGs on \$NEW_POD..."
                    sleep 45

                    echo "Reserializing DAGs to sync database..."
                    kubectl exec \$NEW_POD -c webserver -- airflow dags reserialize || true
                    
                    echo "Triggering DAG: 2_enterprise_elt_pipeline"
                    kubectl exec \$NEW_POD -c webserver -- airflow dags trigger 2_enterprise_elt_pipeline || \
                    kubectl exec \$NEW_POD -- airflow dags trigger 2_enterprise_elt_pipeline
                    """
                }
            }
        }

        stage('Cleanup') {
            steps {
                sh "docker image prune -f"
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Build ${env.BUILD_NUMBER} deployed and DAG triggered!"
        }
        failure {
            echo "FAILURE: Pipeline failed. Check Jenkins logs."
        }
    }
}
