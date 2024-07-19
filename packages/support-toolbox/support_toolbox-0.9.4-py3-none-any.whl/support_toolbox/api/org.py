import json
import requests
import re
import urllib.parse


def validate_org_input(org_name):
    # Check for anything NOT letter, digit, underscore, or space
    regex = re.compile(r'[^\w\s-]')
    return not regex.search(org_name)


def onboard_org(api_url, admin_token, org_id, org_display_name, avatar_url=''):
    onboard_org_url = f"{api_url}/organizations/onboard"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    data = {
        "agentid": org_id,
        "avatarUrl": avatar_url,
        "displayName": org_display_name,
        "orgDetails": {
            "allowMembership": True,
            "allowMembershipRequest": False,
            "allowProposals": False,
            "defaultMembershipType": 'PUBLIC'
        },
        "visibility": 'OPEN'
    }

    body = json.dumps(data)
    response = requests.post(onboard_org_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"Successfully created {org_id}")
    else:
        print(response.text)


# By default, authorizes a party or agent_id access to any org_id passed in
def authorize_access_to_org(api_url, admin_token, org_id, party):
    encoded_party = urllib.parse.quote(party, safe='')

    authorize_access_to_org_url = f"{api_url}/admin/organizations/{org_id}/authorizations/{encoded_party}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    data = {
        "level": "ADMIN",
        "visibility": "PUBLIC"
    }

    body = json.dumps(data)
    response = requests.put(authorize_access_to_org_url, body, headers=header)

    # Verify the authorization
    if response.status_code == 200:
        print(f"Authorized {party} ADMIN in {org_id}")
    else:
        print(response.text)


def deauthorize_access_to_org(api_url, admin_token, agent_id, org_id):
    deauthorize_access_to_org_url = f"{api_url}/organizations/{org_id}/authorizations/agent%3A{agent_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    response = requests.delete(deauthorize_access_to_org_url, headers=header)

    # Verify the authorization
    if response.status_code == 200:
        print(f"Removed {agent_id} from {org_id}")
    else:
        print(response.text)
