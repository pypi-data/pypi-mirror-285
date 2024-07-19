import os
import requests


def upload_file(api_token, org, dataset_id, file_path):
    upload_file_url = f"https://api.data.world/v0/uploads/{org}/{dataset_id}/files"

    header = {
        'Authorization': f'Bearer {api_token}'
    }

    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'))}
    response = requests.post(upload_file_url, headers=header, files=files)

    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        print("File uploaded successfully.")
    else:
        print(response.text)
        print("File upload failed.")
