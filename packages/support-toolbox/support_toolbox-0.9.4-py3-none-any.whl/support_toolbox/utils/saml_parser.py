import xml.etree.ElementTree as ET


class SAMLMetadataParser:
    def __init__(self, metadata_file_path):
        self.metadata_file_path = metadata_file_path
        self.root = self.parse_metadata_file()

    def parse_metadata_file(self):
        try:
            tree = ET.parse(self.metadata_file_path)
            return tree.getroot()
        except Exception as e:
            raise ValueError(f"Error parsing XML file: {str(e)}")

    def get_entity_id(self):
        entity_id = self.root.get('entityID')
        return entity_id

    def get_sso_url(self):
        sso_url_element = self.root.find('.//md:SingleSignOnService', namespaces={'md': 'urn:oasis:names:tc:SAML:2.0:metadata'})
        sso_url = sso_url_element.get('Location')
        return sso_url

    def get_x509_certificate(self):
        x509_cert_element = self.root.find('.//md:KeyDescriptor[@use="signing"]/ds:KeyInfo/ds:X509Data/ds:X509Certificate', namespaces={'md': 'urn:oasis:names:tc:SAML:2.0:metadata', 'ds': 'http://www.w3.org/2000/09/xmldsig#'})
        x509_cert_base64 = x509_cert_element.text

        # Add PEM delimiters
        pem_cert = f"-----BEGIN CERTIFICATE-----\n{x509_cert_base64}\n-----END CERTIFICATE-----"
        return pem_cert
