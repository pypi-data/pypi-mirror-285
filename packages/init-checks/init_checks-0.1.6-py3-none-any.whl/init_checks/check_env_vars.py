import os
import re
import yaml
import sys
import subprocess
from tabulate import tabulate

def get_git_tracked_files():
    try:
        result = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, check=True, text=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error obtaining git tracked files: {e}")
        sys.exit(1)

def check_env_vars():
    root_dir = os.getcwd()
    pattern = r'os\.getenv\(["\'](.*?)["\']\)'

    repo_env_vars = set()
    init_checks_env_vars = set()
    var_to_files = {}

    git_tracked_files = get_git_tracked_files()

    for file in git_tracked_files:
        if file.endswith(".py") and file != "INIT_CHECKS.yaml":
            with open(os.path.join(root_dir, file), 'r') as f:
                content = f.read()
                matches = re.findall(pattern, content)
                repo_env_vars.update(matches)
                for var in matches:
                    if var not in var_to_files:
                        var_to_files[var] = []
                    var_to_files[var].append(file)

    init_checks_path = os.path.join(root_dir, "INIT_CHECKS.yaml")
    if os.path.exists(init_checks_path):
        with open(init_checks_path, 'r') as file:
            init_checks = yaml.safe_load(file) or {}
            if 'env_vars' in init_checks:
                init_checks_env_vars.update(init_checks['env_vars'])

    missing_in_repo = init_checks_env_vars - repo_env_vars
    extra_in_repo = repo_env_vars - init_checks_env_vars

    if missing_in_repo or extra_in_repo:
        if missing_in_repo:
            print("Commit Failed!")
            print("Following environment variables from INIT_CHECKS are missing in the Repository:")
            missing_table = [["Variable", "Paths"]]
            for var in missing_in_repo:
                missing_table.append([var, ", ".join(var_to_files.get(var, ["Not found"]))])
            print(tabulate(missing_table, headers="firstrow", tablefmt="grid"))

        if extra_in_repo:
            print("Commit Failed!")
            print("Following environment variables need to be added to INIT_CHECKS:")
            extra_table = [["Variable", "Paths"]]
            for var in extra_in_repo:
                extra_table.append([var, ", ".join(var_to_files.get(var, ["Not found"]))])
            print(tabulate(extra_table, headers="firstrow", tablefmt="grid"))

        sys.exit(1)
    
    else:
        print("Commit Successful!")
        sys.exit(0)

if __name__ == "__main__":
    check_env_vars()
