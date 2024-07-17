import time
import requests
import yaml
import json
import os

try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

class ConfigLoader:
    @staticmethod
    def load_configuration(config_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'config.json'), 
                           crosswalk_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'crosswalk.json')):
        return MediLink_ConfigLoader.load_configuration(config_path, crosswalk_path)

    @staticmethod
    def load_swagger_file(swagger_path):
        try:
            print("Attempting to load Swagger file: {}".format(swagger_path))
            with open(swagger_path, 'r') as swagger_file:
                if swagger_path.endswith('.yaml') or swagger_path.endswith('.yml'):
                    print("Parsing YAML file: {}".format(swagger_path))
                    swagger_data = yaml.safe_load(swagger_file)
                elif swagger_path.endswith('.json'):
                    print("Parsing JSON file: {}".format(swagger_path))
                    swagger_data = json.load(swagger_file)
                else:
                    raise ValueError("Unsupported Swagger file format.")
            print("Successfully loaded Swagger file: {}".format(swagger_path))
            return swagger_data
        except ValueError as e:
            print("Error parsing Swagger file {}: {}".format(swagger_path, e))
            MediLink_ConfigLoader.log("Error parsing Swagger file {}: {}".format(swagger_path, e), level="ERROR")
        except FileNotFoundError:
            print("Swagger file not found: {}".format(swagger_path))
            MediLink_ConfigLoader.log("Swagger file not found: {}".format(swagger_path), level="ERROR")
        except Exception as e:
            print("Unexpected error loading Swagger file {}: {}".format(swagger_path, e))
            MediLink_ConfigLoader.log("Unexpected error loading Swagger file {}: {}".format(swagger_path, e), level="ERROR")
        return None

# Function to ensure numeric type
def ensure_numeric(value):
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            raise ValueError("Cannot convert {} to a numeric type".format(value))
    return value

class TokenCache:
    def __init__(self):
        self.tokens = {}

    def get(self, endpoint_name, current_time):
        token_info = self.tokens.get(endpoint_name, {})
        if token_info and token_info['expires_at'] > current_time:
            return token_info['access_token']
        return None

    def set(self, endpoint_name, access_token, expires_in, current_time):
        # Ensure types are correct
        current_time = ensure_numeric(current_time)
        expires_in = ensure_numeric(expires_in)
        
        self.tokens[endpoint_name] = {
            'access_token': access_token,
            'expires_at': current_time + expires_in - 120
        }

class BaseAPIClient:
    def __init__(self, config):
        self.config = config
        self.token_cache = TokenCache()

    def get_access_token(self, endpoint_name):
        raise NotImplementedError("Subclasses should implement this!")

    def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        raise NotImplementedError("Subclasses should implement this!")

class APIClient(BaseAPIClient):
    def __init__(self):
        config, _ = MediLink_ConfigLoader.load_configuration()
        super().__init__(config)

    def get_access_token(self, endpoint_name):
        current_time = time.time()
        cached_token = self.token_cache.get(endpoint_name, current_time)
        if cached_token:
            MediLink_ConfigLoader.log("Using cached token for endpoint: {}".format(endpoint_name), level="INFO")
            return cached_token

        endpoint_config = self.config['MediLink_Config']['endpoints'][endpoint_name]
        token_url = endpoint_config['token_url']
        data = {
            'grant_type': 'client_credentials',
            'client_id': endpoint_config['client_id'],
            'client_secret': endpoint_config['client_secret']
        }

        # Add scope if specified in the configuration
        if 'scope' in endpoint_config:
            data['scope'] = endpoint_config['scope']

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data.get('expires_in', 3600)

        self.token_cache.set(endpoint_name, access_token, expires_in, current_time)
        MediLink_ConfigLoader.log("Obtained new token for endpoint: {}".format(endpoint_name), level="INFO")
        return access_token

    def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        token = self.get_access_token(endpoint_name)
        if headers is None:
            headers = {}
        headers.update({'Authorization': 'Bearer {}'.format(token), 'Accept': 'application/json'})
        url = self.config['MediLink_Config']['endpoints'][endpoint_name]['api_url'] + url_extension
        
        # Debug: Print request details
        # print("Request URL: {}".format(url))
        # print("Request Headers: {}".format(headers))
        # print("Request Params: {}".format(params))
        # print("Request Data: {}".format(data))
        
        if call_type == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif call_type == 'POST':
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, json=data)
        elif call_type == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Unsupported call type")

        if response.status_code >= 400:
            error_message = "Error {}: {}".format(response.status_code, response.text)
            MediLink_ConfigLoader.log(error_message, level="ERROR")
            response.raise_for_status()

        return response.json()

def fetch_payer_name_from_api(payer_id, config, primary_endpoint='AVAILITY'):
    client = APIClient()
    config, _ = MediLink_ConfigLoader.load_configuration()
    endpoints = config['MediLink_Config']['endpoints']

    if primary_endpoint and primary_endpoint in endpoints:
        endpoint_order = [primary_endpoint] + [endpoint for endpoint in endpoints if endpoint != primary_endpoint]
    else:
        endpoint_order = list(endpoints.keys())

    for endpoint_name in endpoint_order:
        try:
            response = client.make_api_call(endpoint_name, 'GET', config['MediLink_Config']['endpoints'][endpoint_name].get('payer_list_endpoint', '/availity-payer-list'), {'payerId': payer_id})
            payers = response.get('payers', [])
            if payers:
                payer_name = payers[0].get('displayName', payers[0].get('name'))
                MediLink_ConfigLoader.log("Successfully found payer at {} for ID {}: {}".format(endpoint_name, payer_id, payer_name), level="INFO")
                return payer_name
            else:
                MediLink_ConfigLoader.log("No payer found at {} for ID: {}. Trying next available endpoint.".format(endpoint_name, payer_id), level="INFO")
        except Exception as e:
            MediLink_ConfigLoader.log("API call to {} failed: {}".format(endpoint_name, e), level="ERROR")

    error_message = "All endpoints exhausted for Payer ID {}.".format(payer_id)
    MediLink_ConfigLoader.log(error_message, level="CRITICAL")
    raise ValueError(error_message)

def get_claim_summary_by_provider(client, tin, first_service_date, last_service_date, payer_id, get_standard_error='false'):
    endpoint_name = 'UHCApi'
    url_extension = client.config['MediLink_Config']['endpoints'][endpoint_name]['additional_endpoints']['claim_summary_by_provider']
    headers = {
        'tin': tin,
        'firstServiceDt': first_service_date,
        'lastServiceDt': last_service_date,
        'payerId': payer_id,
        'getStandardError': get_standard_error,
        'Accept': 'application/json'
    }
    return client.make_api_call(endpoint_name, 'GET', url_extension, params=None, data=None, headers=headers)

def get_eligibility(client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi):
    endpoint_name = 'UHCApi'
    url_extension = client.config['MediLink_Config']['endpoints'][endpoint_name]['additional_endpoints']['eligibility']
    url_extension = url_extension + '?payerID={}&providerLastName={}&searchOption={}&dateOfBirth={}&memberId={}&npi={}'.format(
        payer_id, provider_last_name, search_option, date_of_birth, member_id, npi)
    return client.make_api_call(endpoint_name, 'GET', url_extension)

def get_eligibility_v3(client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi, 
                       first_name=None, last_name=None, payer_label=None, payer_name=None, service_start=None, service_end=None, 
                       middle_name=None, gender=None, ssn=None, city=None, state=None, zip=None, group_number=None, 
                       service_type_code=None, provider_first_name=None, tax_id_number=None, provider_name_id=None, 
                       corporate_tax_owner_id=None, corporate_tax_owner_name=None, organization_name=None, 
                       organization_id=None, identify_service_level_deductible=True):

    # Ensure all required parameters have values
    if not all([client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi]):
        raise ValueError("All required parameters must have values: client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi")

    # Validate payer_id
    valid_payer_ids = ["87726", "06111", "25463", "37602", "39026", "74227", "65088", "81400", "03432", "86050", "86047", "95378", "95467"]
    if payer_id not in valid_payer_ids:
        raise ValueError("Invalid payer_id: {}. Must be one of: {}".format(payer_id, ", ".join(valid_payer_ids)))
    
    endpoint_name = 'UHCApi'
    url_extension = client.config['MediLink_Config']['endpoints'][endpoint_name]['additional_endpoints']['eligibility_v3']
    
    # Construct request body
    body = {
        "memberId": member_id,
        "lastName": last_name,
        "firstName": first_name,
        "dateOfBirth": date_of_birth,
        "payerID": payer_id,
        "payerLabel": payer_label,
        "payerName": payer_name,
        "serviceStart": service_start,
        "serviceEnd": service_end,
        "middleName": middle_name,
        "gender": gender,
        "ssn": ssn,
        "city": city,
        "state": state,
        "zip": zip,
        "groupNumber": group_number,
        "serviceTypeCode": service_type_code,
        "providerLastName": provider_last_name,
        "providerFirstName": provider_first_name,
        "taxIdNumber": tax_id_number,
        "providerNameID": provider_name_id,
        "npi": npi,
        "corporateTaxOwnerID": corporate_tax_owner_id,
        "corporateTaxOwnerName": corporate_tax_owner_name,
        "organizationName": organization_name,
        "organizationID": organization_id,
        "searchOption": search_option,
        "identifyServiceLevelDeductible": identify_service_level_deductible
    }
    
    # Remove None values from the body
    body = {k: v for k, v in body.items() if v is not None}

    # Log the request body
    MediLink_ConfigLoader.log("Request body: {}".format(json.dumps(body, indent=4)), level="DEBUG")

    return client.make_api_call(endpoint_name, 'POST', url_extension, params=None, data=body)

if __name__ == "__main__":
    client = APIClient()
    
    # Define a configuration to enable or disable tests
    test_config = {
        'test_fetch_payer_name': False,
        'test_claim_summary': False,
        'test_eligibility': False,
        'test_eligibility_v3': True,
    }
    
    try:
        api_test_cases = client.config['MediLink_Config']['API Test Case']
        
        # Test 1: Fetch Payer Name
        if test_config.get('test_fetch_payer_name', False):
            try:
                for case in api_test_cases:
                    payer_name = fetch_payer_name_from_api(case['payer_id'], client.config)
                    print("TEST API: Payer Name: {}".format(payer_name))
            except Exception as e:
                print("TEST API: Error in Fetch Payer Name Test: {}".format(e))
        
        # Test 2: Get Claim Summary
        if test_config.get('test_claim_summary', False):
            try:
                for case in api_test_cases:
                    claim_summary = get_claim_summary_by_provider(client, case['provider_tin'], '05/01/2024', '06/23/2024', case['payer_id'])
                    print("TEST API: Claim Summary: {}".format(claim_summary))
            except Exception as e:
                print("TEST API: Error in Claim Summary Test: {}".format(e))
        
        # Test 3: Get Eligibility
        if test_config.get('test_eligibility', False):
            try:
                for case in api_test_cases:
                    eligibility = get_eligibility(client, case['payer_id'], case['provider_last_name'], case['search_option'], 
                                                  case['date_of_birth'], case['member_id'], case['npi'])
                    print("TEST API: Eligibility: {}".format(eligibility))
            except Exception as e:
                print("TEST API: Error in Eligibility Test: {}".format(e))

        # Test 4: Get Eligibility v3
        if test_config.get('test_eligibility_v3', False):
            try:
                for case in api_test_cases:
                    eligibility_v3 = get_eligibility_v3(client, payer_id=case['payer_id'], provider_last_name=case['provider_last_name'], 
                                                        search_option=case['search_option'], date_of_birth=case['date_of_birth'], 
                                                        member_id=case['member_id'], npi=case['npi'])
                    print("TEST API: Eligibility v3: {}".format(eligibility_v3))
            except Exception as e:
                print("TEST API: Error in Eligibility v3 Test: {}".format(e))

        """
        # Example of iterating over multiple patients (if needed)
        patients = [
            {'payer_id': '87726', 'provider_last_name': 'VIDA', 'search_option': 'MemberIDDateOfBirth', 'date_of_birth': '1980-01-01', 'member_id': '123456789', 'npi': '9876543210'},
            {'payer_id': '87726', 'provider_last_name': 'SMITH', 'search_option': 'MemberIDDateOfBirth', 'date_of_birth': '1970-02-02', 'member_id': '987654321', 'npi': '1234567890'},
            # Add more patients as needed
        ]

        for patient in patients:
            try:
                eligibility = get_eligibility(client, patient['payer_id'], patient['provider_last_name'], patient['search_option'], patient['date_of_birth'], patient['member_id'], patient['npi'])
                print("Eligibility for {}: {}".format(patient['provider_last_name'], eligibility))
            except Exception as e:
                print("Error in getting eligibility for {}: {}".format(patient['provider_last_name'], e))
        """
    except Exception as e:
        print("TEST API: Unexpected Error: {}".format(e))
