# Resource Types currently supported
ENTITIES = {
    'ANALYSIS': 'https://dwec.data.world/v0/Analysis',
    'BUSINESS_TERM': 'https://dwec.data.world/v0/BusinessTerm',
    'COLLECTION': 'https://dwec.data.world/v0/Catalog',
    'COLUMN': 'https://dwec.data.world/v0/DatabaseColumn',
    'DATA_TYPE': 'http://www.w3.org/ns/csvw#Datatype',
    'DATASET': 'https://dwec.data.world/v0/DwDataset',
    'TABLE': 'https://dwec.data.world/v0/DatabaseTable',
    'DATABASE': 'https://dwec.data.world/v0/Database',
    'CUSTOM_TYPE': ''
}


def select_resource():
    while True:
        for i, entity in enumerate(ENTITIES, start=1):
            print(f"{i}. {entity}")

        try:
            selection = int(input(
                "Enter the number corresponding with the parent type of the resource: "))
            if 1 <= selection <= len(ENTITIES):
                if selection == 9:
                    resource_type = input(
                        "Enter the custom resource type IRI (ex. https://democorp.linked.data.world/d/ddw-catalogs/Sensor): ")
                    return resource_type
                return list(ENTITIES.values())[selection - 1]
            else:
                print("Invalid input. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

