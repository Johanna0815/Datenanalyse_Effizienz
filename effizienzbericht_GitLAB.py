import requests
import csv
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
import os

# Lade die .env-Datei
load_dotenv()

# Tokens auslesen
# Konfigurationseinstellungen
gitlab_token = os.getenv("GITLAB_TOKEN")
gitlab_headers = {"Authorization": f"Bearer {gitlab_token}"}


# headers = {'Authorization': f'Bearer {token}'}
repo_id = '62009936'  # Die Projekt-ID in GitLab
per_page = 101  
total_duration = 0
completed_jobs = 0

# Pfad zur CSV-Datei
csv_dir = '/mnt/wsl/Ubuntu-20.04/home/johanna/python_Datenanalyse/CSV_Datenerhebung_GitLAB'
csv_filename = "gitlab_build_times.csv"
csv_path = os.path.join(csv_dir, csv_filename)

# Stelle sicher, dass das Verzeichnis existiert
os.makedirs(csv_dir, exist_ok=True)

# Öffne und schreibe in die CSV-Datei
with open(csv_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Job ID", "Status", "Start Time", "Duration (s)"])

    # Abrufen und Verarbeiten der Workflow-Daten
    page = 1
    while completed_jobs < 101:
        api_url = f"https://gitlab.com/api/v4/projects/{repo_id}/jobs?per_page={per_page}&page={page}"
        response = requests.get(api_url, headers=gitlab_headers)
        data = response.json()

        if not data or 'message' in data:
            break

        for job in data:
            if job['status'] == 'success':
                start_time = datetime.fromisoformat(job['started_at'].rstrip('Z'))
                end_time = datetime.fromisoformat(job['finished_at'].rstrip('Z'))
                duration = (end_time - start_time).total_seconds()
                total_duration += duration
                writer.writerow([job['id'], job['status'], job['started_at'], duration])

                completed_jobs += 1
                if completed_jobs == 101:
                    break
        page += 1

# Ausgabe der Gesamtdauer und Speicherstatus der CSV-Datei
if os.path.exists(csv_path):
    print(f"CSV-Datei wurde gespeichert: {csv_path}")
    print(f"Die Gesamtdauer der ersten 101 erfolgreichen Jobs beträgt: {total_duration} Sekunden")
else:
    print("CSV-Datei wurde nicht gespeichert.")
