import requests
import time


from dotenv import load_dotenv
import os

# Lade die .env-Datei
load_dotenv()




# persönlichen Zugangsdaten GitHub 
github_token = os.getenv("GITHUB_TOKEN")
headers = {
    'Authorization': f'Bearer {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Repository-Informationen
owner = 'Johanna0815'
repo = 'python_Konsolenanwendung' 
workflow_id = 'python_ci.yml'  

# URL für die GitHub API, um den Workflow auszulösen
workflow_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"

# Daten für den Workflow-Start
data = {
    "ref": "main",
    "inputs": {}
}

# Starte den Workflow 101 Mal
for _ in range(101):
    response = requests.post(workflow_url, headers=headers, json=data)
    print("Workflow gestartet, Status Code:", response.status_code)
    if response.status_code != 204:
        print("Fehler:", response.json())
    time.sleep(10)  # Warte 10 Sekunden zwischen den Starts, um Rate Limits zu vermeiden
