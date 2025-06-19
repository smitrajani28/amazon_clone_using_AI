import os
import subprocess
import requests
import json
import time
import pyautogui
import pyperclip
from requests.auth import HTTPBasicAuth

# CONFIGS
SONAR_HOST_URL = "http://host.docker.internal:9000"
SONAR_PROJECT_KEY = "Amazon-Try"
SONAR_TOKEN = "sqp_88d3457d87ce761402dcf2f3f12f0d7d6838c763"
SOURCE_DIR = "."
SONAR_HOST = "http://localhost:9000"

# STEP 1: sonar-project.properties
def create_sonar_properties(path):
    with open("sonar-project.properties", "w") as f:
        f.write(f"""
sonar.projectKey={SONAR_PROJECT_KEY}
sonar.sources={path}
sonar.host.url={SONAR_HOST_URL}
sonar.login={SONAR_TOKEN}
sonar.inclusions=**/*.py,**/*.js,**/*.java
sonar.exclusions=**/__pycache__/**,**/tests/**,ai-fix-agent/**,ai-fix-agent/**/*.*,**/chat_bot/**
        """.strip())
    print("[✅] sonar-project.properties created.")

# STEP 2: Run scanner
# def run_sonar_scanner():
#     print("[🔍] Running sonar-scanner...")
#     subprocess.run(["sonar-scanner"], check=True)
#     print("[✅] Analysis complete.")

def run_sonar_scanner_docker():
    print("[INFO] Running sonar-scanner via Docker...")

    cmd = [
        "docker", "run", "--rm",
        "-e", f"SONAR_HOST_URL={SONAR_HOST_URL}",
        "-e", f"SONAR_TOKEN={SONAR_TOKEN}",
        "-v", f"{SOURCE_DIR}:/usr/src",
        "sonarsource/sonar-scanner-cli"
    ]

    subprocess.run(cmd, check=True)
    print("[✅] Docker sonar-scanner completed.")

# STEP 3: Fetch SonarQube issues as JSON
# def fetch_sonar_issues():
#     print("[🌐] Fetching issues from SonarQube...")
#     url = f"{SONAR_HOST_URL}/api/issues/search"
#     params = {"componentKeys": SONAR_PROJECT_KEY, "ps": 500}
#     r = requests.get(url, auth=(SONAR_TOKEN, ""), params=params)
#     issues = r.json()
#     with open("sonarqube_issues.json", "w") as f:
#         json.dump(issues, f, indent=2)
#     print("[✅] Issues saved to sonarqube_issues.json")
#     return issues
def fetch_issues(project_key, sonar_host_url):
    """
    Fetch all unresolved issues from SonarQube for the given project
    
    Args:
        project_key (str): SonarQube project key
        sonar_host (str): SonarQube host URL
        
    Returns:
        list: List of issue dictionaries containing file, line, message, and rule
    """
    # Get SonarQube token from environment
    # sonar_token = os.getenv("SONAR_TOKEN")
    # sonar_host = os.getenv("SONAR_HOST")
    # sonar_token = os.getenv("SONAR_TOKEN")
    if not SONAR_TOKEN:
        raise ValueError("SONAR_TOKEN environment variable not set")
    
    print(f"🔍 Fetching issues for project: {project_key}")
    
    # Setup authentication
    auth = HTTPBasicAuth(SONAR_TOKEN, "")
    
    try:
        # Make API request to fetch issues
        response = requests.get(
            f"{sonar_host_url}/api/issues/search",
            params={"componentKeys": project_key, "resolved": "false"},
            auth=auth
        )
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        issues = data.get("issues", [])
        
        # Process and format issues
        parsed_issues = []
        for issue in issues:
            parsed_issues.append({
                "file": issue["component"].split(":")[-1],
                "line": issue.get("line", 1),
                "message": issue["message"],
                "rule": issue["rule"]
            })
        
        with open("parsed_sonar_issues.json", "w") as f:
            json.dump(parsed_issues, f, indent=2)

        print(f"✅ Successfully fetched {len(parsed_issues)} issues")
        return parsed_issues
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching issues: {str(e)}")
        raise

# STEP 4: Auto-paste to Amazon Q in VS Code
def paste_to_amazon_q(issues):
    print("[🤖] Automating paste into Amazon Q...")
    pyperclip.copy(json.dumps(issues, indent=2))  # Copy to clipboard
    time.sleep(5)  # Give user time to focus VS Code

    # Shortcut to open Q panel (usually Cmd+I or Ctrl+I, but confirm manually)
    pyautogui.hotkey("ctrl", "i")  # Windows/Linux; change to "command" if Mac
    time.sleep(2)

    # Paste JSON and send
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")
    print("[✅] JSON sent to Amazon Q.")

    # Send trust confirmation text (if required)
    time.sleep(2)
    pyautogui.write("yes", interval=0.1)
    pyautogui.press("enter")


# ORCHESTRATOR
if __name__ == "__main__":
    create_sonar_properties(SOURCE_DIR)
    run_sonar_scanner_docker()
    # issues = fetch_sonar_issues()
    issues = fetch_issues(SONAR_PROJECT_KEY, SONAR_HOST)
    print("[✅] Issues fetched.")
    # paste_to_amazon_q(issues)