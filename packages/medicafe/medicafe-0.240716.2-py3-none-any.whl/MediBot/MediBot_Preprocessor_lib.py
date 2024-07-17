from collections import OrderedDict, defaultdict
from datetime import datetime
import os
import csv
import sys

# Add parent directory of the project to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

try:
    import MediLink_ConfigLoader
    import MediLink_DataMgmt
except ImportError:
    from MediLink import MediLink_ConfigLoader
    from MediLink import MediLink_DataMgmt
    
try:
    from MediBot_UI import app_control
    from MediBot_docx_decoder import parse_docx
except ImportError:
    from MediBot import MediBot_UI
    app_control = MediBot_UI.app_control
    from MediBot import MediBot_docx_decoder
    parse_docx = MediBot_docx_decoder.parse_docx

class InitializationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def initialize(config):
    global AHK_EXECUTABLE, CSV_FILE_PATH, field_mapping, page_end_markers
    
    try:
        AHK_EXECUTABLE = config.get('AHK_EXECUTABLE', "")
    except AttributeError:
        raise InitializationError("Error: 'AHK_EXECUTABLE' not found in config.")
    
    try:
        CSV_FILE_PATH = config.get('CSV_FILE_PATH', "")
    except AttributeError:
        raise InitializationError("Error: 'CSV_FILE_PATH' not found in config.")
    
    try:
        field_mapping = OrderedDict(config.get('field_mapping', {}))
    except AttributeError:
        raise InitializationError("Error: 'field_mapping' not found in config.")
    
    try:
        page_end_markers = config.get('page_end_markers', [])
    except AttributeError:
        raise InitializationError("Error: 'page_end_markers' not found in config.")


def open_csv_for_editing(csv_file_path):
    try:
        # Open the CSV file with its associated application
        os.system('start "" "{}"'.format(csv_file_path))
        print("After saving the revised CSV, please re-run MediBot.")
    except Exception as e:
        print("Failed to open CSV file:", e)
        
# Function to load and process CSV data
def load_csv_data(csv_file_path):
    try:
        # Check if the file exists
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError("***Error: CSV file '{}' not found.".format(csv_file_path))
        
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]  # Return a list of dictionaries
    except FileNotFoundError as e:
        print(e)  # Print the informative error message
        print("Hint: Check if CSV file is located in the expected directory or specify a different path in config file.")
        print("Please correct the issue and re-run MediBot.")
        sys.exit(1)  # Halt the script
    except IOError as e:
        print("Error reading CSV file: {}. Please check the file path and permissions.".format(e))
        sys.exit(1)  # Halt the script in case of other IO errors

# CSV Pre-processor Helper functions
def add_columns(csv_data, column_headers):
    """
    Adds one or multiple columns to the CSV data.
    
    Parameters:
    csv_data (list of dict): The CSV data where each row is represented as a dictionary.
    column_headers (list of str or str): A list of column headers to be added to each row, or a single column header.
    
    Returns:
    None: The function modifies the csv_data in place.
    """
    if isinstance(column_headers, str):
        column_headers = [column_headers]
    elif not isinstance(column_headers, list):
        raise ValueError("column_headers should be a list or a string")

    for row in csv_data:
        for header in column_headers:
            row[header] = ''  # Initialize the column with empty values

# Extracting the list to a variable for future refactoring:
def filter_rows(csv_data):
    # TODO This should go to the crosswalk.
    excluded_insurance = ['AETNA', 'AETNA MEDICARE', 'HUMANA MED HMO']
    csv_data[:] = [row for row in csv_data if row.get('Patient ID', '').strip()]
    csv_data[:] = [row for row in csv_data if row.get('Primary Insurance', '').strip() not in excluded_insurance]

def convert_surgery_date(csv_data):
    for row in csv_data:
        try:
            row['Surgery Date'] = datetime.strptime(row.get('Surgery Date', ''), '%m/%d/%Y')
        except ValueError:
            row['Surgery Date'] = datetime.min  # Assign a minimum datetime value for sorting purposes

def sort_and_deduplicate(csv_data):
    # TODO we need to figure out a new logic here for doing second-eye charges. I don't know what the flow should be yet.
    csv_data.sort(key=lambda x: (x['Surgery Date'], x.get('Patient Last', '').strip()))
    unique_patients = {}
    for row in csv_data:
        patient_id = row.get('Patient ID')
        if patient_id not in unique_patients or row['Surgery Date'] < unique_patients[patient_id]['Surgery Date']:
            unique_patients[patient_id] = row
    csv_data[:] = list(unique_patients.values())
    # TODO Sorting, now that we're going to have the Surgery Schedules available, should be ordered as the patients show up on the schedule.
    # If we don't have that surgery schedule yet for some reason, we should default to the current ordering strategy.
    csv_data.sort(key=lambda x: (x['Surgery Date'], x.get('Patient Last', '').strip()))

def combine_fields(csv_data):
    for row in csv_data:
        row['Surgery Date'] = row['Surgery Date'].strftime('%m/%d/%Y')
        first_name = row.get('Patient First', '').strip()
        middle_name = row.get('Patient Middle', '').strip()
        if len(middle_name) > 1:
            middle_name = middle_name[0]  # Take only the first character
        last_name = row.get('Patient Last', '').strip()
        row['Patient Name'] = "{}, {} {}".format(last_name, first_name, middle_name).strip()
        address1 = row.get('Patient Address1', '').strip()
        address2 = row.get('Patient Address2', '').strip()
        row['Patient Street'] = "{} {}".format(address1, address2).strip()

def apply_replacements(csv_data, crosswalk):
    replacements = crosswalk.get('csv_replacements', {})
    for row in csv_data:
        for old_value, new_value in replacements.items():
            if row.get('Patient SSN', '') == old_value:
                row['Patient SSN'] = new_value
            elif row.get('Primary Insurance', '') == old_value:
                row['Primary Insurance'] = new_value
            elif row.get('Ins1 Payer ID') == old_value:
                row['Ins1 Payer ID'] = new_value

def update_insurance_ids(csv_data, crosswalk):
    for row in csv_data:
        ins1_payer_id = row.get('Ins1 Payer ID', '').strip()
        # MediLink_ConfigLoader.log("Ins1 Payer ID '{}' associated with Patient ID {}.".format(ins1_payer_id, row.get('Patient ID', "None")))
        if ins1_payer_id:
            if ins1_payer_id in crosswalk.get('payer_id', {}):
                medisoft_ids = crosswalk['payer_id'][ins1_payer_id].get('medisoft_id', [])
                if medisoft_ids:
                    medisoft_ids = [int(id) for id in medisoft_ids]
                    # TODO Try to match OpenPM's Insurance Name to get a better match
                    row['Ins1 Insurance ID'] = medisoft_ids[0] 
                    # MediLink_ConfigLoader.log("Ins1 Insurance ID '{}' used for Payer ID {} in crosswalk.".format(row.get('Ins1 Insurance ID', ''), ins1_payer_id))
            else:
                MediLink_ConfigLoader.log("Ins1 Payer ID '{}' not found in the crosswalk.".format(ins1_payer_id))
                # Create a placeholder entry in the crosswalk, need to consider the medisoft_medicare_id handling later.
                if 'payer_id' not in crosswalk:
                    crosswalk['payer_id'] = {}
                crosswalk['payer_id'][ins1_payer_id] = {
                    'medisoft_id': [],
                    'medisoft_medicare_id': [],
                    'endpoint': 'OPTUMEDI' # Default probably should be a flag for the crosswalk update function to deal with. BUG HARDCODE THERE ARE 3 of these defaults
                } 

def update_procedure_codes(csv_data):
    # Define the Medisoft shorthand to diagnostic codes dictionary
    # TODO The reverse of this will be in the crosswalk. We'll need to reverse it here for lookup.
    medisoft_to_diagnosis = {
        "25811": "H25.811",
        "25812": "H25.812",
        "2512": "H25.12",
        "2511": "H25.11",
        "529XA": "T85.29XA",
        "4301": "H43.01",
        "4302": "H43.02",
        "011X2": "H40.11X2",
        "051X3": "H40.51X3",
        "5398A": "T85.398A"
    }

    # Define the procedure codes to diagnostic codes dictionary
    procedure_to_diagnosis = {
        "00142": ["H25.811", "H25.812", "H25.12", "H25.11", "T85.29XA"],
        "00145": ["H43.01", "H43.02"],
        "00140": ["H40.11X2", "H40.51X3"]
    }

    # Reverse the dictionary for easier lookup from diagnostic code to procedure code
    diagnosis_to_procedure = {}
    for procedure_code, diagnosis_codes in procedure_to_diagnosis.items():
        for diagnosis_code in diagnosis_codes:
            diagnosis_to_procedure[diagnosis_code] = procedure_code

    # Initialize counter for updated rows
    updated_count = 0

    # Update the "Procedure Code" column in the CSV data
    for row_num, row in enumerate(csv_data, start=1):
        try:
            medisoft_code = row.get('Default Diagnosis #1', '').strip()
            diagnosis_code = medisoft_to_diagnosis.get(medisoft_code)
            if diagnosis_code:
                procedure_code = diagnosis_to_procedure.get(diagnosis_code)
                if procedure_code:
                    row['Procedure Code'] = procedure_code
                    updated_count += 1
                else:
                    row['Procedure Code'] = "Unknown"  # Or handle as appropriate
            else:
                row['Procedure Code'] = "Unknown"  # Or handle as appropriate
        except Exception as e:
            MediLink_ConfigLoader.log("In update_procedure_codes, Error processing row {}: {}".format(row_num, e), level="ERROR")

    # Log total count of updated rows
    MediLink_ConfigLoader.log("Total {} 'Procedure Code' rows updated.".format(updated_count), level="INFO")

    return True

def update_diagnosis_codes(csv_data):
    try:
        # Load configuration and crosswalk
        config, _ = MediLink_ConfigLoader.load_configuration()
        
        # Extract the local storage path from the configuration
        local_storage_path = config['MediLink_Config']['local_storage_path']
        
        # Initialize a dictionary to hold diagnosis codes from all DOCX files
        all_patient_data = {}

        # Iterate through all files in the specified directory
        for filename in os.listdir(local_storage_path):
            if filename.endswith(".docx"):
                filepath = os.path.join(local_storage_path, filename)
                MediLink_ConfigLoader.log("Processing DOCX file: {}".format(filepath), level="INFO")
                try:
                    patient_data = parse_docx(filepath)
                    for patient_id, service_dates in patient_data.items():
                        if patient_id not in all_patient_data:
                            all_patient_data[patient_id] = {}
                        for date_of_service, diagnosis_data in service_dates.items():
                            all_patient_data[patient_id][date_of_service] = diagnosis_data
                except Exception as e:
                    MediLink_ConfigLoader.log("Error parsing DOCX file {}: {}".format(filepath, e), level="ERROR")
        
        # Debug logging for all_patient_data
        MediLink_ConfigLoader.log("All patient data collected from DOCX files: {}".format(all_patient_data), level="INFO")

        # Define the diagnosis to Medisoft shorthand dictionary
        diagnosis_to_medisoft = {
            "H25.811": "25811",
            "H25.812": "25812",
            "H25.12": "2512",
            "H25.11": "2511",
            "T85.29XA": "529XA",
            "H43.01": "4301",
            "H43.02": "4302",
            "H40.11X2": "011X2",
            "H40.51X3": "051X3",
            "T85.398A": "5398A"
        }
        
        # Convert surgery dates in CSV data
        convert_surgery_date(csv_data)
        
        # Initialize counter for updated rows
        updated_count = 0

        # Update the "Default Diagnosis #1" column in the CSV data
        for row_num, row in enumerate(csv_data, start=1):
            MediLink_ConfigLoader.log("Processing row number {}.".format(row_num), level="INFO")
            patient_id = row.get('Patient ID', '').strip()
            surgery_date = row.get('Surgery Date', '')

            # Convert surgery_date to string format for lookup
            if surgery_date != datetime.min:
                surgery_date_str = surgery_date.strftime("%m-%d-%Y")
            else:
                surgery_date_str = ''

            MediLink_ConfigLoader.log("Patient ID: {}, Surgery Date: {}".format(patient_id, surgery_date_str), level="INFO")

            if patient_id in all_patient_data:
                if surgery_date_str in all_patient_data[patient_id]:
                    diagnosis_code, left_or_right_eye, femto_yes_or_no = all_patient_data[patient_id][surgery_date_str]
                    MediLink_ConfigLoader.log("Found diagnosis data for Patient ID: {}, Surgery Date: {}".format(patient_id, surgery_date_str), level="INFO")
                    
                    # Convert diagnosis code to Medisoft shorthand format.
                    defaulted_code = diagnosis_code[1:].replace('.', '')[-5:] if diagnosis_code else ''
                    medisoft_shorthand = diagnosis_to_medisoft.get(diagnosis_code, defaulted_code)
                    MediLink_ConfigLoader.log("Converted diagnosis code to Medisoft shorthand: {}".format(medisoft_shorthand), level="INFO")
                    
                    row['Default Diagnosis #1'] = medisoft_shorthand
                    updated_count += 1
                    MediLink_ConfigLoader.log("Updated row number {} with new diagnosis code.".format(row_num), level="INFO")
                else:
                    MediLink_ConfigLoader.log("No matching surgery date found for Patient ID: {} in row {}.".format(patient_id, row_num), level="INFO")
            else:
                MediLink_ConfigLoader.log("Patient ID: {} not found in DOCX data for row {}.".format(patient_id, row_num), level="INFO")

        # Log total count of updated rows
        MediLink_ConfigLoader.log("Total {} 'Default Diagnosis #1' rows updated.".format(updated_count), level="INFO")

    except Exception as e:
        message = "An error occurred while updating diagnosis codes. Please check the DOCX files and configuration: {}".format(e)
        MediLink_ConfigLoader.log(message, level="ERROR")
        print(message)

def load_data_sources(config, crosswalk):
    """Loads historical mappings from MAPAT and Carol's CSVs."""
    patient_id_to_insurance_id = load_insurance_data_from_mapat(config, crosswalk)
    if not patient_id_to_insurance_id:
        raise ValueError("Failed to load historical Patient ID to Insurance ID mappings from MAPAT.")

    payer_id_to_patient_ids = load_historical_payer_to_patient_mappings(config)
    if not payer_id_to_patient_ids:
        raise ValueError("Failed to load historical Carol's CSVs.")

    return patient_id_to_insurance_id, payer_id_to_patient_ids

def map_payer_ids_to_insurance_ids(patient_id_to_insurance_id, payer_id_to_patient_ids):
    """Maps Payer IDs to Insurance IDs based on the historical mappings."""
    payer_id_to_details = {}
    for payer_id, patient_ids in payer_id_to_patient_ids.items():
        medisoft_ids = set()
        for patient_id in patient_ids:
            if patient_id in patient_id_to_insurance_id:
                medisoft_id = patient_id_to_insurance_id[patient_id]
                medisoft_ids.add(medisoft_id)
                MediLink_ConfigLoader.log("Added Medisoft ID {} for Patient ID {} and Payer ID {}".format(medisoft_id, patient_id, payer_id))
            else:
                MediLink_ConfigLoader.log("No matching Insurance ID found for Patient ID {}".format(patient_id))
        if medisoft_ids:
            payer_id_to_details[payer_id] = {
                "endpoint": "OPTUMEDI",  # TODO Default, to be refined via API poll. There are 2 of these defaults!
                "medisoft_id": list(medisoft_ids),
                "medisoft_medicare_id": []  # Placeholder for future implementation
            }
    return payer_id_to_details

def load_insurance_data_from_mains(config):
    """
    Loads insurance data from MAINS and creates a mapping from insurance names to their respective IDs.
    This mapping is critical for the crosswalk update process to correctly associate payer IDs with insurance IDs.

    Args:
        config (dict): Configuration object containing necessary paths and parameters.

    Returns:
        dict: A dictionary mapping insurance names to insurance IDs.
    """
    # Reset config pull to make sure its not using the MediLink config key subset
    config, crosswalk = MediLink_ConfigLoader.load_configuration()
    
    # Retrieve MAINS path and slicing information from the configuration   
    # TODO (Low) For secondary insurance, this needs to be pulling from the correct MAINS (there are 2)
    # TODO (Low) Performance: There probably needs to be a dictionary proxy for MAINS that gets updated.
    mains_path = config['MAINS_MED_PATH']
    mains_slices = crosswalk['mains_mapping']['slices']
    
    # Initialize the dictionary to hold the insurance to insurance ID mappings
    insurance_to_id = {}
    
    # Read data from MAINS using a provided function to handle fixed-width data
    for record, line_number in MediLink_DataMgmt.read_general_fixed_width_data(mains_path, mains_slices):
        insurance_name = record['MAINSNAME']
        # Assuming line_number gives the correct insurance ID without needing adjustment
        insurance_to_id[insurance_name] = line_number
    
    return insurance_to_id

def load_insurance_data_from_mapat(config, crosswalk):
    """
    Loads insurance data from MAPAT and creates a mapping from patient ID to insurance ID.
    
    Args:
        config (dict): Configuration object containing necessary paths and parameters.
        crosswalk ... ADD HERE.

    Returns:
        dict: A dictionary mapping patient IDs to insurance IDs.
    """
    # Retrieve MAPAT path and slicing information from the configuration
    mapat_path = app_control.get_mapat_med_path()
    mapat_slices = crosswalk['mapat_mapping']['slices']
    
    # Initialize the dictionary to hold the patient ID to insurance ID mappings
    patient_id_to_insurance_id = {}
    
    # Read data from MAPAT using a provided function to handle fixed-width data
    for record, _ in MediLink_DataMgmt.read_general_fixed_width_data(mapat_path, mapat_slices):
        patient_id = record['MAPATPXID']
        insurance_id = record['MAPATINID']
        patient_id_to_insurance_id[patient_id] = insurance_id
        
    return patient_id_to_insurance_id

def parse_z_dat(z_dat_path, config):
    """
    Parses the Z.dat file to map Patient IDs to Insurance Names using the provided fixed-width file format.

    Args:
        z_dat_path (str): Path to the Z.dat file.
        config (dict): Configuration object containing slicing information and other parameters.

    Returns:
        dict: A dictionary mapping Patient IDs to Insurance Names.
    """
    patient_id_to_insurance_name = {}

    try:
        # Reading blocks of fixed-width data (up to 5 lines per record)
        for personal_info, insurance_info, service_info, service_info_2, service_info_3 in MediLink_DataMgmt.read_fixed_width_data(z_dat_path):
            # Parsing the data using slice definitions from the config
            parsed_data = MediLink_DataMgmt.parse_fixed_width_data(personal_info, insurance_info, service_info, service_info_2, service_info_3, config.get('MediLink_Config', config))

            # Extract Patient ID and Insurance Name from parsed data
            patient_id = parsed_data.get('PATID')
            insurance_name = parsed_data.get('INAME')

            if patient_id and insurance_name:
                patient_id_to_insurance_name[patient_id] = insurance_name
                MediLink_ConfigLoader.log("Mapped Patient ID {} to Insurance Name {}".format(patient_id, insurance_name), config, level="INFO")

    except FileNotFoundError:
        MediLink_ConfigLoader.log("File not found: {}".format(z_dat_path), config, level="INFO")
    except Exception as e:
        MediLink_ConfigLoader.log("Failed to parse Z.dat: {}".format(str(e)), config, level="INFO")

    return patient_id_to_insurance_name

def load_historical_payer_to_patient_mappings(config):
    """
    Loads historical mappings from multiple Carol's CSV files in a specified directory,
    mapping Payer IDs to sets of Patient IDs.

    Args:
        config (dict): Configuration object containing the directory path for Carol's CSV files
                       and other necessary parameters.

    Returns:
        dict: A dictionary where each key is a Payer ID and the value is a set of Patient IDs.
    """
    directory_path = os.path.dirname(config['CSV_FILE_PATH'])
    payer_to_patient_ids = defaultdict(set)

    try:
        # Check if the directory exists
        if not os.path.isdir(directory_path):
            raise FileNotFoundError("Directory '{}' not found.".format(directory_path))

        # Loop through each file in the directory containing Carol's historical CSVs
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename.endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        patient_count = 0  # Counter for Patient IDs found in this CSV
                        for row in reader:
                            if 'Patient ID' not in row or 'Ins1 Payer ID' not in row:
                                continue  # Skip this row if either key is missing
                            if not row.get('Patient ID').strip() or not row.get('Ins1 Payer ID').strip():
                                continue  # Skip this row if either value is missing or empty
                            
                            payer_id = row['Ins1 Payer ID'].strip()
                            patient_id = row['Patient ID'].strip()
                            payer_to_patient_ids[payer_id].add(patient_id)
                            patient_count += 1  # Increment the counter for each valid mapping
                        
                        # Log the accumulated count for this CSV file
                        if patient_count > 0:
                            MediLink_ConfigLoader.log("CSV file '{}' has {} Patient IDs with Payer IDs.".format(filename, patient_count))
                        else:
                            MediLink_ConfigLoader.log("CSV file '{}' is empty or does not have valid Patient ID or Payer ID mappings.".format(filename))
                except Exception as e:
                    print("Error processing file {}: {}".format(filename, e))
    except FileNotFoundError as e:
        print("Error: {}".format(e))

    if not payer_to_patient_ids:
        print("No historical mappings were generated.")
    
    return dict(payer_to_patient_ids)