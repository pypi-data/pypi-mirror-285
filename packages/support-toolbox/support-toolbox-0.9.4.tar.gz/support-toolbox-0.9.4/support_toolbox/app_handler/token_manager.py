import os
import configparser

TOOLS = {
    "delete_users": ["DWSUPPORT_API_TOKEN", "JIRA_API_TOKEN", "JIRA_USERNAME"],
    "deploy_ctk_service_account": ["CIRCLECI_API_TOKEN"],
    "deploy_pi": ["CIRCLECI_API_TOKEN"],
    "deploy_integrations": ["MT_API_TOKEN"]
    # Add more tools and token names as needed here
}


def check_tokens(selected_tool):
    user_home = os.path.expanduser("~")
    config_file_path = os.path.join(user_home, ".tokens.ini")

    config = configparser.ConfigParser()

    if os.path.exists(config_file_path):
        config.read(config_file_path)

    if selected_tool not in config:
        config[selected_tool] = {}

    for token_name in TOOLS.get(selected_tool, []):
        if token_name not in config[selected_tool]:
            token_value = input(f"Enter your {token_name}: ")
            config[selected_tool][token_name] = token_value

    with open(config_file_path, "w") as configfile:
        config.write(configfile)
