import os

SOURCE_REPO_PATH = "D:\\amazon_clone_using_AI"

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
print("📄 Total Files to include:", len(INCLUDE_FILES))
print("📁 Total Directories to include:", len(INCLUDE_DIRS))