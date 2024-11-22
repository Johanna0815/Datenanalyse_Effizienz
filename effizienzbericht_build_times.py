import requests
import matplotlib.pyplot as plt
from datetime import datetime


from dotenv import load_dotenv
import os

# Lade die .env-Datei
load_dotenv()

# Tokens auslesen

# GitLab API-Konfiguration
gitlab_project_id = "62053421"  # Beispiel: 62053421

# GitHub API-Konfiguration
github_token = os.getenv("GITHUB_TOKEN")

github_owner = "Johanna0815"
github_repo = "python_Konsolenanwendung"


github_headers = {"Authorization": f"Bearer {github_token}"}

github_headers = {"Authorization": f"Bearer {github_token}"}
# --- GitLab: Build-Zeit der `build`-Stage abrufen (ohne Token) ---
def get_gitlab_build_times():
    print("GitLab Build-Zeiten werden abgerufen...")
    pipeline_url = f"https://gitlab.com/api/v4/projects/{gitlab_project_id}/pipelines"
    response = requests.get(pipeline_url, params={"per_page": 101})
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der GitLab-Pipelines: {response.json()}")
        return []

    pipelines = response.json()
    build_times = []

    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        jobs_url = f"https://gitlab.com/api/v4/projects/{gitlab_project_id}/pipelines/{pipeline_id}/jobs"
        jobs_response = requests.get(jobs_url)

        if jobs_response.status_code != 200:
            print(f"Fehler beim Abrufen der Jobs für Pipeline {pipeline_id}: {jobs_response.json()}")
            continue

        jobs = jobs_response.json()
        for job in jobs:
            if job["stage"] == "build" and job["started_at"] and job["finished_at"]:
                started_at = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                finished_at = datetime.fromisoformat(job["finished_at"].replace("Z", "+00:00"))
                build_time = (finished_at - started_at).total_seconds()
                build_times.append(build_time)

    return build_times


# --- GitHub: Build-Zeit der `build`-Stage abrufen ---
def get_github_build_times():
    print("GitHub Build-Zeiten werden abgerufen...")
    workflow_url = f"https://api.github.com/repos/{github_owner}/{github_repo}/actions/runs"
    response = requests.get(workflow_url, headers=github_headers, params={"per_page": 101})

    if response.status_code != 200:
        print(f"Fehler beim Abrufen der GitHub-Workflows: {response.json()}")
        return []

    runs = response.json().get("workflow_runs", [])
    build_times = []

    for run in runs:
        run_id = run["id"]
        jobs_url = f"https://api.github.com/repos/{github_owner}/{github_repo}/actions/runs/{run_id}/jobs"
        jobs_response = requests.get(jobs_url, headers=github_headers)

        if jobs_response.status_code != 200:
            print(f"Fehler beim Abrufen der Jobs für Workflow {run_id}: {jobs_response.json()}")
            continue

        jobs = jobs_response.json().get("jobs", [])
        for job in jobs:
            if "build" in job["name"].lower() and job["started_at"] and job["completed_at"]:
                started_at = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                completed_at = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
                build_time = (completed_at - started_at).total_seconds()
                build_times.append(build_time)

    return build_times


# --- Daten abrufen ---
gitlab_times = get_gitlab_build_times()
github_times = get_github_build_times()

# --- Daten analysieren und visualisieren ---
if gitlab_times and github_times:
    plt.boxplot([gitlab_times, github_times], labels=["GitLab CI/CD", "GitHub Actions"])
    plt.ylabel("Build-Zeit (Sekunden)")
    plt.title("Build-Zeiten: GitLab vs. GitHub (Stage: build)")
    plt.grid(True)
    plt.savefig("build_times_stage_build.png")
    plt.show()
    print("Diagramm gespeichert unter 'build_times_stage_build.png'")
else:
    print("Es konnten nicht genügend Daten gesammelt werden, um einen Vergleich zu erstellen.")

