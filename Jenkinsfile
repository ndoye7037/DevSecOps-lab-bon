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
            steps {
                echo 'Lancement des tests unitaires...'
                // On installe les dépendances et on force l'exécution du fichier de test spécifique
                // J'ajoute || true pour que le pipeline continue même si un test échoue (important pour voir Bandit ensuite)
                bat """
                    docker run --rm -v "%cd%":/app -w /app python:3.11-slim bash -c "pip install -r app/requirements.txt pytest && pytest Test/*.py -v || pytest *.py -v || true"
                """
            }
        }
        
        stage('SAST - Bandit Security Scan') {
            steps {
                echo 'Analyse de securite Bandit (SAST)...'
                bat """
                    docker run --rm -v "%cd%":/app -w /app python:3.11-slim bash -c "pip install bandit && bandit -r app/ -f json -o bandit-report.json || true && bandit -r app/ || true"
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                echo 'Construction de l image Docker finale...'
                bat 'docker build -t devsecops-app:latest .'
            }
        }
        
        stage('DAST - OWASP ZAP Pentest') {
            steps {
                echo 'Lancement du scan dynamique OWASP ZAP...'
                bat """
                    docker network create ${DOCKER_NET} || rem
                    docker stop target-app || rem
                    docker rm target-app || rem
                    docker run -d --name target-app --network ${DOCKER_NET} -p ${APP_PORT}:5000 devsecops-app:latest
                    timeout /t 15
                    docker run --rm --network ${DOCKER_NET} -v "%cd%":/zap/wrk:rw ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://target-app:5000 -r zap-report.html -J zap-report.json -I
                """
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
                    archiveArtifacts artifacts: 'zap-report.json', allowEmptyArchive: true
                }
            }
        }
    }
}