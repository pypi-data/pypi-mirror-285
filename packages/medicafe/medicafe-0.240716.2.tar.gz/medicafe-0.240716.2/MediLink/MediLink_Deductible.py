"""
# Create a summary JSON
summary = {
    "Payer ID": ins_payerID,
    "Provider": provider_last_name,
    "Member ID": ins_memberID,
    "Date of Birth": dob,
    "Patient Name": patient_name,
    "Patient Info": {
        "DOB": dob,
        "Address": "{} {}".format(patient_info.get("addressLine1", ""), patient_info.get("addressLine2", "")).strip(),
        "City": patient_info.get("city", ""),
        "State": patient_info.get("state", ""),
        "ZIP": patient_info.get("zip", ""),
        "Relationship": patient_info.get("relationship", "")
    },
    "Insurance Info": {
        "Payer Name": insurance_info.get("payerName", ""),
        "Payer ID": ins_payerID,
        "Member ID": ins_memberID,
        "Group Number": insurance_info.get("groupNumber", ""),
        "Insurance Type": ins_insuranceType,
        "Type Code": ins_insuranceTypeCode,
        "Address": "{} {}".format(insurance_info.get("addressLine1", ""), insurance_info.get("addressLine2", "")).strip(),
        "City": insurance_info.get("city", ""),
        "State": insurance_info.get("state", ""),
        "ZIP": insurance_info.get("zip", "")
    },
    "Policy Info": {
        "Eligibility Dates": eligibilityDates,
        "Policy Member ID": policy_info.get("memberId", ""),
        "Policy Status": policy_status
    },
    "Deductible Info": {
        "Remaining Amount": remaining_amount
    }
}

# Print debug JSON
# Uncomment below if you need to debug later
# print("\nDebug JSON Summary:")
# print(json.dumps(summary, indent=2))
"""
import MediLink_API_v3
import os
import sys
from datetime import datetime
import requests
import json

try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

try:
    from MediBot import MediBot_Preprocessor_lib
except ImportError:
    import MediBot_Preprocessor_lib

# Load configuration
config, _ = MediLink_ConfigLoader.load_configuration()

# Initialize the API client
client = MediLink_API_v3.APIClient()

# Get provider_last_name and npi from configuration
provider_last_name = config['MediLink_Config'].get('default_billing_provider_last_name')
npi = config['MediLink_Config'].get('default_billing_provider_npi')

# Define the list of payer_id's to iterate over
payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '06111', '37602']

# Get the latest CSV
CSV_FILE_PATH = config.get('CSV_FILE_PATH', "")
csv_data = MediBot_Preprocessor_lib.load_csv_data(CSV_FILE_PATH)

# Only keep rows that contain a valid number from the payer_ids list
valid_rows = [row for row in csv_data if str(row['Ins1 Payer ID']) in payer_ids]

# Function to check if the date format is correct
def validate_and_format_date(date_str):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%d-%m-%Y'):
        try:
            formatted_date = datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            return formatted_date
        except ValueError:
            continue
    return None

# List of patients with DOB and MemberID from CSV data
patients = [
    (validate_and_format_date(row['Patient DOB']), row['Primary Policy Number']) 
    for row in valid_rows if validate_and_format_date(row['Patient DOB']) is not None
]

# Function to get eligibility information
def get_eligibility_info(client, payer_id, provider_last_name, date_of_birth, member_id, npi):
    try:
        # Log the parameters being sent to the function
        MediLink_ConfigLoader.log("Calling get_eligibility_v3 with parameters:", level="INFO")
        MediLink_ConfigLoader.log("payer_id: {}".format(payer_id), level="INFO")
        MediLink_ConfigLoader.log("provider_last_name: {}".format(provider_last_name), level="INFO")
        MediLink_ConfigLoader.log("date_of_birth: {}".format(date_of_birth), level="INFO")
        MediLink_ConfigLoader.log("member_id: {}".format(member_id), level="INFO")
        MediLink_ConfigLoader.log("npi: {}".format(npi), level="INFO")

        # Call the get_eligibility_v3 function
        eligibility = MediLink_API_v3.get_eligibility_v3(
            client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
        )
        
        # Log the response
        MediLink_ConfigLoader.log("Eligibility response: {}".format(json.dumps(eligibility, indent=4)), level="INFO")
        
        return eligibility
    except requests.exceptions.HTTPError as e:
        # Log the HTTP error response
        MediLink_ConfigLoader.log("HTTPError: {}".format(e), level="ERROR")
        MediLink_ConfigLoader.log("Response content: {}".format(e.response.content), level="ERROR")
    except Exception as e:
        # Log any other exceptions
        MediLink_ConfigLoader.log("Error: {}".format(e), level="ERROR")
    return None

# Function to extract required fields and display in a tabular format
def display_eligibility_info(data, dob, member_id):
    if data is None:
        return

    for policy in data["memberPolicies"]:
        # Skip non-medical policies
        if policy["policyInfo"]["coverageType"] != "Medical":
            continue

        patient_info = policy["patientInfo"][0]
        lastName = patient_info.get("lastName", "")
        firstName = patient_info.get("firstName", "")
        middleName = patient_info.get("middleName", "")

        # Check if the remaining amount is per individual first, then fallback to family
        if 'individual' in policy["deductibleInfo"]:
            remaining_amount = policy["deductibleInfo"]["individual"]["inNetwork"].get("remainingAmount", "")
        else:
            remaining_amount = policy["deductibleInfo"]["family"]["inNetwork"].get("remainingAmount", "")

        insurance_info = policy["insuranceInfo"]
        ins_insuranceType = insurance_info.get("insuranceType", "")
        ins_insuranceTypeCode = insurance_info.get("insuranceTypeCode", "")
        ins_memberID = insurance_info.get("memberId", "")
        ins_payerID = insurance_info.get("payerId", "")

        policy_info = policy["policyInfo"]
        eligibilityDates = policy_info.get("eligibilityDates", "")
        policy_status = policy_info.get("policyStatus", "")

        patient_name = "{} {} {}".format(firstName, middleName, lastName).strip()[:20]

        # Display patient information in a table row format
        eligibility_end_date = eligibilityDates.get("endDate", "")
        table_row = "{:<20} | {:<10} | {:<5} | {:<30}".format(
            patient_name, dob, ins_payerID, ins_insuranceType)
        print(table_row)
        table_row_details = "{:<20} | {:<10} | {:<5} | {:<15} | {:<8} | {:<15} | {:<20}".format(
            "", "", "", ins_insuranceTypeCode, eligibility_end_date[-10:], policy_status, remaining_amount)
        print(table_row_details)

# Print the table header once before entering the loop
table_header = "{:<20} | {:<10} | {:<5} | {:<30}".format(
    "Patient Name", "DOB", "Payer ID", "Insurance Type")
print(table_header)
print("-" * len(table_header))
sub_header = "{:<20} | {:<10} | {:<5} | {:<15} | {:<8} | {:<15} | {:<20}".format(
    "", "", "", "Type Code", "End Date", "Policy Status", "Remaining Amount")
print(sub_header)
print("-" * len(sub_header))

# Set to keep track of processed patients
processed_patients = set()

# Loop through each payer_id and patient to call the API, then display the eligibility information
errors = []
for payer_id in payer_ids:
    for dob, member_id in patients:
        # Skip if this patient has already been processed
        if (dob, member_id) in processed_patients:
            continue
        try:
            eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, dob, member_id, npi)
            if eligibility_data is not None:
                display_eligibility_info(eligibility_data, dob, member_id)  # Display as we get the result
                processed_patients.add((dob, member_id))  # Mark this patient as processed
        except Exception as e:
            errors.append((dob, member_id, str(e)))

# Display errors if any
if errors:
    print("\nErrors encountered during API calls:")
    for error in errors:
        print("DOB: {}, Member ID: {}, Error: {}".format(error[0], error[1], error[2]))