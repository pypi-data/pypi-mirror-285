import json
import os
from pathlib import Path
from dotenv import load_dotenv
from github import Github, Auth

import click
from src.util import log

@click.command()
@click.option("--verbose", "-v", help="Verbose output.", is_flag=True)
@click.argument("filename", type=click.Path(exists=True, readable=True), default=".env")
def cli(verbose: bool, filename: click.Path):
    if verbose:
        log.info("Verbose output enabled.")

    results = perform_update(filename)
    log.info(results)


def perform_update(filename: click.Path):
    if not filename:
        raise ValueError("No filename specified. Exiting to avoid an accident.")

    load_dotenv(str(filename))
    github_repo = os.environ.get("GH_REPO", "ObInfra")
    github_org = os.environ.get("GH_ORG", None)
    github_user = os.environ.get("GH_USER", None)

    file_path = Path(filename.__str__())
    # Read the .env file and convert it to a JSON object
    env_data = {}
    with file_path.open("r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";") or "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            # Skip AWS Variables as they'll only confuse the pipeline
            if key.startswith("AWS_PROFILE"):
                continue
            env_data[key] = os.getenv(key)
    env_json = json.dumps(env_data)

    results = []
    result = create_or_update_github_secrets(
        github_repo=github_repo, github_org=github_org, github_user=github_user, env_data=env_data
    )
    results.append(result)

    return results


def create_or_update_github_secrets(github_org, github_repo, github_user, env_data):
    auth = Auth.Token(os.environ.get("GH_TOKEN", None))
    g = Github(auth=auth)
    if github_org:
        g_org = g.get_organization(github_org)
        repo = g_org.get_repo(github_repo)
    elif github_user:
        g_user = g.get_user(github_user)
        repo = g_user.get_repo(github_repo)
    else:
        raise ValueError("Must specify either GITHUB_ORG or GH_USER")
    secrets = [secret for secret in repo.get_secrets()]
    secret_names = [secret.name for secret in secrets]

    results = []
    for env_var_name, env_var_value in env_data.items():
        # Create or update secrets
        if env_var_name in secret_names:
            log.info(f"Updating secret {env_var_name}...")
            results.append(repo.create_secret(env_var_name, env_var_value))

        else:
            log.info(f"Creating secret {env_var_name}...")
            results.append(repo.create_secret(env_var_name, env_var_value))

    for secret_name in secret_names:
        if secret_name not in env_data.keys():
            log.info(f"Deleting secret {secret_name}...")
            results.append(repo.delete_secret(secret_name))

    return results


if __name__ == "__main__":
    cli()
