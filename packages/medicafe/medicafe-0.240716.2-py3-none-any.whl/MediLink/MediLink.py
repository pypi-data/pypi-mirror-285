import os
import MediLink_Down
import MediLink_Up
import MediLink_ConfigLoader
import MediLink_DataMgmt

# For UI Functions
import os
import MediLink_UI  # Import UI module for handling all user interfaces
from tqdm import tqdm

# Add parent directory of the project to the Python path
import sys
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

from MediBot import MediBot_Preprocessor_lib
load_insurance_data_from_mains = MediBot_Preprocessor_lib.load_insurance_data_from_mains
from MediBot import MediBot_Crosswalk_Library

# Retrieve insurance options with codes and descriptions
config, _ = MediLink_ConfigLoader.load_configuration()
insurance_options = config['MediLink_Config'].get('insurance_options')
    
def collect_detailed_patient_data(selected_files, config, crosswalk):
    """
    Collects detailed patient data from the selected files.
    
    :param selected_files: List of selected file paths.
    :param config: Configuration settings loaded from a JSON file.
    :param crosswalk: Crosswalk data for mapping purposes.
    :return: A list of detailed patient data.
    """
    detailed_patient_data = []
    for file_path in selected_files:
        detailed_data = extract_and_suggest_endpoint(file_path, config, crosswalk)
        detailed_patient_data.extend(detailed_data)  # Accumulate detailed data for processing
        
    # Enrich the detailed patient data with insurance type
    detailed_patient_data = enrich_with_insurance_type(detailed_patient_data, insurance_options)
    
    # Display summaries and provide an option for bulk edit
    MediLink_UI.display_patient_summaries(detailed_patient_data)

    return detailed_patient_data

def enrich_with_insurance_type(detailed_patient_data, patient_insurance_type_mapping=None):
    """
    Enriches the detailed patient data with insurance type based on patient ID.

    Parameters:
    - detailed_patient_data: List of dictionaries containing detailed patient data.
    - patient_insurance_mapping: Dictionary mapping patient IDs to their insurance types.

    Returns:
    - Enriched detailed patient data with insurance type added.
    
    TODO: Implement a function to provide `patient_insurance_mapping` from a reliable source.
    """
    if patient_insurance_type_mapping is None:
        MediLink_ConfigLoader.log("No Patient:Insurance-Type mapping available.")
        patient_insurance_type_mapping = {}
    
    for data in detailed_patient_data:
        patient_id = data.get('PATID') # I think this is the right name?
        insurance_type = patient_insurance_type_mapping.get(patient_id, '12')  # Default to '12' (PPO)
        data['insurance_type'] = insurance_type
    return detailed_patient_data

def extract_and_suggest_endpoint(file_path, config, crosswalk):
    """
    Reads a fixed-width file, extracts file details including surgery date, patient ID, 
    patient name, primary insurance, and other necessary details for each record. It suggests 
    an endpoint based on insurance provider information found in the crosswalk and prepares 
    detailed patient data for processing.
    
    Parameters:
    - file_path: Path to the fixed-width file.
    - crosswalk: Crosswalk dictionary loaded from a JSON file.

    Returns:
    - A comprehensive data structure retaining detailed patient claim details needed for processing,
      including new key-value pairs for file path, surgery date, patient name, and primary insurance.
    """
    detailed_patient_data = []
    
    # Load insurance data from MAINS to create a mapping from insurance names to their respective IDs
    insurance_to_id = load_insurance_data_from_mains(config)
    MediLink_ConfigLoader.log("Insurance data loaded from MAINS. {} insurance providers found.".format(len(insurance_to_id)))

    for personal_info, insurance_info, service_info, service_info_2, service_info_3 in MediLink_DataMgmt.read_fixed_width_data(file_path):
        parsed_data = MediLink_DataMgmt.parse_fixed_width_data(personal_info, insurance_info, service_info, service_info_2, service_info_3, config.get('MediLink_Config', config))
        
        primary_insurance = parsed_data.get('INAME')
        
        # Retrieve the insurance ID associated with the primary insurance
        insurance_id = insurance_to_id.get(primary_insurance)
        MediLink_ConfigLoader.log("Primary insurance ID retrieved for '{}': {}".format(primary_insurance, insurance_id))

        # Use insurance ID to retrieve the payer ID(s) associated with the insurance
        payer_ids = []
        if insurance_id:
            for payer_id, payer_data in crosswalk.get('payer_id', {}).items():
                medisoft_ids = [str(id) for id in payer_data.get('medisoft_id', [])]
                # MediLink_ConfigLoader.log("Payer ID: {}, Medisoft IDs: {}".format(payer_id, medisoft_ids))
                if str(insurance_id) in medisoft_ids:
                    payer_ids.append(payer_id)
        if payer_ids:
            MediLink_ConfigLoader.log("Payer IDs retrieved for insurance '{}': {}".format(primary_insurance, payer_ids))
        else:
            MediLink_ConfigLoader.log("No payer IDs found for insurance '{}'".format(primary_insurance))
        
        # Find the suggested endpoint from the crosswalk based on the payer IDs
        suggested_endpoint = 'AVAILITY'  # Default endpoint if no matching payer IDs found
        if payer_ids:
            payer_id = payer_ids[0]  # Select the first payer ID
            suggested_endpoint = crosswalk['payer_id'].get(payer_id, {}).get('endpoint', 'AVAILITY')
            MediLink_ConfigLoader.log("Suggested endpoint for payer ID '{}': {}".format(payer_id, suggested_endpoint))
        else:
            MediLink_ConfigLoader.log("No suggested endpoint found for payer IDs: {}".format(payer_ids))

        # Enrich detailed patient data with additional information and suggested endpoint
        detailed_data = parsed_data.copy()  # Copy parsed_data to avoid modifying the original dictionary
        detailed_data.update({
            'file_path': file_path,
            'patient_id': parsed_data.get('CHART'),
            'surgery_date': parsed_data.get('DATE'),
            'patient_name': ' '.join([parsed_data.get(key, '') for key in ['FIRST', 'MIDDLE', 'LAST']]),
            'amount': parsed_data.get('AMOUNT'),
            'primary_insurance': primary_insurance,
            'suggested_endpoint': suggested_endpoint
        })
        detailed_patient_data.append(detailed_data)

    # Return only the enriched detailed patient data, eliminating the need for a separate summary list
    return detailed_patient_data

def check_for_new_remittances(config):
    print("\nChecking for new files across all endpoints...")
    endpoints = config['MediLink_Config']['endpoints']
    processed_endpoints = []
    
    if isinstance(endpoints, dict): # BUG This check can probably be removed later.
        for endpoint_key, endpoint_info in tqdm(endpoints.items(), desc="Processing endpoints"):
            if 'remote_directory_down' in endpoint_info:  # Check if the 'remote_directory_down' key exists
                #print("Processing endpoint: ", endpoint_info['name']) 
                # BUG (Debug and verbosity removal) this is really for debug only. Positive statements can be muted.
                try:
                    ERA_path = MediLink_Down.main(desired_endpoint=endpoint_key)
                    processed_endpoints.append((endpoint_info['name'], ERA_path))
                    MediLink_ConfigLoader.log("Results for {} saved to: {}".format(endpoint_info['name'], ERA_path))
                    # TODO (Low SFTP - Download side) This needs to check to see if this actually worked maybe winscplog before saying it completed successfully 
                    # Check if there is commonality with the upload side so we can use the same validation function.
                except Exception as e:
                    print("An error occurred while checking remittances for {}: {}".format(endpoint_info['name'], e))
            else:
                MediLink_ConfigLoader.log("Skipping endpoint '{}' as it does not have 'remote_directory_down' configured.".format(endpoint_info['name']))
    else:
        print("Error: Endpoint config is not a 'dictionary' as expected.")
    # Check if all ERA paths are the same
    unique_era_paths = set(path for _, path in processed_endpoints)
    if len(unique_era_paths) == 1:
        common_era_path = unique_era_paths.pop()  # Get the common ERA path
        endpoints_list = ", ".join(endpoint for endpoint, _ in processed_endpoints)
        print("\nProcessed Endpoints: {}".format(endpoints_list))
        print("File located at: {}\n".format(common_era_path))
        # TODO (MediPost) These prints will eventually be logs when MediPost is made.
        
    else:
        if processed_endpoints:
            print("\nProcessed Endpoints:")
            for endpoint, path in processed_endpoints:
                print("Endpoint: {}, ERA Path: {}".format(endpoint, path))
        else:
            print("No endpoints were processed.")

def user_decision_on_suggestions(detailed_patient_data, config):
    """
    Presents the user with all patient summaries and suggested endpoints,
    then asks for confirmation to proceed with all or specify adjustments manually.
    
    BUG (Med suggested_endpoint) The display summary suggested_endpoint key isn't updating per the user's decision 
    although the user decision is persisting. Possibly consider making the current/suggested/confirmed endpoint 
    part of a class that the user can interact with via these menus? Probably better handling that way.
    """
    # Display summaries of patient details and endpoints.
    MediLink_UI.display_patient_summaries(detailed_patient_data)

    # Ask the user if they want to proceed with all suggested endpoints.
    proceed = MediLink_UI.ask_for_proceeding_with_endpoints()

    # If the user agrees to proceed with all suggested endpoints, confirm them.
    if proceed:
        return MediLink_DataMgmt.confirm_all_suggested_endpoints(detailed_patient_data)
    # Otherwise, allow the user to adjust the endpoints manually.
    else:
        return select_and_adjust_files(detailed_patient_data, config)
   
def select_and_adjust_files(detailed_patient_data, config):
    """
    Allows users to select patients and adjust their endpoints by interfacing with UI functions.
    
    BUG (Med suggested_endpoint) After the user is done making their selection (probably via a class?), 
    Then suggested_endpoint should update to persist the user selection as priority over its original suggestion. 
    Which means the crosswalk should persist the change in the endpoint as well.
    """
    # Display options for patients
    MediLink_UI.display_patient_options(detailed_patient_data)

    # Get user-selected indices for adjustment
    selected_indices = MediLink_UI.get_selected_indices(len(detailed_patient_data))
    
    # Get an ordered list of endpoint keys
    endpoint_keys = list(config['MediLink_Config']['endpoints'].keys())

    # Iterate over each selected index and process endpoint changes
    for i in selected_indices:
        data = detailed_patient_data[i]
        MediLink_UI.display_patient_for_adjustment(data['patient_name'], data.get('suggested_endpoint', 'N/A'))
        
        endpoint_change = MediLink_UI.get_endpoint_decision()
        if endpoint_change == 'y':
            MediLink_UI.display_endpoint_options(config['MediLink_Config']['endpoints'])
            endpoint_index = int(MediLink_UI.get_new_endpoint_choice()) - 1  # Adjusting for zero-based index
            
            if 0 <= endpoint_index < len(endpoint_keys):
                selected_endpoint_key = endpoint_keys[endpoint_index]
                data['confirmed_endpoint'] = selected_endpoint_key
                print("Endpoint changed to {0} for patient {1}.".format(config['MediLink_Config']['endpoints'][selected_endpoint_key]['name'], data['patient_name']))
                # BUG (Med, Crosswalk & suggested_endpoint) Probably update crosswalk and suggested endpoint here???
            else:
                print("Invalid selection. Keeping the suggested endpoint.")
        else:
            data['confirmed_endpoint'] = data.get('suggested_endpoint', 'N/A')

    return detailed_patient_data

def main_menu():
    """
    Initializes the main menu loop and handles the overall program flow,
    including loading configurations and managing user input for menu selections.
    """
    # Load configuration settings and display the initial welcome message.
    config, crosswalk = MediLink_ConfigLoader.load_configuration() 
    
    # Check to make sure payer_id key is available in crosswalk, otherwise, go through that crosswalk initialization flow
    MediBot_Crosswalk_Library.check_and_initialize_crosswalk(config)
    
    # Check if the application is in test mode
    if config.get("MediLink_Config", {}).get("TestMode", False):
        print("\n--- MEDILINK TEST MODE --- \nTo enable full functionality, please update the config file \nand set 'TestMode' to 'false'.")
    
    # Display Welcome Message
    MediLink_UI.display_welcome()

    # Normalize the directory path for file operations.
    directory_path = os.path.normpath(config['MediLink_Config']['inputFilePath'])

    # Detect files and determine if a new file is flagged.
    all_files, file_flagged = MediLink_DataMgmt.detect_new_files(directory_path)

    while True:
        # Define the menu options. Base options include checking remittances and exiting the program.
        options = ["Check for new remittances", "Exit"]
        # If any files are detected, add the option to submit claims.
        if all_files:
            options.insert(1, "Submit claims")

        # Display the dynamically adjusted menu options.
        MediLink_UI.display_menu(options)
        # Retrieve user choice and handle it.
        choice = MediLink_UI.get_user_choice()

        if choice == '1':
            # Handle remittance checking.
            check_for_new_remittances(config)
        elif choice == '2' and all_files:
            # Handle the claims submission flow if any files are present.
            if file_flagged:
                # Extract the newest single latest file from the list if a new file is flagged.
                selected_files = [max(all_files, key=os.path.getctime)]
            else:
                # Prompt the user to select files if no new file is flagged.
                selected_files = MediLink_UI.user_select_files(all_files)

            # Collect detailed patient data for selected files.
            detailed_patient_data = collect_detailed_patient_data(selected_files, config, crosswalk)
            
            # Process the claims submission.
            handle_submission(detailed_patient_data, config)
        elif choice == '3' or (choice == '2' and not all_files):
            # Exit the program if the user chooses to exit or if no files are present.
            MediLink_UI.display_exit_message()
            break
        else:
            # Display an error message if the user's choice does not match any valid option.
            MediLink_UI.display_invalid_choice()

def handle_submission(detailed_patient_data, config):
    """
    Handles the submission process for claims based on detailed patient data.
    This function orchestrates the flow from user decision on endpoint suggestions to the actual submission of claims.
    """
    # TODO If we get here via a user decline we end up not displaying the patient summary data, but this doesn't happen in the first round. Can be de-tangled later.
    
    # Ask the user if they want to edit insurance types
    edit_insurance = input("Do you want to edit insurance types? (y/n): ").strip().lower()
    if edit_insurance in ['y', 'yes', '']:
        while True:
            # Bulk edit insurance types
            MediLink_DataMgmt.bulk_edit_insurance_types(detailed_patient_data, insurance_options)
    
            # Review and confirm changes
            if MediLink_DataMgmt.review_and_confirm_changes(detailed_patient_data, insurance_options):
                break  # Exit the loop if changes are confirmed
            else:
                print("Returning to bulk edit insurance types.")
    
    # Initiate user interaction to confirm or adjust suggested endpoints.
    adjusted_data = user_decision_on_suggestions(detailed_patient_data, config)
    
    # Confirm all remaining suggested endpoints.
    confirmed_data = MediLink_DataMgmt.confirm_all_suggested_endpoints(adjusted_data)
    if confirmed_data:  # Proceed if there are confirmed data entries.
        # Organize data by confirmed endpoints for submission.
        organized_data = MediLink_DataMgmt.organize_patient_data_by_endpoint(confirmed_data)
        # Confirm transmission with the user and check for internet connectivity.
        if MediLink_Up.confirm_transmission(organized_data):
            if MediLink_Up.check_internet_connection():
                # Submit claims if internet connectivity is confirmed.
                _ = MediLink_Up.submit_claims(organized_data, config)
                # TODO submit_claims will have a receipt return in the future.
            else:
                # Notify the user of an internet connection error.
                print("Internet connection error. Please ensure you're connected and try again.")
        else:
            # Notify the user if the submission is cancelled.
            print("Submission cancelled. No changes were made.")

if __name__ == "__main__":
    main_menu()