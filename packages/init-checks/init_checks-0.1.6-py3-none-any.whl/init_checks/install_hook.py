import os
import subprocess


def create_init_check_yaml():
    init_check_content = """
MONGO:
  host: "MONGO_HOST"
  port: "MONGO_PORT"
  username: "MONGO_USERNAME"
  password: "MONGO_PASSWORD"
  database: "MONGO_DB"

SNOWFLAKE:
  account: "SF_ACCOUNT"
  warehouse: "SF_WAREHOUSE"
  username: "SF_USERNAME"
  password: "SF_PASSWORD"
  database: "SF_DATABASE"

ELASTICSEARCH:
  host: "ES_HOST"
  port: "ES_PORT"
  username: "ES_USERNAME"
  password: "ES_PASSWORD"

KAFKA:
  host: "KAFKA_BOOTSTRAP_SERVERS"
  username: "KAFKA_USER"
  password: "KAFKA_PASSWORD"
  protocol: "KAFKA_PROTOCOL"
  mechanism: "KAFKA_MECHANISM"

SERVICES:
  service1: "K8s discoverable service name url"
  service2: "http://airflow-web-server:8080/health"
"""

    with open("INIT_CHECKS.yaml", 'w') as f:
        f.write(init_check_content)


def install_pre_commit_hook():
    subprocess.run(["pip", "install", "pre-commit"], check=True)

    config_content = f"""
repos:
  - repo: local
    hooks:
      - id: check-env-vars
        name: Check Environment Variables
        entry: {os.getcwd()}/venv/bin/python3 -m init_checks.check_env_vars
        language: python
        types: [python]
"""

    with open(".pre-commit-config.yaml", "w") as f:
        f.write(config_content)

    if not os.path.exists("INIT_CHECKS.yaml"):
        create_init_check_yaml()

    subprocess.run(["pre-commit", "install"], check=True)

    print("Pre-Commit hook installed successfully!")


if __name__ == "__main__":
    install_pre_commit_hook()
