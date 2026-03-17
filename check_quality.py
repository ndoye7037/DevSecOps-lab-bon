import json
import sys
import os

REPORT_FILE = 'bandit-report.json'

if not os.path.exists(REPORT_FILE):
    print(f"Erreur : Le fichier {REPORT_FILE} est introuvable.")
    sys.exit(1)

try:
    with open(REPORT_FILE) as f:
        data = json.load(f)
        medium_count = sum(1 for issue in data['results'] if issue['issue_severity'] == 'MEDIUM')
        
        print(f"--- Rapport Quality Gate ---")
        print(f"Erreurs MEDIUM detectees : {medium_count}")
        
        if medium_count > 4:
            print("ECHEC : Le nombre d'erreurs MEDIUM depasse le seuil de 4.")
            sys.exit(1)
            
        print("SUCCES : Le code respecte les criteres de securite.")
        sys.exit(0)
except Exception as e:
    print(f"Erreur durant l'analyse : {e}")
    sys.exit(1)