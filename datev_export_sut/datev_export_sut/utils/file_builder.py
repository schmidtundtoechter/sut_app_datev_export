import frappe
import os
import tempfile
from datetime import datetime
from datev_export_sut.datev_export_sut.utils.employee_data import map_employee_to_lodas

def generate_lodas_files(employees_by_company, settings):
    """Generate LODAS files for each company."""
    consultant_number = settings.consultant_number
    
    # Store file paths for later email attachment
    file_paths = []
    
    # Get company to client number mapping
    client_numbers = {}
    for mapping in settings.company_client_mapping:
        client_numbers[mapping.company] = mapping.client_number
    
    # Generate file for each company
    for company, employees in employees_by_company.items():
        # Skip if no mapping exists
        if company not in client_numbers:
            frappe.log_error(f"No client number mapping for company: {company}", 
                           "DATEV Export Error")
            continue
        
        client_number = client_numbers[company]
        
        # Generate file content
        content = generate_lodas_file_header(consultant_number, client_number)
        content += generate_record_description()
        content += generate_employee_data(employees)
        
        # Create temporary file
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"DATEV_LODAS_{company.replace(' ', '_')}_{timestamp}.txt"
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_paths.append({
            'path': temp_path,
            'filename': filename,
            'company': company,
            'employee_count': len(employees)
        })
    
    return file_paths

def generate_lodas_file_header(consultant_number, client_number):
    """Generate the [Allgemein] section of the LODAS file."""
    header = "[Allgemein]\n"
    header += "Ziel=Lodas\n"
    header += "Version_SST=1.0\n"
    header += f"BeraterNr={consultant_number}\n"
    header += f"MandantenNr={client_number}\n"
    header += "Feldtrennzeichen=;\n"
    header += "Zahlenkomma=,\n"
    header += "Datumsformat=TT.MM.JJJJ\n"
    header += "Stringbegrenzer=\"\"\n"
    header += "Kommentarzeichen=*\n"
    header += f"StammdatenGueltigAb={datetime.now().strftime('%d.%m.%Y')}\n"
    header += "BetrieblichePNrVerwenden=Ja\n\n"
    
    return header

def generate_record_description():
    """Generate the [Satzbeschreibung] section of the LODAS file."""
    description = "[Satzbeschreibung]\n"
    # Only include the fields we're mapping
    description += "1;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;duevo_familienname#psd;duevo_vorname#psd;staatsangehoerigkeit#psd;geburtsdatum_ttmmjj#psd;geschlecht#psd;familienstand#psd;\n"
    
    # Add record description for employment type and designation
    description += "11;u_lod_psd_taetigkeit;pnr_betriebliche#psd;custom_arbeitsverhältnis#psd;designation#psd;\n\n"
    
    return description

def generate_employee_data(employees):
    """Generate the [Stammdaten] section of the LODAS file."""
    data = "[Stammdaten]\n"
    
    for employee in employees:
        mapped_data = map_employee_to_lodas(employee)
        
        # Format according to LODAS requirements - Personal data (only the fields we're mapping)
        line = '1;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["duevo_familienname"]}";'
        line += f'"{mapped_data["duevo_vorname"]}";'
        line += f'{mapped_data["staatsangehoerigkeit"]};'
        line += f'{mapped_data["geburtsdatum_ttmmjj"]};'
        line += f' {mapped_data["geschlecht"]};'
        line += f'{mapped_data["familienstand"]};\n'
        
        data += line
        
        # Employment type and designation data
        line = '11;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["custom_arbeitsverhältnis"]};'
        line += f'{mapped_data["designation"]};\n'
        
        data += line
    
    return data