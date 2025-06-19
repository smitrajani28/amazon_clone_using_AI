# --- SonarQube Issue Parser ---
import os
import requests
from requests.auth import HTTPBasicAuth

def fetch_issues(project_key, sonar_host):
    """
    Fetch all unresolved issues from SonarQube for the given project
    
    Args:
        project_key (str): SonarQube project key
        sonar_host (str): SonarQube host URL
        
    Returns:
        list: List of issue dictionaries containing file, line, message, and rule
    """
    # Get SonarQube token from environment
    sonar_token = os.getenv("SONAR_TOKEN")
    sonar_host = os.getenv("SONAR_HOST")
    # sonar_token = os.getenv("SONAR_TOKEN")
    if not sonar_token:
        raise ValueError("SONAR_TOKEN environment variable not set")
    
    print(f"🔍 Fetching issues for project: {project_key}")
    
    # Setup authentication
    auth = HTTPBasicAuth(sonar_token, "")
    
    try:
        # Make API request to fetch issues
        response = requests.get(
            f"{sonar_host}/api/issues/search",
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
        
        print(f"✅ Successfully fetched {len(parsed_issues)} issues")
        return parsed_issues
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching issues: {str(e)}")
        raise

def fetch_rule_details(sonar_host, rule_key):
    """
    Fetch detailed information about a specific SonarQube rule
    
    Args:
        sonar_host (str): SonarQube host URL
        rule_key (str): The rule key/id
        
    Returns:
        str: HTML description of the rule
    """
    # Get SonarQube token from environment
    sonar_token = os.getenv("SONAR_TOKEN")
    sonar_host = os.getenv("SONAR_HOST")
    if not sonar_token:
        raise ValueError("SONAR_TOKEN environment variable not set")
    
    print(f"📖 Fetching details for rule: {rule_key}")
    
    # Setup authentication
    auth = HTTPBasicAuth(sonar_token, "")
    
    try:
        # Make API request to fetch rule details
        response = requests.get(
            f"{sonar_host}/api/rules/show",
            params={"key": rule_key},
            auth=auth
        )
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        rule_data = data.get("rule", {})
        
        # Try to get HTML description first
        html_desc = rule_data.get("htmlDesc")
        if html_desc:
            print("✅ Found HTML description")
            return html_desc
        
        # If no HTML description, try to build from description sections
        if "descriptionSections" in rule_data:
            sections = rule_data["descriptionSections"]
            html_desc = "\n\n".join(
                f"### {section.get('key', '').replace('_', ' ').title()}\n{section.get('content', '')}"
                for section in sections
                if section.get("content")
            )
            if html_desc:
                print("✅ Generated description from sections")
                return html_desc
        
        # If still no description, return whatever we can find
        print("⚠️ No detailed description found, using basic description")
        return rule_data.get("name", "") + "\n" + rule_data.get("description", "")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching rule details: {str(e)}")
        raise