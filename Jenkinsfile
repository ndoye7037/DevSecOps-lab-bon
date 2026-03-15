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
                docker { 
                    image 'python:3.11-slim' 
                   
                    args '-u root:root --workdir /app'
                }
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
                docker { 
                    image 'python:3.11-slim' 
                    
                    args '-u root:root --workdir /app'
                }
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
                
                bat 'docker build -t devsecops-app:latest .'
            }
        }
        
        stage('DAST - OWASP ZAP Pentest') {
            steps {
                echo 'Lancement du pentest dynamique avec OWASP ZAP...'
                
                bat '''
                    docker network create devsecops-lab || rem
                    docker run -d --name target-app --network devsecops-lab -p 5000:5000 devsecops-app:latest
                    timeout /t 10
                '''
                bat '''
                    docker run --rm --network devsecops-lab -v "%cd%":/zap/wrk:rw ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://target-app:5000 -r zap-report.html -J zap-report.json -I
                '''
            }
            post {
                always {
                    bat 'docker stop target-app || rem'
                    bat 'docker rm target-app || rem'
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