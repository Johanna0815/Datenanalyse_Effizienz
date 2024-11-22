import requests
import time

# Konfigurationseinstellungen
token = 'gtlab_token'  
headers = {
    'Private-Token': token
}
project_id = '62051658'   
ref = 'main'  # Branch, für den die Pipeline gestartet werden soll

# URL für die GitLab API, um die Pipeline auszulösen
pipeline_url = f"https://gitlab.com/api/v4/projects/{project_id}/pipeline"

# Daten für den Pipeline-Start
data = {
    "ref": ref
}

# Starte die Pipeline 101 Mal
for _ in range(101):
    response = requests.post(pipeline_url, headers=headers, data=data)
    print("Pipeline gestartet, Status Code:", response.status_code)
    if response.status_code != 201:
        print("Fehler:", response.json())
    time.sleep(10)  # Warte 10 Sekunden zwischen den Starts, um Rate Limits zu vermeiden 
