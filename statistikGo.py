import requests
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime, timedelta, timezone
import numpy as np



from dotenv import load_dotenv
import os

# Lade die .env-Datei
load_dotenv()

# Tokens auslesen
gitlab_token = os.getenv("GITLAB_TOKEN")


# GitLab API-Konfiguration
gitlab_project_id = "62051658"
gitlab_headers = {}
# gitlab_headers = {"Authorization": f"Bearer {gitlab_token}"}

# GitHub API-Konfiguration
github_token = os.getenv("GITHUB_TOKEN")

github_owner = "Johanna0815"
github_repo = "Go_Konsolenanwendung"
github_headers = {"Authorization": f"Bearer {github_token}"}

# --- Zeitspanne für Builds ---
two_weeks_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(weeks=2)

# --- GitLab: Build-Zeit der `build`-Stage abrufen ---
def get_gitlab_build_times():
    print("GitLab Build-Zeiten werden abgerufen...")
    build_times = []
    page = 1

    while len(build_times) < 120:
        pipeline_url = f"https://gitlab.com/api/v4/projects/{gitlab_project_id}/pipelines"
        response = requests.get(pipeline_url, headers=gitlab_headers, params={"per_page": 100, "page": page})
        
        if response.status_code != 200:
            print(f"Fehler beim Abrufen der GitLab-Pipelines: {response.json()}")
            break

        pipelines = response.json()
        if not pipelines:
            break

        for pipeline in pipelines:
            pipeline_created_at = datetime.fromisoformat(pipeline["created_at"].replace("Z", "+00:00"))
            if pipeline_created_at < two_weeks_ago:
                continue  # Überspringe Pipelines älter als zwei Wochen erstellt

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

                    if len(build_times) == 120:
                        break
            if len(build_times) == 120:
                break
        page += 1

    return build_times


# --- GitHub: Build-Zeit der `build`-Stage abrufen ---
def get_github_build_times():
    print("GitHub Build-Zeiten werden abgerufen...")
    build_times = []
    page = 1

    while len(build_times) < 120:
        workflow_url = f"https://api.github.com/repos/{github_owner}/{github_repo}/actions/runs"
        response = requests.get(workflow_url, headers=github_headers, params={"per_page": 100, "page": page})
        
        if response.status_code != 200:
            print(f"Fehler beim Abrufen der GitHub-Workflows: {response.json()}")
            break

        runs = response.json().get("workflow_runs", [])
        if not runs:
            break

        for run in runs:
            run_created_at = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            if run_created_at < two_weeks_ago:
                continue  # Überspringe Runs älter als zwei Wochen

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

                    if len(build_times) == 120:
                        break
            if len(build_times) == 120:
                break
        page += 1

    return build_times


# --- Statistik berechnen ---
def calculate_statistics(times):
    count = len(times)
    mean = np.mean(times)
    variance = np.var(times, ddof=1)
    std_dev = np.std(times, ddof=1)
    median = np.median(times)
    q1 = np.percentile(times, 25)
    q3 = np.percentile(times, 75)
    iqr = q3 - q1
    minimum = np.min(times)
    maximum = np.max(times)
    return count, mean, variance, std_dev, median, minimum, maximum, iqr


# --- Normalverteilung prüfen ---
def check_normality(times):
    stat, p_value = stats.shapiro(times)
    is_normal = p_value > 0.05
    return stat, p_value, is_normal


# --- Daten abrufen ---
gitlab_times = get_gitlab_build_times()
github_times = get_github_build_times()

# --- Ergebnisse speichern ---
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
runtime = "Go"
txt_filename = f"{runtime}_build_times_{timestamp}.txt"

# nach 10 werten einen zeilenumbruch einfügen. 
def format_values(values):
    return "\n".join(
        ", ".join(f"{values[i]:.2f}" for i in range(start, min(start + 10, len(values))))
        for start in range(0, len(values), 10)
)




with open(txt_filename, "w") as file:
    if gitlab_times and github_times:
        gitlab_stats = calculate_statistics(gitlab_times)
        github_stats = calculate_statistics(github_times)

        # Shapiro-Wilk Test
        gitlab_normality = check_normality(gitlab_times)
        github_normality = check_normality(github_times)

        # Mann-Whitney-U-Test
        u_stat, mw_p_value = stats.mannwhitneyu(gitlab_times, github_times, alternative='two-sided')
        significance = "Ja" if mw_p_value < 0.05 else "Nein"

        
# Ergebnisse in Datei schreiben
        file.write("GitLab Build-Zeiten:\n")
        file.write(format_values(gitlab_times) + "\n\n")
        file.write(f"Statistiken, mit (build-Wert)-Anzahl: {gitlab_stats[0]} Messwerten:\n")
        file.write(f"  Mittelwert: {gitlab_stats[1]:.2f}\n  Varianz: {gitlab_stats[2]:.2f}\n")
        file.write(f"  Standardabweichung: {gitlab_stats[3]:.2f}\n  Median: {gitlab_stats[4]:.2f}\n")
        file.write(f"  Minimum: {gitlab_stats[5]:.2f}\n  Maximum: {gitlab_stats[6]:.2f}\n")
        file.write(f"  Interquartilsabstand (IQR): {gitlab_stats[7]:.2f}\n")
        file.write(f"  Shapiro-Wilk-Teststatistik: {gitlab_normality[0]:.4f}, P-Wert: {gitlab_normality[1]:.4f}\n")
        file.write(f"  Normalverteilung: {'Ja' if gitlab_normality[2] else 'Nein'}\n\n")

        file.write("GitHub Build-Zeiten:\n")
        file.write(format_values(github_times) + "\n\n")
        file.write(f"Statistiken, mit (build-Wert)-Anzahl: {github_stats[0]} Messwerten:\n")
        file.write(f"  Mittelwert: {github_stats[1]:.2f}\n  Varianz: {github_stats[2]:.2f}\n")
        file.write(f"  Standardabweichung: {github_stats[3]:.2f}\n  Median: {github_stats[4]:.2f}\n")
        file.write(f"  Minimum: {github_stats[5]:.2f}\n  Maximum: {github_stats[6]:.2f}\n")
        file.write(f"  Interquartilsabstand (IQR): {github_stats[7]:.2f}\n")
        file.write(f"  Shapiro-Wilk-Teststatistik: {github_normality[0]:.4f}, P-Wert: {github_normality[1]:.4f}\n")
        file.write(f"  Normalverteilung: {'Ja' if github_normality[2] else 'Nein'}\n\n")

        file.write(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Vergleich build-time von Gitlab CI/CD und GitHub Actions, um signifikanten Unterschied festzustellen ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

        file.write(f"Mann-Whitney-U-Test:\n")
        file.write(f"  U-Statistik: {u_stat:.2f}, P-Wert: {mw_p_value:.4f}\n")
        file.write(f"  Signifikanter Unterschied: {significance}\n\n")


# --- Boxplot mit Median anzeigen ---
if gitlab_times and github_times:
    plt.figure(figsize=(12, 8))
    boxplot_data = [gitlab_times, github_times]
    labels = [
        f"GitLab CI/CD\n(Median: {gitlab_stats[4]:.2f}s, IQR: {gitlab_stats[7]:.2f}s)",
        f"GitHub Actions\n(Median: {github_stats[4]:.2f}s, IQR: {github_stats[7]:.2f}s)"
    ]

  # Boxplot erstellen
    plt.boxplot(boxplot_data, labels=labels, showfliers=True)
    # #plt.yticks(np.arange(0, max(max(gitlab_times), max(github_times)) + 10, 10))
#     # Dynamische Anpassung der y-Achse
    plt.ylim(0, max(max(gitlab_times), max(github_times)) * 1.1)  # Skalierung für bessere Sichtbarkeit
    plt.yticks(np.arange(0, max(max(gitlab_times), max(github_times)) + 10, 5))  # Kleinere Intervalle


   
    plt.ylabel("Build-Zeit: (Sekunden)")
    plt.title(f"GitLab CI/CD vs. GitHub Actions\nRuntime: {runtime}")
    plt.grid(True)





    # Diagramm speichern
    boxplot_filename = f"build_times_{runtime}_{timestamp}_Boxplot.png"
    plt.savefig(boxplot_filename)
    plt.show()
    print(f"Boxplot gespeichert unter '{boxplot_filename}'")
else:
    print("Es konnten nicht genügend Daten gesammelt werden, um eine Analyse zu erstellen.")
