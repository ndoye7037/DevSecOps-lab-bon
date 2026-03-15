
pipeline {
    agent any
    environment {
        APP_PORT   = '5000'
        ZAP_PORT   = '8090'
        DOCKER_NET = 'devsecops-lab'
    }
    stages {
        
        stage('Checkout') {
            steps {
                echo 'Recuperation du code source...'
                checkout scm
            }
        }
       
        stage('Build & Test') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                echo 'Installation des dependances...'
                sh 'pip install -r app/requirements.txt pytest'
                echo 'Execution des tests unitaires...'
                sh 'pytest tests/ -v'
            }
        }
        
        stage('SAST - Bandit Security Scan') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                echo 'Analyse de securite statique (SAST)...'
                sh 'pip install bandit'
                sh 'bandit -r app/ -f json -o bandit-report.json || true'
                sh 'bandit -r app/ || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json',
                                     allowEmptyArchive: true
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                echo 'Construction de l image Docker...'
                sh 'docker build -t devsecops-app:latest .'
            }
        }
        
        stage('DAST - OWASP ZAP Pentest') {
            steps {
                echo 'Lancement du pentest dynamique avec OWASP ZAP...'
                sh '''
                    docker run -d \
                      --name target-app \
                      --network ${DOCKER_NET} \
                      -p ${APP_PORT}:5000 \
                      devsecops-app:latest
                    sleep 5
                '''
                sh '''
                    docker run --rm \
                      --network ${DOCKER_NET} \
                      -v $(pwd):/zap/wrk \
                      ghcr.io/zaproxy/zaproxy:stable \
                      zap-baseline.py \
                        -t http://target-app:5000 \
                        -r zap-report.html \
                        -J zap-report.json \
                        -I
                '''
            }
            post {
                always {
                    sh 'docker stop target-app || true'
                    sh 'docker rm target-app || true'
                    publishHTML([
                        allowMissing: true,
                        reportDir: '.',
                        reportFiles: 'zap-report.html',
                        reportName: 'ZAP Security Report'
                    ])
                    archiveArtifacts artifacts: 'zap-report.json',
                                     allowEmptyArchive: true
                }
            }
        }
    }
    post {
        success {
            echo 'Pipeline termine ! Consulte les rapports de securite.'
        }
        failure {
            echo 'Pipeline echoue. Regarde les logs pour plus de details.'
        }
    }
}