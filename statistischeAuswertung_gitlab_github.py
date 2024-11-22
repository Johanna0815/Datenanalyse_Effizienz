import requests
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime
import math
import numpy as np



from dotenv import load_dotenv
import os

# Lade die .env-Datei
load_dotenv()


# GitLab API-Konfiguration
gitlab_project_id = "62053421"
gitlab_headers = {}

# GitHub API-Konfiguration
github_token = os.getenv("GITHUB_TOKEN")
github_owner = "Johanna0815"
github_repo = "python_Konsolenanwendung"
github_headers = {"Authorization": f"Bearer {github_token}"}

# --- GitLab: Build-Zeit der `build`-Stage abrufen ---
def get_gitlab_build_times():
    print("GitLab Build-Zeiten werden abgerufen...")
    pipeline_url = f"https://gitlab.com/api/v4/projects/{gitlab_project_id}/pipelines"
    response = requests.get(pipeline_url, headers=gitlab_headers, params={"per_page": 115})
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der GitLab-Pipelines: {response.json()}")
        return []

    pipelines = response.json()
    build_times = []

    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        jobs_url = f"https://gitlab.com/api/v4/projects/{gitlab_project_id}/pipelines/{pipeline_id}/jobs"
        jobs_response = requests.get(jobs_url, headers=gitlab_headers)

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
    response = requests.get(workflow_url, headers=github_headers, params={"per_page": 115})
    
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

# --- Statistik berechnen ---
def calculate_statistics(times):
    mean = np.mean(times)
    variance = np.var(times, ddof=1)
    std_dev = np.std(times, ddof=1)
    median = np.median(times)
    minimum = np.min(times)
    maximum = np.max(times)
    return mean, variance, std_dev, median, minimum, maximum

# --- Ergebnisse speichern ---
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
txt_filename = f"build_times_{timestamp}.txt"

with open(txt_filename, "w") as file:
    if gitlab_times:
        gitlab_stats = calculate_statistics(gitlab_times)
        file.write("GitLab Build-Zeiten:\n")
        file.write(", ".join(map(str, gitlab_times)) + "\n\n")
        file.write(f"Statistiken:\n  Mittelwert: {gitlab_stats[0]:.2f}\n  Varianz: {gitlab_stats[1]:.2f}\n")
        file.write(f"  Standardabweichung: {gitlab_stats[2]:.2f}\n  Median: {gitlab_stats[3]:.2f}\n")
        file.write(f"  Minimum: {gitlab_stats[4]:.2f}\n  Maximum: {gitlab_stats[5]:.2f}\n\n")
    if github_times:
        github_stats = calculate_statistics(github_times)
        file.write("GitHub Build-Zeiten:\n")
        file.write(", ".join(map(str, github_times)) + "\n\n")
        file.write(f"Statistiken:\n  Mittelwert: {github_stats[0]:.2f}\n  Varianz: {github_stats[1]:.2f}\n")
        file.write(f"  Standardabweichung: {github_stats[2]:.2f}\n  Median: {github_stats[3]:.2f}\n")
        file.write(f"  Minimum: {github_stats[4]:.2f}\n  Maximum: {github_stats[5]:.2f}\n\n")
print(f"Build-Zeiten gespeichert unter '{txt_filename}'")


# --- Streudiagramm erstellen ---
if gitlab_times and github_times:
    plt.figure(figsize=(10, 6))

    # X-Achse: Indizes der Builds
    gitlab_x = range(1, len(gitlab_times) + 1)
    github_x = range(1, len(github_times) + 1)

    # Streudiagramm erstellen
    plt.scatter(gitlab_x, gitlab_times, color='blue', label='GitLab CI/CD', alpha=0.7)
    plt.scatter(github_x, github_times, color='green', label='GitHub Actions', alpha=0.7)

    # Achsen beschriften
    plt.xlabel("Build-Index")
    plt.ylabel("Build-Zeit (Sekunden)")
    plt.title("Streudiagramm der Build-Zeiten: GitLab vs. GitHub")
    plt.legend()
    plt.grid(True)

    # Streudiagramm speichern
    scatter_filename = f"build_times_{timestamp}_Scatterplot.png"
    plt.savefig(scatter_filename)
    plt.show()
    print(f"Streudiagramm gespeichert unter '{scatter_filename}'")

    # --- Boxplot erstellen ---
    plt.boxplot([gitlab_times, github_times], labels=["GitLab CI/CD", "GitHub Actions"])
    plt.ylabel("Build-Zeit (Sekunden)")
    plt.title("Build-Zeiten: GitLab vs. GitHub (Stage: build)")
    plt.grid(True)

    # Diagramm speichern
    boxplot_filename = f"build_times_{timestamp}_Boxplot.png"
    plt.savefig(boxplot_filename)
    plt.show()
    print(f"Boxplot gespeichert unter '{boxplot_filename}'")

    # Statistischer Vergleich
    t_stat, p_value = stats.ttest_ind(gitlab_times, github_times, equal_var=False)
    print("\nStatistischer Vergleich:")
    print(f"  T-Statistik: {t_stat:.2f}")
    print(f"  P-Wert: {p_value:.4f}")
    if p_value < 0.05:
        print("  Ergebnis: Statistisch signifikant (p < 0.05)")
    else:
        print("  Ergebnis: Nicht signifikant (p ≥ 0.05)")
else:
    print("Es konnten nicht genügend Daten gesammelt werden, um eine Analyse zu erstellen.")
