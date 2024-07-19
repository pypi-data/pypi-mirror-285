import requests
import json


def create_site(admin_token, entity_id, public_slug, sso_url, x509_cert, api_url):
    url = f"{api_url}/admin/sites/create"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    data = {
        'entityid': entity_id,
        'publicSlug': public_slug,
        'ssoUrl': sso_url,
        'x509Certificate': x509_cert
    }

    body = json.dumps(data)
    response = requests.post(url, body, headers=header)

    if response.status_code == 200:
        print(f"Successfully created the site: {response.text}")
    else:
        print(response.text)


def edit_saml(admin_token, entity_id, site_id, default_org_list, sso_url, x509_cert, api_url):
    resource_id = f"site%3A{site_id}"
    url = f"{api_url}/admin/saml/{resource_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    # Prepare the data to be sent in the request
    data = {
      "agentid": site_id,
      "defaultOrgList": default_org_list,
      "entityid": entity_id,
      "ssoUrl": sso_url,
      "x509Certificate": x509_cert
    }

    body = json.dumps(data)
    response = requests.put(url, body, headers=header)

    if response.status_code == 200:
        print(f"Successfully updated SAML!")
        print(f"Entity ID: {entity_id}")
        print(f"SSO Url: {sso_url}")
        print(f"x509 Certificate: {x509_cert}")
    else:
        print(response.text)


def get_site_id(admin_token, public_slug, api_url):
    url = f"{api_url}/site/slug/{public_slug}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        response_json = response.json()
        site_id = response_json['site']
        print(f"Found site_id: {site_id} for {public_slug}")

        return site_id, True
    else:
        print(response.text)
        return None, False
