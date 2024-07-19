import requests
import json


def create_saved_query(admin_token, q, org_id, project_id):
    create_saved_query_url = f"https://api.data.world/v0/projects/{org_id}/{project_id}/queries"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    body = json.dumps(q)

    # Create the query
    response = requests.post(create_saved_query_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
    else:
        print(response.text)


def create_project(admin_token, org_id, project_title, visibility, summary):
    create_project_url = f"https://api.data.world/v0/projects/{org_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    payload = {
        "title": project_title,
        "summary": summary,
        "visibility": visibility
    }

    body = json.dumps(payload)

    # Create the project
    response = requests.post(create_project_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"created project: {project_title}")
    else:
        print(response.text)
