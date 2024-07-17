from datetime import datetime
import os
import MediLink_ConfigLoader

def display_welcome():
    print("\n" + "-" * 60)
    print("          *~^~*:    Welcome to MediLink!    :*~^~*")
    print("-" * 60)

def display_menu(options):
    print("Menu Options:")
    for i, option in enumerate(options):
        print("{0}. {1}".format(i+1, option))

def get_user_choice():
    return input("Enter your choice: ").strip()

def display_exit_message():
    print("\nExiting MediLink.")

def display_invalid_choice():
    print("Invalid choice. Please select a valid option.")

def display_patient_options(detailed_patient_data):
    """
    Displays a list of patients with their current suggested endpoints, prompting for selections to adjust.
    """
    print("\nPlease select the patients to adjust by entering their numbers separated by commas\n(e.g., 1,3,5):")
    # Can disable this extra print for now because the px list would already be on-screen.
    #for i, data in enumerate(detailed_patient_data, start=1):
    #    patient_info = "{0} ({1}) - {2}".format(data['patient_name'], data['patient_id'], data['surgery_date'])
    #    endpoint = data.get('suggested_endpoint', 'N/A')
    #    print("{:<3}. {:<30} Current Endpoint: {}".format(i, patient_info, endpoint))

def get_selected_indices(patient_count):
    """
    Collects user input for selected indices to adjust endpoints.
    """
    selected_indices_input = input("> ")
    selected_indices = [int(index.strip()) - 1 for index in selected_indices_input.split(',') if index.strip().isdigit() and 0 <= int(index.strip()) - 1 < patient_count]
    return selected_indices

def display_patient_for_adjustment(patient_name, suggested_endpoint):
    """
    Displays the current endpoint for a selected patient and prompts for a change.
    """
    print("\n- {0} | Current Endpoint: {1}".format(patient_name, suggested_endpoint))

def get_endpoint_decision():
    """
    Asks the user if they want to change the endpoint.
    """
    return input("Change endpoint? (Y/N): ").strip().lower()

def display_endpoint_options(endpoints_config):
    """
    Displays the endpoint options to the user based on the provided mapping.

    Args:
        endpoints_config (dict): A dictionary mapping endpoint keys to their properties, 
                                 where each property includes a 'name' key for the user-friendly name.
                                 Example: {'Availity': {'name': 'Availity'}, 'OptumEDI': {'name': 'OptumEDI'}, ...}

    Returns:
        None
    """
    print("Select the new endpoint for the patient:")
    for index, (key, details) in enumerate(endpoints_config.items(), 1):
        print("{0}. {1}".format(index, details['name']))

def get_new_endpoint_choice():
    """
    Gets the user's choice for a new endpoint.
    """
    return input("Select desired endpoint (e.g. 1, 2): ").strip()

# Function to display full list of insurance options
def display_insurance_options(insurance_options=None):

    # Retrieve insurance options with codes and descriptions
    config, _ = MediLink_ConfigLoader.load_configuration()
    insurance_options = config['MediLink_Config'].get('insurance_options')
    
    print("\nInsurance Type Options:")
    for code, description in sorted(insurance_options.items()):
        print("{}: {}".format(code, description))
    print()  # Add a blank line for better readability

def display_patient_summaries(detailed_patient_data):
    """
    Displays summaries of all patients and their suggested endpoints.
    """
    print("\nSummary of patient details and suggested endpoint:")
    for index, summary in enumerate(detailed_patient_data, start=1):
        try:
            display_file_summary(index, summary)
        except KeyError as e:
            print("Summary at index {} is missing key: {}".format(index, e))
    print() # add blank line for improved readability.

def ask_for_proceeding_with_endpoints():
    """
    Asks the user if they want to proceed with all suggested endpoints.
    """
    proceed = input("Do you want to proceed with all suggested endpoints? (Y/N): ").strip().lower()
    return proceed == 'y'

def display_file_summary(index, summary):
    # Ensure surgery_date is converted to a datetime object
    surgery_date = datetime.strptime(summary['surgery_date'], "%m-%d-%y")
    
    # Add header row if it's the first index
    if index == 1:
        print("{:<3} {:5} {:<10} {:20} {:15} {:2} {:20}".format(
            "No.", "Date", "ID", "Name", "Primary Ins.", "IT", "Suggested Endpoint"
        ))
        print("-"*80)

    # Check if insurance_type is available; if not, set a default placeholder (this should already be '12' at this point)
    insurance_type = summary.get('insurance_type', '--')

    # Displays the summary of a file.
    print("{:02d}. {:5} ({:<8}) {:20} {:15} {:2} {:20}".format(
        index,
        surgery_date.strftime("%m-%d"),
        summary['patient_id'],
        summary['patient_name'][:20],
        summary['primary_insurance'][:15],
        insurance_type[:2],
        summary['suggested_endpoint'][:20])
    )
    
def user_select_files(file_list):
    """
    Prompt the user to select files from a list of detected files.
    
    :param file_list: List of detected files.
    :return: List of files selected by the user.
    """
    # Sort the files by creation time in descending order
    file_list = sorted(file_list, key=os.path.getctime, reverse=True)
    
    print("Select claim files to submit from the following list:")
    for i, file in enumerate(file_list):
        print("{}: {}".format(i+1, os.path.basename(file)))
    
    selected_indices = input("\nEnter the numbers of the files to process, separated by commas\n(or press Enter to select all): ")
    if not selected_indices:
        return file_list
    
    selected_indices = [int(i.strip()) - 1 for i in selected_indices.split(',')]
    selected_files = [file_list[i] for i in selected_indices]
    
    return selected_files
