pipeline {
    agent any

    environment {
        // --- TOOL PATHS ---
        // Ensures Jenkins can find the terraform and ansible binaries in /usr/local/bin
        PATH = "/usr/local/bin:${env.PATH}"

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
                    // This will now work because terraform is in /usr/local/bin
                    sh 'terraform init'
                    sh 'terraform plan'
                }
            }
        }

        stage('Build Airflow Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:latest -f docker/Dockerfile ."
                sh "docker tag ${IMAGE_NAME}:latest ${DOCKER_USER}/${IMAGE_NAME}:latest"
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

        stage('Configure Server (Ansible)') {
            steps {
                dir('ansible') {
                    // This will now work because ansible is installed in Jenkins
                    sh "ansible-playbook -i inventory.ini setup_data_node.yml"
                }
            }
        }

        stage('Deploy to K8s') {
            steps {
                dir('k8s') {
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
            echo "FAILURE: Deployment failed. Review Jenkins console output."
        }
    }
}
