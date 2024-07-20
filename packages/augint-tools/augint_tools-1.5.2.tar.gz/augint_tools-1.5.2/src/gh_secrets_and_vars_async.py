import asyncio
import os
from pathlib import Path

import github.GithubException
from dotenv import load_dotenv
from github import Github, Auth

import click
from github.Repository import Repository

from src.util import logger

from rich import print


@click.command()
@click.option('--verbose', "-v", is_flag=True, help="Print verbose output.")
@click.argument("filename", type=click.Path(exists=True, readable=True), default=".env")
def cli(verbose: bool, filename: click.Path):
    results = asyncio.run(perform_update(filename))
    if verbose:
        print(results)
    total_secrets = len(results["SECRETS"])
    total_vars = len(results["VARIABLES"])
    print(f"Updated {total_secrets} secrets and {total_vars} variables.")


async def perform_update(filename: click.Path):
    if not filename:
        raise ValueError("No filename specified. Exiting to avoid an accident.")

    load_dotenv(str(filename))
    github_repo = os.environ.get("GH_REPO", None)
    github_account = os.environ.get("GH_ACCOUNT", None)

    file_path = Path(filename.__str__())
    # Read the .env file and convert it to a JSON object
    secrets = {}
    not_secrets = {}
    SECRETS_INDICATORS = ['secret', 'key', 'token', 'bearer',
                          'password', 'pass', 'pwd', 'pword', 'hash']

    with file_path.open("r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";") or "=" not in line:
                continue
            key, value = line.strip().split("=", 1)

            match key:
                case key if key.startswith("AWS_PROFILE"):
                    continue
                case key if any(indicator in key.casefold() for indicator in SECRETS_INDICATORS):
                    secrets[key] = value
                case _:
                    not_secrets[key] = value

    try:
        repo = get_github_repo(github_account, github_repo)
    except github.GithubException.UnknownObjectException as e:
        logger.critical("You must add GH_REPO to your env file.")
        exit(1)

    secret_update_result = await create_or_update_github_secrets(
        repo=repo, env_data=secrets
    )
    not_secret_update_result = await create_or_update_github_variables(
        repo=repo, env_data=not_secrets
    )

    results = {
        "SECRETS": secret_update_result,
        "VARIABLES": not_secret_update_result
    }

    return results

def get_github_repo(github_account, github_repo_name) -> Repository:
    auth = Auth.Token(os.environ.get("GH_TOKEN", None))
    g = Github(auth=auth)
    try:
        repo = g.get_user(github_account).get_repo(github_repo_name)
    except github.GithubException.UnknownObjectException as e:
        logger.critical(e)
        try:
            repo = g.get_organization(github_account).get_repo(github_repo_name)
        except github.GithubException.UnknownObjectException as e:
            logger.critical("You must add GH_USER to your env file.")
            raise e

    return repo


async def create_or_update_github_secrets(repo, env_data):
    secrets = await asyncio.to_thread(repo.get_secrets)
    secret_names = [secret.name for secret in secrets]

    tasks = []
    for env_var_name, env_var_value in env_data.items():
        # Create or update secrets
        if env_var_name in secret_names:
            logger.info(f"Updating secret {env_var_name}...")
            tasks.append(asyncio.to_thread(repo.create_secret, env_var_name, env_var_value))
        else:
            logger.info(f"Creating secret {env_var_name}...")
            tasks.append(asyncio.to_thread(repo.create_secret, env_var_name, env_var_value))

    for secret_name in secret_names:
        if secret_name not in env_data.keys():
            logger.info(f"Deleting secret {secret_name}...")
            tasks.append(asyncio.to_thread(repo.delete_secret, secret_name))

    results = await asyncio.gather(*tasks)
    return results

async def create_or_update_github_variables(repo, env_data):
    vars = await asyncio.to_thread(repo.get_variables)
    var_names = [var.name for var in vars]

    tasks = []
    for env_var_name, env_var_value in env_data.items():
        # Create or update secrets
        if env_var_name in var_names:
            logger.info(f"Updating variable {env_var_name}...")
            def delete_then_create_variable(repo, env_var_name, env_var_value):
                repo.delete_variable(env_var_name)
                return repo.create_variable(env_var_name, env_var_value)
            # tasks.append(asyncio.to_thread(repo.delete_variable, env_var_name))
            tasks.append(asyncio.to_thread(delete_then_create_variable, repo, env_var_name, env_var_value))
        else:
            logger.info(f"Creating variable {env_var_name}...")
            tasks.append(asyncio.to_thread(repo.create_variable, env_var_name, env_var_value))

    for var_name in var_names:
        if var_name not in env_data.keys():
            logger.info(f"Deleting variable {var_name}...")
            tasks.append(asyncio.to_thread(repo.delete_variable, var_name))

    results = await asyncio.gather(*tasks)
    return results


if __name__ == "__main__":
    cli()
