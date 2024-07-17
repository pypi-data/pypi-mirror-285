import json
import sys
import os

# Add parent directory of the project to the Python path
import sys

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

try:
    import MediLink_ConfigLoader
except ImportError:
    from MediLink import MediLink_ConfigLoader

try:
    from MediLink_API_v3 import fetch_payer_name_from_api
except ImportError:
    from MediLink import MediLink_API_v3
    fetch_payer_name_from_api = MediLink_API_v3.fetch_payer_name_from_api

try:
    from MediBot import MediBot_Preprocessor_lib
except ImportError:
    import MediBot_Preprocessor_lib

def check_and_initialize_crosswalk(config):
    """
    Checks if the 'payer_id' key exists in the crosswalk. If not, prompts the user
    to initialize the crosswalk.

    Args:
        config (dict): Configuration settings.

    Returns:
        boolean: True if succeeded.
    """
    # Reload for safety
    config, crosswalk = MediLink_ConfigLoader.load_configuration(None, config.get('crosswalkPath', 'crosswalk.json'))
    
    try:
        # Attempt to access the 'payer_id' key to ensure it exists
        if 'payer_id' not in crosswalk:
            raise KeyError("Missing 'payer_id' key in crosswalk.")
    except KeyError:
        error_message = "The 'payer_id' key does not exist in the crosswalk configuration. \n" \
                        "This could be because the crosswalk is not initialized. \n" \
                        "Consider running the Crosswalk initializer."
        print(error_message)
        MediLink_ConfigLoader.log(error_message, config, level="ERROR")
        
        # Prompt user to initialize crosswalk
        initialize_choice = input("\nADVANCED OPTION: The crosswalk may not be initialized. \nType 'yes' to initialize it now: ").strip().lower()
        if initialize_choice == 'yes':
            initialize_crosswalk_from_mapat()
            _, crosswalk = MediLink_ConfigLoader.load_configuration() # Reload crosswalk
            MediLink_ConfigLoader.log("Crosswalk reloaded successfully.", config, level="INFO")
        else:
            raise KeyError(error_message)
    
    return True

def validate_and_correct_payer_ids(crosswalk, config):
    """Validates payer IDs via API and handles invalid IDs through user intervention."""
    for payer_id in list(crosswalk['payer_id'].keys()):
        try:
            fetch_payer_name_from_api(payer_id, config, primary_endpoint=None)
            MediLink_ConfigLoader.log("Payer ID {} validated successfully.".format(payer_id), config, level="INFO")
        except Exception as e:
            MediLink_ConfigLoader.log("Payer ID validation failed for {}: {}".format(payer_id, e), config, level="WARNING")
            
            while True:
                corrected_payer_id = input("WWARNING: Invalid Payer ID {}. Enter the correct Payer ID for replacement or type 'FORCE' to continue with the unresolved Payer ID: ".format(payer_id))
                
                if corrected_payer_id.strip().upper() == 'FORCE':
                    MediLink_ConfigLoader.log("User opted to force-continue with unresolved Payer ID {}. Warning: This may indicate an underlying issue.".format(payer_id), config, level="WARNING")
                    break

                if corrected_payer_id:
                    try:
                        fetch_payer_name_from_api(corrected_payer_id, config, primary_endpoint=None)
                        MediLink_ConfigLoader.log("Corrected Payer ID {} validated successfully.".format(corrected_payer_id), config, level="INFO")
                        
                        if update_crosswalk_with_corrected_payer_id(payer_id, corrected_payer_id, config, crosswalk):
                            if 'csv_replacements' not in crosswalk:
                                crosswalk['csv_replacements'] = {}
                            crosswalk['csv_replacements'][payer_id] = corrected_payer_id
                            MediLink_ConfigLoader.log("Added replacement filter: {} -> {}".format(payer_id, corrected_payer_id), config, level="INFO")
                        else:
                            print("Failed to update crosswalk with the corrected Payer ID {}.".format(corrected_payer_id))
                            MediLink_ConfigLoader.log("Failed to update crosswalk with the corrected Payer ID {}.".format(corrected_payer_id), config, level="ERROR")
                        break
                    except Exception as e:
                        print("Corrected Payer ID {} validation failed: {}".format(corrected_payer_id, e))
                        MediLink_ConfigLoader.log("Corrected Payer ID {} validation failed: {}".format(corrected_payer_id, e), config, level="ERROR")
                else:
                    print("Exiting initialization. Please correct the Payer ID and retry.")
                    sys.exit(1)

def initialize_crosswalk_from_mapat():
    """
    Input: Historical Carol's CSVs and MAPAT data.

    Process:
        Extract mappings from Carol's old CSVs to identify Payer IDs and associated Patient IDs.
        Use MAPAT to correlate these Patient IDs with Insurance IDs.
        Compile these mappings into the crosswalk, setting Payer IDs as keys and corresponding Insurance IDs as values.

    Output: A fully populated crosswalk.json file that serves as a baseline for future updates.
    """
    config, crosswalk = MediLink_ConfigLoader.load_configuration()
    
    # Load historical mappings
    try:
        patient_id_to_insurance_id, payer_id_to_patient_ids = MediBot_Preprocessor_lib.load_data_sources(config, crosswalk)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    # Map Payer IDs to Insurance IDs
    payer_id_to_details = MediBot_Preprocessor_lib.map_payer_ids_to_insurance_ids(patient_id_to_insurance_id, payer_id_to_patient_ids)
    
    # Update the crosswalk for payer IDs only, retaining other mappings
    crosswalk['payer_id'] = payer_id_to_details
    
    # Validate payer IDs via API and handle invalid IDs
    validate_and_correct_payer_ids(crosswalk, config)
    
    # Save the initial crosswalk
    if save_crosswalk(config, crosswalk):
        message = "Crosswalk initialized with mappings for {} payers.".format(len(crosswalk.get('payer_id', {})))
        print(message)
        MediLink_ConfigLoader.log(message, config, level="INFO")
    else:
        print("Failed to save the crosswalk.")
        sys.exit(1)
    return payer_id_to_details

def crosswalk_update(config, crosswalk):
    """
    Updates the `crosswalk.json` file using mappings from MAINS, Z.dat, and Carol's CSV. This function integrates
    user-defined insurance mappings from Z.dat with existing payer-to-insurance mappings in the crosswalk, 
    and validates these mappings using MAINS.

    Steps:
    1. Load mappings from MAINS for translating insurance names to IDs.
    2. Load mappings from the latest Carol's CSV for new patient entries mapping Patient IDs to Payer IDs.
    3. Parse incremental data from Z.dat which contains recent user interactions mapping Patient IDs to Insurance Names.
    4. Update the crosswalk using the loaded and parsed data, ensuring each Payer ID maps to the correct Insurance IDs.
    5. Persist the updated mappings back to the crosswalk file.

    Args:
        config (dict): Configuration dictionary containing paths and other settings.
        crosswalk (dict): Existing crosswalk mapping Payer IDs to sets of Insurance IDs.

    Returns:
        bool: True if the crosswalk was successfully updated and saved, False otherwise.
    """    
    # Load insurance mappings from MAINS (Insurance Name to Insurance ID)
    insurance_name_to_id = MediBot_Preprocessor_lib.load_insurance_data_from_mains(config)
    MediLink_ConfigLoader.log("Loaded insurance data from MAINS...")
    
    # Load new Patient ID to Payer ID mappings from Carol's CSV (if necessary)
    # TODO This is a low performance strategy.
    patient_id_to_payer_id = MediBot_Preprocessor_lib.load_historical_payer_to_patient_mappings(config)
    MediLink_ConfigLoader.log("Loaded historical mappings...")
  
    # Load incremental mapping data from Z.dat (Patient ID to Insurance Name)
    # TODO This may be a redundant approach?
    # This is a singular path. This is fine though because any time we process a Z.DAT we'd have the crosswalk incremented.
    patient_id_to_insurance_name = MediBot_Preprocessor_lib.parse_z_dat(config['MediLink_Config']['Z_DAT_PATH'], config['MediLink_Config'])
    MediLink_ConfigLoader.log("Parsed Z data...")

    # Update the crosswalk with new or revised mappings
    for patient_id, payer_id in patient_id_to_payer_id.items():
        insurance_name = patient_id_to_insurance_name.get(patient_id)
        if insurance_name and insurance_name in insurance_name_to_id:
            insurance_id = insurance_name_to_id[insurance_name]

            # Ensure payer ID is in the crosswalk and initialize if not
            MediLink_ConfigLoader.log("Initializing payer_id key...")
            if 'payer_id' not in crosswalk:
                crosswalk['payer_id'] = {}
            if payer_id not in crosswalk['payer_id']:
                # TODO The OPTUMEDI default here should be gathered via API and not just a default. There are 2 of these defaults!!
                crosswalk['payer_id'][payer_id] = {'endpoint': 'OPTUMEDI', 'medisoft_id': set(), 'medisoft_medicare_id': set()}

            # Update the medisoft_id set, temporarily using a set to avoid duplicates
            crosswalk['payer_id'][payer_id]['medisoft_id'].add(insurance_id)
            MediLink_ConfigLoader.log("Added new insurance ID {} to payer ID {}".format(insurance_id, payer_id))

    # Convert sets to lists just before saving
    for payer_id in crosswalk['payer_id']:
        if isinstance(crosswalk['payer_id'][payer_id]['medisoft_id'], set):
            crosswalk['payer_id'][payer_id]['medisoft_id'] = list(crosswalk['payer_id'][payer_id]['medisoft_id'])
        if isinstance(crosswalk['payer_id'][payer_id]['medisoft_medicare_id'], set):
            crosswalk['payer_id'][payer_id]['medisoft_medicare_id'] = list(crosswalk['payer_id'][payer_id]['medisoft_medicare_id'])
            
    # Save the updated crosswalk to the specified file
    return save_crosswalk(config, crosswalk)

def update_crosswalk_with_corrected_payer_id(old_payer_id, corrected_payer_id, config, crosswalk):
    """Updates the crosswalk with the corrected payer ID."""
    # Update the payer_id section
    if old_payer_id in crosswalk['payer_id']:
        crosswalk['payer_id'][corrected_payer_id] = crosswalk['payer_id'].pop(old_payer_id)
        MediLink_ConfigLoader.log("Crosswalk updated: replaced Payer ID {} with {}".format(old_payer_id, corrected_payer_id), config, level="INFO")
    else:
        MediLink_ConfigLoader.log("Failed to update crosswalk: could not find old Payer ID {}".format(old_payer_id), config, level="ERROR")
        return False

    # Update the csv_replacements section
    if 'csv_replacements' not in crosswalk:
        crosswalk['csv_replacements'] = {}
    crosswalk['csv_replacements'][old_payer_id] = corrected_payer_id
    MediLink_ConfigLoader.log("Crosswalk csv_replacements updated: added {} -> {}".format(old_payer_id, corrected_payer_id), config, level="INFO")
    
    # Save the updated crosswalk
    return save_crosswalk(config, crosswalk)

def update_crosswalk_with_new_payer_id(insurance_name, payer_id, config):
    """Updates the crosswalk with a new payer ID."""
    _, crosswalk = MediLink_ConfigLoader.load_configuration(None, config.get('crosswalkPath', 'crosswalk.json'))
    medisoft_id = MediBot_Preprocessor_lib.load_insurance_data_from_mains(config).get(insurance_name)
    
    if medisoft_id:
        medisoft_id_str = str(medisoft_id)
        if payer_id not in crosswalk['payer_id']:
            crosswalk['payer_id'][payer_id] = {"medisoft_id": [medisoft_id_str], "medisoft_medicare_id": []}
        else:
            crosswalk['payer_id'][payer_id]['medisoft_id'].append(medisoft_id_str)
        save_crosswalk(config, crosswalk)
        MediLink_ConfigLoader.log("Updated crosswalk with new payer ID {} for insurance name {}".format(payer_id, insurance_name), config, level="INFO")
    else:
        message = "Failed to update crosswalk: Medisoft ID not found for insurance name {}".format(insurance_name)
        print(message)
        MediLink_ConfigLoader.log(message, config, level="ERROR")
        
def save_crosswalk(config, crosswalk):
    """
    Saves the updated crosswalk to a JSON file.
    Args:
        crosswalk_path (str): Path to the crosswalk.json file.
        crosswalk (dict): The updated crosswalk data.
    Returns:
        bool: True if the file was successfully saved, False otherwise.
    """
    # Attempt to fetch crosswalkPath from MediLink_Config
    try:
        crosswalk_path = config['MediLink_Config']['crosswalkPath']
    except KeyError:
        # If KeyError occurs, fall back to fetching crosswalkPath directly
        crosswalk_path = config.get('crosswalkPath', None)  # Replace None with a default value if needed

    try:
        # Initialize 'payer_id' key if not present
        if 'payer_id' not in crosswalk:
            print("save_crosswalk is initializing 'payer_id' key...")
            crosswalk['payer_id'] = {}

        # Convert all 'medisoft_id' fields from sets to lists if necessary
        for k, v in crosswalk.get('payer_id', {}).items():
            if isinstance(v.get('medisoft_id'), set):
                v['medisoft_id'] = list(v['medisoft_id'])

        with open(crosswalk_path, 'w') as file:
            json.dump(crosswalk, file, indent=4)  # Save the entire dictionary
        return True

    except KeyError as e:
        # Log the KeyError with specific information about what was missing
        print("Key Error: A required key is missing in the crosswalk data -", e)
        return False

    except TypeError as e:
        # Handle data type errors (e.g., non-serializable types)
        print("Type Error: There was a type issue with the data being saved in the crosswalk -", e)
        return False

    except IOError as e:
        # Handle I/O errors related to file operations
        print("I/O Error: An error occurred while writing to the crosswalk file -", e)
        return False

    except Exception as e:
        # A general exception catch to log any other exceptions that may not have been anticipated
        print("Unexpected crosswalk error:", e)
        return False