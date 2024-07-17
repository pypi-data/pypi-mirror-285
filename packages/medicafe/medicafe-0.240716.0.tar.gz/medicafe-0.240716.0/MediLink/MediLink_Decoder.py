# MediLink_Decoder.py
import os
import sys
import csv
from MediLink_ConfigLoader import load_configuration, log
from MediLink_Parser import parse_era_content, parse_277_content, parse_277IBR_content, parse_277EBR_content, parse_dpt_content, parse_ebt_content, parse_ibt_content

def process_file(file_path, output_directory, return_records=False):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    file_type = determine_file_type(file_path)
    content = read_file(file_path)
    
    if file_type == 'ERA':
        records = parse_era_content(content)
    elif file_type in ['277', '277IBR', '277EBR']:
        records = parse_277_content(content) if file_type == '277' else parse_277IBR_content(content) if file_type == '277IBR' else parse_277EBR_content(content)
    elif file_type == 'DPT':
        records = parse_dpt_content(content)
    elif file_type == 'EBT':
        records = parse_ebt_content(content)
    elif file_type == 'IBT':
        records = parse_ibt_content(content)
    else:
        log("Unsupported file type: {}".format(file_type))
        return []

    formatted_records = format_records(records, file_type)
    if not return_records:
        display_table(formatted_records)
        output_file_path = os.path.join(output_directory, os.path.basename(file_path) + '_decoded.csv')
        write_records_to_csv(formatted_records, output_file_path)
        log("Decoded data written to {}".format(output_file_path))
    return formatted_records

def determine_file_type(file_path):
    if file_path.endswith('.era'):
        return 'ERA'
    elif file_path.endswith('.277'):
        return '277'
    elif file_path.endswith('.277ibr'):
        return '277IBR'
    elif file_path.endswith('.277ebr'):
        return '277EBR'
    elif file_path.endswith('.dpt'):
        return 'DPT'
    elif file_path.endswith('.ebt'):
        return 'EBT'
    elif file_path.endswith('.ibt'):
        return 'IBT'
    else:
        log("Unsupported file type for file: {}".format(file_path))
        return None

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def write_records_to_csv(records, output_file_path):
    fieldnames = ['Claim #', 'Status', 'Patient', 'Proc.', 'Serv.', 'Allowed', 'Paid', 'Pt Resp', 'Charged']
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

def format_records(records, file_type):
    formatted_records = []
    for record in records:
        if file_type == 'IBT':
            formatted_record = {
                'Claim #': record.get('Patient Control Number', ''),
                'Status': record.get('Status', ''),
                'Patient': record.get('Patient Name', ''),
                'Proc.': format_date(record.get('To Date', '')),
                'Serv.': format_date(record.get('From Date', '')),
                'Allowed': '',
                'Paid': '',
                'Pt Resp': '',
                'Charged': record.get('Charge', '')
            }
        else:
            formatted_record = {
                'Claim #': record.get('Chart Number', record.get('Claim Status Tracking #', record.get('Claim #', ''))),
                'Status': record.get('claimStatus', record.get('Status', '')),
                'Patient': record.get('memberInfo', {}).get('ptntFn', '') + ' ' + record.get('memberInfo', {}).get('ptntLn', '') if 'memberInfo' in record else record.get('Patient', ''),
                'Proc.': format_date(record.get('processed_date', record.get('Received Date', ''))),
                'Serv.': format_date(record.get('firstSrvcDt', record.get('Date of Service', ''))),
                'Allowed': record.get('totalAllowdAmt', record.get('Allowed Amount', '')),
                'Paid': record.get('totalPaidAmt', record.get('Amount Paid', '')),
                'Pt Resp': record.get('totalPtntRespAmt', record.get('Patient Responsibility', '')),
                'Charged': record.get('totalChargedAmt', record.get('Charge', ''))
            }
        formatted_records.append(formatted_record)
    return formatted_records

def format_date(date_str):
    if date_str and len(date_str) >= 10:
        return date_str[5:7] + '-' + date_str[8:10]  # Assuming date format is YYYY-MM-DD, this returns MM-DD
    return ''

def display_table(records):
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

def display_consolidated_records(records):
    if not records:
        return
    
    new_fieldnames = ['Claim #', 'Status', 'Patient', 'Proc.', 'Serv.', 'Allowed', 'Paid', 'Pt Resp', 'Charged']
    col_widths = {field: len(field) for field in new_fieldnames}

    for record in records:
        for field in new_fieldnames:
            col_widths[field] = max(col_widths[field], len(str(record.get(field, ''))))

    header = " | ".join("{:<{}}".format(field, col_widths[field]) for field in new_fieldnames)
    print(header)
    print("-" * len(header))

    for record in records:
        row = " | ".join("{:<{}}".format(str(record.get(field, '')), col_widths[field]) for field in new_fieldnames)
        print(row)

if __name__ == "__main__":
    config, _ = load_configuration()
    
    files = sys.argv[1:]
    if not files:
        log("No files provided as arguments.", 'error')
        sys.exit(1)

    output_directory = config['MediLink_Config'].get('local_storage_path')
    all_records = []
    for file_path in files:
        try:
            records = process_file(file_path, output_directory, return_records=True)
            all_records.extend(records)
        except Exception as e:
            log("Failed to process {}: {}".format(file_path, e), 'error')
    
    display_consolidated_records(all_records)

    if input("Do you want to export the consolidated records to a CSV file? (y/n): ").strip().lower() == 'y':
        consolidated_csv_path = os.path.join(output_directory, "Consolidated_Records.csv")
        write_records_to_csv(all_records, consolidated_csv_path)
        log("Consolidated records written to {}".format(consolidated_csv_path))
