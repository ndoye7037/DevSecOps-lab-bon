/ Jenkinsfile
pipeline {
    agent any
    environment {
        APP_PORT    = '5000'
        ZAP_PORT    = '8090'
        DOCKER_NET  = 'devsecops-lab'
    }
    stages {
        // ── STAGE 1 : Récupérer le code ──
        stage('Checkout') {
            steps {
                echo 'Récupération du code source...'
                checkout scm
            }
        }
        // ── STAGE 2 : Build et tests unitaires ──
        stage('Build & Test') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                echo '🧪Installation des dépendances...'
                sh 'pip install -r app/requirements.txt pytest'
                echo '🔧Exécution des tests unitaires...'
                sh 'pytest tests/ -v'
            }
        }
        // ── STAGE 3 : SAST avec Bandit ──
        stage('SAST - Bandit Security Scan') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                echo '🔍 Analyse de sécurité statique du code (SAST)...'
                sh 'pip install bandit'
                // -ll = niveau HIGH uniquement, -r = récursif
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
        // ── STAGE 4 : Build de l'image Docker ──
        stage('Docker Build') {
            steps {
                echo ' Construction de l image Docker...' 🐳
                sh 'docker build -t devsecops-app:latest .'
            }
        }
        // ── STAGE 5 : DAST avec OWASP ZAP ──
        stage('DAST - OWASP ZAP Pentest') {
            steps {
                echo ' Lancement du pentest dynamique avec OWASP ZAP...' 🚨
                // Démarrer l'application cible
                sh '''
                    docker run -d \
                      --name target-app \
                      --network ${DOCKER_NET} \
                      -p ${APP_PORT}:5000 \
                      devsecops-app:latest
                    sleep 5
                '''
                // Lancer ZAP en mode baseline scan
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
                    // Arrêter l'app cible
                    sh 'docker stop target-app || true'
                    sh 'docker rm target-app || true'
                    // Sauvegarder les rapports
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
            echo 'Pipeline terminé ! Consulte les rapports de sécurité.'
        }
        failure {
            echo 'Pipeline échoué. Regarde les logs pour plus de détails.'
        }
}