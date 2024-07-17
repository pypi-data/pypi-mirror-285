# MediLink_DataMgmt.py
import csv
import os
from datetime import datetime, timedelta
import re
import subprocess 

# Need this for running Medibot and MediLink
try:
    import MediLink_ConfigLoader
    import MediLink_UI
except ImportError:
    from . import MediLink_ConfigLoader
    from . import MediLink_UI

# Helper function to slice and strip values with optional key suffix
def slice_data(data, slices, suffix=''):
    # Convert slices list to a tuple for slicing operation
    return {key + suffix: data[slice(*slices[key])].strip() for key in slices}

# Function to parse fixed-width Medisoft output and extract claim data
def parse_fixed_width_data(personal_info, insurance_info, service_info, service_info_2=None, service_info_3=None, config=None):
    
    # Make sure we have the right config
    if not config:  # Checks if config is None or an empty dictionary
        MediLink_ConfigLoader.log("No config passed to parse_fixed_width_data. Re-loading config...", level="WARNING")
        config, _ = MediLink_ConfigLoader.load_configuration()
    
    config = config.get('MediLink_Config', config) # Safest config call.
    
    # Load slice definitions from config within the MediLink_Config section
    personal_slices = config['fixedWidthSlices']['personal_slices']
    insurance_slices = config['fixedWidthSlices']['insurance_slices']
    service_slices = config['fixedWidthSlices']['service_slices']

    # Parse each segment
    parsed_data = {}
    parsed_data.update(slice_data(personal_info, personal_slices))
    parsed_data.update(slice_data(insurance_info, insurance_slices))
    parsed_data.update(slice_data(service_info, service_slices))
    
    if service_info_2:
        parsed_data.update(slice_data(service_info_2, service_slices, suffix='_2'))
    
    if service_info_3:
        parsed_data.update(slice_data(service_info_3, service_slices, suffix='_3'))
    
    MediLink_ConfigLoader.log("Successfully parsed data from segments", config, level="INFO")
    
    return parsed_data

# Function to read fixed-width Medisoft output and extract claim data
def read_fixed_width_data(file_path):
    # Reads the fixed width data from the file and yields each patient's
    # personal, insurance, and service information.
    MediLink_ConfigLoader.log("Starting to read fixed width data...")
    with open(file_path, 'r') as file:
        lines_buffer = []  # Buffer to hold lines for current patient data
        
        def yield_record(buffer):
            personal_info = buffer[0]
            insurance_info = buffer[1]
            service_info = buffer[2]
            service_info_2 = buffer[3] if len(buffer) > 3 else None
            service_info_3 = buffer[4] if len(buffer) > 4 else None
            MediLink_ConfigLoader.log("Successfully read data from file: {}".format(file_path), level="INFO")
            return personal_info, insurance_info, service_info, service_info_2, service_info_3
        
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                lines_buffer.append(stripped_line)
                if 3 <= len(lines_buffer) <= 5:
                    next_line = file.readline().strip()
                    if not next_line:
                        yield yield_record(lines_buffer)
                        lines_buffer.clear()
            else:
                if len(lines_buffer) >= 3:
                    yield yield_record(lines_buffer)
                    lines_buffer.clear()
                    
        if lines_buffer:  # Yield any remaining buffer if file ends without a blank line
            yield yield_record(lines_buffer)

# TODO (Refactor) Consider consolidating with the other read_fixed_with_data 
def read_general_fixed_width_data(file_path, slices):
    # handle any fixed-width data based on provided slice definitions
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)  # Skip the header
        for line_number, line in enumerate(file, start=1):
            insurance_name = {key: line[start:end].strip() for key, (start, end) in slices.items()}
            yield insurance_name, line_number

def consolidate_csvs(source_directory, file_prefix="Consolidated", interactive=False):
    """
    Consolidate CSV files in the source directory into a single CSV file.
    
    Parameters:
        source_directory (str): The directory containing the CSV files to consolidate.
        file_prefix (str): The prefix for the consolidated file's name.
        interactive (bool): If True, prompt the user for confirmation before overwriting existing files.
    
    Returns:
        str: The filepath of the consolidated CSV file, or None if no files were consolidated.
    """
    today = datetime.now()
    consolidated_filename = "{}_{}.csv".format(file_prefix, today.strftime("%m%d%y"))
    consolidated_filepath = os.path.join(source_directory, consolidated_filename)

    consolidated_data = []
    header_saved = False
    expected_header = None

    # Check if the file already exists and log the action
    if os.path.exists(consolidated_filepath):
        MediLink_ConfigLoader.log("The file {} already exists. It will be overwritten.".format(consolidated_filename), level="INFO")
        if interactive:
            overwrite = input("The file {} already exists. Do you want to overwrite it? (y/n): ".format(consolidated_filename)).strip().lower()
            if overwrite != 'y':
                MediLink_ConfigLoader.log("User opted not to overwrite the file {}.".format(consolidated_filename), level="INFO")
                return None

    for filename in os.listdir(source_directory):
        filepath = os.path.join(source_directory, filename)
        if not filepath.endswith('.csv') or os.path.isdir(filepath) or filepath == consolidated_filepath:
            continue  # Skip non-CSV files, directories, and the target consolidated file itself

        # Check if the file was created within the last day
        modification_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if modification_time < today - timedelta(days=1):
            continue  # Skip files not modified in the last day

        try:
            with open(filepath, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Read the header
                if not header_saved:
                    expected_header = header
                    consolidated_data.append(header)
                    header_saved = True
                elif header != expected_header:
                    MediLink_ConfigLoader.log("Header mismatch in file {}. Skipping file.".format(filepath), level="WARNING")
                    continue

                consolidated_data.extend(row for row in reader)
        except StopIteration:
            MediLink_ConfigLoader.log("File {} is empty or contains only header. Skipping file.".format(filepath), level="WARNING")
            continue
        except Exception as e:
            MediLink_ConfigLoader.log("Error processing file {}: {}".format(filepath, e), level="ERROR")
            continue

        os.remove(filepath)
        MediLink_ConfigLoader.log("Deleted source file after consolidation: {}".format(filepath), level="INFO")

    if consolidated_data:
        with open(consolidated_filepath, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(consolidated_data)
        MediLink_ConfigLoader.log("Consolidated CSVs into {}".format(consolidated_filepath), level="INFO")
        return consolidated_filepath
    else:
        MediLink_ConfigLoader.log("No valid CSV files were found for consolidation.", level="INFO")
        return None

def operate_winscp(operation_type, files, endpoint_config, local_storage_path, config):
    """
    General function to operate WinSCP for uploading or downloading files.

    :param operation_type: 'upload' or 'download'
    :param files: List of files to upload or pattern for files to download.
    :param endpoint_config: Dictionary containing endpoint configuration.
    :param local_storage_path: Base local storage path for logs and files.

    # Example of how to call this function for uploads
    upload_files = ['path/to/local/file1.txt', 'path/to/local/file2.txt']
    upload_config = {
        'session_name': 'MySession',
        'remote_directory_up': '/remote/upload/path'
    }

    operate_winscp('upload', upload_files, upload_config, 'path/to/local/storage', config)

    # Example of how to call this function for downloads
    download_config = {
        'session_name': 'MySession',
        'remote_directory_down': '/remote/download/path'
    }

    operate_winscp('download', None, download_config, 'path/to/local/storage', config)
    """
    # Setup paths
    try:
        # TODO (Easy / Config) Get this updated. ??
        winscp_path = config['winscp_path']
    except KeyError:
        winscp_path = os.path.join(os.getcwd(), "Installers", "WinSCP-Portable", "WinSCP.com")
    except Exception as e:
        # Handle any other exceptions here
        print("An error occurred while running WinSCP:", e)
        winscp_path = None
        
    if not os.path.isfile(winscp_path):
        MediLink_ConfigLoader.log("WinSCP.com not found at {}".format(winscp_path))
        return []

    # Setup logging
    log_filename = "winscp_upload.log" if operation_type == "upload" else "winscp_download.log"
    winscp_log_path = os.path.join(local_storage_path, log_filename)

    # Session and directory setup
    try:
        session_name = endpoint_config.get('session_name', '')
        if operation_type == "upload":
            remote_directory = endpoint_config['remote_directory_up']
        else:
            remote_directory = endpoint_config['remote_directory_down']
    except KeyError as e:
        # Log the missing key information
        missing_key = str(e)
        message = "KeyError: Endpoint config is missing key: {}".format(missing_key)
        MediLink_ConfigLoader.log(message)
        # Set default values or handle the situation accordingly
        session_name = ''
        remote_directory = ''
    # Command building
    command = [
        winscp_path,
        '/log=' + winscp_log_path,
        '/loglevel=1',
        '/command',
        'open {}'.format(session_name),
        'cd /',
        'cd {}'.format(remote_directory)
    ]

    # Add commands to WinSCP script
    # BUG (Low SFTP) We really need to fix this path situation.
    #  Unfortunately, this just needs to be a non-spaced path because WinSCP can't
    #  handle the spaces. Also, Windows won't let me use shutil to move the files out of G:\ into C:\ and it it wants an administrator security 
    #  check or verification thing for me to even move the file by hand so that doesn't work either. 
    #  command.append("put {}".format("C:\\Z_optumedi_04161742.txt"))
    if operation_type == "upload":
        for file_path in files:
            normalized_path = os.path.normpath(file_path)
            command.append("put {}".format(normalized_path))
    else:
        command.append('get *')  # Adjust pattern as needed

    command += ['close', 'exit']

    # Check if TestMode is enabled in the configuration
    if config.get("MediLink_Config", {}).get("TestMode", True):
        # TestMode is enabled, do not execute the command
        print("Test Mode is enabled! WinSCP Command not executed.")
        MediLink_ConfigLoader.log("Test Mode is enabled! WinSCP Command not executed.")
        MediLink_ConfigLoader.log("TEST MODE: Simulating WinSCP {} File List.".format(operation_type))
        uploaded_files = []
        if files is not None:  # Check if files is not None
            for file_path in files:
                normalized_path = os.path.normpath(file_path)
                if os.path.exists(normalized_path):  # Check if the file exists before appending
                    uploaded_files.append(normalized_path)
                else:
                    MediLink_ConfigLoader.log("TEST MODE: Failed to {} file: {} does not exist.".format(operation_type, normalized_path))
        else:
            MediLink_ConfigLoader.log("TEST MODE: No files to upload.")
        return uploaded_files if files is not None else []
    else:
        # TestMode is not enabled, execute the command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate()
    
    if process.returncode == 0: # BUG Does this work as intended?
        MediLink_ConfigLoader.log("WinSCP {} attempted.".format(operation_type))
        # Construct a list of downloaded files if operation_type is 'download'
        if operation_type == 'download':
            downloaded_files = []
            for root, dirs, files in os.walk(local_storage_path):
                for file in files:
                    downloaded_files.append(os.path.join(root, file))
            return downloaded_files
        
        if operation_type == 'upload':
            # Return a list of uploaded files
            uploaded_files = []
            for file_path in files:
                normalized_path = os.path.normpath(file_path)
                if os.path.exists(normalized_path):  # Check if the file exists before appending
                    uploaded_files.append(normalized_path)
                else:
                    MediLink_ConfigLoader.log("Failed to upload file: {} does not exist.".format(normalized_path))
            return uploaded_files
    else:
        MediLink_ConfigLoader.log("Failed to {} files. Details: {}".format(operation_type, stderr.decode('utf-8')))
        return []  # Return empty list to indicate failure. BUG check to make sure this doesn't break something else.

def detect_new_files(directory_path, file_extension='.DAT'):
    """
    Scans the specified directory for new files with a given extension and adds a timestamp if needed.
    
    :param directory_path: Path to the directory containing files to be detected.
    :param file_extension: Extension of the files to detect.
    :return: A tuple containing a list of paths to new files detected in the directory and a flag indicating if a new file was just renamed.
    """
    MediLink_ConfigLoader.log("Scanning directory: {}".format(directory_path), level="INFO")
    detected_file_paths = []
    file_flagged = False
    
    try:
        filenames = os.listdir(directory_path)
        MediLink_ConfigLoader.log("Files in directory: {}".format(filenames), level="INFO")
        
        for filename in filenames:
            MediLink_ConfigLoader.log("Checking file: {}".format(filename), level="INFO")
            if filename.endswith(file_extension):
                MediLink_ConfigLoader.log("File matches extension: {}".format(file_extension), level="INFO")
                name, ext = os.path.splitext(filename)
                MediLink_ConfigLoader.log("File name: {}, File extension: {}".format(name, ext), level="INFO")
                
                if not is_timestamped(name):
                    MediLink_ConfigLoader.log("File is not timestamped: {}".format(filename), level="INFO")
                    new_name = "{}_{}{}".format(name, datetime.now().strftime('%Y%m%d_%H%M%S'), ext)
                    os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_name))
                    MediLink_ConfigLoader.log("Renamed file from {} to {}".format(filename, new_name), level="INFO")
                    file_flagged = True
                    filename = new_name
                else:
                    MediLink_ConfigLoader.log("File is already timestamped: {}".format(filename), level="INFO")
                
                file_path = os.path.join(directory_path, filename)
                detected_file_paths.append(file_path)
                MediLink_ConfigLoader.log("Detected file path: {}".format(file_path), level="INFO")
    
    except Exception as e:
        MediLink_ConfigLoader.log("Error occurred: {}".format(str(e)), level="INFO")
    
    MediLink_ConfigLoader.log("Detected files: {}".format(detected_file_paths), level="INFO")
    MediLink_ConfigLoader.log("File flagged status: {}".format(file_flagged), level="INFO")
    
    return detected_file_paths, file_flagged

def is_timestamped(name):
    """
    Checks if the given filename has a timestamp in the expected format.
    
    :param name: The name of the file without extension.
    :return: True if the filename includes a timestamp, False otherwise.
    """
    # Regular expression to match timestamps in the format YYYYMMDD_HHMMSS
    timestamp_pattern = re.compile(r'.*_\d{8}_\d{6}$')
    return bool(timestamp_pattern.match(name))

def organize_patient_data_by_endpoint(detailed_patient_data):
    """
    Organizes detailed patient data by their confirmed endpoints.
    This simplifies processing and conversion per endpoint basis, ensuring that claims are generated and submitted
    according to the endpoint-specific requirements.

    :param detailed_patient_data: A list of dictionaries, each containing detailed patient data including confirmed endpoint.
    :return: A dictionary with endpoints as keys and lists of detailed patient data as values for processing.
    """
    organized = {}
    for data in detailed_patient_data:
        # Retrieve confirmed endpoint from each patient's data
        endpoint = data['confirmed_endpoint'] if 'confirmed_endpoint' in data else data['suggested_endpoint']
        # Initialize a list for the endpoint if it doesn't exist
        if endpoint not in organized:
            organized[endpoint] = []
        organized[endpoint].append(data)
    return organized

def confirm_all_suggested_endpoints(detailed_patient_data):
    """
    Confirms all suggested endpoints for each patient's detailed data.
    """
    for data in detailed_patient_data:
        if 'confirmed_endpoint' not in data:
            data['confirmed_endpoint'] = data['suggested_endpoint']
    return detailed_patient_data

def bulk_edit_insurance_types(detailed_patient_data, insurance_options):
    # Allow user to edit insurance types in a table-like format with validation
    print("Edit Insurance Type (Enter the 2-character code). Enter 'LIST' to display available insurance types.")

    for data in detailed_patient_data:
        current_insurance_type = data['insurance_type']
        current_insurance_description = insurance_options.get(current_insurance_type, "Unknown")
        print("({}) {:<25} | Current Ins. Type: {} - {}".format(
            data['patient_id'], data['patient_name'], current_insurance_type, current_insurance_description))

        while True:
            new_insurance_type = input("Enter new insurance type (or press Enter to keep current): ").upper()
            if new_insurance_type == 'LIST':
                MediLink_UI.display_insurance_options(insurance_options)
            elif not new_insurance_type or new_insurance_type in insurance_options:
                if new_insurance_type:
                    data['insurance_type'] = new_insurance_type
                break
            else:
                print("Invalid insurance type. Please enter a valid 2-character code or type 'LIST' to see options.")

def review_and_confirm_changes(detailed_patient_data, insurance_options):
    # Review and confirm changes
    print("\nReview changes:")
    print("{:<20} {:<10} {:<30}".format("Patient Name", "Ins. Type", "Description"))
    print("="*65)
    for data in detailed_patient_data:
        insurance_type = data['insurance_type']
        insurance_description = insurance_options.get(insurance_type, "Unknown")
        print("{:<20} {:<10} {:<30}".format(data['patient_name'], insurance_type, insurance_description))
    confirm = input("\nConfirm changes? (y/n): ").strip().lower()
    return confirm in ['y', 'yes', '']