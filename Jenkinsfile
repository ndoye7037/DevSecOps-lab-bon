pipeline {
    agent any
    environment {
        APP_PORT   = '5000'
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

        stage('Quality Gate') {
            steps {
                echo 'Verification des seuils de securite (Quality Gate)...'
                // Ce script Python analyse le JSON et check si MEDIUM > 4
                bat """
                    docker run --rm -v "%cd%":/app -w /app python:3.11-slim python -c "
import json
try:
    with open('bandit-report.json') as f:
        data = json.load(f)
        medium_count = sum(1 for issue in data['results'] if issue['issue_severity'] == 'MEDIUM')
        print(f'Nombre d erreurs MEDIUM : {medium_count}')
        if medium_count > 4:
            print('ERREUR : Trop d erreurs de niveau MEDIUM (> 4). Echec de la Quality Gate.')
            exit(1)
        print('Quality Gate PASSEE avec succes.')
except Exception as e:
    print(f'Erreur lors de l analyse du rapport : {e}')
    exit(1)
"
                """
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
                    archiveArtifacts artifacts: 'zap-report.html, zap-report.json', allowEmptyArchive: true
                }
            }
        }
    }
}