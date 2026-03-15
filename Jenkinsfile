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
                    // Build local image using your Dockerfile
                    sh "docker build -t ${IMAGE_NAME}:latest -f docker/Dockerfile ."
                    
                    // Tag for Public Docker Hub
                    sh "docker tag ${IMAGE_NAME}:latest ${DOCKER_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        /* 
        STAGE BYPASSED: Artifactory is currently undergoing maintenance/resource issues.
        Proceeding directly to Docker Hub and K8s Deployment.
        
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
        */

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Push the latest tag to your public repository
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

        stage('Deploy to K8s') {
            steps {
                dir('k8s') {
                    // Update Kubernetes with your manifests
                    sh "kubectl apply -f airflow-deployment.yaml"
                    sh "kubectl apply -f airflow-service.yaml"
                    
                    // Force K8s to pull the fresh image we just pushed to Docker Hub
                    sh "kubectl rollout restart deployment/airflow-platform"
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
            echo "SUCCESS: Build ${env.BUILD_NUMBER} deployed to K8s via Docker Hub!"
        }
        failure {
            echo "FAILURE: Pipeline failed. Review the Jenkins console output."
        }
    }
}
