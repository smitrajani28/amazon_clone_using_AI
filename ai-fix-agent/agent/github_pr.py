import os
import subprocess

def create_pull_request():
    branch = "auto/fix-bugs"
    subprocess.run(["git", "checkout", "-b", branch])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "AI Auto Fix: Resolved SonarQube Issues"])
    subprocess.run(["git", "push", "origin", branch])
    subprocess.run(["gh", "pr", "create", "--title", "AI Bug Fix", "--body", "Automated fixes for SonarQube issues"])

if __name__ == "__main__":
    create_pull_request()
