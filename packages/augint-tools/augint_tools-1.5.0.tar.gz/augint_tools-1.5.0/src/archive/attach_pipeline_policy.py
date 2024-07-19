import json
import os
from pathlib import Path

import click
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

APP_NAME = os.getenv('APP_NAME', "ob-desert-road")


def get_policy_arn(policy_name, iam, verbose=False, dry_run=False):
    try:
        response = iam.list_policies(Scope='Local')
        policies = response.get('Policies', [])
        for policy in policies:
            if policy['PolicyName'] == policy_name:
                return policy['Arn']
        return None
    except ClientError as e:
        print(f"Error getting policy ARN: {e}")
        return None


def create_or_update_policy(policy_name, policy_document, iam, verbose=False, dry_run=False):
    policy_arn = get_policy_arn(policy_name, iam)
    if policy_arn:
        print(f"Updating policy: {policy_name}")
        if not dry_run:
            iam.create_policy_version(
                PolicyArn=policy_arn,
                PolicyDocument=json.dumps(policy_document),
                SetAsDefault=True
            )
    else:
        print(f"Creating policy: {policy_name}")
        if not dry_run:
            iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )


def attach_policy(role_arn, policy_name, iam, verbose=False, dry_run=False):
    policy_arn = get_policy_arn(policy_name, iam)
    if not policy_arn:
        print(f"Policy {policy_name} does not exist.")
        return

    try:
        if not dry_run:
            iam.attach_role_policy(
                RoleName=role_arn.split('/')[-1],
                PolicyArn=policy_arn
            )
        print(f"Policy {policy_name} attached to role {role_arn}")
    except ClientError as e:
        print(f"Error attaching policy: {e}")


@click.command()
@click.option("--dev", '-D', help="Use dev env vars", is_flag=True)
@click.option("--prod", '-P', help="Use prod env vars", is_flag=True)
@click.option('--env-file', '-e', help="Path to .env file", type=click.Path(exists=True))

@click.option("--verbose", '-v', help="Verbose output", is_flag=True)
@click.option("--dry-run", '-d', help="Dry run", is_flag=True)
@click.option("--role", '-r', help="Pipeline ole to augment with the new policy",
              type=click.STRING)
@click.option("--stack", '-s', help="Permissions for the development or production stack", type=click.STRING)
@click.option("--aws-profile", '-a', help="AWS profile name to use", type=click.STRING)
@click.option("--policy-name-prefix", '-p', help="Permissions for the development or production stack",
              type=click.STRING, default=APP_NAME)
def main(verbose: bool, dry_run: bool, role: str, stack: str, aws_profile: str, filename: click.Path):
    """Attach or update a policy for a given IAM role."""

    runs = []
    if not env_file:
        load_dotenv('.env')
    else:
        load_dotenv(env_file)

    if stack and role and policy_name_prefix:
        policy_name = f"{policy_name_prefix}-pipeline-policy{stack}"
        runs.append((stack, role, policy_name))
    if dev:
        stack = os.environ['DEV_INFRA_STACK_NAME']
        role = os.environ['TESTING_PIPELINE_EXECUTION_ROLE']
        policy_name = f"{APP_NAME}-pipeline-policy{stack}"
        runs.append((stack, role, policy_name))
    if prod:
        stack = os.environ['PROD_INFRA_STACK_NAME']
        role = os.environ['PROD_PIPELINE_EXECUTION_ROLE']
        policy_name = f"{APP_NAME}-pipeline-policy{stack}"
        runs.append((stack, role, policy_name))

    if aws_profile:
        os.environ['AWS_PROFILE'] = aws_profile

    # Policy document - define your permissions here
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }

    iam = boto3.client('iam')
    for stack, role, policy_name in runs:
        print(f"Stack: {stack}")
        print(f"Role: {role}")
        print(f"Policy name: {policy_name}")

        create_or_update_policy(policy_name, policy_document, iam, verbose, dry_run)
        attach_policy(role, policy_name, iam, verbose, dry_run)


if __name__ == '__main__':
    main()
