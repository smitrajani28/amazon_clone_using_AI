# --- LLM Code Fixer ---
import os
import requests
import time

# LLM Configuration
# GROQ_API_KEY = "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"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Prompt template for code fixing
PROMPT_TEMPLATE_PYTHON = """
You are an expert Python engineer specializing in code quality and bug fixing.

Your task is to fix a specific code issue identified by SonarQube static analysis.

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
1. Fix ONLY the single faulty line — do NOT modify or return additional lines.
2. Do NOT add comments, explanations, or blank lines.
3. Keep the original indentation exactly.
4. If the line must be removed, return an empty line (`""`) — not a placeholder or comment.
5. For SSL issues, use `verify=certifi.where()` instead of disabling verification.
6. If removing unused variables, delete the line completely.
7. If replacing unsafe f-strings, use `.format()` or `f"..."` safely.
8. Maintain exact same functionality unless the rule explicitly requests change.

**Response Requirements:**
- Return only the **fixed version of the original line**.
- Do NOT return any surrounding lines.
- Do NOT include markdown (like ```python).
- Return a completely empty line if the fix is deletion.

**Examples:**

1. 🔒 SSL fix:
Original:
    response = requests.post(url, headers=headers, json=data, verify=False)
Fixed:
    response = requests.post(url, headers=headers, json=data, verify=certifi.where())

2. 🗑️ Unused variable:
Original:
    temp_response = requests.get(endpoint)
Fixed:
    
3. ⚙️ f-string correction:
Original:
    print(f"Value: {{}}")
Fixed:
    print("Value: {{}}".format(value))

**Fixed Code:**
"""

PROMPT_TEMPLATE_JAVA = """
You are an expert Java engineer fixing SonarQube-detected issues with precise, production-safe code changes.

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
1. Only return the corrected version of the specific faulty line.
2. Do NOT include extra lines, comments, or unrelated fixes.
3. Do NOT return multiple lines — only one.
4. If the line must be removed (e.g., unused variable), return a completely blank line.
5. Preserve the original indentation and syntax.
6. For logging (S106), replace `System.out.println()` with `logger.info()` or `logger.error()` as appropriate.
7. For class naming (S101), use PascalCase.
8. For object comparison (S4973), use `.equals()` and ensure null safety using `Objects.equals(a, b)` where needed.
9. Do NOT add new variables, duplicate code, or explanations.

**Response Format Requirements:**
- Return only the **fixed version of the original line**.
- If nothing should remain, return a blank line (not a marker like __DELETE_LINE__).
- Do NOT return more than one line.
- Do NOT modify lines above or below.

**Examples:**

1. 🚫 Hardcoded output:
Original:
    System.out.println("Error occurred");
Fixed:
    logger.error("Error occurred");

2. 🧼 Unused variable:
Original:
    int temp = 42;
Fixed:

3. 🧠 Class naming:
Original:
    public class my_class {{
Fixed:
    public class MyClass {{

4. ✅ Null-safe equals:
Original:
    if (a == b)
Fixed:
    if (Objects.equals(a, b))

**Fixed Code:**
"""

PROMPT_TEMPLATE_HTML_CSS = """
You are an expert front-end engineer with deep knowledge in HTML5, CSS3, and web accessibility standards.

Your task is to fix a specific code issue identified by SonarQube static analysis.

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
1. Fix ONLY the faulty line — do NOT modify or return additional lines.
2. Preserve exact indentation, formatting, and nesting.
3. Do NOT return comments, blank lines, explanations, or multiple lines.
4. If the line should be deleted, return a completely empty string (`""`).

**Fix Guidelines (Apply When Relevant):**
- ✅ Add missing `alt` text on `<img>` tags.
- ✅ Replace deprecated tags like `<center>`, `<font>`, `<b>`, `<i>` with semantic or modern equivalents (`<strong>`, `<em>`, CSS classes).
- ✅ Use semantic HTML: prefer `<section>`, `<nav>`, `<article>`, `<header>`, `<footer>` over generic `<div>`/`<span>` for structure.
- ✅ Ensure all form inputs have associated `<label>`.
- ✅ Avoid inline CSS (`style="..."`), move styles to classes.
- ✅ Use CSS shorthand where possible (`margin: 10px 5px;` instead of individual properties).
- ✅ Remove unused or duplicate CSS rules.
- ✅ Avoid `!important` unless absolutely necessary.
- ✅ Ensure color contrast meets WCAG 2.1 accessibility standards.
- ✅ Avoid hard-coded widths/heights that break responsiveness.

**Response Requirements:**
- Return only the **fixed version of the original line**.
- Do NOT include surrounding context.
- Do NOT return markdown formatting (e.g., no ```html).
- Return an empty line if the fix is deletion.

**Examples:**

1. 🖼️ Image accessibility fix:
Original:
    <img src="banner.jpg">
Fixed:
    <img src="banner.jpg" alt="Promotional Banner">

2. 🧼 Remove deprecated tag:
Original:
    <center>Welcome</center>
Fixed:
    <div class="text-center">Welcome</div>

3. 🎨 Remove inline style:
Original:
    <h1 style="color: blue;">Welcome</h1>
Fixed:
    <h1 class="title">Welcome</h1>

4. 🗑️ Remove unused CSS:
Original:
    .temp-style { padding: 10px; }
Fixed:
    

**Fixed Code:**
"""
PROMPT_TEMPLATE_JS_GENERAL = """
You are an expert JavaScript/TypeScript engineer specializing in modern coding practices and bug fixing.

Your task is to fix a specific code issue identified by SonarQube static analysis.

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
1. Fix ONLY the single faulty line — do NOT modify other lines.
2. Do NOT include comments, explanations, or blank lines.
3. Preserve original indentation and formatting.
4. Return an empty line (`""`) if the line must be deleted.
5. Use ES6+ best practices (e.g., `let`, `const`, arrow functions).
6. Avoid global variables and side effects.
7. For unused variables/functions: remove the line completely.
8. Handle promises properly using `async/await` or `.then().catch()`.
9. Prefer strict comparison (`===` over `==`) and avoid implicit coercion.

**Response Requirements:**
- Return only the **fixed version of the original line**.
- Do NOT include markdown formatting or surrounding code.

**Examples:**

1. 🚫 Unused variable:
Original:
    var temp = calculate();
Fixed:
    

2. ✅ Prefer `const`:
Original:
    var total = 10;
Fixed:
    const total = 10;

3. 🧠 Async fix:
Original:
    fetch(url).then(data => process(data)).catch(err => console.log(err));
Fixed:
    try { const data = await fetch(url); process(data); } catch (err) { console.log(err); }

**Fixed Code:**
"""
PROMPT_TEMPLATE_GENERAL = """
You are an expert software engineer skilled in multiple programming and configuration languages.

Your task is to fix a code or configuration issue identified by SonarQube static analysis.

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
1. Fix ONLY the single faulty line — do NOT modify or return surrounding lines.
2. Maintain original indentation and formatting.
3. Do NOT add comments, explanations, or blank lines.
4. If the line must be removed, return a completely empty string (`""`).
5. Follow the correct syntax for the given file type (JSON, XML, YAML, etc.).
6. Escape characters properly if required.
7. Maintain the intended behavior, structure, and formatting unless the rule demands change.
8. Avoid breaking the schema or syntax (e.g., trailing commas in JSON, unclosed tags in XML).

**Response Requirements:**
- Return only the **fixed version of the original line**.
- Do NOT return multiple lines, markdown, or any explanation.
- Return an empty line if the fix requires deletion.

**Examples:**

1. 🧱 Fix malformed JSON:
Original:
    "timeout": 30,
Fixed:
    "timeout": 30

2. ⚙️ Remove unused property:
Original:
    enableDebug: true
Fixed:
    

3. 🧼 Fix XML tag mismatch:
Original:
    </configurations>
Fixed:
    </configuration>

4. ✅ YAML indentation fix:
Original:
    retry:   5
Fixed:
    retry: 5

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
        extension_prompt_map = {
            "py": PROMPT_TEMPLATE_PYTHON,
            "java": PROMPT_TEMPLATE_JAVA,
            "js": PROMPT_TEMPLATE_JS_GENERAL,
            "html": PROMPT_TEMPLATE_HTML_CSS,
            "htm": PROMPT_TEMPLATE_HTML_CSS,
            "css": PROMPT_TEMPLATE_HTML_CSS,
            # default fallback handled below
        }

        prompt_template = extension_prompt_map.get(file_ext, PROMPT_TEMPLATE_GENERAL)
        
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
            "model": "llama3-70b-8192",
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
        response = None
        for attempt in range(retries):
            print("🔄 Calling Groq API...")
            try:
                response = requests.post(GROQ_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                if "choices" not in result or not result["choices"]:
                    print("❌ Unexpected LLM response structure.")
                    return None
                fixed_code = result["choices"][0]["message"]["content"].strip()

                # Remove code block formatting
                if fixed_code.startswith("```"):
                    lines = fixed_code.split("\n")
                    lines = lines[1:] if len(lines) > 1 else lines
                    if lines and lines[-1].strip().startswith("```"):
                        lines = lines[:-1]
                    fixed_code = "\n".join(lines).strip()

                # if not fixed_code:
                #     print("⚠️ Model returned empty fix. Interpreting as a line deletion.")
                #     return "__DELETE_LINE__"
                if fixed_code.count('\n') > 0:
                    print("⚠️ Model returned multiple lines. Rejecting as invalid.")
                    return None
                
                if not fixed_code.strip():
                    print("✅ Empty line detected — this is a valid deletion.")
                    return ''  # Actually blank, no __DELETE_LINE__
                
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

def validate_fix(original_line, fixed_line):
    """
    Basic validation to ensure the fix is reasonable
    
    Args:
        original_line (str): Original code line
        fixed_line (str): Fixed code line
        
    Returns:
        bool: True if fix seems valid
    """
    # Basic checks
    if not fixed_line or not fixed_line.strip():
        return False
    
    # Check if it's not just a comment
    if fixed_line.strip().startswith('#'):
        return False
    
    # Check if indentation is preserved (basic check)
    original_indent = len(original_line) - len(original_line.lstrip())
    fixed_indent = len(fixed_line) - len(fixed_line.lstrip())
    
    # Allow some flexibility in indentation
    if abs(original_indent - fixed_indent) > 4:
        return False
    
    return True