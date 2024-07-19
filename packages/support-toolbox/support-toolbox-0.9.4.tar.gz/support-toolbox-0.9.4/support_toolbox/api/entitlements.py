import json
import requests
from datetime import datetime

ORG_DEFAULT_ENTITLEMENTS = {
    "Organization Member Seat Count - Unlimited": "2c20846c-57b2-491f-bbd7-1f32bf0dec2c"
    # Adding an Entitlement here will automatically
}

ORG_ADDON_ENTITLEMENTS = {
    "Native Lineage": "c269642a-c0f8-4fa6-80ed-4d7380b9b6c4",
    "Governance Premium": "f35301e6-c5d2-46e7-81b7-164d866523f4"
    # Adding an Entitlement here will allow the user to opt in or out
}

USER_DEFAULT_ENTITLEMENTS = {
    "No Personal Datasets": "d9cdbf86-06c4-4e39-8d15-2874e50d2fae"
    # Adding an Entitlement here will automatically be deployed
}


def update_org_entitlements(api_url, admin_token, org_id, product_id, order, source, name):
    update_entitlements_url = f"{api_url}/entitlements"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    # Format the datetime as a string in the expected format
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    data = {
      "agentid": org_id,
      "entitlementItems": [
        {
          "productid": product_id,
          "quantity": "1"
        }
      ],
      "order": order,
      "source": source,
      "startDate": timestamp
    }

    body = json.dumps(data)
    response = requests.post(update_entitlements_url, body, headers=header)

    # Verify the update
    if response.status_code == 200:
        print(f"Successfully updated {org_id} with {name}")
    else:
        print(response.text)


def get_entitlements(api_url, admin_token, org_id):
    get_entitlements_url = f"{api_url}/entitlements/{org_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    response = requests.get(get_entitlements_url, headers=header)

    # Verify the response
    if response.status_code == 200:
        response_json = response.json()
        return response_json['records'][0]['source']
    else:
        print(response.text)


def get_default_values(api_url, admin_token, agent_type):
    get_offering_url = f"{api_url}/offerings/agentTypes/{agent_type}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    response = requests.get(get_offering_url, headers=header)

    # Verify the response
    if response.status_code == 200:
        response_json = response.json()

        result = {
            'agent_type': response_json['records'][0]['agentType'],
            'offering_slug': response_json['records'][0]['offeringSlug'],
            'offering_id': response_json['records'][0]['offeringid'],
            'product_ids': response_json['records'][0]['productids']
        }

        return result
    else:
        print(response.text)


# Take an agentType (org or user) as parameter to update the default plan
def update_default_plan(api_url, admin_token, offering_id, agent_type, offering_slug, product_ids):
    update_default_plan_url = f"{api_url}/offerings/{offering_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': f'token={admin_token};adminToken={admin_token}'
    }

    # Format the datetime as a string in the expected format
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    data = {
        "agentType": agent_type,
        "defaultOffering": True,
        "offeringSlug": offering_slug,
        "offeringid": offering_id,
        "pricingModel": {},
        "productids": product_ids,
        "requiresPayment": False,
        "startDate": timestamp
    }

    body = json.dumps(data)
    response = requests.put(update_default_plan_url, body, headers=header)

    if response.status_code == 200:
        all_products = {**ORG_DEFAULT_ENTITLEMENTS, **ORG_ADDON_ENTITLEMENTS, **USER_DEFAULT_ENTITLEMENTS}
        deployed_products = [key for key, value in all_products.items() if value in product_ids]
        print(f"Successfully updated the {agent_type} Default Plan with: {deployed_products}")
    else:
        print(response.text)
