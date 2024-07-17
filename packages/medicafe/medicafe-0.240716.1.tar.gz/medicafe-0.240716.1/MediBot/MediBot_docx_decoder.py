from docx import Document
import re
from lxml import etree
import zipfile
from datetime import datetime
import os
import sys
from collections import OrderedDict

# Add parent directory of the project to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

try:
    import MediLink_ConfigLoader
except ImportError:
    from MediLink import MediLink_ConfigLoader

def parse_docx(filepath):
    try:
        doc = Document(filepath)  # Open the .docx file
    except Exception as e:
        MediLink_ConfigLoader.log("Error opening document: {}".format(e))  # Log error
        return {}

    patient_data = OrderedDict()  # Initialize OrderedDict to store data
    MediLink_ConfigLoader.log("Extracting Date of Service from {}".format(filepath), level="DEBUG")
    
    date_of_service = extract_date_of_service(filepath)  # Extract date of service
    MediLink_ConfigLoader.log("Date of Service recorded as: {}".format(date_of_service), level="DEBUG")

    for table in doc.tables:  # Iterate over tables in the document
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) > 4 and cells[3].startswith('#'):
                try:
                    patient_id = parse_patient_id(cells[3])
                    diagnosis_code = parse_diagnosis_code(cells[4])
                    left_or_right_eye = parse_left_or_right_eye(cells[4])
                    femto_yes_or_no = parse_femto_yes_or_no(cells[4])

                    if patient_id not in patient_data:
                        patient_data[patient_id] = {}

                    if date_of_service in patient_data[patient_id]:
                        MediLink_ConfigLoader.log("Duplicate entry for patient ID {} on date {}. Skipping.".format(patient_id, date_of_service))
                    else:
                        patient_data[patient_id][date_of_service] = [diagnosis_code, left_or_right_eye, femto_yes_or_no]
                except Exception as e:
                    MediLink_ConfigLoader.log("Error processing row: {}. Error: {}".format(cells, e))
    
    # Validation steps
    validate_unknown_entries(patient_data)
    validate_diagnostic_code(patient_data)
    
    return patient_data

def validate_unknown_entries(patient_data):
    for patient_id, dates in list(patient_data.items()):
        for date, details in list(dates.items()):
            if 'Unknown' in details:
                warning_message = "Warning: 'Unknown' entry found. Patient ID: {}, Date: {}, Details: {}".format(patient_id, date, details)
                MediLink_ConfigLoader.log(warning_message, level="WARNING")
                print(warning_message)
                del patient_data[patient_id][date]
        if not patient_data[patient_id]:  # If no dates left for the patient, remove the patient
            del patient_data[patient_id]

def validate_diagnostic_code(patient_data):
    for patient_id, dates in patient_data.items():
        for date, details in dates.items():
            diagnostic_code, eye, _ = details
            if diagnostic_code[-1].isdigit():
                if eye == 'Left' and not diagnostic_code.endswith('2'):
                    log_and_warn(patient_id, date, diagnostic_code, eye)
                elif eye == 'Right' and not diagnostic_code.endswith('1'):
                    log_and_warn(patient_id, date, diagnostic_code, eye)

def log_and_warn(patient_id, date, diagnostic_code, eye):
    warning_message = (
        "Warning: Mismatch found for Patient ID: {}, Date: {}, "
        "Diagnostic Code: {}, Eye: {}".format(patient_id, date, diagnostic_code, eye)
    )
    MediLink_ConfigLoader.log(warning_message, level="WARNING")
    print(warning_message)

# Extract and parse the date of service from the .docx file
def extract_date_of_service(docx_path):
    extract_to = "extracted_docx"
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
        with zipfile.ZipFile(docx_path, 'r') as docx:
            docx.extractall(extract_to)
            MediLink_ConfigLoader.log("Extracted DOCX to: {}".format(extract_to), level="DEBUG")

        file_path = find_text_in_xml(extract_to, "Surgery Schedule")
        if file_path:
            return extract_date_from_file(file_path)
        else:
            MediLink_ConfigLoader.log("Target text 'Surgery Schedule' not found in any XML files.", level="WARNING")
            return None
    finally:
        # Clean up the extracted files
        remove_directory(extract_to)
        MediLink_ConfigLoader.log("Cleaned up extracted files in: {}".format(extract_to), level="DEBUG")

def remove_directory(path):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)

# Find the target text in the extracted XML files
def find_text_in_xml(directory, target_text):
    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root_dir, file)
                try:
                    tree = etree.parse(file_path)
                    root = tree.getroot()
                    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'} # hardcoded for XP handling BUG
                    for elem in root.xpath('//w:t', namespaces=namespaces):
                        if elem.text and target_text in elem.text:
                            MediLink_ConfigLoader.log("Found target text in file: {}".format(file_path), level="DEBUG")
                            return file_path
                except Exception as e:
                    MediLink_ConfigLoader.log("Error parsing XML file {}: {}".format(file_path, e))
                    print("Error parsing XML file {}: {}".format(file_path, e))
    return None

# Normalize month and day abbreviations
def normalize_text(text):
    month_map = {
        'JAN': 'JANUARY', 'FEB': 'FEBRUARY', 'MAR': 'MARCH', 'APR': 'APRIL', 
        'MAY': 'MAY', 'JUN': 'JUNE', 'JUL': 'JULY', 'AUG': 'AUGUST', 
        'SEP': 'SEPTEMBER', 'OCT': 'OCTOBER', 'NOV': 'NOVEMBER', 'DEC': 'DECEMBER'
    }
    day_map = {
        'MON': 'MONDAY', 'TUE': 'TUESDAY', 'WED': 'WEDNESDAY', 'THU': 'THURSDAY', 
        'FRI': 'FRIDAY', 'SAT': 'SATURDAY', 'SUN': 'SUNDAY'
    }
    
    for abbr, full in month_map.items():
        text = re.sub(r'\b' + abbr + r'\b', full, text, flags=re.IGNORECASE)
    for abbr, full in day_map.items():
        text = re.sub(r'\b' + abbr + r'\b', full, text, flags=re.IGNORECASE)
    
    return text

def reassemble_year(text):
    # First, handle the most common case where a 4-digit year is split as (3,1), (1,3), or (2,2)
    text = re.sub(r'(\d{3}) (\d{1})', r'\1\2', text)
    text = re.sub(r'(\d{1}) (\d{3})', r'\1\2', text)
    text = re.sub(r'(\d{2}) (\d{2})', r'\1\2', text)
    
    # Handle the less common cases where the year might be split as (1,1,2) or (2,1,1) or (1,2,1)
    parts = re.findall(r'\b(\d{1,2})\b', text)
    if len(parts) >= 4:
        for i in range(len(parts) - 3):
            candidate = ''.join(parts[i:i + 4])
            if len(candidate) == 4 and candidate.isdigit():
                combined_year = candidate
                text = re.sub(r'\b' + r'\b \b'.join(parts[i:i + 4]) + r'\b', combined_year, text)
                break
    
    return text

# Extract and parse the date from the file
def extract_date_from_file(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        collected_text = []
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'} # hardcoded for XP handling BUG
        for elem in root.xpath('//w:t', namespaces=namespaces):
            if elem.text:
                collected_text.append(elem.text.strip())
        
        for elem in root.iter():
            if elem.tag.endswith('t') and elem.text:
                collected_text.append(elem.text.strip())

        combined_text = ' '.join(collected_text)
        combined_text = reassemble_year(combined_text) # Fix OCR splitting years
        # combined_text = re.sub(r'(\d{3}) (\d{1})', r'\1\2', combined_text) # initial year regex.
        combined_text = normalize_text(combined_text)  # Normalize abbreviations
        combined_text = re.sub(r',', '', combined_text)  # Remove commas if they exist

        # Log the combined text
        MediLink_ConfigLoader.log("Combined text: {}".format(combined_text), level="DEBUG")
        # print("DEBUG: Combined text: {}".format(combined_text))
        
        day_week_pattern = r"(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)"
        month_day_pattern = r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) \d{1,2}"
        year_pattern = r"\d{4}"

        day_of_week = re.search(day_week_pattern, combined_text, re.IGNORECASE)
        month_day = re.search(month_day_pattern, combined_text, re.IGNORECASE)
        year_match = re.search(year_pattern, combined_text, re.IGNORECASE)
        
        # Log the results of the regex searches
        MediLink_ConfigLoader.log("Day of week found: {}".format(day_of_week.group() if day_of_week else 'None'), level="DEBUG")
        MediLink_ConfigLoader.log("Month and day found: {}".format(month_day.group() if month_day else 'None'), level="DEBUG")
        MediLink_ConfigLoader.log("Year found: {}".format(year_match.group() if year_match else 'None'), level="DEBUG")

        if day_of_week and month_day and year_match:
            date_str = "{} {} {}".format(day_of_week.group(), month_day.group(), year_match.group())
            try:
                date_obj = datetime.strptime(date_str, '%A %B %d %Y')
                return date_obj.strftime('%m-%d-%Y')
            except ValueError as e:
                MediLink_ConfigLoader.log("Error converting date: {}. Error: {}".format(date_str, e), level="ERROR")
        else:
            MediLink_ConfigLoader.log("Date components not found or incomplete in the text. Combined text: {}, Day of week: {}, Month and day: {}, Year: {}"
                .format(combined_text, 
                        day_of_week.group() if day_of_week else 'None', 
                        month_day.group() if month_day else 'None', 
                        year_match.group() if year_match else 'None'),
                level="WARNING")
    except Exception as e:
        MediLink_ConfigLoader.log("Error extracting date from file: {}. Error: {}".format(file_path, e))
        print("Error extracting date from file: {}. Error: {}".format(file_path, e))
    
    return None

def parse_patient_id(text):
    try:
        return text.split()[0].lstrip('#')  # Extract patient ID number (removing the '#')
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing patient ID: {}. Error: {}".format(text, e))
        return None

def parse_diagnosis_code(text):
    try:
        # Regular expression to find all ICD-10 codes starting with 'H' and containing a period
        pattern = re.compile(r'H\d{2}\.\d+')
        matches = pattern.findall(text)
        
        if matches:
            return matches[0]  # Return the first match
        else:
            # Fallback to original method if no match is found
            if '(' in text and ')' in text:  # Extract the diagnosis code before the '/'
                full_code = text[text.index('(')+1:text.index(')')]
                return full_code.split('/')[0]
            return text.split('/')[0]
    
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing diagnosis code: {}. Error: {}".format(text, e))
        return "Unknown"

def parse_left_or_right_eye(text):
    try:
        if 'LEFT EYE' in text.upper():
            return 'Left'
        elif 'RIGHT EYE' in text.upper():
            return 'Right'
        else:
            return 'Unknown'
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing left or right eye: {}. Error: {}".format(text, e))
        return 'Unknown'

def parse_femto_yes_or_no(text):
    try:
        if 'FEMTO' in text.upper():
            return True
        else:
            return False
    except Exception as e:
        MediLink_ConfigLoader.log("Error parsing femto yes or no: {}. Error: {}".format(text, e))
        return False

def rotate_docx_files(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # Filter files that contain "DR" and "SS" in the filename
    filtered_files = [file for file in files if "DR" in file and "SS" in file]

    # Iterate through filtered files
    for filename in filtered_files:
        filepath = os.path.join(directory, filename)
        # Parse each document and print the resulting dictionary
        patient_data_dict = parse_docx(filepath)
        print("Data from file '{}':".format(filename))
        import pprint
        pprint.pprint(patient_data_dict)
        print()

def main():
    # Call the function with the directory containing your .docx files
    directory = "C:\\Users\\danie\\Downloads\\"
    rotate_docx_files(directory)

if __name__ == "__main__":
    main()