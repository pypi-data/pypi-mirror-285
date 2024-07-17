from datetime import datetime
import os
import re
import subprocess
from tqdm import tqdm
import MediLink_837p_encoder
from MediLink_ConfigLoader import log
from MediLink_DataMgmt import operate_winscp

# Internet Connectivity Check
def check_internet_connection():
    """
    Checks if there is an active internet connection.
    Returns: Boolean indicating internet connectivity status.
    """
    try:
        # Run a ping command to a reliable external server (e.g., Google's DNS server)
        ping_process = subprocess.Popen(["ping", "-n", "1", "8.8.8.8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_output, ping_error = ping_process.communicate()

        # Check if the ping was successful
        if "Reply from" in ping_output.decode("utf-8"):
            return True
        else:
            return False
    except Exception as e:
        print("An error occurred checking for internet connectivity:", e)
        return False

def submit_claims(detailed_patient_data_grouped_by_endpoint, config):
    # Accumulate submission results
    submission_results = {}
    
    if not detailed_patient_data_grouped_by_endpoint:
        print("No new files detected for submission.")
        return

    # Wrap the iteration with tqdm for a progress bar
    for endpoint, patients_data in tqdm(detailed_patient_data_grouped_by_endpoint.items(), desc="Progress", unit="endpoint"):
        if not patients_data:  # Skip if no patient data for the endpoint
            continue

        # Attempt submission to each endpoint
        if True: #confirm_transmission({endpoint: patients_data}): # Confirm transmission to each endpoint with detailed overview
            if check_internet_connection():
                # Process files per endpoint
                converted_files = MediLink_837p_encoder.convert_files_for_submission(patients_data, config)
                if converted_files:  # Check if files were successfully converted
                    # Transmit files per endpoint
                    try:
                        operation_type = "upload"
                        transmission_result = operate_winscp(operation_type, converted_files, config['MediLink_Config']['endpoints'][endpoint], config['MediLink_Config']['local_claims_path'], config)
                        success_dict = handle_transmission_result(transmission_result, config, operation_type)
                        submission_results[endpoint] = success_dict
                        # TODO Future work: Availity SentFiles: Retrieve and interpret the response file from Availity SentFiles to acknowledge successful transfers.
                    except FileNotFoundError as e:
                        # Log that the log file is not found
                        print("Failed to transmit files to {0}. Error: Log file not found - {1}".format(endpoint, str(e)))
                        submission_results[endpoint] = {"status": False, "error": "Log file not found - " + str(e)}

                    except IOError as e:
                        # Log IO errors
                        print("Failed to transmit files to {0}. Error: Input/output error - {1}".format(endpoint, str(e)))
                        submission_results[endpoint] = {"status": False, "error": "Input/output error - " + str(e)}

                    except Exception as e:
                        # Log other exceptions
                        print("Failed to transmit files to {0}. Error: {1}".format(endpoint, str(e)))
                        submission_results[endpoint] = {"status": False, "error": str(e)}
                else:
                    
                    print("No files were converted for transmission to {0}.".format(endpoint))
            else:
                print("Error: No internet connection detected.")
                log("Error: No internet connection detected.", level="ERROR")
                try_again = input("Do you want to try again? (Y/N): ").strip().lower()
                if try_again != 'y':
                    print("Exiting transmission process. Please try again later.")
                    return  # Exiting the function if the user decides not to retry
        else:
            print("Transmission canceled for endpoint {0}.".format(endpoint))
        
        # Continue to next endpoint regardless of the previous outcomes

    # Build and display receipt
    build_and_display_receipt(submission_results, config)
    
    print("Claim submission process completed.\n")    

def handle_transmission_result(transmission_result, config, operation_type):
    """
    Analyze the outcomes of file transmissions based on WinSCP log entries.
    
    :param transmission_result: List of paths for files that were attempted to be transmitted.
    :param config: Configuration dictionary containing paths and settings.
    :return: Dictionary mapping each file path to a boolean indicating successful transmission.
    """
    log_filename = "winscp_{}.log".format(operation_type)
    
    # BUG local_claims_path is where the uploads are only. this needs to have a switch. Check where WinSCP actually logs though.
    log_path = os.path.join(config['MediLink_Config']['local_claims_path'], log_filename)
    success_dict = {}

    try:
        with open(log_path, 'r') as log_file:
            log_contents = log_file.readlines()

        log("WinSCP Log file opened and contents read successfully.")

        if log_contents is None:
            log("Unexpected NoneType for log_contents")
        elif not log_contents:
            log("Log file '{}' is empty.".format(log_path))
            success_dict = {file_path: False for file_path in transmission_result}
        else:
            last_lines = log_contents[-15:]
            log("Processing the last {} lines of the log file.".format(len(last_lines)))
            for file_path in transmission_result:
                if file_path is None:
                    log("Error: NoneType file path found in transmission results.")
                    continue
                try:
                    success_message = "Transfer done: '{}'".format(file_path)
                    log("Looking for: {} in WinSCP log.".format(success_message))
                    success = any(success_message in line for line in last_lines)
                    log("Validation: {0} - Transfer done for file: {1}".format(success, file_path))
                    success_dict[file_path] = success
                except TypeError as e:
                    log("TypeError during processing file path '{}': {}".format(file_path, e))
            log("Completed WinSCP log verification check.")

    except FileNotFoundError:
        log("Log file '{}' not found.".format(log_path))
        success_dict = {file_path: False for file_path in transmission_result}

    except IOError as e:
        log("IO error when handling the log file '{}': {}".format(log_path, e))
        success_dict = {file_path: False for file_path in transmission_result}

    except Exception as e:
        log("Error processing the transmission log: {}".format(e))
        success_dict = {file_path: False for file_path in transmission_result}

    return success_dict

def build_and_display_receipt(submission_results, config):
    """
    Define Submission Receipt:

    A receipt of submitted claims is typically attached to each printed facesheet for recordkeeping confirming submission.

    input: accumulated success_dict
    (historical record won't work because the winscp logs will be incomplete, use clearinghouse to check historical records.)

    2.) Parse each of the 837p files from filepaths in success_dict:
    
    Note: each file will only have one receiver name and one date & time of submission. The dictionary should be organized such that the receiver name (for that file) is the key for a list of patients with patient data.

    output: print to screen a pretty ASCII human-readable organized 'receipt' by receiver name using the dictionary data, then dump to a notepad called Receipt_[date of submission].txt at config[MediLink_Config][local_storage_path] and subprocess open the file to the user to see.
    """
    # Prepare data for receipt
    # Organize submission results into a format suitable for the receipt
    log("Preparing receipt data...")
    receipt_data = prepare_receipt_data(submission_results)

    # Build the receipt
    receipt_content = build_receipt_content(receipt_data)

    # Print the receipt to the screen
    log("Printing receipt...")
    print(receipt_content)

    # Save the receipt to a text file
    save_receipt_to_file(receipt_content, config)
    
    # Probably return receipt_data since its the easier to use dictionary
    return receipt_data

def prepare_receipt_data(submission_results):
    """
    Prepare submission results for a receipt, including data from both successful and failed submissions.
    
    This function extracts patient names, dates of service, amounts billed, and insurance names from an 837p file.
    It also includes the date and time of batch claim submission, and the receiver name from the 1000B segment.
    Data is organized by receiver name and includes both successful and failed submissions.
    
    Parameters:
    - submission_results (dict): Contains submission results grouped by endpoint, with success status.
    
    Returns:
    - dict: Organized data for receipt preparation, including both successful and failed submission details.
    """
    receipt_data = {}
    for endpoint, files in submission_results.items():
        for file_path, success in files.items():
            # Parse the 837p file for patient data, regardless of success.
            patient_data, date_of_submission = parse_837p_file(file_path)
            
            if endpoint not in receipt_data:
                receipt_data[endpoint] = {
                    "date_of_submission": date_of_submission,
                    "patients": []
                }

            # Enhance patient data with success status
            for patient in patient_data:
                patient['status'] = success
            
            receipt_data[endpoint]["patients"].extend(patient_data)
    
    validate_data(receipt_data)
    return receipt_data

def validate_data(receipt_data):
    # Simple validation to check if data fields are correctly populated
    for endpoint, data in receipt_data.items():
        patients = data.get("patients", [])
        for index, patient in enumerate(patients, start=1):
            missing_fields = [field for field in ('name', 'service_date', 'amount_billed', 'insurance_name', 'status') if not patient.get(field)]
            
            if missing_fields:
                # Log the missing fields without revealing PHI
                log("Receipt Data validation error for endpoint '{}', patient {}: Missing information in fields: {}".format(endpoint, index, ", ".join(missing_fields)))
    return True

def parse_837p_file(file_path):
    """
    Parse an 837p file to extract patient details and date of submission.

    This function reads the specified 837p file, extracts patient details such as name, service date, and amount billed,
    and retrieves the date of submission from the GS segment. It then organizes this information into a list of dictionaries
    containing patient data. If the GS segment is not found, it falls back to using the current date and time.

    Parameters:
    - file_path (str): The path to the 837p file to parse.

    Returns:
    - tuple: A tuple containing two elements:
        - A list of dictionaries, where each dictionary represents patient details including name, service date, and amount billed.
        - A string representing the date and time of submission in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    patient_details = []
    date_of_submission = None
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            log("Parsing submitted 837p...")

            # Extract the submission date from the GS segment
            gs_match = re.search(r'GS\*HC\*[^*]*\*[^*]*\*([0-9]{8})\*([0-9]{4})', content)
            if gs_match:
                date = gs_match.group(1)
                time = gs_match.group(2)
                date_of_submission = datetime.strptime("{}{}".format(date, time), "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Fallback to the current date and time if GS segment is not found
                date_of_submission = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Split content using 'SE*{count}*{control_number}~' as delimiter
            patient_records = re.split(r'SE\*\d+\*\d{4}~', content)
            
            # Remove any empty strings from list that may have been added from split
            patient_records = [record for record in patient_records if record.strip()]
            
            for record in patient_records:
                # Extract patient name
                name_match = re.search(r'NM1\*IL\*1\*([^*]+)\*([^*]+)\*([^*]*)', record)
                # Extract service date
                service_date_match = re.search(r'DTP\*472\D*8\*([0-9]{8})', record)
                # Extract claim amount
                amount_match = re.search(r'CLM\*[^\*]*\*([0-9]+\.?[0-9]*)', record)
                # Extract insurance name (payer_name)
                insurance_name_match = re.search(r'NM1\*PR\*2\*([^*]+)\*', record)
                
                if name_match and service_date_match and amount_match:
                    # Handle optional middle name
                    middle_name = name_match.group(3).strip() if name_match.group(3) else ""
                    patient_name = "{} {} {}".format(name_match.group(2), middle_name, name_match.group(1)).strip()
                    service_date = "{}-{}-{}".format(service_date_match.group(1)[:4], service_date_match.group(1)[4:6], service_date_match.group(1)[6:])
                    amount_billed = float(amount_match.group(1))
                    insurance_name = insurance_name_match.group(1)
                    
                    patient_details.append({
                        "name": patient_name,
                        "service_date": service_date,
                        "amount_billed": amount_billed,
                        "insurance_name": insurance_name
                    })
    except Exception as e:
        print("Error reading or parsing the 837p file: {0}".format(str(e)))
    
    return patient_details, date_of_submission

def build_receipt_content(receipt_data):
    """
    Build the receipt content in a human-readable ASCII format with a tabular data presentation for patient information.

    Args:
        receipt_data (dict): Dictionary containing receipt data with patient details.

    Returns:
        str: Formatted receipt content as a string.
    """
    # Build the receipt content in a human-readable ASCII format
    receipt_lines = ["Submission Receipt", "=" * 60, ""]  # Header

    for endpoint, data in receipt_data.items():
        header = "Endpoint: {0} (Submitted: {1})".format(endpoint, data['date_of_submission'])
        receipt_lines.extend([header, "-" * len(header)])
        
        # Table headers
        table_header = "{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format("Patient", "Service Date", "Amount Billed", "Insurance", "Status")
        receipt_lines.append(table_header)
        receipt_lines.append("-" * len(table_header))
        
        # Adding patient information in a tabular format
        for patient in data["patients"]:
            success_status = "SUCCESS" if patient['status'] else "FAILED"
            patient_info = "{:<20} | {:<15} | ${:<14} | {:<20} | {:<10}".format(
                patient['name'], 
                patient['service_date'], 
                patient['amount_billed'], 
                patient['insurance_name'], 
                success_status
            )
            receipt_lines.append(patient_info)
        
        receipt_lines.append("")  # Blank line for separation
    
    receipt_content = "\n".join(receipt_lines)
    return receipt_content

def save_receipt_to_file(receipt_content, config):
    try:
        # Save the receipt content to a text file named Receipt_[date_of_submission].txt
        # Use the configured local storage path to determine the file location
        file_name = "Receipt_{0}.txt".format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        file_path = os.path.join(config['MediLink_Config']['local_claims_path'], file_name)
        
        with open(file_path, 'w') as file:
            file.write(receipt_content)
        
        # Open the file automatically for the user
        os.startfile(file_path)
    except Exception as e:
        print("Failed to save or open receipt file:", e)

# Secure File Transmission
def confirm_transmission(detailed_patient_data_grouped_by_endpoint):
    """
    Displays detailed patient data ready for transmission and their endpoints, 
    asking for user confirmation before proceeding.

    :param detailed_patient_data_grouped_by_endpoint: Dictionary with endpoints as keys and 
            lists of detailed patient data as values.
    :param config: Configuration settings loaded from a JSON file.
    """ 
    # Clear terminal for clarity
    os.system('cls')
    
    print("\nReview of patient data ready for transmission:")
    for endpoint, patient_data_list in detailed_patient_data_grouped_by_endpoint.items():
        print("\nEndpoint: {0}".format(endpoint))
        for patient_data in patient_data_list:
            patient_info = "({1}) {0}".format(patient_data['patient_name'], patient_data['patient_id'])
            print("- {:<33} | {:<5}, ${:<6}, {}".format(
                patient_info, patient_data['surgery_date'][:5], patient_data['amount'], patient_data['primary_insurance']))
    
    confirmation = input("\nProceed with transmission to all endpoints? (Y/N): ").strip().lower()
    return confirmation == 'y'

# Entry point if this script is run directly. Probably needs to be handled better.
if __name__ == "__main__":
    print("Please run MediLink directly.")