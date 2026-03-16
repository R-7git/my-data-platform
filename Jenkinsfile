pipeline {
    agent any

    environment {
        // --- TOOL PATHS ---
        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"

        // --- DOCKER HUB CONFIG ---
        DOCKERHUB_CREDENTIALS = 'dockerhub-pass'
        DOCKER_USER = 'rs121093'
        IMAGE_NAME = 'my-data-platform-airflow'
        
        // --- SNOWFLAKE CONFIG ---
        SNOW_PASS = credentials('snowflake-password') 
        TF_VAR_snowflake_account = 'BKVGNQZ-UO15536'
        TF_VAR_snowflake_user    = 'ROSHAN'
        
        // --- KUBECONFIG ---
        KUBECONFIG = "/var/jenkins_home/.kube/config"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Terraform Snowflake Plan') {
            steps {
                dir('terraform') {
                    withEnv(["TF_VAR_snowflake_password=${env.SNOW_PASS}"]) {
                        sh 'terraform init'
                        sh 'terraform plan'
                    }
                }
            }
        }

        // --- SENIOR DATA TRANSFORMATION & VALIDATION ---
        stage('dbt Transformation & Validation') {
            steps {
                dir('dbt_project') {
                    script {
                        // Pass the Snowflake password to dbt
                        withEnv(["DBT_SNOWFLAKE_PASSWORD=${env.SNOW_PASS}"]) {
                            sh 'dbt deps'
                            // 1. Build models with CURRENT Snowflake data (the poisoned rows)
                            sh 'dbt run --target dev --full-refresh'
                            // 2. Test the new models (this WILL catch the duplicates)
                            sh 'dbt test --target dev'
                        }
                    }
                }
            }
        }

        stage('Build Airflow Image') {
            steps {
                script {
                    sh "docker build --pull -t ${IMAGE_NAME}:latest -f docker/Dockerfile ."
                    sh "docker tag ${IMAGE_NAME}:latest ${DOCKER_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", passwordVariable: 'D_PASS', usernameVariable: 'D_USER')]) {
                        sh 'echo "${D_PASS}" | docker login -u "${D_USER}" --password-stdin'
                        sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:latest"
                        sh "docker logout"
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
                    sh "kubectl apply -f airflow-deployment.yaml"
                    sh "kubectl apply -f airflow-service.yaml"
                    
                    sh "kubectl rollout restart deployment/airflow-platform"
                    sh "kubectl rollout status deployment/airflow-platform --timeout=120s"
                    
                    sh """
                    NEW_POD=\$(kubectl get pods -l app=airflow --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
                    
                    echo "Cooldown: Waiting 45s for Airflow to parse new DAGs on \$NEW_POD..."
                    sleep 45

                    echo "Reserializing DAGs to sync database..."
                    kubectl exec \$NEW_POD -c webserver -- airflow dags reserialize || true
                    
                    echo "Triggering DAG: 2_enterprise_elt_pipeline"
                    kubectl exec \$NEW_POD -c webserver -- airflow dags trigger 2_enterprise_elt_pipeline
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
            echo "SUCCESS: Build ${env.BUILD_NUMBER} passed Data Quality and deployed!"
        }
        failure {
            echo "FAILURE: Pipeline failed. Check dbt logs for data quality errors."
        }
    }
}
