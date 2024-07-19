import re
import os
import configparser
from support_toolbox.utils.api_url import get_api_url_location
from support_toolbox.api.user import get_agent_id, create_user, update_user_roles
from support_toolbox.deploy_browse_card import deploy_browse_card
from support_toolbox.deploy_integrations import deploy_integrations
from support_toolbox.api.org import authorize_access_to_org, deauthorize_access_to_org, validate_org_input
from support_toolbox.onboard_ctk_orgs import deploy_ctk, CTK_STACK
from support_toolbox.api.entitlements import update_org_entitlements, get_entitlements, get_default_values, update_default_plan, ORG_DEFAULT_ENTITLEMENTS, ORG_ADDON_ENTITLEMENTS, USER_DEFAULT_ENTITLEMENTS
from support_toolbox.api.site import create_site
from support_toolbox.api.service_account import deploy_service_accounts
from support_toolbox.utils.metrics import deploy_metrics
from support_toolbox.api.project import create_project, create_saved_query
from support_toolbox.api.dataset import set_dataset_ingest

# TODO: Remove if Service Account creation is sunset from deploy_pi
# Get the path to the user's home directory
user_home = os.path.expanduser("~")

# Construct the full path to the configuration file
tokens_file_path = os.path.join(user_home, ".tokens.ini")

# Initialize the configparser and read the tokens configuration file
config = configparser.ConfigParser()
config.read(tokens_file_path)

# Read tokens/variables for the deploy_service_accounts tool
circleci_api_token = config['deploy_pi']['CIRCLECI_API_TOKEN']

DEFAULT_ORGS = ["datadotworldsupport",
                "ddw",
                "datadotworld-apps"
                ]

SAML_PLACEHOLDER = {
    "entity_id": "http://www.okta.com/placeholder",
    "sso_url": "https://dev-placeholder.okta.com/app/placeholder/sso/saml",
    "x509_cert": """-----BEGIN CERTIFICATE-----
                MIIDqDCCApCgAwIBAgIGAYDyMs9qMA0GCSqGSIb3DQEBCwUAMIGUMQswCQYDVQQGEwJVUzETMBEG
                A1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsGA1UECgwET2t0YTEU
                MBIGA1UECwwLU1NPUHJvdmlkZXIxFTATBgNVBAMMDGRldi0xNjk5NDUxNzEcMBoGCSqGSIb3DQEJ
                ARYNaW5mb0Bva3RhLmNvbTAeFw0yMjA1MjMxODMzMTdaFw0zMjA1MjMxODM0MTdaMIGUMQswCQYD
                VQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsG
                A1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxFTATBgNVBAMMDGRldi0xNjk5NDUxNzEc
                MBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
                ggEBANMQI4i1roai7bnDCAiwDr3FbkKz6RkTOi1Uz1qjnIRfyWIHJRa2yUmjN3+wBmTBHYNkxgMK
                I3g8iElMX3Fz/FFjEYKsCNAq4RZG+sn/zo/8Y6g7bMvz7kc/oXikiuSK/BWFkvx7rSm1fRA+cX6W
                iy3HlsqNPXLUMXlZYV5RK8vF0wxITVJxyvxBaQeKezJD+CNIxVwMBZfgptMxIbKMEHcucVqkp8sa
                aQt0/9Xjser0DbMwPVHKctCyjkXUz/rMfWIw7E6ehL3gFKfHfZn/Mld8PzFg71Ql7AqkYZ8gB9HO
                xUXEeqvIMlqsMu3IlVsEAhF4m+S75TJQJdpvW8NiiRUCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEA
                iOoPf0SRBZE3aE4O65HCYwmCNRBJdbCJqqBEcT1rHUuACCtyq4KB1sOPZfoHURHern7o8jB3UpCV
                aVgdYX05FIkfZnGHYxeZ/7exeDW0kVydhpVouqCqSAdyDhci053Isz2VwAvs5zh2oTa5ChFFZ4bS
                WSmv/eM6RhBePRYe+pExiFhMy2+Rx8O4UV1hTQMr2s3Zp6YYUMqPC23t/3wQaY5YskbZ4E3Qsq6K
                iB7h/2MLj4XZnX+cdmdYmS8K1fPsBPiz5B35v3CqvpzcmfVVyPlIzDVWe87AJneAcqxRrnhHFO3N
                20Qc7OFBZxC0xde8mrIfIaX4y99g4yk8hzHqRQ==
                -----END CERTIFICATE-----"""
}


def sanitize_public_slug(slug):
    slug = slug.lower()

    # Remove spaces, symbols, and numbers
    slug = re.sub(r'[^a-z]+', '', slug)

    return slug


def config_default_orgs(api_url, admin_token):
    # Update the DEFAULT_ORGS with the ORG_DEFAULT_ENTITLEMENTS
    for org_id in DEFAULT_ORGS:
        source = get_entitlements(api_url, admin_token, org_id)
        order = 1
        for name, product_id in ORG_DEFAULT_ENTITLEMENTS.items():
            update_org_entitlements(api_url, admin_token, org_id, product_id, order, source, name)
            order += 1

    # Authorize 'datadotworldsupport' access to 'ddw', this is not done by default during create_site for some reason
    authorize_access_to_org(api_url, admin_token, 'ddw', party="group:datadotworldsupport/members")


def config_default_org_plan(api_url, admin_token):
    # Get the Org Default Values used to update the Org Default Plan
    org_values = get_default_values(api_url, admin_token, "organization")
    org_agent_type = org_values['agent_type']
    org_offering_slug = org_values['offering_slug']
    org_offering_id = org_values['offering_id']
    org_product_ids = org_values['product_ids']

    # Update Org Default Plan with the ORG_DEFAULT_ENTITLEMENTS
    for entitlement in ORG_DEFAULT_ENTITLEMENTS.values():
        org_product_ids.append(entitlement)

    # Update the Org Default Plan with the optional ORG_ADDON_ENTITLEMENTS
    for addon_entitlement in ORG_ADDON_ENTITLEMENTS:
        while True:
            selection = input(f"Add {addon_entitlement}? (y/n): ")
            if selection == 'y':
                org_product_ids.append(ORG_ADDON_ENTITLEMENTS[addon_entitlement])
                break
            elif selection == 'n':
                break
            else:
                print("Enter a valid option: (y/n)")

    update_default_plan(api_url, admin_token, org_offering_id, org_agent_type, org_offering_slug, org_product_ids)


def config_default_user_plan(api_url, admin_token):
    # Get the User Default Values used to update the User Default Plan
    user_values = get_default_values(api_url, admin_token, "user")
    user_agent_type = user_values['agent_type']
    user_offering_slug = user_values['offering_slug']
    user_offering_id = user_values['offering_id']
    user_product_ids = user_values['product_ids']

    # Update Product IDs with the USER_DEFAULT_ENTITLEMENTS
    for entitlement in USER_DEFAULT_ENTITLEMENTS.values():
        user_product_ids.append(entitlement)

    update_default_plan(api_url, admin_token, user_offering_id, user_agent_type, user_offering_slug, user_product_ids)


def cleanup_site_creation(api_url, admin_token, metrics_org=''):
    agent_id = get_agent_id(api_url, admin_token)
    print(f"Cleaning up any resources {agent_id} is in...")

    for org_id in DEFAULT_ORGS:
        if org_id == 'datadotworldsupport':
            continue
        deauthorize_access_to_org(api_url, admin_token, agent_id, org_id)

    deauthorize_access_to_org(api_url, admin_token, agent_id, metrics_org)


def add_support(api_url, admin_token):
    SUPPORT = [
        {
            "agent_id": "jack-compton",
            "display_name": "Jack Compton",
            "email": "jack.compton@data.world",
        },
        {
            "agent_id": "ren-curry",
            "display_name": "Ren Curry",
            "email": "ren.curry@data.world",
        },
        {
            "agent_id": "will-kiyola",
            "display_name": "Will Kiyola",
            "email": "will.kiyola@data.world",
        },
        {
            "agent_id": "carrie-couch",
            "display_name": "Carrie Couch",
            "email": "carrie.couch@data.world",
        },
        {
            "agent_id": "marcus-vialva",
            "display_name": "Marcus Vialva",
            "email": "marcus.vialva@data.world",
        }
    ]

    ALLOWED_SUPPORT_ROLES = [
        "user",
        "user_api",
        "dwadmin",
        "employee",
        "instance-admin",
        "rate_limit_tier1",
        "support_team",
        "grafo_admin",
        "dwpayments",
        "view-creator"
    ]

    for values in SUPPORT:
        agent_id = values["agent_id"]
        display_name = values["display_name"]
        email = values["email"]

        create_user(api_url, admin_token, agent_id, display_name, email)
        update_user_roles(api_url, admin_token, agent_id, ALLOWED_SUPPORT_ROLES)
        authorize_access_to_org(api_url, admin_token, org_id="datadotworldsupport", party="agent:" + agent_id)


def add_pm(api_url, admin_token):
    PM = [
        {
            "agent_id": "bernie-albright",
            "display_name": "Bernie Albright",
            "email": "bernie.albright@data.world",
        }
    ]

    ALLOWED_PM_ROLES = [
        "user",
        "user_api",
        "instance-admin"
    ]

    for values in PM:
        agent_id = values["agent_id"]
        display_name = values["display_name"]
        email = values["email"]

        create_user(api_url, admin_token, agent_id, display_name, email)
        update_user_roles(api_url, admin_token, agent_id, ALLOWED_PM_ROLES)
        authorize_access_to_org(api_url, admin_token, org_id="datadotworldsupport", party="agent:" + agent_id)


def setup_implementation_project(api_url, admin_token, org_id, public_slug, visibility):
    IMPLEMENTATION_QUERIES = [
        {
            "name": "01. First Login",
            "content": """
    SELECT
    displayname as UserID,
    onboard_date as Firstlogin

    FROM membership_current_last_90_days

    WHERE email not like '%data.world%'

    group BY
    displayname,
    onboard_date

    order by 2,1 ASC""",
            "language": "SQL",
            "published": True
        },
        {
            "name": "02. Days Since Last Activity",
            "content": """
    SELECT
    displayname as User,
    min(DATE_DIFF(lastseen, now() ,"day")) as days_since_active

    From membership_current_by_org_last_90_days

    Where email not like '%@data.world%'

    Group by 
    displayname

    order by 2 ASCSample""",
            "language": "SQL",
            "published": True
        },
        {
            "name": "10. Views, Edits, and Creates Last 7 Days",
            "content": """
    SELECT
    owner as org,
    displayname as user_id,
    sum(views) as Resources_Viewed,
    sum(Edits)as Resources_Edited,
    sum(creates) as Resources_Created

    FROM events_catalog_resources_pages_activity_by_day_last_90_days e
        INNER JOIN membership_current_last_90_days m ON e.agentid = m.agentid

    WHERE email not like '%data.world%' and DATE_DIFF(DATE,NOW(),"day")<7

    Group BY
    Owner,
    displayname

    order by 1,2 ASC""",
            "language": "SQL",
            "published": True
        },
        {
            "name": "11. Production Catalog Resources Created and Edited last 7 days",
            "content": """
    SELECT
    case when creates > 0 then "Created" when edits > 0 then "Edited" else NULL END as Activity,
    owner as Org,
    date,
    displayname as User_Id,
    resourcetype as Resource_Type,
    resourcename as Resource_Name

    FROM events_catalog_resources_pages_activity_by_day_last_90_days e
        INNER JOIN membership_current_last_90_days m ON e.agentid = m.agentid

    where (creates >0 or edits >0) and email not like '%data.world%'and owner like '%main%' and DATE_DIFF(DATE,NOW(),"day")<7

    order by 1,2,3,4,5,6 ASC""",
            "language": "SQL",
            "published": True
        },
        {
            "name": "12. Suggestion Status",
            "content": """
    SELECT 
    e.event_date_utc as DATE,
    e.org as Org,
    m.displayname as Suggestor,
    e.event_type Event_Type, 
    suggestion_completedby as Suggestion_closed_by,
      CASE
        WHEN g.current_value LIKE '%://%'THEN REGEXP_REPLACE(g.current_value, '^.*/', '')
        ELSE g.current_value
      END AS Original_Value,
    #current_value as original_value,
      CASE
        WHEN g.value LIKE '%://%'THEN REGEXP_REPLACE(g.value, '^.*/', '')
        ELSE g.value
      END AS New_Value
     #value as New_value

    FROM audit_events_last_90_days e
        INNER JOIN membership_current_last_90_days m ON e.suggestion_requestor = m.agentid
        Inner JOIN audit_events_with_changes_last_90_days g on e.id = g.event_id

    WHERE e.suggestion_id is not NULL""",
            "language": "SQL",
            "published": True
        },
        {
            "name": "20. [Last 90 Days] Production Catalog Resources Created and Edited by Date",
            "content": """
    SELECT
    case when creates > 0 then "Created" when edits > 0 then "Edited" else NULL END as Activity,
    owner as Org,
    date,
    displayname as User_Id,
    resourcetype as Resource_Type,
    resourcename as Resource_Name

    FROM events_catalog_resources_pages_activity_by_day_last_90_days e
        INNER JOIN membership_current_last_90_days m ON e.agentid = m.agentid

    where (creates >0 or edits >0) and email not like '%data.world%'and owner like 'main'

    order by 1,2,3,4,5,6 ASC""",
            "language": "SQL",
            "published": True
        },
        {
            "name": "30. Files uploaded to Datasets and Projects",
            "content": """
    Select
    rdf.owner as Org,
    cdp.resource as `Dataset | Project Name`,
    cdp.type as `Location Type`,
    case 
        when rdf.file_materialized_or_virtualized like 'materialized' then 'stored in platform' else 'Virtualized'
    end as `Mechanism`,
    case 
        when cast(rdf.is_file_discoverable as string)  like 'true' then 'discoverable' else 'hidden'
    end as `Status`,
    displayname as `Uploaded By`,
    rdf.file_created_date as `Date Uploaded`,
    rdf.file_name as `File Name`,
    concat (round (rdf.file_size_in_bytes/1000000,3),"Mb") as `File Size`, 
    dsv.versionid as `Current Version ID`,
    dsv.previousversionid as `Previous Version ID`,
    case 
        when dsv.previousversionid is NOT NULL then DATE_FORMAT(dsv.updated, "yyyy.mm.dd") else "N/A"
    end as `Updated On`

    from events_create_dataset_project_events as cdp 
        join resources_dataset_files as rdf on rdf.resourceid = cdp.resourceid
        join membership_all_time_list as ma on file_createdby_agentid = ma.agentid 
        join datasetversions_last_90_days as dsv on agentdatasetid = CONCAT(rdf.owner,':',rdf.resource)

    where cdp.email not like '%data%'
        and rdf.file_name not like '.data%'
        and rdf.file_materialized_or_virtualized like 'materialized'

    order by 1,2,3,7 ASC""",
            "language": "SQL",
            "published": True
        }
    ]

    summary = """
    # *Project Team*

    ## *[data.world](http://data.world/) Team*

    - *<name> - Project Manager (PM) |@Tag | Email*
    - *<name> - Solution Architect (SA) | @Tag | Email*
    - *<name> - Customer Success Director (CSD) | @Tag | Email*

    ## *<Customer> Team*

    - *Name - Role/Title | @Tag | Email*
    - *Name - Role/Title | @Tag | Email*
    - *Name - Role/Title | @Tag | Email*

    # *Project Plan*

    ## *Typical Implementation Overview*

    *<insert diagram>*

    ## *<Customer> Project Schedule*

    *<Insert Gantt Chart>*

    # *Project Files*

    - *Scope Acknowledgement*
    - *Project Management Plan*
    - *Initial Schedule*
    - *Final Schedule*
    - *Detailed Implementation Plan*
    - *Project Kick-off Slide Deck*
    - *Project Summary Doc*

    # *Helpful Links*

    - *[data.world University - Onboarding](https://university.data.world/page/customer-onboarding)*
    - *[data.world connection manager setup](https://implementation.data.world/docs/collect-metadata-using-connection-manager)*
    - *[data.world collector setup](https://docs.data.world/en/98627-connect-to-data.html#UUID-546857a2-0226-3d5e-cb99-0e81d072b63b)*
    - *[Catalog Toolkit - source and metadata profile configuration](https://docs.data.world/en/201702-about-catalog-toolkit.html)*
    - *[Eureka Automations](https://docs.data.world/en/203152-configure-eureka-automations.html)*
    - *[Eureka Action Center](https://docs.data.world/en/98583-home-page.html)*
    - *[Browse Card Setup - Organization](https://docs.data.world/en/200191-browse-card-for-organization-profile-pages.html)*
    - *[Metrics](https://docs.data.world/en/114572-metrics-and-auditing.html)*

    # *Status Reports*

    - <date> - Status Report
    - <date> - Status Report

    # *Workshop/ Meeting Recordings:*

    - <date> - data.world | <Customer> | <Meeting Description>
    - <date> - data.world | <Customer> | <Meeting Description>
    - <date> - data.world | <Customer> | <Meeting Description>

    # *Support Tickets & Feature/ Enhancement Requests*

    - *DWS-<Ticket #> - <Type> - <Short Description>*
    """

    project_title = f"{public_slug} Implementation Project"
    create_project(admin_token, org_id, project_title, visibility, summary)

    project_id = project_title.replace(" ", "-").lower()
    for q in IMPLEMENTATION_QUERIES:
        create_saved_query(admin_token, q, org_id, project_id)

    set_dataset_ingest(api_url, admin_token, org_id, project_id)


def run():
    api_url = get_api_url_location()

    while True:
        user_input = input("Enter the URL slug: ")
        public_slug = sanitize_public_slug(user_input)

        if not public_slug:
            print("Invalid slug. Please enter a valid URL slug.")
            continue

        preview_url = f"https://{public_slug}.app.data.world"
        selection = input(f"Here is a preview of the URL: {preview_url}\nDoes this look correct? (y/n): ")

        if selection == 'y':
            entity_id = SAML_PLACEHOLDER['entity_id']
            sso_url = SAML_PLACEHOLDER['sso_url']
            x509_cert = SAML_PLACEHOLDER['x509_cert']

            # Create site
            admin_token = input("Enter your active adminToken to begin deployment (US-community/EU-admingatewayeu): ")
            create_site(admin_token, entity_id, public_slug, sso_url, x509_cert, api_url)

            # Get the users active admin_token to complete the deployment using Private APIs
            admin_token = input(f"Enter your active adminToken for the {public_slug} site: ")

            # Configure site
            config_default_orgs(api_url, admin_token)
            config_default_org_plan(api_url, admin_token)
            config_default_user_plan(api_url, admin_token)

            # Deploy CTK using the entered 'main' org as the Display Name
            while True:
                main_display_name = input("What will the Display Name for the 'main' org be called? (CASE SENSITIVE): ")
                if validate_org_input(main_display_name):
                    CTK_STACK['main'] = main_display_name
                    break
                else:
                    print('Invalid organization name. Please try again.')
            deploy_ctk(api_url, admin_token)

            # Deploy Metrics and return metrics org_id and existing_customer boolean
            metrics_org, existing_customer = deploy_metrics(api_url, admin_token, public_slug)

            print("Deploying browse card...")
            deploy_browse_card(admin_token, 'n')

            print("Deploying integrations...")
            deploy_integrations(admin_token, '1')

            # # TODO: Remove if you cannot hit Private API to generate CTK SA token
            # print("Deploying service accounts...")
            # deploy_service_accounts(api_url, admin_token, public_slug, circleci_api_token, existing_customer)

            cleanup_site_creation(api_url, admin_token, metrics_org)

            print("Adding the Support Team to the PI...")
            add_support(api_url, admin_token)

            print("Adding the PM Team to the PI...")
            add_pm(api_url, admin_token)

            print("Setting up Implementation Project...")
            setup_implementation_project(api_url, admin_token, "data-catalog-team", public_slug, "OPEN")
            break

        # preview URL denied
        elif selection == 'n':
            continue

        else:
            print("Enter a valid option: 'y'/'n'")
