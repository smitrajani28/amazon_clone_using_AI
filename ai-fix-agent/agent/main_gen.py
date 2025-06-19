# --- AI Fix Agent Main Entry Point ---
import os
import shutil
import subprocess
from sonar_issue_parser_gen import fetch_issues, fetch_rule_details
from llm_fixer_gen import generate_fix
# from file_editor_gen_new import generate_fix
from file_editor_gen import apply_fix
import time
import json

# === CONFIGURATION ===
SOURCE_REPO_PATH = "D:\\amazon_clone_using_AI"  # Path to your original project
TARGET_REPO_URL = "https://github.com/drashtisavsani/testgit.git"
TARGET_REPO_PATH = "D:/test-repo"  # Local path where test repo will be cloned
PROJECT_KEY = "amazon-try"  # SonarQube project key
SONAR_HOST = "http://localhost:9000"

# Files name get
def get_all_files_and_dirs(base_path):
    include_files = []
    include_dirs = []

    for root, dirs, files in os.walk(base_path):
        # Skip hidden folders like .git, __pycache__, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'ai-fix-agent']

        # Add relative folder paths (excluding root itself)
        for d in dirs:
            dir_path = os.path.relpath(os.path.join(root, d), base_path)
            include_dirs.append(dir_path)

        # Add relative file paths
        for f in files:
            if not f.startswith('.'):
                file_path = os.path.relpath(os.path.join(root, f), base_path)
                include_files.append(file_path)

    return include_files, include_dirs

INCLUDE_FILES, INCLUDE_DIRS = get_all_files_and_dirs(SOURCE_REPO_PATH)
print("📄 Files to include:", INCLUDE_FILES)
print("📁 Directories to include:", INCLUDE_DIRS)

# === CLONE OR PULL TARGET REPO ===
def clone_or_pull_target_repo():
    """Clone target repo if it doesn't exist, otherwise pull latest changes"""
    if os.path.exists(TARGET_REPO_PATH):
        print("🔄 Target repo already exists. Pulling latest changes...")
        result = subprocess.run(["git", "pull"], cwd=TARGET_REPO_PATH, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error pulling repo: {result.stderr}")
            return False
        print("✅ Successfully pulled latest changes")
    else:
        print("📥 Cloning target repo...")
        result = subprocess.run(["git", "clone", TARGET_REPO_URL, TARGET_REPO_PATH], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error cloning repo: {result.stderr}")
            return False
        print("✅ Successfully cloned target repo")
    return True

# === COPY SOURCE FILES TO TARGET REPO ===
def copy_source_files():
    """Copy specified files and directories from source project to target repo"""
    print("📂 Copying source files and directories to target repo...")

    # Combine files and directories into one list of paths to copy
    all_items = INCLUDE_FILES + INCLUDE_DIRS

    for item in all_items:
        src = os.path.join(SOURCE_REPO_PATH, item)
        dst = os.path.join(TARGET_REPO_PATH, item)

        if not os.path.exists(src):
            print(f"⚠️ Source item not found: {src}")
            continue

        try:
            # If it's a directory
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"📁 Copied directory: {item}")
            # If it's a file
            elif os.path.isfile(src):
                dst_dir = os.path.dirname(dst)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy2(src, dst)
                print(f"📄 Copied file: {item}")
        except Exception as e:
            print(f"⚠️ Failed to copy {item}: {e}")

    print("✅ File and directory copying completed")

# === COMMIT AND PUSH CHANGES ===
def commit_and_push_changes():
    """Commit and push all changes to the target repo"""
    print("🚀 Committing and pushing changes to target repo...")
    
    try:
        # Ensure we're on main branch
        subprocess.run(["git", "checkout", "main"], cwd=TARGET_REPO_PATH, check=True)
        
        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=TARGET_REPO_PATH, check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], cwd=TARGET_REPO_PATH, capture_output=True, text=True)
        if not result.stdout.strip():
            print("ℹ️ No changes to commit")
            return True
        
        # Commit changes
        subprocess.run([
            "git", "commit", "-m", "AI Auto Fix: Resolved SonarQube Issues"
        ], cwd=TARGET_REPO_PATH, check=True)
        
        # Push changes
        subprocess.run(["git", "push"], cwd=TARGET_REPO_PATH, check=True)
        
        print("✅ Successfully committed and pushed changes")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during git operations: {e}")
        return False

# === MAIN FIXING PIPELINE ===
def run_fixing_pipeline():
    """Main logic to fetch issues, get fixes, and apply them"""
    print("🔍 Starting SonarQube issue fixing pipeline...")
    
    # Change to target repo directory for SonarQube analysis
    original_cwd = os.getcwd()
    os.chdir(TARGET_REPO_PATH)
    
    try:
        # Fetch issues from SonarQube
        print("📊 Fetching issues from SonarQube...")
        issues = fetch_issues(PROJECT_KEY, SONAR_HOST)
        
        if not issues:
            print("ℹ️ No issues found in SonarQube")
            return True
        
        os.makedirs("analysis_output", exist_ok=True)
        with open("analysis_output/sonarqube_issues.json", "w", encoding="utf-8") as f:
            json.dump(issues, f, indent=2)
        print("📝 Issues saved to analysis_output/sonarqube_issues.json")

        print(f"📋 Found {len(issues)} issues to fix")
        
        fixed_count = 0
        error_count = 0
        unique_rules = {}
        # Process each issue
        for i, issue in enumerate(issues, 1):
            print(f"\n🔧 Processing issue {i}/{len(issues)}")
            print(f"   File: {issue['file']}")
            print(f"   Line: {issue['line']}")
            print(f"   Rule: {issue['rule']}")
            print(f"   Message: {issue['message']}")
            
            file_path = os.path.join(TARGET_REPO_PATH, issue['file'])
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"⚠️ Skipping missing file: {file_path}")
                error_count += 1
                continue
            
            try:
                # Get rule details
                rule_key = issue['rule']
                if rule_key in unique_rules:
                    print(f"📦 Reusing cached rule details for {rule_key}")
                    rule_details = unique_rules[rule_key]
                else:
                    print("📖 Fetching rule details...")
                    rule_details = fetch_rule_details(SONAR_HOST, rule_key)
                    unique_rules[rule_key] = rule_details

                with open("analysis_output/all_rule_details.json", "w", encoding="utf-8") as f:
                    json.dump(unique_rules, f, indent=2)
                print("📝 All unique rule details saved to analysis_output/all_rule_details.json")
                # Generate fix using LLM
                print("🤖 Generating fix using AI...")
                fixed_code = generate_fix(issue, rule_details)
                
                # Apply the fix
                print("✏️ Applying fix to file...")
                apply_fix(file_path, issue['line'], fixed_code)

                print(f"✅ Successfully fixed: {issue['file']} at line {issue['line']}")
                fixed_count += 1
                # added code to fix the issue rate limit (30 req/minute) 
                time.sleep(3)
                print("⚠️ Take 3sec because of Rate limit hit.")

            except Exception as e:
                print(f"❌ Error fixing {issue['file']}: {str(e)}")
                error_count += 1
        
        print(f"\n📊 Fixing Summary:")
        print(f"   ✅ Successfully fixed: {fixed_count}")
        print(f"   ❌ Errors encountered: {error_count}")
        print(f"   📋 Total issues: {len(issues)}")
        
        return fixed_count > 0
        
    except Exception as e:
        print(f"❌ Error in fixing pipeline: {str(e)}")
        return False
    finally:
        # Return to original directory
        os.chdir(original_cwd)

# === MAIN ENTRY POINT ===
def main():
    """Main function that orchestrates the entire process"""
    print("🚀 Starting AI Fix Agent...")
    print("=" * 50)
    
    try:
        # Step 1: Clone or pull target repo
        if not clone_or_pull_target_repo():
            print("❌ Failed to setup target repository")
            return False
        
        # Step 2: Copy source files to target repo
        copy_source_files()
        
        # Step 3: Run the fixing pipeline
        fixes_applied = run_fixing_pipeline()
        
        # Step 4: Commit and push changes (only if fixes were applied)
        if fixes_applied:
            if commit_and_push_changes():
                print("\n🎉 AI Fix Agent completed successfully!")
                print("✅ All SonarQube issues have been processed and pushed to target repo")
            else:
                print("\n⚠️ Fixes were applied but failed to push changes")
        else:
            print("\n ℹ️ No fixes were applied, skipping commit and push")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error in main process: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)