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
    """Generate the [Satzbeschreibung] section following exact Excel mapping."""
    description = "[Satzbeschreibung]\n"
    
    # Record 1: u_lod_psd_mitarbeiter (Main employee data - following Excel mapping)
    description += "1;u_lod_psd_mitarbeiter;pnr#psd;duevo_familienname#psd;duevo_vorname#psd;"
    description += "geschlecht#psd;geburtsdatum_ttmmjj#psd;adresse_nation_kz#psd;duevo_titel#psd;"
    description += "kz_alleinerziehend#psd;adresse_anschriftenzusatz#psd;arbeitserlaubnis#psd;"
    description += "aufenthaltserlaubnis#psd;geburtsland#psd;gebname#psd;gebort#psd;"
    description += "email#psd;kz_erstbeschaeftigung#psd;ersteintrittsdatum#psd;"
    description += "verw_ersteintr_elena_bn#psd;adresse_strasse_nr#psd;adresse_ort#psd;"
    description += "adresse_plz#psd;adresse_strassenname#psd;schwerbeschaedigt#psd;"
    description += "staatsangehoerigkeit#psd;telefon#psd;url_tage_jhrl#psd;familienstand#psd;"
    description += "duevo_namenszusatz#psd;duevo_vorsatzwort#psd;nazu_gebname#psd;"
    description += "vorsatzwort_gebname#psd;datum_studienbesch#psd;loesch_nach_austr_unterdr#psd;\n"
    
    # Record 2: u_lod_psd_taetigkeit (Job/Activity - following Excel mapping)  
    description += "2;u_lod_psd_taetigkeit;pnr#psd;berufsbezeichnung#psd;kst_abteilungs_nr#psd;"
    description += "schulabschluss#psd;ausbildungsabschluss#psd;sba_ausbildungsbeginn#psd;"
    description += "sba_ausbildungsende#psd;datum_ben_ergeb_pruef#psd;ehrenamtliche_taetigkeit#psd;\n"
    
    # Record 3: u_lod_psd_beschaeftigung (Employment - following Excel mapping)
    description += "3;u_lod_psd_beschaeftigung;pnr#psd;arbeitsverhaeltnis#psd;eintrittdatum#psd;"
    description += "austrittdatum#psd;kz_arbbes_nae_abrech_autom#psd;eel_nach_austritt_kz#psd;"
    description += "ebz_nach_austritt_kz#psd;kz_besch_nebenbesch#psd;\n"
    
    # Record 4: u_lod_psd_steuer (Tax - following Excel mapping)
    description += "4;u_lod_psd_steuer;pnr#psd;identifikationsnummer#psd;st_klasse#psd;"
    description += "konf_an#psd;kfb_anzahl#psd;pausch_einhtl_2#psd;els_2_haupt_ag_kz#psd;\n"
    
    # Record 5: u_lod_psd_ma_bank (Bank - keep current as shown in images)
    description += "5;u_lod_psd_ma_bank;pnr#psd;ma_iban#psd;ma_bic#psd;"
    description += "ma_bank_kto_inhaber_abw#psd;\n"
    
    # Record 6: u_lod_psd_schwerbeh (Disability - following Excel mapping)
    description += "6;u_lod_psd_schwerbeh;pnr#psd;sba_sb_ausweis_bis#psd;sba_unter_18_std_aa_kz#psd;"
    description += "sba_kz_dienststelle#psd;sba_az_geschaeftsstelle#psd;sba_ort_dienstelle#psd;"
    description += "sba_sb_ausweis_ab#psd;\n"
    
    # Record 7: u_lod_psd_arbeitszeit_regelm (Working time - following Excel mapping)
    description += "7;u_lod_psd_arbeitszeit_regelm;pnr#psd;az_wtl_indiv#psd;urlaubsanspr_pro_jahr#psd;\n"
    
    # Record 8: u_lod_psd_lohn_gehalt_bezuege (Salary - keep current as shown in images)
    description += "8;u_lod_psd_lohn_gehalt_bezuege;pnr#psd;std_lohn_1#psd;lfd_brutto_vereinbart#psd;\n"
    
    # Record 9: u_lod_psd_fahrtkostenzuschuss (Travel subsidy - following Excel mapping)
    description += "9;u_lod_psd_fahrtkostenzuschuss;pnr#psd;jobticket#psd;\n"
    
    # Record 10: u_lod_psd_besonderheiten (Special features - following Excel mapping)
    description += "10;u_lod_psd_besonderheiten;pnr#psd;entlohnungsform#psd;\n"
    
    # Record 11: u_lod_psd_kindergeld (Children - keep current as shown in images)
    description += "11;u_lod_psd_kindergeld;pnr#psd;kind_nr#psd;kind_vorname#psd;"
    description += "kind_nachname#psd;kind_geburtsdatum#psd;\n"
    
    # Record 12: u_lod_psd_festbezuege (Fixed salary - keep current as shown in images)
    description += "12;u_lod_psd_festbezuege;pnr#psd;lohnart_nummer#psd;betrag#psd;"
    description += "intervall#psd;kuerzung#psd;feld6#psd;feld7#psd;\n"
    
    # Additional records following Excel mapping for missing fields
    # Record 13: u_lod_psd_st_besond (Special tax)
    description += "13;u_lod_psd_st_besond;pnr#psd;sfn_basislohn#psd;sfn_std_lohn#psd;\n"
    
    # Record 14: u_lod_mpd_arbeitszeit_sonst (Other working time)
    description += "14;u_lod_mpd_arbeitszeit_sonst;pnr#psd;urlaubsanspr_pro_jahr#mpd;\n"
    
    # Record 15: u_lod_psd_a1_anvb (A1 certificate)
    description += "15;u_lod_psd_a1_anvb;pnr#psd;adresse_plz#psd;\n"
    
    # # Record 16: u_lod_psd_fehlzeiten (Absence times)
    # description += "16;u_lod_psd_fehlzeiten;pnr#psd;kind_nr#psd;\n"


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
    """Generate all records for an employee following Excel structure."""
    data = ""
    
    try:
        # Main employee records (records 1-10 + additional records)
        data += generate_main_employee_records(employee)
        
        # Child records (record 11) - if any - keep current logic as shown in images
        if 'children' in employee and employee['children']:
            for child in employee['children']:
                data += generate_child_record(employee, child)
        
        # Fixed salary components (record 12) - keep current logic as shown in images
        data += generate_festbezuege_records(employee)
        
        # Additional special records (13-16)
        data += generate_additional_records(employee)
        
    except Exception as e:
        frappe.log_error(f"Error in generate_complete_employee_records for {employee.get('name', 'Unknown')}: {str(e)}", 
                      "DATEV Export Error")
        raise
    
    return data

def generate_main_employee_records(employee):
    """Generate records 1-10 following exact Excel field mapping."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # Record type 1: Main employee data (following Excel mapping exactly)
        line = '1;'
        line += f'"{mapped_data["pnr"]}";' # Employee number
        line += f'"{mapped_data["duevo_familienname"]}";'  # Last name
        line += f'"{mapped_data["duevo_vorname"]}";'       # First name
        line += f'{mapped_data["geschlecht"]};'            # Gender
        line += f'{mapped_data["geburtsdatum_ttmmjj"]};'    # Birth date
        line += f'{mapped_data["adresse_nation_kz"]};'      # Country (Excel mapping: adresse_nation_kz)
        line += f'"{mapped_data["duevo_titel"]}";'          # Academic title
        line += f'{mapped_data["kz_alleinerziehend"]};'     # Single parent
        line += f'"{mapped_data["adresse_anschriftenzusatz"]}";'  # Address addition
        line += f'{mapped_data["arbeitserlaubnis"]};'       # Work permit
        line += f'{mapped_data["aufenthaltserlaubnis"]};'   # Residence permit
        line += f'{mapped_data["geburtsland"]};'            # Birth country
        line += f'"{mapped_data["gebname"]}";'              # Birth name
        line += f'"{mapped_data["gebort"]}";'               # Birth place
        line += f'"{mapped_data["email"]}";'                # Email
        line += f'{mapped_data["kz_erstbeschaeftigung"]};'  # First employment
        line += f'{mapped_data["ersteintrittsdatum"]};'     # First entry date
        line += f'{mapped_data["verw_ersteintr_elena_bn"]};'  # Use first entry for AAG
        line += f'"{mapped_data["adresse_strasse_nr"]}";'   # House number
        line += f'"{mapped_data["adresse_ort"]}";'          # City
        line += f'{mapped_data["adresse_plz"]};'            # Postal code
        line += f'"{mapped_data["adresse_strassenname"]}";' # Street name
        line += f'{mapped_data["schwerbeschaedigt"]};'      # Disability
        line += f'{mapped_data["staatsangehoerigkeit"]};'   # Nationality
        line += f'"{mapped_data["telefon"]}";'              # Phone
        line += f'{mapped_data["url_tage_jhrl"]};'          # Vacation days yearly
        line += f'{mapped_data["familienstand"]};'          # Marital status (keep current)
        line += f'"{mapped_data["duevo_namenszusatz"]}";'   # Name addition
        line += f'"{mapped_data["duevo_vorsatzwort"]}";'    # Prefix word
        line += f'"{mapped_data["nazu_gebname"]}";'         # Birth name addition
        line += f'"{mapped_data["vorsatzwort_gebname"]}";'  # Birth name prefix
        line += f'{mapped_data["datum_studienbesch"]};'     # Study certificate date
        line += f'{mapped_data["loesch_nach_austr_unterdr"]};\n'  # Suppress automatic deletion
        data += line
        
        # Record type 2: Job/Activity (following Excel mapping)
        line = '2;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'"{mapped_data["berufsbezeichnung"]}";'     # Job title
        line += f'"{mapped_data["kst_abteilungs_nr"]}";'    # Department number
        line += f'{mapped_data["schulabschluss"]};'         # School education
        line += f'{mapped_data["ausbildungsabschluss"]};'   # Professional education
        line += f'{mapped_data["sba_ausbildungsbeginn"]};'  # Training start
        line += f'{mapped_data["sba_ausbildungsende"]};'    # Training end
        line += f'{mapped_data["datum_ben_ergeb_pruef"]};'  # Actual training end
        line += f'{mapped_data["ehrenamtliche_taetigkeit"]};\n'  # Voluntary work
        data += line
        
        # Record type 3: Employment (following Excel mapping)
        line = '3;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["arbeitsverhaeltnis"]};'      # Employment type
        line += f'{mapped_data["eintrittdatum"]};'          # Entry date
        line += f'{mapped_data["austrittdatum"]};'          # Exit date
        line += f'{mapped_data["kz_arbbes_nae_abrech_autom"]};'  # Work certificate
        line += f'{mapped_data["eel_nach_austritt_kz"]};'   # EEL after exit
        line += f'{mapped_data["ebz_nach_austritt_kz"]};'   # One-time payments after exit
        line += f'{mapped_data["kz_besch_nebenbesch"]};\n'  # Certificate § 313
        data += line
        
        # Record type 4: Tax (following Excel mapping)
        line = '4;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'"{mapped_data["identifikationsnummer"]}";'  # Tax ID
        line += f'{mapped_data["st_klasse"]};'              # Tax class
        line += f'{mapped_data["konf_an"]};'                # Religion
        line += f'{mapped_data["kfb_anzahl"]};'             # Number of child allowances
        line += f'{mapped_data["pausch_einhtl_2"]};'        # Flat tax
        line += f'{mapped_data["els_2_haupt_ag_kz"]};\n'    # Main/secondary employer
        data += line
        
        # Record type 5: Bank (keep current as shown in images)
        line = '5;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'"{mapped_data["ma_iban"]}";'
        line += f'"{mapped_data["ma_bic"]}";'
        line += f'"{mapped_data["ma_bank_kto_inhaber_abw"]}";\n'
        data += line
        
        # Record type 6: Disability (following Excel mapping)
        line = '6;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["sba_sb_ausweis_bis"]};'     # Disability ID valid until
        line += f'{mapped_data["sba_unter_18_std_aa_kz"]};' # Under 18 hours with AA approval
        line += f'"{mapped_data["sba_kz_dienststelle"]}";'  # Issuing authority
        line += f'"{mapped_data["sba_az_geschaeftsstelle"]}";'  # ID number/file number
        line += f'"{mapped_data["sba_ort_dienstelle"]}";'   # Authority location
        line += f'{mapped_data["sba_sb_ausweis_ab"]};\n'    # Disability ID valid from
        data += line
        
        # Record type 7: Working time (following Excel mapping)
        line = '7;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["az_wtl_indiv"]};'           # Weekly working hours
        line += f'{mapped_data["urlaubsanspr_pro_jahr"]};\n'  # Basic vacation entitlement
        data += line
        
        # Record type 8: Salary (keep current as shown in images)
        line = '8;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["std_lohn_1"]};'             # Hourly wage 1
        line += f'{mapped_data["lfd_brutto_vereinbart"]};\n'  # Current gross agreed
        data += line
        
        # Record type 9: Travel subsidy (following Excel mapping)
        line = '9;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["jobticket"]};\n'            # Job ticket
        data += line
        
        # Record type 10: Special features (following Excel mapping)
        line = '10;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["entlohnungsform"]};\n'      # Remuneration form
        data += line
        
    except KeyError as e:
        frappe.log_error(f"Missing key in employee data: {str(e)} for employee {employee.get('name', 'Unknown')}", 
                      "DATEV Export Error")
        # Create a placeholder for the missing field
        mapped_data[str(e).strip("'")] = ""
        # Try again recursively with the fixed data
        return generate_main_employee_records(employee)
    except Exception as e:
        frappe.log_error(f"Error in generate_main_employee_records: {str(e)}", "DATEV Export Error")
        raise
    
    return data

def generate_child_record(employee, child):
    """Generate a child record (type 11) - keep current logic as shown in images."""
    data = ""
    
    try:
        mapped_data = map_child_to_lodas(employee, child)
        
        # Record type 11: Child information (keep current structure)
        line = '11;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data["kind_nr"]};'                # Child number
        line += f'"{mapped_data["kind_vorname"]}";'         # Child first name
        line += f'"{mapped_data["kind_nachname"]}";'        # Child last name
        line += f'{mapped_data["kind_geburtsdatum"]};\n'    # Child birth date
        
        data += line
    except Exception as e:
        frappe.log_error(f"Error generating child record for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                       "DATEV Export Error")
        # Return empty string to continue with export
        return ""
    
    return data

def generate_festbezuege_records(employee):
    """Generate festbezuege records (type 12) - keep current logic as shown in images."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # Keep the existing 7 wage type records logic as shown in images
        # 1. Grundgehalt (GG) - lohnart_nummer 1
        basic_salary = determine_basic_salary(employee)
        lohnart_gg = employee.get('custom_lohnart_gg', "999")
        
        # Always output record 1 (Grundgehalt)
        line = '12;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{lohnart_gg};'  # Use the actual lohnart_nummer value or 999 default
        
        # Use actual amount if available, otherwise 0
        amount = "0"
        if basic_salary:
            amount = basic_salary
        
        line += f'{amount};'  # Amount
        line += f'0;'  # intervall (0 = monthly)
        line += f'0;\n'  # kuerzung (0 = no reduction)
        data += line
        
        # 2-5. Project salaries (P1-P4) - lohnart_nummer 2-5
        for i in range(1, 5):
            field_name = f'custom_lohnart_p{i}'
            project_salary_field = f'custom_gehalt_projekt_{i}'
            
            # Always get lohnart_nummer (default 999 if not available)
            lohnart_nummer = employee.get(field_name, "999")
            
            # Always output the festbezuege entry 
            line = '12;'
            line += f'"{mapped_data["pnr"]}";'
            line += f'{lohnart_nummer};'  # Use the actual lohnart_nummer value
            
            # Use actual amount if available, otherwise 0
            amount = "0"
            if employee.get(project_salary_field) and str(employee.get(project_salary_field)).strip():
                amount = employee.get(project_salary_field)
            
            line += f'{amount};'  # Amount
            line += f'0;'  # intervall (0 = monthly)
            line += f'0;\n'  # kuerzung (0 = no reduction)
            data += line
        
        # 6-7. Supplementary salaries (Z1-Z2) - lohnart_nummer 6-7
        for i in range(1, 3):
            field_name = f'custom_lohnart_z{i}'
            supplement_field = f'custom_zulage_zulage_{i}'
            
            # Always get lohnart_nummer (default 998 if not available)
            lohnart_nummer = employee.get(field_name, "998")
            
            # Always output the festbezuege entry
            line = '12;'
            line += f'"{mapped_data["pnr"]}";'
            line += f'{lohnart_nummer};'  # Use the actual lohnart_nummer value
            
            # Use actual amount if available, otherwise 0
            amount = "0"
            if employee.get(supplement_field) and str(employee.get(supplement_field)).strip():
                amount = employee.get(supplement_field)
            
            line += f'{amount};'  # Amount
            line += f'0;'  # intervall (0 = monthly)
            line += f'0;\n'  # kuerzung (0 = no reduction)
            data += line
    except Exception as e:
        frappe.log_error(f"Error in generate_festbezuege_records for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                      "DATEV Export Error")
        # Return empty string to continue with export
        return ""
    
    return data

def generate_additional_records(employee):
    """Generate additional records 13-16 following Excel mapping."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # Record type 13: u_lod_psd_st_besond (Special tax)
        line = '13;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data.get("sfn_basislohn", "")};'  # Base salary (removed field)
        line += f'{mapped_data.get("sfn_std_lohn", "")};\n'  # Standard hourly wage
        data += line
        
        # Record type 14: u_lod_mpd_arbeitszeit_sonst (Other working time)
        line = '14;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data.get("urlaubsanspr_pro_jahr_mpd", "")};\n'  # MPD working time
        data += line
        
        # Record type 15: u_lod_psd_a1_anvb (A1 certificate)
        line = '15;'
        line += f'"{mapped_data["pnr"]}";'
        line += f'{mapped_data.get("adresse_plz", "")};\n'  # Postal code for A1
        data += line
        
        # Record type 16: u_lod_psd_fehlzeiten (Absence times)
        # line = '16;'
        # line += f'"{mapped_data["pnr"]}";'
        # line += f'{mapped_data.get("kind_nr", "")};\n'  # Child number for absence
        # data += line

        
    except Exception as e:
        frappe.log_error(f"Error in generate_additional_records: {str(e)}", "DATEV Export Error")
        # Return empty data to avoid failing the export completely
        return ""
    
    return data

def determine_basic_salary(employee):
    """Determine the basic salary - keep current logic as shown in images."""
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
        
        # Determine which basic salary to use
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
    
    return [{
        'path': temp_path,
        'filename': filename,
        'company': employee['company'],
        'employee_count': 1,
        'children_count': children_count

    }]

