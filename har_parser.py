import json
import base64
import xml.etree.ElementTree as ET
import urllib.parse


def load_har(file_path):
    '''Load the .har file
    #### to do load this from input
    '''
    with open(file_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    return har_data


def extract_failed_requests(har_data):
    """
    Extracts the failed requests from the .har file uploades.
    input:raw JSON input .har file
    """
    failed_requests = []
    entries = har_data.get('log', {}).get('entries', [])
    # print(entries)

    for entry in entries:
        status = entry.get('response', {}).get('status', 0)
        url = entry.get('request', {}).get('url', '')
        method = entry.get('request', {}).get('method', '')
        request_body = entry.get('request', {}).get(
            'postData', {}).get('text', '')
        if status >= 400:
            failed_requests.append({
                "method": method,
                "url": url,
                "status": status,
                "response_body": entry.get('response', {}).get('content', {}).get('text', ''),
                "request_body": request_body
            })
    return failed_requests


def decode_saml_response(failed_requests):
    """
    If the fail request is from SAML Use this function, Need to enable a check if the fail request has SAML. 
    This function will decode the SAML response into the XML document. 
    retuns: 
        * decode_xml
        * root element of the xml document of SAMLresponse
    """
    for request in failed_requests:
        samlresponse = request["request_body"]
        if samlresponse:
            saml_response_url_enc = samlresponse.split(
                'SAMLResponse=')[1].split('&RelayState')[0]
            saml_response_b64 = urllib.parse.unquote(saml_response_url_enc)
            try:
                # Step 1: Decode Base64 to raw XML string
                decoded_bytes = base64.b64decode(saml_response_b64)
                decoded_xml = decoded_bytes.decode('utf-8')

                # Step 2: Optional – Pretty-print or return as ElementTree
                root = ET.fromstring(decoded_xml)
                return decoded_xml, root

            except Exception as e:
                return None, f"Failed to decode SAML response: {e}"

        else:
            return ("no saml respose present in .har file")


def parse_saml_response_print(xml_string):
    """
    This will parse the SAML response, The decode_saml_response function outputs the XML raw data, 
    This function will print the details of the SAML response beautifully. 
    need to run after decode_saml_response as this is the XML string which will be needed to fetch the data. 
    """
    ns = {
        'samlp': "urn:oasis:names:tc:SAML:2.0:protocol",
        'saml': "urn:oasis:names:tc:SAML:2.0:assertion",
        'ds': "http://www.w3.org/2000/09/xmldsig#"
    }

    root = ET.fromstring(xml_string)

    print("\n🔹 General Info:")
    print("ID:", root.attrib.get('ID'))
    print("Destination:", root.attrib.get('Destination'))
    print("InResponseTo:", root.attrib.get('InResponseTo'))
    print("IssueInstant:", root.attrib.get('IssueInstant'))

    issuer = root.find("saml:Issuer", ns)
    if issuer is not None:
        print("Issuer:", issuer.text.strip())

    status_code = root.find("samlp:Status/samlp:StatusCode", ns)
    if status_code is not None:
        print("StatusCode:", status_code.attrib.get("Value"))

    assertion = root.find("saml:Assertion", ns)
    if assertion is not None:
        print("\n🔹 Assertion Info:")
        print("Assertion ID:", assertion.attrib.get("ID"))
        print("IssueInstant:", assertion.attrib.get("IssueInstant"))
        print("Version:", assertion.attrib.get("Version"))

        subject = assertion.find("saml:Subject/saml:NameID", ns)
        if subject is not None:
            print("Subject NameID:", subject.text)

        print("\n🔹 Attributes:")
        for attr in assertion.findall(".//saml:Attribute", ns):
            attr_name = attr.attrib.get("Name")
            values = [val.text for val in attr.findall(
                "saml:AttributeValue", ns)]
            print(f"{attr_name}: {', '.join(values)}")

        print("\n🔹 Authentication Info:")
        authn_statement = assertion.find("saml:AuthnStatement", ns)
        if authn_statement is not None:
            print("AuthnInstant:", authn_statement.attrib.get("AuthnInstant"))
            print("SessionIndex:", authn_statement.attrib.get("SessionIndex"))

            context = authn_statement.find(
                "saml:AuthnContext/saml:AuthnContextClassRef", ns)
            if context is not None:
                print("AuthnContext:", context.text)

    else:
        print("❌ No Assertion found in SAML response.")


def parse_saml_response(xml_string):
    """
    This will parse the SAML response, The decode_saml_response function outputs the XML raw data, 
    This function will return the response data in the dictionary format. 
    This can be used for further processing. 
    need to run after decode_saml_response as this is the XML string which will be needed to fetch the data. 
    """
    ns = {
        'samlp': "urn:oasis:names:tc:SAML:2.0:protocol",
        'saml': "urn:oasis:names:tc:SAML:2.0:assertion",
        'ds': "http://www.w3.org/2000/09/xmldsig#"
    }

    parsed_result = {
        "general_info": {},
        "assertion_info": {},
        "attributes": {},
        "authentication_info": {}
    }

    try:
        root = ET.fromstring(xml_string)

        # General Info
        parsed_result["general_info"]["id"] = root.attrib.get('ID')
        parsed_result["general_info"]["destination"] = root.attrib.get(
            'Destination')
        parsed_result["general_info"]["in_response_to"] = root.attrib.get(
            'InResponseTo')
        parsed_result["general_info"]["issue_instant"] = root.attrib.get(
            'IssueInstant')

        issuer = root.find("saml:Issuer", ns)
        if issuer is not None:
            parsed_result["general_info"]["issuer"] = issuer.text.strip()

        status_code = root.find("samlp:Status/samlp:StatusCode", ns)
        if status_code is not None:
            parsed_result["general_info"]["status_code"] = status_code.attrib.get(
                "Value")

        # Assertion Info
        assertion = root.find("saml:Assertion", ns)
        if assertion is not None:
            parsed_result["assertion_info"]["assertion_id"] = assertion.attrib.get(
                "ID")
            parsed_result["assertion_info"]["issue_instant"] = assertion.attrib.get(
                "IssueInstant")
            parsed_result["assertion_info"]["version"] = assertion.attrib.get(
                "Version")

            subject = assertion.find("saml:Subject/saml:NameID", ns)
            if subject is not None:
                parsed_result["assertion_info"]["subject_name_id"] = subject.text

            # Attributes
            for attr in assertion.findall(".//saml:Attribute", ns):
                attr_name = attr.attrib.get("Name")
                values = [val.text for val in attr.findall(
                    "saml:AttributeValue", ns)]
                parsed_result["attributes"][attr_name] = values

            # Authentication Info
            authn_statement = assertion.find("saml:AuthnStatement", ns)
            if authn_statement is not None:
                parsed_result["authentication_info"]["authn_instant"] = authn_statement.attrib.get(
                    "AuthnInstant")
                parsed_result["authentication_info"]["session_index"] = authn_statement.attrib.get(
                    "SessionIndex")

                context = authn_statement.find(
                    "saml:AuthnContext/saml:AuthnContextClassRef", ns)
                if context is not None:
                    parsed_result["authentication_info"]["authn_context"] = context.text

        return parsed_result

    except ET.ParseError as e:
        return {"error": f"XML parsing failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


# importent fields
def important_attributes(parsed_result):
    """
    Fetch the importan details which will be used to used later to fetch the details from snowflake. 
    The input of this function is the output of the function parse_saml_response()
    """
    general_info = parsed_result['general_info']
    assertion_info = parsed_result['assertion_info']

    # general attributes.
    StatusCode = general_info['status_code']
    InResponseTo = general_info['in_response_to']
    Destination = general_info['destination']
    Issuer = general_info['issuer']

    # assertion_info
    Timestamp = assertion_info['issue_instant']
    NameId = assertion_info["subject_name_id"]

    # identifier fetch
    identifier = Destination.split(".")[0].split("/")[2]

    imp_attr = {
        "StatusCode": StatusCode,
        "InResponseTo": InResponseTo,
        "Destination": Destination,
        "Issuer": Issuer,
        "Timestamp": Timestamp,
        "NameId": NameId,
        "Identifier": identifier
    }

    return imp_attr


# sample test load har file.
har_file = load_har("sample.har")
failed_request = extract_failed_requests(har_file)


# print(decode_saml_response(failed_request))
decoded_xml, root = decode_saml_response(failed_request)


parsed_response = parse_saml_response(decoded_xml)

# print the response header
# for key, val in parsed_response.items():
#     print(key)

#     print(parsed_response[key],"\n")


# print(parsed_response)

parse_saml_response_print(decoded_xml)

print(important_attributes(parsed_response))
