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
                    
                    // 2. Restart to pull the new image
                    sh "kubectl rollout restart deployment/airflow-platform"

                    // 3. Wait for the new pod to reach "Ready" status (better than just sleeping)
                    sh "kubectl rollout status deployment/airflow-platform --timeout=90s"
                    
                    // 4. AUTO-TRIGGER: targeting the deployment directly
                    // Uses container 'webserver' as defined in your multi-container pod
                    sh """
                    kubectl exec deployment/airflow-platform -c webserver -- \
                    airflow dags trigger 2_enterprise_elt_pipeline
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
