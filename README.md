# Datenanalyse Effizienzvergleich

Dieses Repository enthält Python-Skripte, die folgende Aufgaben ermöglichen:
- **Triggern von CI/CD-Pipelines** auf GitLab und GitHub
- **Erfassung von Build-Zeiten** der letzten 120 gebuildeten pipelines 
- **Statistische Analyse** der erfassten Daten
- **Visualisierung** der Ergebnisse in Form von Boxplots

## Enthaltene Skripte und deren Funktionen

### 1. **Triggern von CI/CD-Pipelines**
- **`trigger_GitLAB_workflow.py`**:
  - Startet die CI/CD-Pipeline eines GitLab-Projekts automatisiert 101-mal.
  - Nutzt die GitLab API und wartet 10 Sekunden zwischen den Starts, um API-Rate-Limits zu vermeiden.

- **`trigger_workflows.py`**:
  - Löst den Workflow einer GitHub Actions Pipeline 101-mal aus.
  - Nutzt die GitHub API und ermöglicht das einfache Auslösen von CI/CD-Stages über den Branch `main`.

### 2. **Statistische Analyse**
- **`statistischeAuswertung_gitlab_github.py`**:
  - Erfasst die Build-Zeiten der `build`-Stage für CI/CD-Pipelines auf GitLab und GitHub.
  - Berechnet wichtige statistische Kennzahlen wie:
    - Mittelwert
    - Varianz
    - Standardabweichung
    - Median
    - Minimum und Maximum
    - Signifikanz
  - Vergleicht die Daten 
  Zusatz: 
   Der Shapiro-Wilk-Test wird häufig verwendet, um zu entscheiden, ob ein parametrischer Test (z. B. t-Test) oder ein nicht-parametrischer Test (z. B. Mann-Whitney-U-Test) angewendet werden sollte.
   daher -> "Mann-Whitney-U-Test"

### 3. **Visualisierung**
- **Streudiagramme**:
  - Zeigt die Verteilung der Build-Zeiten für einzelne Builds in GitLab und GitHub an.
- **Boxplots**:
  - Visualisiert die Verteilung und Ausreißer der Build-Zeiten zwischen GitLab CI/CD und GitHub Actions.

### 4. **Speicherung der Ergebnisse**
- Die Analyse- und Visualisierungsergebnisse werden in Textdateien (`StatistikTextFiles/`) und Diagrammen (`Boxplots/`) gespeichert.

---

## Nutzung

### Voraussetzungen
- **Python 3.8+**
- Installation der Abhängigkeiten:
  ```bash
  pip install -r requirements.txt
