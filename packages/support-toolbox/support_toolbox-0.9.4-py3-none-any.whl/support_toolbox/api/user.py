import json
import requests


def get_agent_id(api_url, admin_token):
    get_user_url = f"{api_url}/user"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    response = requests.get(get_user_url, headers=header)

    # Verify the get
    if response.status_code == 200:
        response_json = response.json()
        agent_id = response_json['agentid']
        return agent_id
    else:
        print(response.text)


def create_user(api_url, admin_token, agent_id, display_name, email):
    create_user_url = f"{api_url}/admin/users"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }


    data = {
      "agentid": agent_id,
      "displayName": display_name,
      "email": email,
      "visibility": "OPEN"
    }

    body = json.dumps(data)

    response = requests.post(create_user_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"Successfully created: {agent_id}")
    else:
        print(response.text)


def update_user_roles(api_url, admin_token, agent_id, allowed_roles):
    update_user_roles_url = f"{api_url}/admin/{agent_id}/auth"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }


    data = {
        "allowedRoles": allowed_roles
    }

    body = json.dumps(data)

    response = requests.put(update_user_roles_url, body, headers=header)

    # Verify the update
    if response.status_code == 200:
        print(f"Successfully updated: {agent_id} with: {allowed_roles}")
    else:
        print(response.text)
