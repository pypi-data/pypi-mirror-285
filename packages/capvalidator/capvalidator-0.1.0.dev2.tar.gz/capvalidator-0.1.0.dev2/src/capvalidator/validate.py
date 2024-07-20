from importlib.resources import files
from lxml import etree as ET
from lxml.etree import DocumentInvalid
from signxml import XMLVerifier, InvalidSignature


class Validator:
    def __init__(self, cap):
        self.cap = cap

    def schema(self):
        """Validates the CAP alert against the CAP 1.2 schema.

        Returns:
            tuple: The validation result and the associated message.
        """
        parser = self.get_schema_parser()

        # Try to parse the CAP alert XML string.
        # If it fails, the XML is not valid.
        try:
            ET.fromstring(self.cap, parser)
            return True, "CAP alert follows the CAP v1.2 schema."
        except ET.XMLSyntaxError:
            return False, "CAP alert does not follow the CAP v1.2 schema."

    def get_schema_parser(self) -> ET.XMLParser:
        """Performs the necessary steps to prepare the schema validator.

        Returns:
            XMLParser: The schema validator parser object.
        """
        # Load the XSD schema
        resource = files('capvalidator').joinpath('static/CAP-v1.2-schema.xsd')
        with resource.open() as f:
            schema_bytes = f.read()
        # Create the parser object
        schema_root = ET.XML(schema_bytes)
        schema = ET.XMLSchema(schema_root)
        return ET.XMLParser(schema=schema)

    def signature(self) -> tuple:
        """Verifies the digital signature and digest value of the CAP alert.

        Returns:
            tuple: The verification result and the associated message.
        """
        xml_bytes = self.canonicalize_xml()
        root = ET.fromstring(xml_bytes)

        namespaces = {
            'ds': 'http://www.w3.org/2000/09/xmldsig#'
        }

        # Locate the <ds:X509Certificate> element in the XML
        certificate_element = root.find('.//ds:X509Certificate', namespaces)

        if certificate_element is None:
            return False, "CAP alert has not been signed."

        # Extract the certificate data, removing leading/trailing whitespace
        certificate_data = certificate_element.text.strip()

        # Format the certificate data as a PEM certificate
        certificate_pem = f"-----BEGIN CERTIFICATE-----\n{certificate_data}\n-----END CERTIFICATE-----"  # noqa

        try:
            XMLVerifier().verify(root, x509_cert=certificate_pem).signed_xml
            return True, "CAP alert signature is valid."
        except (InvalidSignature, DocumentInvalid):
            return False, "CAP alert signature is invalid or the data has been tampered with."  # noqa

    def canonicalize_xml(self) -> bytes:
        """Parses the CAP XML in canonicalized form so that it is
        in a standard format. This ensures that every byte of the
        XML is the same for the signature to verify correctly.

        Returns:
            bytes: The canonicalized XML byte string.
        """
        parser = ET.XMLParser(remove_blank_text=True)
        xml_tree = ET.XML(self.cap, parser=parser)
        return ET.tostring(xml_tree)

    def get_dates(self) -> dict:
        """Extracts the four date-time values from the CAP alert.

        Returns:
            dict: The extracted date-time values.
        """
        root = ET.fromstring(self.cap)

        # Register the namespace
        namespace = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}

        sent_element = root.find('.//cap:sent', namespace)
        effective_element = root.find('.//cap:effective', namespace)
        onset_element = root.find('.//cap:onset', namespace)
        expires_element = root.find('.//cap:expires', namespace)

        sent = sent_element.text if sent_element is not None else None
        effective = effective_element.text if effective_element is not None else None  # noqa
        onset = onset_element.text if onset_element is not None else None
        expiry = expires_element.text if expires_element is not None else None

        return {
            'sent': sent,
            'effective': effective,
            'onset': onset,
            'expiry': expiry
        }
