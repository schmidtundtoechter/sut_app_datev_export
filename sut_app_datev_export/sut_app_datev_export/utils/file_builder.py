import frappe
import os
import tempfile
from datetime import datetime
from sut_app_datev_export.sut_app_datev_export.utils.employee_data import map_employee_to_lodas, map_child_to_lodas
from frappe import _

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
        
        # Count total employees including those with child records
        total_employees = len(employees)
        children_count = sum(len(emp.get('children', [])) for emp in employees)
        
        file_paths.append({
            'path': temp_path,
            'filename': filename,
            'company': company,
            'employee_count': total_employees,
            'children_count': children_count
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
    
    # Main employee data record
    description += "1;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;duevo_familienname#psd;duevo_vorname#psd;"
    description += "staatsangehoerigkeit#psd;geburtsdatum_ttmmjj#psd;geschlecht#psd;"
    description += "\n"
    
    # Address record
    description += "2;u_lod_psd_adresse;pnr_betriebliche#psd;adresse_strassenname#psd;adresse_strasse_nr#psd;"
    description += "adresse_ort#psd;adresse_plz#psd;adresse_anschriftenzusatz#psd;\n"
    
    # Employment record
    description += "3;u_lod_psd_beschaeftigung;pnr_betriebliche#psd;employment_type#psd;arbeitsverhältnis#psd;"
    description += "eintrittsdatum#psd;austrittsdatum#psd;ersteintritt#psd;\n"
    
    # Tax and social security record
    description += "4;u_lod_psd_steuer;pnr_betriebliche#psd;steueridentnummer#psd;steuerklasse#psd;konfession#psd;\n"
    
    # Bank details record
    description += "5;u_lod_psd_bank;pnr_betriebliche#psd;iban#psd;bic#psd;abweichender_kontoinhaber#psd;\n"
    
    # Additional personal details
    description += "6;u_lod_psd_personal;pnr_betriebliche#psd;email#psd;telefon#psd;akademischer_grad#psd;"
    description += "namenszusatz#psd;vorsatzwort#psd;geburtsname#psd;namenszusatz_geburt#psd;vorsatzwort_geburt#psd;"
    description += "geburtsort#psd;geburtsland#psd;familienstand#psd;versicherungsnummer#psd;\n"
    
    # Work information
    description += "7;u_lod_psd_arbeit;pnr_betriebliche#psd;summe_wochenarbeitszeit#psd;schwerbehinderung#psd;"
    description += "höchster_schulabschluss#psd;höchste_berufsausbildung#psd;befristung_gdb_bescheid#psd;"
    description += "befristung_arbeitserlaubnis#psd;befristung_aufenthaltserlaubnis#psd;alleinerziehend#psd;\n"
    
    # Salary information
    description += "8;u_lod_psd_gehalt;pnr_betriebliche#psd;basislohn#psd;stundenlohn#psd;stundenlohn_1#psd;"
    description += "summe_gehalt#psd;pauschalsteuer#psd;jobticket#psd;entlohnungsform#psd;\n"
    
    # Education and training
    description += "9;u_lod_psd_bildung;pnr_betriebliche#psd;arbeits_ausbildungsbeginn#psd;arbeits_ausbildungsende#psd;"
    description += "beginn_ausbildung#psd;ende_ausbildung_tatsaechlich#psd;ende_ausbildung_vertrag#psd;"
    description += "studienbescheinigung#psd;urlaubsanspruch#psd;grundurlaubsanspruch#psd;\n"
    
    # Child information
    description += "10;u_lod_psd_kindergeld;pnr_betriebliche#psd;kind_nummer#psd;vorname_kind#psd;familienname_kind#psd;"
    description += "geburtsdatum_kind#psd;anzahl_kinderfreibetraege#psd;\n"
    
    # Fixed salary components (wage types/salary elements)
    # description += "11;u_lod_psd_festbezuege;pnr_betriebliche#psd;lohnart_nummer#psd;betrag#psd;intervall#psd;kuerzung#psd;\n"
    description += "11;u_lod_psd_lohn_gehalt_bezuege;pnr_betriebliche#psd;lohnart_nummer#psd;betrag#psd;intervall#psd;kuerzung#psd;\n"
    # Additional flags and indicators
    description += "12;u_lod_psd_flags;pnr_betriebliche#psd;erstbeschaeftigung#psd;arbeitszeit_18_std#psd;"
    description += "automatische_loeschung#psd;arbeitsbescheinigung#psd;bescheinigung_313#psd;"
    description += "eel_meldung#psd;ehrenamtliche_taetigkeit#psd;einmalbezuege#psd;"
    description += "kennzeichnung_arbeitgeber#psd;ersteintrittsdatum_aag#psd;\n"
    
    # Office and official documents
    description += "13;u_lod_psd_dokumente;pnr_betriebliche#psd;ausweis_nr#psd;ausstellende_dienststelle#psd;"
    description += "sb_ausweis_gueltig#psd;ort_dienststelle#psd;datum_des_todes#psd;staatsangehoerigkeit_peb#psd;\n"
    
    description += "\n"
    return description

def generate_employee_data(employees):
    """Generate the [Stammdaten] section of the LODAS file."""
    data = "[Stammdaten]\n"
    
    for employee in employees:
        try:
            # Generate all records for this employee in correct order
            data += generate_complete_employee_records(employee)
        except Exception as e:
            frappe.log_error(f"Error generating records for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                          "DATEV Export Error")
            # Continue with next employee rather than failing the entire export
            continue
    
    return data

def generate_complete_employee_records(employee):
    """Generate all records for an employee including children and wage types in the correct order."""
    data = ""
    
    try:
        # Basic employee data (records 1-9)
        data += generate_employee_basic_records(employee)
        
        # Child records (record 10) - if any
        if 'children' in employee and employee['children']:
            for child in employee['children']:
                data += generate_child_record(employee, child)
        
        # Fixed salary components (record 11)
        data += generate_wage_type_records(employee)
        
        # Flags and documents (records 12-13)
        data += generate_employee_additional_records(employee)
    except Exception as e:
        frappe.log_error(f"Error in generate_complete_employee_records for {employee.get('name', 'Unknown')}: {str(e)}", 
                      "DATEV Export Error")
        raise
    
    return data

def generate_employee_basic_records(employee):
    """Generate records 1-9 for an employee."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # Record type 1: Main employee data
        line = '1;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["duevo_familienname"]}";'
        line += f'"{mapped_data["duevo_vorname"]}";'
        line += f'{mapped_data["staatsangehoerigkeit"]};'
        line += f'{mapped_data["geburtsdatum_ttmmjj"]};'
        line += f'{mapped_data["geschlecht"]};\n'
        data += line
        
        # Record type 2: Address
        line = '2;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["adresse_strassenname"]}";'
        line += f'"{mapped_data["adresse_strasse_nr"]}";'
        line += f'"{mapped_data["adresse_ort"]}";'
        line += f'{mapped_data["adresse_plz"]};'
        line += f'"{mapped_data["adresse_anschriftenzusatz"]}";\n'
        data += line
        
        # Record type 3: Employment
        line = '3;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["employment_type"]};'
        line += f'{mapped_data["arbeitsverhältnis"]};'
        line += f'{mapped_data["eintrittsdatum"]};'
        line += f'{mapped_data["austrittsdatum"]};'
        line += f'{mapped_data["ersteintritt"]};\n'
        data += line
        
        # Record type 4: Tax
        line = '4;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["steueridentnummer"]}";'
        line += f'{mapped_data["steuerklasse"]};'
        line += f'{mapped_data["konfession"]};\n'
        data += line
        
        # Record type 5: Bank
        line = '5;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["iban"]}";'
        line += f'"{mapped_data["bic"]}";'
        line += f'"{mapped_data["abweichender_kontoinhaber"]}";\n'
        data += line
        
        # Record type 6: Personal
        line = '6;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["email"]}";'
        line += f'"{mapped_data["telefon"]}";'
        line += f'"{mapped_data["akademischer_grad"]}";'
        line += f'"{mapped_data["namenszusatz"]}";'
        line += f'"{mapped_data["vorsatzwort"]}";'
        line += f'"{mapped_data["geburtsname"]}";'
        line += f'"{mapped_data["namenszusatz_geburt"]}";'
        line += f'"{mapped_data["vorsatzwort_geburt"]}";'
        line += f'"{mapped_data["geburtsort"]}";'
        line += f'{mapped_data["geburtsland"]};'
        line += f'{mapped_data["familienstand"]};'
        line += f'"{mapped_data["versicherungsnummer"]}";\n'
        data += line
        
        # Record type 7: Work
        line = '7;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["summe_wochenarbeitszeit"]};'
        line += f'{mapped_data["schwerbehinderung"]};'
        line += f'{mapped_data["höchster_schulabschluss"]};'
        line += f'{mapped_data["höchste_berufsausbildung"]};'
        line += f'{mapped_data["befristung_gdb_bescheid"]};'
        line += f'{mapped_data["befristung_arbeitserlaubnis"]};'
        line += f'{mapped_data["befristung_aufenthaltserlaubnis"]};'
        line += f'{mapped_data["alleinerziehend"]};\n'
        data += line
        
        # Record type 8: Salary
        line = '8;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["basislohn"]};'
        line += f'{mapped_data["stundenlohn"]};'
        line += f'{mapped_data["stundenlohn_1"]};'
        # line += f'{mapped_data["lfd_brutto"]};'
        line += f'{mapped_data["summe_gehalt"]};'
        line += f'{mapped_data["pauschalsteuer"]};'
        line += f'{mapped_data["jobticket"]};'
        line += f'{mapped_data["entlohnungsform"]};\n'
        data += line
        
        # Record type 9: Education
        line = '9;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        
        # Make sure these fields exist in mapped_data
        arbeits_ausbildungsbeginn = mapped_data.get("arbeits_ausbildungsbeginn", "")
        arbeits_ausbildungsende = mapped_data.get("arbeits_ausbildungsende", "")
        beginn_ausbildung = mapped_data.get("beginn_ausbildung", "")
        ende_ausbildung_tatsaechlich = mapped_data.get("ende_ausbildung_tatsaechlich", "")
        ende_ausbildung_vertrag = mapped_data.get("ende_ausbildung_vertrag", "")
        studienbescheinigung = mapped_data.get("studienbescheinigung", "")
        urlaubsanspruch = mapped_data.get("urlaubsanspruch", "")
        grundurlaubsanspruch = mapped_data.get("grundurlaubsanspruch", "")
        
        line += f'{arbeits_ausbildungsbeginn};'
        line += f'{arbeits_ausbildungsende};'
        line += f'{beginn_ausbildung};'
        line += f'{ende_ausbildung_tatsaechlich};'
        line += f'{ende_ausbildung_vertrag};'
        line += f'{studienbescheinigung};'
        line += f'{urlaubsanspruch};'
        line += f'{grundurlaubsanspruch};\n'
        data += line
        
    except KeyError as e:
        frappe.log_error(f"Missing key in employee data: {str(e)} for employee {employee.get('name', 'Unknown')}", 
                      "DATEV Export Error")
        # Create a placeholder for the missing field
        mapped_data[str(e).strip("'")] = ""
        # Try again recursively with the fixed data
        return generate_employee_basic_records(employee)
    except Exception as e:
        frappe.log_error(f"Error in generate_employee_basic_records: {str(e)}", "DATEV Export Error")
        raise
    
    return data

def generate_wage_type_records(employee):
    """Generate fixed wage type records (type 11) for an employee."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # Array to track which wage types have been processed
        processed_wage_types = [False] * 7  # For types 1-7
        
        # Process basic salary (Grundgehalt)
        basic_salary = determine_basic_salary(employee)
        if basic_salary:
            line = '11;'
            line += f'"{mapped_data["pnr_betriebliche"]}";'
            line += f'1;'  # lohnart_nummer 1 for Grundgehalt
            line += f'{basic_salary};'  # Amount
            line += f'0;'  # intervall (0 = monthly)
            line += f'0;\n'  # kuerzung (0 = no reduction)
            data += line
            processed_wage_types[0] = True
        
        # Process project salaries (custom_lohnart_p1 to custom_lohnart_p4)
        for i in range(1, 5):
            field_name = f'custom_lohnart_p{i}'
            project_salary_field = f'custom_gehalt_projekt_{i}'
            
            # Only include if field exists and has a value
            if (employee.get(field_name) and employee.get(field_name) != "999" and 
                employee.get(project_salary_field) and str(employee.get(project_salary_field)).strip()):
                
                line = '11;'
                line += f'"{mapped_data["pnr_betriebliche"]}";'
                line += f'{i+1};'  # lohnart_nummer (2-5 for project salaries)
                line += f'{employee.get(project_salary_field)};'  # Amount
                line += f'0;'  # intervall (0 = monthly)
                line += f'0;\n'  # kuerzung (0 = no reduction)
                data += line
                processed_wage_types[i] = True
        
        # Process supplementary salaries (custom_lohnart_z1, custom_lohnart_z2)
        for i in range(1, 3):
            field_name = f'custom_lohnart_z{i}'
            supplement_field = f'custom_zulage_zulage_{i}'
            
            # Only include if field exists and has a value
            if (employee.get(field_name) and employee.get(field_name) != "998" and 
                employee.get(supplement_field) and str(employee.get(supplement_field)).strip()):
                
                line = '11;'
                line += f'"{mapped_data["pnr_betriebliche"]}";'
                line += f'{i+5};'  # lohnart_nummer (6-7 for supplements)
                line += f'{employee.get(supplement_field)};'  # Amount
                line += f'0;'  # intervall (0 = monthly)
                line += f'0;\n'  # kuerzung (0 = no reduction)
                data += line
                processed_wage_types[i+4] = True
        
        # Add missing wage type records with zero values
        for i in range(7):
            if not processed_wage_types[i]:
                wage_type_number = i + 1
                line = '11;'
                line += f'"{mapped_data["pnr_betriebliche"]}";'
                line += f'{wage_type_number};'  # lohnart_nummer
                line += f'0;'  # Amount (zero)
                line += f'0;'  # intervall (0 = monthly)
                line += f'0;\n'  # kuerzung (0 = no reduction)
                data += line
    except Exception as e:
        frappe.log_error(f"Error in generate_wage_type_records for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                      "DATEV Export Error")
        # Return empty string to continue with export
        return ""
    
    return data

def determine_basic_salary(employee):
    """Determine the basic salary based on the logic in the requirements."""
    try:
        # Check if any project salaries are active
        has_project_salary = False
        for i in range(1, 5):
            project_field = f'custom_gehalt_projekt_{i}'
            if (employee.get(project_field) and 
                str(employee.get(project_field)).strip() and 
                float(employee.get(project_field, 0)) > 0):
                has_project_salary = True
                break
        
        # Check additional wage criteria
        has_zusatzliche_vergutung = False
        for field in ['custom_ist_zusätzliche_vergütung_zum_grundgehalt', 
                    'custom_ist_zusätzliche_vergütung_zum_grundgehalt_1',
                    'custom_ist_zusätzliche_vergütung_zum_grundgehalt_2',
                    'custom_ist_zusätzliche_vergütung_zum_grundgehalt_3']:
            if employee.get(field) and str(employee.get(field)).strip():
                has_zusatzliche_vergutung = True
                break
        
        # Determine which basic salary to use based on the logic in Image 2
        if has_project_salary and not has_zusatzliche_vergutung:
            # Project salary is exclusive - no basic salary
            return None
        elif employee.get('custom_gehalt_des_grundvertrags') and str(employee.get('custom_gehalt_des_grundvertrags')).strip():
            # Use the explicitly defined basic salary
            return employee.get('custom_gehalt_des_grundvertrags')
        elif not has_project_salary and employee.get('custom_lohnart_gg') and employee.get('custom_lohnart_gg') != "999":
            # If no project salary, use custom_lohnart_gg if available
            return employee.get('custom_lohnart_gg')
        
        # Default case: no basic salary to record
        return None
    except Exception as e:
        frappe.log_error(f"Error in determine_basic_salary for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                      "DATEV Export Error")
        # Return None for safety
        return None

def generate_employee_additional_records(employee):
    """Generate records 12-13 for an employee (previously 11-12)."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # Record type 12: Flags (previously 11)
        line = '12;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        
        # Use safe access for all fields with defaults
        erstbeschaeftigung = mapped_data.get("erstbeschaeftigung", "")
        arbeitszeit_18_std = mapped_data.get("arbeitszeit_18_std", "")
        automatische_loeschung = mapped_data.get("automatische_loeschung", "")
        arbeitsbescheinigung = mapped_data.get("arbeitsbescheinigung", "")
        bescheinigung_313 = mapped_data.get("bescheinigung_313", "")
        eel_meldung = mapped_data.get("eel_meldung", "")
        ehrenamtliche_taetigkeit = mapped_data.get("ehrenamtliche_taetigkeit", "")
        einmalbezuege = mapped_data.get("einmalbezuege", "")
        kennzeichnung_arbeitgeber = mapped_data.get("kennzeichnung_arbeitgeber", "")
        ersteintrittsdatum_aag = mapped_data.get("ersteintrittsdatum_aag", "")
        
        line += f'{erstbeschaeftigung};'
        line += f'{arbeitszeit_18_std};'
        line += f'{automatische_loeschung};'
        line += f'{arbeitsbescheinigung};'
        line += f'{bescheinigung_313};'
        line += f'{eel_meldung};'
        line += f'{ehrenamtliche_taetigkeit};'
        line += f'{einmalbezuege};'
        line += f'{kennzeichnung_arbeitgeber};'
        line += f'{ersteintrittsdatum_aag};\n'
        data += line
        
        # Record type 13: Documents (previously 12)
        line = '13;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        
        # Use safe access for all fields with defaults
        ausweis_nr = mapped_data.get("ausweis_nr", "")
        ausstellende_dienststelle = mapped_data.get("ausstellende_dienststelle", "")
        sb_ausweis_gueltig = mapped_data.get("sb_ausweis_gueltig", "")
        ort_dienststelle = mapped_data.get("ort_dienststelle", "")
        datum_des_todes = mapped_data.get("datum_des_todes", "")
        staatsangehoerigkeit_peb = mapped_data.get("staatsangehoerigkeit_peb", "")
        
        line += f'"{ausweis_nr}";'
        line += f'"{ausstellende_dienststelle}";'
        line += f'{sb_ausweis_gueltig};'
        line += f'"{ort_dienststelle}";'
        line += f'{datum_des_todes};'
        line += f'{staatsangehoerigkeit_peb};\n'
        data += line
        
    except KeyError as e:
        frappe.log_error(f"Missing key in employee data: {str(e)} for employee {employee.get('name', 'Unknown')}", 
                      "DATEV Export Error")
        # Create a placeholder for the missing field
        mapped_data[str(e).strip("'")] = ""
        # Try again recursively with the fixed data
        return generate_employee_additional_records(employee)
    except Exception as e:
        frappe.log_error(f"Error in generate_employee_additional_records: {str(e)}", "DATEV Export Error")
        # Return empty data to avoid failing the export completely
        return ""
    
    return data

def generate_child_record(employee, child):
    """Generate a child record (type 10) for an employee."""
    data = ""
    
    try:
        mapped_data = map_child_to_lodas(employee, child)
        
        # Record type 10: Child information
        line = '10;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["kind_nummer"]};'
        line += f'"{mapped_data["vorname_kind"]}";'
        line += f'"{mapped_data["familienname_kind"]}";'
        line += f'{mapped_data["geburtsdatum_kind"]};'
        line += f'{mapped_data["anzahl_kinderfreibetraege"]};\n'
        
        data += line
    except Exception as e:
        frappe.log_error(f"Error generating child record for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                       "DATEV Export Error")
        # Return empty string to continue with export
        return ""
    
    return data

def generate_single_employee_file(employee, settings):
    """Generate LODAS file for a single employee."""
    consultant_number = settings.consultant_number
    
    # Get company to client number mapping
    client_numbers = {}
    for mapping in settings.company_client_mapping:
        client_numbers[mapping.company] = mapping.client_number
    
    # Skip if no mapping exists for the employee's company
    if employee['company'] not in client_numbers:
        frappe.throw(_("No client number mapping found for company: {0}").format(employee['company']))
    
    client_number = client_numbers[employee['company']]
    
    # Get Personalerfassungsbogen data for the employee if not already present
    if not employee.get('children') and frappe.db.exists('DocType', 'Personalerfassungsbogen'):
        try:
            personalerfassungsbogen = frappe.get_all(
                'Personalerfassungsbogen',
                filters={'employee': employee['name']},
                fields=['name']
            )
            
            if personalerfassungsbogen:
                peb_name = personalerfassungsbogen[0].name
                
                # Get table columns to check if the child table exists
                if frappe.db.exists('DocType', 'Kinder Tabelle'):
                    children = frappe.get_all(
                        'Kinder Tabelle',
                        filters={'parent': peb_name},
                        fields=[
                            'kind_nummer',
                            'vorname_personaldaten_kinderdaten_allgemeine_angaben',
                            'familienname_personaldaten_kinderdaten_allgemeine_angaben',
                            'geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben'
                        ],
                        order_by='kind_nummer asc'
                    )
                    
                    if children:
                        employee['children'] = children
        except Exception as e:
            frappe.log_error(f"Error fetching children for single employee export: {str(e)}", 
                            "DATEV Export Error")
    
    # Generate file content
    content = generate_lodas_file_header(consultant_number, client_number)
    content += generate_record_description()
    content += generate_employee_data([employee])
    
    # Create temporary file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"DATEV_LODAS_Single_{employee['name']}_{timestamp}.txt"
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Count children
    children_count = len(employee.get('children', []))
    
    return [{'path': temp_path,
    'filename': filename,
    'company': employee['company'],
    'employee_count': 1,
    'children_count': children_count
}]

