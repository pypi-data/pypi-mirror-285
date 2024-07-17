# MediLink_Down.py
import os
import argparse
import shutil
import glob
import csv
from MediLink_Decoder import process_file
from MediLink_ConfigLoader import load_configuration, log
from MediLink_DataMgmt import operate_winscp

def move_downloaded_files(local_storage_path, config):
    local_response_directory = os.path.join(local_storage_path, "responses")
    
    if not os.path.exists(local_response_directory):
        os.makedirs(local_response_directory)
    
    download_dir = config['MediLink_Config']['local_storage_path']
    file_extensions = ['.era', '.277', '.277ibr', '.277ebr', '.dpt', '.ebt', '.ibt']  # Extendable list of file extensions
    
    for ext in file_extensions:
        downloaded_files = [f for f in os.listdir(download_dir) if f.endswith(ext)]
        for file in downloaded_files:
            source_path = os.path.join(download_dir, file)
            destination_path = os.path.join(local_response_directory, file)
            shutil.move(source_path, destination_path)
            log("Moved '{}' to '{}'".format(file, local_response_directory))

def find_files(file_path_pattern):
    normalized_path = os.path.normpath(file_path_pattern)
    if os.path.isdir(normalized_path):
        return [os.path.join(normalized_path, f) for f in os.listdir(normalized_path) if os.path.isfile(os.path.join(normalized_path, f))]
    elif "*" in normalized_path:
        matching_files = glob.glob(normalized_path)
        return [os.path.normpath(file) for file in matching_files]
    else:
        return [normalized_path] if os.path.exists(normalized_path) else []

def translate_files(files, output_directory):
    translated_files = []
    consolidated_records = []
    file_counts = {'.era': 0, '.277': 0, '.277ibr': 0, '.277ebr': 0, '.dpt': 0, '.ebt': 0, '.ibt': 0}

    for file in files:
        ext = os.path.splitext(file)[1]
        if ext in file_counts:
            file_counts[ext] += 1

        try:
            records = process_file(file, output_directory, return_records=True)
            consolidated_records.extend(records)
            csv_file_path = os.path.join(output_directory, os.path.basename(file) + '_decoded.csv')
            log("Translated file to CSV: {}".format(csv_file_path), level="INFO")
            translated_files.append(csv_file_path)
        except ValueError as ve:
            log("Unsupported file type: {}".format(file), level="WARNING")
        except Exception as e:
            log("Error processing file {}: {}".format(file, e), level="ERROR")
    
    print("Detected and processed file counts by type:")
    for ext, count in file_counts.items():
        print("{}: {} files detected".format(ext, count))

    return consolidated_records, translated_files

def display_translated_files(translated_files):
    print("\nTranslated Files Summary:")
    for file in translated_files:
        print(" - {}".format(file))

def main():
    parser = argparse.ArgumentParser(description="Process files and convert them to CSV format.")
    parser.add_argument('--config_path', type=str, help='Path to the configuration JSON file', default="json/config.json")
    parser.add_argument('--file_path_pattern', type=str, help='Path pattern or directory for files to process.', default=None)
    args = parser.parse_args()
    
    config, _ = load_configuration(args.config_path)
    local_storage_path = config['MediLink_Config']['local_storage_path']
    output_directory = os.path.join(local_storage_path, "translated_csvs")

    # If a file path pattern is provided, process those files directly
    if args.file_path_pattern:
        files = find_files(args.file_path_pattern)
        if files:
            files_str = ', '.join(files)
            log("Translating files: {}".format(files_str), level="INFO")
            consolidated_records, translated_files = translate_files(files, output_directory)
            log("Translation completed.", level="INFO")
            if consolidated_records:
                display_consolidated_records(consolidated_records)
            prompt_csv_export(consolidated_records, output_directory)
            return
        else:
            log("No files found matching: {}".format(args.file_path_pattern), level="WARNING")
            return

    # Handle downloading files via WinSCP
    endpoint_key = 'AVAILITY'
    if endpoint_key not in config['MediLink_Config']['endpoints']:
        log("Endpoint '{}' not found in configuration. Using default 'AVAILITY'.".format(endpoint_key), level="WARNING")
        endpoint_key = 'AVAILITY'
    
    endpoint_configs = [config['MediLink_Config']['endpoints'][key] for key in config['MediLink_Config']['endpoints']]
    downloaded_files = []

    for endpoint_config in endpoint_configs:
        downloaded_files += operate_winscp("download", None, endpoint_config, local_storage_path, config)
    
    move_downloaded_files(local_storage_path, config)
    
    consolidated_records, translated_files = translate_files(downloaded_files, output_directory)
    if consolidated_records:
        display_consolidated_records(consolidated_records)
    prompt_csv_export(consolidated_records, output_directory)

def display_consolidated_records(records):
    # Define the new fieldnames and their respective widths
    new_fieldnames = ['Claim #', 'Status', 'Patient', 'Proc.', 'Serv.', 'Allowed', 'Paid', 'Pt Resp', 'Charged']
    col_widths = {field: len(field) for field in new_fieldnames}
    
    # Update column widths based on records
    for record in records:
        for field in new_fieldnames:
            col_widths[field] = max(col_widths[field], len(str(record.get(field, ''))))
    
    # Create table header
    header = " | ".join("{:<{}}".format(field, col_widths[field]) for field in new_fieldnames)
    print(header)
    print("-" * len(header))
    
    # Create table rows
    for record in records:
        row = " | ".join("{:<{}}".format(str(record.get(field, '')), col_widths[field]) for field in new_fieldnames)
        print(row)

def prompt_csv_export(records, output_directory):
    if records:
        user_input = input("Do you want to export the consolidated records to a CSV file? (y/n): ")
        if user_input.lower() == 'y':
            output_file_path = os.path.join(output_directory, "Consolidated_Records.csv")
            write_records_to_csv(records, output_file_path)
            log("Consolidated CSV file created at: {}".format(output_file_path), level="INFO")
        else:
            log("CSV export skipped by user.", level="INFO")

def write_records_to_csv(records, output_file_path):
    fieldnames = ['Claim #', 'Status', 'Patient', 'Proc.', 'Serv.', 'Allowed', 'Paid', 'Pt Resp', 'Charged']
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

if __name__ == "__main__":
    main()
