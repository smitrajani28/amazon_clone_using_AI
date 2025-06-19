# --- File Editor for Applying Fixes ---
import os
import shutil
from datetime import datetime

def apply_fix(filepath, line_number, fixed_code):
    """
    Replace the faulty line in the file with the fixed code.

    Args:
        filepath (str): Path to the file to be fixed.
        line_number (int): Line number to replace (1-based).
        fixed_code (str): The corrected line(s) to replace the original line.
    """
    print(f"✏️ Applying fix to {filepath} at line {line_number}")
    
    try:
        # Create backup before modifying
        backup_path = create_backup(filepath)
        print(f"📋 Created backup: {backup_path}")
        
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Validate line number
        if line_number < 1 or line_number > len(lines):
            raise ValueError(f"Invalid line number {line_number}. File has {len(lines)} lines.")
        
        # Store original line for logging
        original_line = lines[line_number - 1].rstrip()
        
        # Handle multi-line fixes
        if '\n' in fixed_code:
            # Multi-line fix
            fixed_lines = fixed_code.split('\n')
            # Ensure each line ends with newline except the last one
            fixed_lines = [line + '\n' for line in fixed_lines[:-1]] + [fixed_lines[-1] + '\n']
            
            # Replace the single line with multiple lines
            lines[line_number - 1:line_number] = fixed_lines
        else:
            # Single line fix
            # Preserve original indentation if the fix doesn't include it
            original_indent = get_indentation(lines[line_number - 1])
            if not fixed_code.startswith(' ') and not fixed_code.startswith('\t'):
                fixed_code = original_indent + fixed_code.lstrip()
            
            # Ensure the line ends with newline
            if not fixed_code.endswith('\n'):
                fixed_code += '\n'
            
            # Replace the line
            lines[line_number - 1] = fixed_code
        # Deduplicate consecutive identical lines
        deduped_lines = []
        for i, line in enumerate(lines):
            if i == 0 or line != lines[i - 1]:
                deduped_lines.append(line)
        
        # Write the modified content back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(deduped_lines)
            
        # Write the modified content back to file
        # with open(filepath, 'w', encoding='utf-8') as f:
        #     f.writelines(lines)
        
        print(f"✅ Successfully applied fix")
        print(f"   Original: {original_line}")
        print(f"   Fixed:    {fixed_code.strip()}")

        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"🗑️ Deleted backup: {backup_path}")
            
    except Exception as e:
        print(f"❌ Error applying fix: {str(e)}")
        # Restore from backup if it exists
        if 'backup_path' in locals() and os.path.exists(backup_path):
            shutil.copy2(backup_path, filepath)
            print(f"🔄 Restored from backup")
        raise

def create_backup(filepath):
    """
    Create a backup of the file before modifying it
    
    Args:
        filepath (str): Path to the file to backup
        
    Returns:
        str: Path to the backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def get_indentation(line):
    """
    Get the indentation (whitespace) from the beginning of a line
    
    Args:
        line (str): The line to analyze
        
    Returns:
        str: The indentation string (spaces/tabs)
    """
    return line[:len(line) - len(line.lstrip())]

def validate_file_syntax(filepath):
    """
    Basic syntax validation for Python files
    
    Args:
        filepath (str): Path to the Python file
        
    Returns:
        bool: True if syntax is valid, False otherwise
    """
    if not filepath.endswith('.py','.java'):
        return True  # Skip validation for non-Python files
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the code
        compile(content, filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"⚠️ Syntax error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Error validating {filepath}: {e}")
        return False

def cleanup_backups(directory, keep_count=5):
    """
    Clean up old backup files, keeping only the most recent ones
    
    Args:
        directory (str): Directory to clean up
        keep_count (int): Number of backup files to keep per original file
    """
    try:
        backup_files = {}
        
        # Group backup files by original file
        for filename in os.listdir(directory):
            if '.backup_' in filename:
                original_file = filename.split('.backup_')[0]
                if original_file not in backup_files:
                    backup_files[original_file] = []
                backup_files[original_file].append(filename)
        
        # Clean up old backups for each file
        for original_file, backups in backup_files.items():
            if len(backups) > keep_count:
                # Sort by modification time (newest first)
                backups.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
                
                # Remove old backups
                for backup in backups[keep_count:]:
                    backup_path = os.path.join(directory, backup)
                    os.remove(backup_path)
                    print(f"🗑️ Removed old backup: {backup}")
                    
    except Exception as e:
        print(f"⚠️ Error cleaning up backups: {e}")