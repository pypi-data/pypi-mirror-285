import requests
import json


def create_dataset(admin_token, org_id, dataset_id, visibility, summary=''):
    create_dataset_url = f"https://api.data.world/v0/datasets/{org_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    payload = {
        "title": dataset_id,
        "summary": summary,
        "visibility": visibility
    }

    body = json.dumps(payload)

    # Create the dataset
    response = requests.post(create_dataset_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"created dataset: {dataset_id}")
    else:
        print(response.text)


def set_dataset_ingest(api_url, admin_token, org_id, dataset_id):
    set_ingest_limit_url = f"{api_url}/admin/datasets/{org_id}/{dataset_id}/ingest"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    payload = {
        "agentid": org_id,
        "datasetid": dataset_id,
        # 50GB as requested by Bernie for PMs to upload implementation recordings
        "ingestQuota": 53690000000
    }

    body = json.dumps(payload)

    response = requests.put(set_ingest_limit_url, body, headers=header)

    if response.status_code == 200:
        print(f"Set 50GB ingest limit for: {org_id}/{dataset_id}")
    else:
        print(response.text)
