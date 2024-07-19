import time
from support_toolbox.api.org import onboard_org, authorize_access_to_org, deauthorize_access_to_org, validate_org_input
from support_toolbox.api.user import get_agent_id
from support_toolbox.utils.api_url import select_api_url

CTK_STACK = {
    'catalog-config': 'Catalog Config',
    'catalog-sources': 'Catalog Sources',
    'catalog-sandbox': 'Catalog Sandbox',
    'main': 'Main'
}

CTK_STACK_IMAGES = {
      'catalog-config': 'https://media.data.world/iSELaVlgTWeiy2bh2jhw_catalog-config.png',
      'catalog-sources': 'https://media.data.world/uDofsZwIR1SDUgUfEYp7_catalog-sources.png',
      'catalog-sandbox': 'https://media.data.world/Sue4Y8WVSrCqApwtZDvp_catalog-sandbox.png'
}


def deploy_ctk(api_url, admin_token, prefix=None):
    orgs_to_cleanup = []
    for org_id, org_display_name in CTK_STACK.items():
        avatar_url = '' if org_id == 'main' else CTK_STACK_IMAGES[org_id]
        if prefix:
            org_id = f"{prefix} {org_id}"
            org_id = org_id.replace(' ', '-').lower()
            org_display_name = f"{prefix} {org_display_name}"

        orgs_to_cleanup.append(org_id)
        onboard_org(api_url, admin_token, org_id, org_display_name, avatar_url)
        authorize_access_to_org(api_url, admin_token, org_id, party="group:datadotworldsupport/members")

    # Platform lag is intense, use this to force a wait
    time.sleep(1)
    cleanup_ctk_deployment(api_url, admin_token, orgs_to_cleanup)


def cleanup_ctk_deployment(api_url, admin_token, orgs_to_cleanup):
    agent_id = get_agent_id(api_url, admin_token)

    for org_id in orgs_to_cleanup:
        # Platform lag is intense, use this to force a wait
        time.sleep(1)
        deauthorize_access_to_org(api_url, admin_token, agent_id, org_id)


def run():
    api_url = select_api_url("private")
    admin_token = input("Enter your active admin token for the site you are deploying CTK to: ")

    while True:
        selection = input("Does this CTK stack require an org prefix? (y/n): ")

        if selection == 'y':
            prefix = input("What will the org prefix be? (CASE SENSITIVE): ")
            if validate_org_input(prefix):
                deploy_ctk(api_url, admin_token, prefix=prefix)
                break
            else:
                print('Invalid prefix name. Please try again.')

        else:
            main_display_name = input("What will the Display Name for the 'main' org be called? (CASE SENSITIVE): ")
            if validate_org_input(main_display_name):
                CTK_STACK['main'] = main_display_name
                deploy_ctk(api_url, admin_token)
                break
            else:
                print('Invalid organization name. Please try again.')
