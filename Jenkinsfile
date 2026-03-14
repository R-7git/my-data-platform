pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-pass' // Create this ID in Jenkins Credentials (Username/Password)
        DOCKER_USER = 'rs121093'
        IMAGE_NAME = 'my-data-platform-airflow'
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
                    // Requires Terraform installed on Jenkins agent
                    sh 'terraform init'
                    sh 'terraform plan'
                }
            }
        }

                stage('Build Airflow Image') {
            steps {
                // Point to the Dockerfile inside the docker/ directory
                // Use -f to specify the path to the Dockerfile
                sh "docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest -f docker/Dockerfile ."
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

        stage('Cleanup') {
            steps {
                sh "docker image prune -f"
            }
        }
    }

    post {
        failure {
            echo "Deployment Failed. Check Slack Alerts."
        }
    }
}
