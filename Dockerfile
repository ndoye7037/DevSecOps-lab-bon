# Dockerfile
FROM python:3.11-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier et installer les dépendances
COPY app/requirements.txt .
RUN pip install --no-cache-dir flask

# Copier le code de l'application
COPY app/ .

# Exposer le port 5000
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]