import os
import re
import yaml
import sys


def check_env_vars():
    root_dir = os.getcwd()
    pattern = r'os\.getenv\(["\'](.*?)["\']\)'

    repo_env_vars = set()
    init_checks_env_vars = set()

    for subdir, dir, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and file != "INIT_CHECKS.yaml":
                with open(os.path.join(subdir, file), 'r') as f:
                    content = f.read()
                    matches = re.findall(pattern, content)
                    repo_env_vars.update(matches)


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
            for var in missing_in_repo:
                print(var)

        if extra_in_repo:
            print("Commit Failed!")
            print("Following environment variables need to be added to INIT_CHECKS:")
            for var in extra_in_repo:
                print(var)

        sys.exit(1)
    
    else:
        print("Commit Successful!")
        sys.exit(0)



if __name__ == "__main__":
    check_env_vars()

