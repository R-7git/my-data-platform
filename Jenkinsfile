pipeline {
    agent any

    environment {
        // --- TOOL PATHS ---
        // Ensures Jenkins can find terraform, ansible, and the docker-cli in /usr/local/bin
        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"

        // --- DOCKER HUB CONFIG ---
        DOCKERHUB_CREDENTIALS = 'dockerhub-pass'
        DOCKER_USER = 'rs121093'
        IMAGE_NAME = 'my-data-platform-airflow'
        
        // --- JFROG ARTIFACTORY CONFIG ---
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
                    // Build the local image
                    sh "docker build -t ${IMAGE_NAME}:latest -f docker/Dockerfile ."
                    
                    // Tag for Public Docker Hub
                    sh "docker tag ${IMAGE_NAME}:latest ${DOCKER_USER}/${IMAGE_NAME}:latest"
                    
                    // Tag for Private Artifactory with versioning
                    sh "docker tag ${IMAGE_NAME}:latest ${ARTIFACTORY_URL}/${JFROG_REPO}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Push to Artifactory') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${JFROG_CREDS_ID}", 
                                     passwordVariable: 'JF_PASS', 
                                     usernameVariable: 'JF_USER')]) {
                        
                        // Login and Push to private JFrog repository
                        sh "echo ${JF_PASS} | docker login ${ARTIFACTORY_URL} -u ${JF_USER} --password-stdin"
                        sh "docker push ${ARTIFACTORY_URL}/${JFROG_REPO}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Push the latest tag to public Docker Hub
                    docker.withRegistry('', "${DOCKERHUB_CREDENTIALS}") {
                        sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Configure Server (Ansible)') {
            steps {
                dir('ansible') {
                    // Standardizes the target server environment
                    sh "ansible-playbook -i inventory.ini setup_data_node.yml"
                }
            }
        }

        stage('Deploy to K8s') {
            steps {
                dir('k8s') {
                    // Update Kubernetes with new manifests and force image pull
                    sh "kubectl apply -f airflow-deployment.yaml"
                    sh "kubectl apply -f airflow-service.yaml"
                    sh "kubectl rollout restart deployment/airflow-platform"
                }
            }
        }

        stage('Cleanup') {
            steps {
                // Housekeeping: Remove intermediate build layers
                sh "docker image prune -f"
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Build ${env.BUILD_NUMBER} is LIVE on Kubernetes port 30007."
        }
        failure {
            echo "FAILURE: Deployment failed. Review Jenkins console output."
        }
    }
}
