pipeline {
    agent any

    environment {
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
                // 1. Build local image
                sh "docker build -t ${IMAGE_NAME}:latest -f docker/Dockerfile ."
                
                // 2. Tag for Docker Hub
                sh "docker tag ${IMAGE_NAME}:latest ${DOCKER_USER}/${IMAGE_NAME}:latest"
                
                // 3. Tag for JFrog with Build Number
                sh "docker tag ${IMAGE_NAME}:latest ${ARTIFACTORY_URL}/${JFROG_REPO}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
            }
        }

        stage('Push to Artifactory') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${JFROG_CREDS_ID}", 
                                     passwordVariable: 'JF_PASS', 
                                     usernameVariable: 'JF_USER')]) {
                        
                        sh "echo ${JF_PASS} | docker login ${ARTIFACTORY_URL} -u ${JF_USER} --password-stdin"
                        sh "docker push ${ARTIFACTORY_URL}/${JFROG_REPO}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                    }
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

        // --- NEW: ANSIBLE CONFIGURATION STAGE ---
        stage('Configure Server (Ansible)') {
            steps {
                dir('ansible') {
                    // Ensures the target directories and docker environment are ready
                    sh "ansible-playbook -i inventory.ini setup_data_node.yml"
                }
            }
        }

        // --- NEW: KUBERNETES DEPLOYMENT STAGE ---
        stage('Deploy to K8s') {
            steps {
                dir('k8s') {
                    // Apply manifests and force a fresh pull of the 'latest' image
                    sh "kubectl apply -f airflow-deployment.yaml"
                    sh "kubectl apply -f airflow-service.yaml"
                    sh "kubectl rollout restart deployment/airflow-webserver"
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
            echo "SUCCESS: Build ${env.BUILD_NUMBER} is LIVE on Kubernetes port 30007."
        }
        failure {
            echo "FAILURE: Deployment failed. Check Jenkins logs for details."
        }
    }
}
