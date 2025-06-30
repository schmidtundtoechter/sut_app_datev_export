import frappe
from frappe.utils import now_datetime, format_datetime  # Add these imports for timezone handling
import os
import tempfile
from datetime import datetime
from sut_app_datev_export.sut_app_datev_export.utils.employee_data import map_employee_to_lodas, map_child_to_lodas
from frappe import _

def generate_lodas_files(employees_by_company, settings):
    """Generate LODAS files for each company - FIXED: Use correct timezone for filenames."""
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
            # frappe.log_error(f"No client number mapping for company: {company}", 
            #                "DATEV Export Error")
            continue
        
        client_number = client_numbers[company]
        
        # Generate file content - NEW: Pass settings for dynamic restrictions
        content = generate_lodas_file_header(consultant_number, client_number)
        content += generate_record_description()
        content += generate_employee_data(employees, settings)
        
        # Create temporary file with correct timezone timestamp
        # FIXED: Use now_datetime() and format with correct timezone
        current_time = now_datetime()
        timestamp = format_datetime(current_time, "yyyyMMddHHmmss")
        filename = f"DATEV_LODAS_{company.replace(' ', '_')}_{timestamp}.txt"
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        
        with open(temp_path, 'w', encoding='cp1252', newline='\r\n') as f:
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
    """Generate the [Allgemein] section of the LODAS file - FIXED: Use correct timezone."""
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
    
    # FIXED: Use first day of current month instead of current date
    current_time = now_datetime()
    # Get first day of current month
    first_day_of_month = current_time.replace(day=1)
    formatted_date = format_datetime(first_day_of_month, "dd.MM.yyyy")
    header += f"StammdatenGueltigAb={formatted_date}\n"
    header += "BetrieblichePNrVerwenden=Nein\n\n"
    
    return header

def generate_record_description():
    """Generate the [Satzbeschreibung] section following exact Excel mapping."""
    description = "[Satzbeschreibung]\n"
    
    # Record 1: u_lod_psd_mitarbeiter (Main employee data - following Excel mapping) - small change
    description += "1;u_lod_psd_mitarbeiter;pnr#psd;duevo_familienname#psd;duevo_vorname#psd;"
    description += "geschlecht#psd;geburtsdatum_ttmmjj#psd;adresse_nation_kz#psd;duevo_titel#psd;"
    description += "kz_alleinerziehend#psd;adresse_anschriftenzusatz#psd;arbeitserlaubnis#psd;"
    description += "aufenthaltserlaubnis#psd;geburtsland#psd;gebname#psd;gebort#psd;"
    description += "email#psd;ersteintrittsdatum#psd;"
    description += "verw_ersteintr_elena_bn#psd;adresse_strasse_nr#psd;adresse_ort#psd;"
    description += "adresse_plz#psd;adresse_strassenname#psd;schwerbeschaedigt#psd;"
    description += "staatsangehoerigkeit#psd;telefon#psd;familienstand#psd;"
    description += "duevo_namenszusatz#psd;duevo_vorsatzwort#psd;nazu_gebname#psd;"
    description += "vorsatzwort_gebname#psd;datum_studienbesch#psd;loesch_nach_austr_unterdr#psd;sozialversicherung_nr#psd;sba_ausbildungsbeginn#psd;sba_ausbildungsende#psd;ebz_nach_austritt_kz#psd;datum_tod#psd;\n"
    
    # Record 2: u_lod_psd_taetigkeit (Job/Activity - FIXED: Added additional field for fixed value 1)
    description += "2;u_lod_psd_taetigkeit;pnr#psd;berufsbezeichnung#psd;beschaeft_nr#psd;kst_abteilungs_nr#psd;"
    description += "schulabschluss#psd;ausbildungsabschluss#psd;ausbildungsbeginn#psd;vorr_ausbildungsende#psd;"
    description += "datum_ben_ergeb_pruef#psd;ehrenamtliche_taetigkeit#psd;kz_erstbeschaeftigung#psd;kz_besch_nebenbesch#psd;\n"
    
    # Record 3: u_lod_psd_beschaeftigung (Employment - following Excel mapping)
    description += "3;u_lod_psd_beschaeftigung;pnr#psd;arbeitsverhaeltnis#psd;eintrittdatum#psd;"
    description += "austrittdatum#psd;eel_nach_austritt_kz#psd;\n"
    
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
    description += "7;u_lod_psd_arbeitszeit_regelm;pnr#psd;az_wtl_indiv#psd;url_tage_jhrl#psd;urlaubsanspr_pro_jahr#psd;\n"
    
    # Record 8: u_lod_psd_lohn_gehalt_bezuege (Salary - keep current as shown in images)
    description += "8;u_lod_psd_lohn_gehalt_bezuege;pnr#psd;std_lohn_1#psd;std_lohn_2#psd;lfd_brutto_vereinbart#psd;\n"
    
    # Record 9: u_lod_psd_fahrtkostenzuschuss (Travel subsidy - following Excel mapping)
    description += "9;u_lod_psd_fahrtkostenzuschuss;pnr#psd;jobticket#psd;\n"
    
    # Record 10: u_lod_psd_besonderheiten (Special features - following Excel mapping)
    description += "10;u_lod_psd_besonderheiten;pnr#psd;entlohnungsform#psd;\n"
    
    # Record 11: u_lod_psd_kindergeld (Children - keep current as shown in images)
    description += "11;u_lod_psd_kindergeld;pnr#psd;kind_nr#psd;kind_vorname#psd;"
    description += "kind_nachname#psd;kind_geburtsdatum#psd;\n"
    
    # Record 12: u_lod_psd_festbezuege (Fixed salary - keep current as shown in images)
    description += "12;u_lod_psd_festbezuege;pnr#psd;festbez_id#psd;lohnart_nr#psd;betrag#psd;"
    description += "intervall#psd;kuerzung#psd;\n"

    description += "\n"
    return description

def format_numeric_value(value):
    """Format numeric values to use comma instead of dot for decimal separator."""
    if value is None or value == "" or str(value).lower() == "none":
        return ""
    
    # Convert to string if not already
    str_value = str(value)
    
    # If it's a number, format it properly
    try:
        # Try to convert to float to check if it's numeric
        float_value = float(str_value)
        # Format with 2 decimal places and replace dot with comma
        formatted = f"{float_value:.2f}".replace('.', ',')
        return formatted
    except (ValueError, TypeError):
        # If it's not a number, return empty
        return ""

def clean_value(value):
    """Clean values - replace 'None' and empty strings with empty."""
    if value is None or value == "" or str(value).lower() == "none":
        return ""
    return str(value)

def format_field(value, is_numeric=False, needs_quotes=True):
    """Format field values according to DATEV requirements."""
    if is_numeric:
        cleaned = format_numeric_value(value)
    else:
        cleaned = clean_value(value)
    
    if cleaned == "":
        return ""  # Empty field, no quotes
    elif needs_quotes:
        return f'"{cleaned}"'
    else:
        return cleaned

def generate_employee_data(employees, settings):
    """Generate the [Stammdaten] section of the LODAS file - NEW: with settings parameter."""
    data = "[Stammdaten]\n"
    
    for employee in employees:
        try:
            # Generate all records for this employee in correct order - NEW: Pass settings
            data += generate_complete_employee_records(employee, settings)
        except Exception as e:
            # frappe.log_error(f"Error generating records for employee {employee.get('name', 'Unknown')}: {str(e)}", 
            #               "DATEV Export Error")
            # Continue with next employee rather than failing the entire export
            continue
    
    return data

def generate_complete_employee_records(employee, settings):
    """Generate all records for an employee following Excel structure - NEW: with settings parameter."""
    data = ""
    
    try:
        # Main employee records (records 1-10 + additional records) - NEW: Pass settings
        data += generate_main_employee_records(employee, settings)
        
        # Child records (record 11) - ONLY if child data exists
        if has_child_data(employee):
            for child in employee['children']:
                data += generate_child_record(employee, child)
        
        # Fixed salary components (record 12)
        data += generate_festbezuege_records(employee)
        
    except Exception as e:
        # frappe.log_error(f"Error in generate_complete_employee_records for {employee.get('name', 'Unknown')}: {str(e)}", 
        #               "DATEV Export Error")
        raise
    
    return data

def has_child_data(employee):
    """Check if employee has any child data to export."""
    if not employee.get('children'):
        return False
    
    # Check if any child has meaningful data
    for child in employee['children']:
        if (child.get('kind_nummer') or 
            child.get('vorname_personaldaten_kinderdaten_allgemeine_angaben') or 
            child.get('familienname_personaldaten_kinderdaten_allgemeine_angaben') or 
            child.get('geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben')):
            return True
    
    return False

def has_disability_data(employee):
    """Check if employee has any disability data to export."""
    mapped_data = map_employee_to_lodas(employee)
    
    # Check all disability-related fields
    disability_fields = [
        mapped_data.get("sba_sb_ausweis_bis", ""),
        mapped_data.get("sba_unter_18_std_aa_kz", ""),
        mapped_data.get("sba_kz_dienststelle", ""),
        mapped_data.get("sba_az_geschaeftsstelle", ""),
        mapped_data.get("sba_ort_dienstelle", ""),
        mapped_data.get("sba_sb_ausweis_ab", "")
    ]
    
    # Return True if any field has data
    for field_value in disability_fields:
        if field_value and str(field_value).strip():
            return True
    
    return False

# NEW FUNCTION: Apply dynamic export restrictions
def apply_dynamic_export_restrictions(mapped_data, settings):
    """Apply export restrictions dynamically to ALL fields based on child table settings."""
    try:
        # Get export restrictions from child table
        restrictions = {}
        if hasattr(settings, 'mehrfach_export_unterdruecken'):
            for restriction in settings.mehrfach_export_unterdruecken:
                restrictions[restriction.field_name] = restriction.no_export
        
        # Debug: Log what restrictions we found
        # frappe.log_error(f"Found export restrictions: {restrictions}", "DATEV Export Debug")
        
        # Apply restrictions to any field that exists in mapped_data
        for field_name, no_export in restrictions.items():
            if no_export and field_name in mapped_data:
                original_value = mapped_data[field_name]
                mapped_data[field_name] = ""
                # frappe.log_error(f"Field {field_name} restricted: '{original_value}' -> ''", "DATEV Export Dynamic Restriction")
        
        # Debug: Log the final mapped data for key fields
        # debug_fields = ['st_klasse', 'duevo_familienname', 'duevo_vorname']
        # for field in debug_fields:
        #     if field in mapped_data:
        #         frappe.log_error(f"Final {field} value: '{mapped_data[field]}'", "DATEV Export Debug")
        
        return mapped_data
        
    except Exception as e:
        # frappe.log_error(f"Error applying dynamic export restrictions: {str(e)}", "DATEV Export Error")
        return mapped_data  # Return original data on error

def generate_main_employee_records(employee, settings):
    """Generate records 1-10 following exact Excel field mapping with NEW: dynamic export restrictions."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    # NEW: Apply dynamic export restrictions to ALL fields
    mapped_data = apply_dynamic_export_restrictions(mapped_data, settings)
    
    try:
        # Record type 1: Main employee data
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["duevo_familienname"], False, True),  # Last name (quoted) - NOW DYNAMICALLY RESTRICTED
            format_field(mapped_data["duevo_vorname"], False, True),  # First name (quoted) - NOW DYNAMICALLY RESTRICTED
            format_field(mapped_data["geschlecht"], False, False),  # Gender (no quotes)
            format_field(mapped_data["geburtsdatum_ttmmjj"], False, False),  # Birth date (no quotes)
            format_field(mapped_data["adresse_nation_kz"], False, False),  # Country (no quotes)
            format_field(mapped_data["duevo_titel"], False, True),  # Academic title (quoted)
            format_field(mapped_data["kz_alleinerziehend"], False, False),  # Single parent (no quotes)
            format_field(mapped_data["adresse_anschriftenzusatz"], False, True),  # Address addition (quoted)
            format_field(mapped_data["arbeitserlaubnis"], False, False),  # Work permit (no quotes)
            format_field(mapped_data["aufenthaltserlaubnis"], False, False),  # Residence permit (no quotes)
            format_field(mapped_data["geburtsland"], False, False),  # Birth country (no quotes)
            format_field(mapped_data["gebname"], False, True),  # Birth name (quoted)
            format_field(mapped_data["gebort"], False, True),  # Birth place (quoted)
            format_field(mapped_data["email"], False, True),  # Email (quoted)
            
            format_field(mapped_data["ersteintrittsdatum"], False, False),  # First entry date (no quotes)
            format_field(mapped_data["verw_ersteintr_elena_bn"], False, False),  # Use first entry for AAG (no quotes)
            format_field(mapped_data["adresse_strasse_nr"], False, True),  # House number (quoted)
            format_field(mapped_data["adresse_ort"], False, True),  # City (quoted)
            format_field(mapped_data["adresse_plz"], False, False),  # Postal code (no quotes)
            format_field(mapped_data["adresse_strassenname"], False, True),  # Street name (quoted)
            format_field(mapped_data["schwerbeschaedigt"], False, False),  # Disability (no quotes)
            format_field(mapped_data["staatsangehoerigkeit"], False, False),  # Nationality (no quotes)
            format_field(mapped_data["telefon"], False, True),  # Phone (quoted)
            format_field(mapped_data["familienstand"], False, False),  # Marital status (no quotes)
            format_field(mapped_data["duevo_namenszusatz"], False, True),  # Name addition (quoted)
            format_field(mapped_data["duevo_vorsatzwort"], False, True),  # Prefix word (quoted)
            format_field(mapped_data["nazu_gebname"], False, True),  # Birth name addition (quoted)
            format_field(mapped_data["vorsatzwort_gebname"], False, True),  # Birth name prefix (quoted)
            format_field(mapped_data["datum_studienbesch"], False, False),  # Study certificate date (no quotes)
            format_field(mapped_data["loesch_nach_austr_unterdr"], False, False),  # Suppress automatic deletion (no quotes)
            format_field(mapped_data["sozialversicherung_nr"], False, True),  # Insurance number (quoted)
            format_field(mapped_data["sba_ausbildungsbeginn"], False, False),  # Training start (no quotes)
            format_field(mapped_data["sba_ausbildungsende"], False, False),  # Training end (no quotes)
            format_field(mapped_data["ebz_nach_austritt_kz"], False, False),  # One-time payments after exit (no quotes)
            format_field(mapped_data["datum_tod"], False, False),  # Date of death (no quotes)
        ]
        data += f'1;{";".join(fields)};\n'
        
        # Record type 2: Job/Activity
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["berufsbezeichnung"], False, True),  # Job title (quoted)
            format_field(mapped_data["kst_abteilungs_nr"], False, True),  # Department number (quoted)
            "1",  # Fixed value 1 as required
            format_field(mapped_data["schulabschluss"], False, False),  # School education (no quotes)
            format_field(mapped_data["ausbildungsabschluss"], False, False),  # Professional education (no quotes)
            format_field(mapped_data["ausbildungsbeginn"], False, False),  # Training start (no quotes)
            format_field(mapped_data["vorr_ausbildungsende"], False, False),  # Expected training end (no quotes)
            format_field(mapped_data["datum_ben_ergeb_pruef"], False, False),  # Actual training end (no quotes)
            format_field(mapped_data["ehrenamtliche_taetigkeit"], False, False) , # Voluntary work (no quotes)
            format_field(mapped_data["kz_erstbeschaeftigung"], False, False),  # First employment (no quotes)
            format_field(mapped_data["kz_besch_nebenbesch"], False, False)  # Certificate § 313 (no quotes)
        ]
        data += f'2;{";".join(fields)};\n'
        
        # Record type 3: Employment
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["arbeitsverhaeltnis"], False, False),  # Employment type (no quotes)
            format_field(mapped_data["eintrittdatum"], False, False),  # Entry date (no quotes)
            format_field(mapped_data["austrittdatum"], False, False),  # Exit date (no quotes)
            # format_field(mapped_data["kz_arbbes_nae_abrech_autom"], False, False),  # Work certificate (no quotes)
            format_field(mapped_data["eel_nach_austritt_kz"], False, False),  # EEL after exit (no quotes)
        ]
        data += f'3;{";".join(fields)};\n'
        
        # Record type 4: Tax - All restrictions applied dynamically above
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["identifikationsnummer"], False, True),  # Tax ID (quoted)
            format_field(mapped_data["st_klasse"], False, False),  # Tax class (no quotes) - NOW DYNAMICALLY RESTRICTED
            format_field(mapped_data["konf_an"], False, False),  # Religion (no quotes)
            format_field(mapped_data["kfb_anzahl"], True, False),  # Number of child allowances (numeric, no quotes)
            format_field(mapped_data["pausch_einhtl_2"], False, False),  # Flat tax (no quotes)
            format_field(mapped_data["els_2_haupt_ag_kz"], False, False)  # Main/secondary employer (no quotes)
        ]
        data += f'4;{";".join(fields)};\n'
        
        # Record type 5: Bank
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["ma_iban"], False, True),  # IBAN (quoted)
            format_field(mapped_data["ma_bic"], False, True),  # BIC (quoted)
            format_field(mapped_data["ma_bank_kto_inhaber_abw"], False, True)  # Account holder (quoted)
        ]
        data += f'5;{";".join(fields)};\n'
        
        # Record type 6: Disability - ONLY if disability data exists
        if has_disability_data(employee):
            fields = [
                format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
                format_field(mapped_data["sba_sb_ausweis_bis"], False, False),  # Disability ID valid until (no quotes)
                format_field(mapped_data["sba_unter_18_std_aa_kz"], False, False),  # Under 18 hours with AA approval (no quotes)
                format_field(mapped_data["sba_kz_dienststelle"], False, True),  # Issuing authority (quoted)
                format_field(mapped_data["sba_az_geschaeftsstelle"], False, True),  # ID number/file number (quoted)
                format_field(mapped_data["sba_ort_dienstelle"], False, True),  # Authority location (quoted)
                format_field(mapped_data["sba_sb_ausweis_ab"], False, False)  # Disability ID valid from (no quotes)
            ]
            data += f'6;{";".join(fields)};\n'
        
        # Record type 7: Working time - All restrictions applied dynamically above
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["az_wtl_indiv"], True, False),  # Weekly working hours (numeric, no quotes) - NOW DYNAMICALLY RESTRICTED
            format_field(mapped_data["url_tage_jhrl"], True, False),  # Vacation days yearly (numeric, no quotes)
            format_field(mapped_data.get("urlaubsanspr_pro_jahr", ""), True, False)  # MPD working time (numeric, no quotes)
        ]
        data += f'7;{";".join(fields)};\n'
        
        # Record type 8: Salary
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data.get("std_lohn_1", ""), True, False) , # Standard hourly wage (numeric, no quotes)
            format_field(mapped_data["std_lohn_2"], True, False),  # Hourly wage 1 (numeric, no quotes)
            format_field(mapped_data["lfd_brutto_vereinbart"], True, False)  # Current gross agreed (numeric, no quotes)
        ]
        data += f'8;{";".join(fields)};\n'
        
        # Record type 9: Travel subsidy
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["jobticket"], True, False)  # Job ticket (numeric, no quotes)
        ]
        data += f'9;{";".join(fields)};\n'
        
        # Record type 10: Special features
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["entlohnungsform"], False, False)  # Remuneration form (no quotes)
        ]
        data += f'10;{";".join(fields)};\n'
        
    except KeyError as e:
        # frappe.log_error(f"Missing key in employee data: {str(e)} for employee {employee.get('name', 'Unknown')}", 
        #               "DATEV Export Error")
        # Create a placeholder for the missing field
        mapped_data[str(e).strip("'")] = ""
        # Try again recursively with the fixed data
        return generate_main_employee_records(employee, settings)
    except Exception as e:
        # frappe.log_error(f"Error in generate_main_employee_records: {str(e)}", "DATEV Export Error")
        raise
    
    return data

def generate_child_record(employee, child):
    """Generate a child record (type 11) - only if child has data."""
    data = ""
    
    try:
        # Check if this specific child has any meaningful data - update dont export kind number
        if not (child.get('kind_nummer') or 
                child.get('vorname_personaldaten_kinderdaten_allgemeine_angaben') or 
                child.get('familienname_personaldaten_kinderdaten_allgemeine_angaben') or 
                child.get('geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben')):
            return ""  # Skip this child if no data
        
        mapped_data = map_child_to_lodas(employee, child)
        
        # Record type 11: Child information
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field(mapped_data["kind_nr"], False, False),  # Child number (no quotes)
            format_field(mapped_data["kind_vorname"], False, True),  # Child first name (quoted)
            format_field(mapped_data["kind_nachname"], False, True),  # Child last name (quoted)
            format_field(mapped_data["kind_geburtsdatum"], False, False)  # Child birth date (no quotes)
        ]
        data += f'11;{";".join(fields)};\n'
        
    except Exception as e:
        # frappe.log_error(f"Error generating child record for employee {employee.get('name', 'Unknown')}: {str(e)}", 
        #                "DATEV Export Error")
        # Return empty string to continue with export
        return ""
    
    return data

def generate_festbezuege_records(employee):
    """Generate festbezuege records (type 12) with festbez_id field."""
    data = ""
    mapped_data = map_employee_to_lodas(employee)
    
    try:
        # DEBUG: Log employee data for salary records
        # frappe.log_error(f"Generate festbezuege for {employee.get('name', 'Unknown')}", "DATEV Export Debug")
        
        # 1. Grundgehalt (GG) - festbez_id = 1
        basic_salary = determine_basic_salary(employee)
        lohnart_gg = employee.get('custom_lohnart_gg', "999")
        
        amount = "0" if not basic_salary else basic_salary
        # frappe.log_error(f"Grundgehalt (ID 1): lohnart_gg={lohnart_gg}, basic_salary={basic_salary}, amount={amount}", "DATEV Export Debug")
        
        fields = [
            format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
            format_field("1", False, False),  # FIXED: festbez_id = 1 (no quotes)
            format_field(lohnart_gg, False, False),  # Lohnart number (no quotes)
            format_field(amount, True, False),  # Amount (numeric, no quotes)
            format_field("0", False, False),  # Interval (no quotes)
            format_field("0", False, False)  # Reduction (no quotes)
        ]
        data += f'12;{";".join(fields)};\n'
        
        # 2-5. Project salaries (P1-P4) - festbez_id = 2, 3, 4, 5
        for i in range(1, 5):
            field_name = f'custom_lohnart_p{i}'
            project_salary_field = f'custom_gehalt_projekt_{i}'
            
            lohnart_nummer = employee.get(field_name, "999")
            amount = "0"
            project_salary_value = employee.get(project_salary_field)
            
            if project_salary_value and str(project_salary_value).strip():
                amount = project_salary_value
            
            festbez_id = str(i + 1)  # FIXED: festbez_id = 2, 3, 4, 5
            
            # frappe.log_error(f"Project {i} (ID {festbez_id}): {field_name}={lohnart_nummer}, {project_salary_field}={project_salary_value}, amount={amount}", "DATEV Export Debug")
            
            fields = [
                format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
                format_field(festbez_id, False, False),  # FIXED: festbez_id (no quotes)
                format_field(lohnart_nummer, False, False),  # Lohnart number (no quotes)
                format_field(amount, True, False),  # Amount (numeric, no quotes)
                format_field("0", False, False),  # Interval (no quotes)
                format_field("0", False, False)  # Reduction (no quotes)
            ]
            data += f'12;{";".join(fields)};\n'
        
        # 6-7. Supplementary salaries (Z1-Z2) - festbez_id = 6, 7
        for i in range(1, 3):
            field_name = f'custom_lohnart_z{i}'
            supplement_field = f'custom_zulage_zulage_{i}'
            
            lohnart_nummer = employee.get(field_name, "998")
            amount = "0"
            supplement_value = employee.get(supplement_field)
            
            if supplement_value and str(supplement_value).strip():
                amount = supplement_value
            
            festbez_id = str(i + 5)  # FIXED: festbez_id = 6, 7
            
            # frappe.log_error(f"Supplement {i} (ID {festbez_id}): {field_name}={lohnart_nummer}, {supplement_field}={supplement_value}, amount={amount}", "DATEV Export Debug")
            
            fields = [
                format_field(mapped_data["pnr"], False, True),  # Employee number (quoted)
                format_field(festbez_id, False, False),  # FIXED: festbez_id (no quotes)
                format_field(lohnart_nummer, False, False),  # Lohnart number (no quotes)
                format_field(amount, True, False),  # Amount (numeric, no quotes)
                format_field("0", False, False),  # Interval (no quotes)
                format_field("0", False, False)  # Reduction (no quotes)
            ]
            data += f'12;{";".join(fields)};\n'
            
    except Exception as e:
        # frappe.log_error(f"Error in generate_festbezuege_records for employee {employee.get('name', 'Unknown')}: {str(e)}", 
        #               "DATEV Export Error")
        # Return empty string to continue with export
        return ""
    
    return data

def determine_basic_salary(employee):
    """Determine the basic salary - keep current logic as shown in images."""
    try:
        # DEBUG: Log what we have for this employee
        # frappe.log_error(f"Determine basic salary for {employee.get('name', 'Unknown')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_des_grundvertrags: {employee.get('custom_gehalt_des_grundvertrags')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_projekt_1: {employee.get('custom_gehalt_projekt_1')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_projekt_2: {employee.get('custom_gehalt_projekt_2')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_projekt_3: {employee.get('custom_gehalt_projekt_3')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_projekt_4: {employee.get('custom_gehalt_projekt_4')}", "DATEV Export Debug")
        
        # Check if any project salaries are active
        has_project_salary = False
        for i in range(1, 5):
            project_field = f'custom_gehalt_projekt_{i}'
            project_value = employee.get(project_field)
            # frappe.log_error(f"Checking {project_field}: '{project_value}' (type: {type(project_value)})", "DATEV Export Debug")
            
            if (project_value and 
                str(project_value).strip() and 
                str(project_value).strip() != "0" and
                str(project_value).strip() != "0.0" and
                str(project_value).strip() != "0,0"):
                try:
                    float_val = float(str(project_value).replace(',', '.'))
                    if float_val > 0:
                        has_project_salary = True
                        # frappe.log_error(f"Found active project salary in {project_field}: {float_val}", "DATEV Export Debug")
                        break
                except (ValueError, TypeError):
                    pass
        
        # frappe.log_error(f"has_project_salary: {has_project_salary}", "DATEV Export Debug")
        
        # Check additional wage criteria
        has_zusatzliche_vergutung = False
        for field in ['custom_ist_zusätzliche_vergütung_zum_grundgehalt', 
                    'custom_ist_zusätzliche_vergütung_zum_grundgehalt_1',
                    'custom_ist_zusätzliche_vergütung_zum_grundgehalt_2',
                    'custom_ist_zusätzliche_vergütung_zum_grundgehalt_3']:
            field_value = employee.get(field)
            if field_value and str(field_value).strip():
                has_zusatzliche_vergutung = True
                # frappe.log_error(f"Found zusatzliche_vergutung in {field}: {field_value}", "DATEV Export Debug")
                break
        
        # frappe.log_error(f"has_zusatzliche_vergutung: {has_zusatzliche_vergutung}", "DATEV Export Debug")
        
        # Determine which basic salary to use
        if has_project_salary and not has_zusatzliche_vergutung:
            # Project salary is exclusive - no basic salary
            # frappe.log_error("Result: No basic salary (project salary is exclusive)", "DATEV Export Debug")
            return None
        elif employee.get('custom_gehalt_des_grundvertrags') and str(employee.get('custom_gehalt_des_grundvertrags')).strip():
            # Use the explicitly defined basic salary
            result = employee.get('custom_gehalt_des_grundvertrags')
            # frappe.log_error(f"Result: Using custom_gehalt_des_grundvertrags: {result}", "DATEV Export Debug")
            return result
        elif not has_project_salary and employee.get('custom_lohnart_gg') and employee.get('custom_lohnart_gg') != "999":
            # If no project salary, use custom_lohnart_gg if available
            result = employee.get('custom_lohnart_gg')
            # frappe.log_error(f"Result: Using custom_lohnart_gg: {result}", "DATEV Export Debug")
            return result
        
        # Default case: no basic salary to record
        # frappe.log_error("Result: No basic salary (default case)", "DATEV Export Debug")
        return None
    except Exception as e:
        # frappe.log_error(f"Error in determine_basic_salary for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                    #   "DATEV Export Error")
        # Return None for safety
        return None

def generate_single_employee_file(employee, settings):
    """Generate LODAS file for a single employee - FIXED: Use correct timezone for filename and NEW: with settings parameter."""
    consultant_number = settings.consultant_number
    
    # Get company to client number mapping
    client_numbers = {}
    for mapping in settings.company_client_mapping:
        client_numbers[mapping.company] = mapping.client_number
    
    # Skip if no mapping exists for the employee's company
    if employee['company'] not in client_numbers:
        frappe.throw(_("No client number mapping found for company: {0}").format(employee['company']))
    
    client_number = client_numbers[employee['company']]
    
    # REMOVED: Duplicate Personalerfassungsbogen logic (now handled in prepare_employee_dict)
    # Data consistency is now ensured by using the same logic as bulk export
    
    # Generate file content - NEW: Pass settings for dynamic restrictions
    content = generate_lodas_file_header(consultant_number, client_number)
    content += generate_record_description()
    content += generate_employee_data([employee], settings)
    
    # Create temporary file with correct timezone timestamp
    # FIXED: Use now_datetime() and format with correct timezone
    current_time = now_datetime()
    timestamp = format_datetime(current_time, "yyyyMMddHHmmss")
    filename = f"DATEV_LODAS_Single_{employee['name']}_{timestamp}.txt"
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    
    with open(temp_path, 'w', encoding='cp1252', newline='\r\n') as f:
        f.write(content)
    
    # Count children
    children_count = len(employee.get('children', []))

    get_doc = frappe.get_doc('Employee' , employee['name'])
    get_doc.db_set('custom_for_next_export', 0 , update_modified=False)
    # get_doc.db_set('custom_bereits_exportiert', 1 , update_modified=False)

    # frappe.db.commit()
    return [{
        'path': temp_path,
        'filename': filename,
        'company': employee['company'],
        'employee_count': 1,
        'children_count': children_count
    }]