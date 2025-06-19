import torch
import os
import requests
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Prompt template for code fixing
PROMPT_TEMPLATE_PYTHON = """
You are an expert software engineer specializing in code quality and bug fixing.

Your task is to fix a specific code issue identified by SonarQube analysis.

**Issue Details:**
- File: {file}
- Line: {line}
- Issue: {message}
- Rule: {rule}

**Rule Description:**
{rule_details}

**Original Code Context:**
{original_code}

**Critical Instructions:**
1. Analyze the issue and understand exactly what needs to be fixed
2. Replace ONLY the faulty line(s) - do NOT add, remove or modify other lines
3. Preserve ALL original code structure, indentation, and surrounding context
4. For duplicate lines, remove ALL duplicates and keep only one instance
5. For SSL verification issues, either add proper verification or explicitly disable it with a comment explaining why
6. Ensure the fixed code maintains EXACTLY the same functionality
7. Do NOT include line numbers, comments, or explanations in the fix
8. Do NOT change the overall code structure or add/remove functions
9. Match indentation precisely - count the spaces/tabs in the original line
10. If the issue is a duplicate request, ensure only one request remains

**Common Issues to Fix:**
- Duplicate API calls: Keep only one
- Missing SSL verification: Either add certifi verification or disable with reason
- Unused variables: Remove them completely
- Code structure: Maintain exact original structure
- Indentation: Must match original exactly

**Your Response Must:**
Contain ONLY the fixed line(s) that replace the faulty one(s), with:
- EXACT same indentation
- NO extra lines
- NO comments or explanations
- NO changes to surrounding code

**Example Fix:**
Original:
    response1 = requests.post(url, headers=headers, json=data, verify=False)
    response = requests.post(url, headers=headers, json=data, verify=False)

Fixed:
    response = requests.post(url, headers=headers, json=data, verify=certifi.where())

**Fixed Code:**
"""

PROMPT_TEMPLATE_JAVA = """
You are an expert Java engineer fixing SonarQube issues. Follow these instructions precisely:

**File:** {file}
**Line:** {line}
**Rule:** {rule} ({message})

**Rule Description:**
{rule_details}

**Original Code:**
{original_code}

**Critical Requirements:**
1. Modify ONLY the specific line(s) with issues
2. Preserve EXACT original indentation
3. Maintain ALL existing functionality
4. Output MUST be compilable Java code
5. Follow Oracle Java Code Conventions

**Specific Fix Directives:**
• For S101 (Class Naming): Use PascalCase
• For S106 (Logging): Replace System.out with SLF4J/Log4J
• For S1481/S1854 (Unused Variables): Remove completely
• For Null Safety: Add null checks where needed
• For Resources: Use try-with-resources
• For Comparisons: Always use equals() for objects

**Response Format Requirements:**
▼▼▼ ONLY PROVIDE THE FIXED CODE LINE(S) ▼▼▼
- No explanations
- No comments
- No markdown
- Just the corrected Java code with original indentation

**Example Fixes:**
1. Class Naming (S101):
Original: 
  public class badClassName {{
Fixed:
  public class GoodClassName {{

2. Logging (S106):
Original:
  System.out.println("Error");
Fixed:
  logger.error("Error");

3. Unused Variable (S1481):
Original:
  int unused = 5;
Fixed:
  
**Fixed Code:**
"""

def generate_fix(issue, rule_details):
    """
    Generate a fix for the given issue using LLM
    
    Args:
        issue (dict): Issue details containing file, line, message, rule
        rule_details (str): Detailed description of the SonarQube rule
        
    Returns:
        str: The corrected code line(s)
    """
    print(f"🤖 Generating AI fix for {issue['file']} line {issue['line']}")
    
    try:
        file_ext = issue['file'].split('.')[-1].lower()
        if file_ext == "py":
            prompt_template = PROMPT_TEMPLATE_PYTHON
        elif file_ext == "java":
            prompt_template = PROMPT_TEMPLATE_JAVA
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Read the file to get context
        with open(issue['file'], 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get context around the problematic line (3 lines before and after)
        start_line = max(0, issue['line'] - 4)
        end_line = min(len(lines), issue['line'] + 3)
        context_lines = lines[start_line:end_line]
        
        # Add line numbers for better context
        numbered_context = []
        for i, line in enumerate(context_lines):
            line_num = start_line + i + 1
            marker = " >>> " if line_num == issue['line'] else "     "
            numbered_context.append(f"{line_num:3d}{marker}{line.rstrip()}")
        
        original_code = "\n".join(numbered_context)
        
        # Create the prompt
        prompt = prompt_template.format(
            file=issue['file'],
            line=issue['line'],
            message=issue['message'],
            rule=issue['rule'],
            rule_details=rule_details,
            original_code=original_code
        )
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gemma-7b-it",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert code fixer. Provide only the corrected code without explanations."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent fixes
            "max_tokens": 512
        }
        print("📨 Prompt being sent to LLM:")
        retries=3
        delay=3
        # Make API request
        for attempt in range(retries):
            print("🔄 Calling Groq API...")
            try:
                response = requests.post(GROQ_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                fixed_code = result["choices"][0]["message"]["content"].strip()

                # Remove code block formatting
                if fixed_code.startswith("```"):
                    lines = fixed_code.split("\n")
                    lines = lines[1:] if len(lines) > 1 else lines
                    if lines and lines[-1].strip().startswith("```"):
                        lines = lines[:-1]
                    fixed_code = "\n".join(lines).strip()

                if not fixed_code:
                    print("⚠️ Model returned empty fix. Interpreting as a line deletion.")
                    return "__DELETE_LINE__"

                print("✅ Successfully generated fix")
                return fixed_code
            
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait_time = delay * (attempt + 2)
                    print(f"⚠️ Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                print(f"❌ Error generating fix: {str(e)}")
                raise

        print("❌ All retries failed due to rate limits.")
        return None
    
    except FileNotFoundError:
        print(f"❌ File not found: {issue['file']}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Error generating fix: {str(e)}")
        raise

# # --- File Editor for Applying Fixes ---
# import os
# import shutil
# from datetime import datetime

# def apply_fix(filepath, line_number, fixed_code):
#     """
#     Replace the faulty line in the file with the fixed code.

#     Args:
#         filepath (str): Path to the file to be fixed.
#         line_number (int): Line number to replace (1-based).
#         fixed_code (str): The corrected line(s) to replace the original line.
#     """
#     print(f"✏️ Applying fix to {filepath} at line {line_number}")

#     try:
#         # Create backup before modifying
#         backup_path = create_backup(filepath)
#         print(f"📋 Created backup: {backup_path}")

#         # Read the file
#         with open(filepath, 'r', encoding='utf-8') as f:
#             lines = f.readlines()

#         # Validate line number
#         if line_number < 1 or line_number > len(lines):
#             raise ValueError(f"Invalid line number {line_number}. File has {len(lines)} lines.")

#         # Store original line for logging
#         original_line = lines[line_number - 1].rstrip()

#         # Handle multi-line fixes
#         if '\n' in fixed_code:
#             # Multi-line fix
#             fixed_lines = fixed_code.split('\n')
#             # Ensure each line ends with newline except the last one
#             fixed_lines = [line + '\n' for line in fixed_lines[:-1]] + [fixed_lines[-1] + '\n']

#             # Replace the single line with multiple lines
#             lines[line_number - 1:line_number] = fixed_lines
#         else:
#             # Single line fix
#             # Preserve original indentation if the fix doesn't include it
#             original_indent = get_indentation(lines[line_number - 1])
#             if not fixed_code.startswith(' ') and not fixed_code.startswith('\t'):
#                 fixed_code = original_indent + fixed_code.lstrip()

#             # Ensure the line ends with newline
#             if not fixed_code.endswith('\n'):
#                 fixed_code += '\n'

#             # Replace the line
#             lines[line_number - 1] = fixed_code

#         # Write the modified content back to file
#         with open(filepath, 'w', encoding='utf-8') as f:
#             f.writelines(lines)

#         print(f"✅ Successfully applied fix")
#         print(f"   Original: {original_line}")
#         print(f"   Fixed:    {fixed_code.strip()}")

#         if os.path.exists(backup_path):
#             os.remove(backup_path)
#             print(f"🗑️ Deleted backup: {backup_path}")

#     except Exception as e:
#         print(f"❌ Error applying fix: {str(e)}")
#         # Restore from backup if it exists
#         if 'backup_path' in locals() and os.path.exists(backup_path):
#             shutil.copy2(backup_path, filepath)
#             print(f"🔄 Restored from backup")
#         raise

# def create_backup(filepath):
#     """
#     Create a backup of the file before modifying it

#     Args:
#         filepath (str): Path to the file to backup

#     Returns:
#         str: Path to the backup file
#     """
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     backup_path = f"{filepath}.backup_{timestamp}"
#     shutil.copy2(filepath, backup_path)
#     return backup_path

# def get_indentation(line):
#     """
#     Get the indentation (whitespace) from the beginning of a line

#     Args:
#         line (str): The line to analyze

#     Returns:
#         str: The indentation string (spaces/tabs)
#     """
#     return line[:len(line) - len(line.lstrip())]

# def validate_file_syntax(filepath):
#     """
#     Basic syntax validation for Python files

#     Args:
#         filepath (str): Path to the Python file

#     Returns:
#         bool: True if syntax is valid, False otherwise
#     """
#     if not filepath.endswith('.py'):
#         return True  # Skip validation for non-Python files

#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             content = f.read()

#         # Try to compile the code
#         compile(content, filepath, 'exec')
#         return True
#     except SyntaxError as e:
#         print(f"⚠️ Syntax error in {filepath}: {e}")
#         return False
#     except Exception as e:
#         print(f"⚠️ Error validating {filepath}: {e}")
#         return False

# def cleanup_backups(directory, keep_count=5):
#     """
#     Clean up old backup files, keeping only the most recent ones

#     Args:
#         directory (str): Directory to clean up
#         keep_count (int): Number of backup files to keep per original file
#     """
#     try:
#         backup_files = {}

#         # Group backup files by original file
#         for filename in os.listdir(directory):
#             if '.backup_' in filename:
#                 original_file = filename.split('.backup_')[0]
#                 if original_file not in backup_files:
#                     backup_files[original_file] = []
#                 backup_files[original_file].append(filename)

#         # Clean up old backups for each file
#         for original_file, backups in backup_files.items():
#             if len(backups) > keep_count:
#                 # Sort by modification time (newest first)
#                 backups.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

#                 # Remove old backups
#                 for backup in backups[keep_count:]:
#                     backup_path = os.path.join(directory, backup)
#                     os.remove(backup_path)
#                     print(f"🗑️ Removed old backup: {backup}")

#     except Exception as e:
#         print(f"⚠️ Error cleaning up backups: {e}")