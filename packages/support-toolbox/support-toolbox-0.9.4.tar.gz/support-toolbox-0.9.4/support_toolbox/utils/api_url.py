PUBLIC_API_URLS = {
    "INDEED": "https://api.indeed.data.world/v0",
    "MCKINSEY": "https://api.mckinsey.data.world/v0",
    "MT/PI/EU": "https://api.data.world/v0"
}

PRIVATE_API_URLS = {
    "INDEED": "https://cgtslzqhl5-admin.indeed.data.world/_/admin/api/v0",
    "MCKINSEY": "https://tecsreqzb1-admin.mckinsey.data.world/_/admin/api/v0",
    "MT/PI": "https://k2xz8y420efx4a3j.data.world/_/admin/api/v0",
    "EU": "https://l0bbade1vhkqoxau.data.world/_/admin/api/v0"
    # "INDEED": "https://indeed.data.world/_/admin/api/v0",
    # "MCKINSEY": "https://mckinsey.data.world/_/admin/api/v0",
    # "MT": "https://data.world/_/admin/api/v0",
    # "PI/EU": "https://{public_slug}.app.data.world/_/admin/api/v0"
}


def select_api_url(api_type):
    if api_type == "private":
        api_urls = PRIVATE_API_URLS
    elif api_type == "public":
        api_urls = PUBLIC_API_URLS
    else:
        raise ValueError("Invalid API type. Use 'private' or 'public'")

    while True:
        for i, customer in enumerate(api_urls, start=1):
            print(f"{i}. {customer}")

        try:
            selection = int(input("Enter the number corresponding with the site your customer is in: "))
            if 1 <= selection <= len(api_urls):
                selected_customer = list(api_urls.keys())[selection - 1]
                return api_urls[selected_customer]
            else:
                print("Invalid input. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_api_url_location():
    while True:
        eu_deployment = input("Is this an EU deployment? (y/n): ").strip().lower()
        if eu_deployment == 'y':
            api_url = PRIVATE_API_URLS['EU']
            break
        elif eu_deployment == 'n':
            api_url = PRIVATE_API_URLS['MT/PI']
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    return api_url
