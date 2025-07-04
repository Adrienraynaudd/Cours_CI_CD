import requests
import os

REPO = "adrienraynaudd/Cours_CI_CD"
from dotenv import load_dotenv
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


API_URL = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

def fetch_issues():
    issues = []
    page = 1

    while True:
        url = f"{API_URL}&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Erreur lors de la récupération : {response.status_code}")
            break

        data = response.json()
        if not data:
            break
        issues.extend(data)
        page += 1

    return issues

def generate_metrics(issues):
    total = len(issues)
    open_issues = sum(1 for i in issues if i['state'] == 'open')
    closed_issues = total - open_issues

    label_count = {}
    for issue in issues:
        for label in issue.get('labels', []):
            name = label['name']
            label_count[name] = label_count.get(name, 0) + 1

    print(f" Projet : {REPO}")
    print(f"- Total issues : {total}")
    print(f"- Ouvertes     : {open_issues}")
    print(f"- Fermées      : {closed_issues}\n")

    print(" Répartition par label :")
    for label, count in sorted(label_count.items(), key=lambda x: -x[1]):
        print(f"  - {label}: {count}")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print(" Veuillez définir la variable d’environnement GITHUB_TOKEN.")
        exit(1)

    issues = fetch_issues()
    generate_metrics(issues)
