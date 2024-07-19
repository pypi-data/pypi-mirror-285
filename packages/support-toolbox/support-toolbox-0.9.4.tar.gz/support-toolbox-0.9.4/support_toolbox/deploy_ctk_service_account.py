from support_toolbox.api.service_account import create_service_account, SERVICE_ACCOUNTS, CIRCLECI_PROJECTS, create_env_variable
from support_toolbox.utils.api_url import select_api_url
import os
import configparser

# Get the path to the user's home directory
user_home = os.path.expanduser("~")

# Construct the full path to the configuration file
tokens_file_path = os.path.join(user_home, ".tokens.ini")

# Initialize the configparser and read the tokens configuration file
config = configparser.ConfigParser()
config.read(tokens_file_path)

# Read tokens/variables for the deploy_service_accounts tool
circleci_api_token = config['deploy_ctk_service_account']['CIRCLECI_API_TOKEN']


def deploy_ctk_service_account(api_url, api_token, site_slug, circleci_api_token):
    token = create_service_account(api_url, api_token, SERVICE_ACCOUNTS[0])

    # Configure parameters for CircleCI API
    circleci_project = CIRCLECI_PROJECTS[0]
    name = site_slug.upper() + "_API_TOKEN"
    create_env_variable(circleci_project, name, token, circleci_api_token=circleci_api_token)


def run():
    api_url = select_api_url("public")
    site_slug = input(f"Enter the site slug for this deployment (CASE SENSITIVE): ")
    api_token = input(f"Enter your {site_slug} API token: ")

    deploy_ctk_service_account(api_url, api_token, site_slug, circleci_api_token)