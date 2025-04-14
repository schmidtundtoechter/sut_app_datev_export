import frappe
import os
import tempfile
from datetime import datetime
from sut_app_datev_export.sut_app_datev_export.utils.employee_data import map_employee_to_lodas

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
    
    # Main employee data record
    description += "1;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;duevo_familienname#psd;duevo_vorname#psd;"
    description += "staatsangehoerigkeit#psd;geburtsdatum_ttmmjj#psd;geschlecht#psd;\n"
    
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
    description += "lfd_brutto#psd;summe_gehalt#psd;pauschalsteuer#psd;jobticket#psd;entlohnungsform#psd;\n"
    
    # Education and training
    description += "9;u_lod_psd_bildung;pnr_betriebliche#psd;arbeits_ausbildungsbeginn#psd;arbeits_ausbildungsende#psd;"
    description += "beginn_ausbildung#psd;ende_ausbildung_tatsaechlich#psd;ende_ausbildung_vertrag#psd;"
    description += "studienbescheinigung#psd;urlaubsanspruch#psd;grundurlaubsanspruch#psd;\n"
    
    # Child information
    description += "10;u_lod_psd_kind;pnr_betriebliche#psd;kind_nummer#psd;familienname_kind#psd;vorname_kind#psd;"
    description += "geburtsdatum_kind#psd;anzahl_kinderfreibetraege#psd;\n"
    
    # Additional flags and indicators
    description += "11;u_lod_psd_flags;pnr_betriebliche#psd;erstbeschaeftigung#psd;arbeitszeit_18_std#psd;"
    description += "automatische_loeschung#psd;arbeitsbescheinigung#psd;bescheinigung_313#psd;"
    description += "eel_meldung#psd;ehrenamtliche_taetigkeit#psd;einmalbezuege#psd;"
    description += "kennzeichnung_arbeitgeber#psd;ersteintrittsdatum_aag#psd;\n"
    
    # Office and official documents
    description += "12;u_lod_psd_dokumente;pnr_betriebliche#psd;ausweis_nr#psd;ausstellende_dienststelle#psd;"
    description += "sb_ausweis_gueltig#psd;ort_dienststelle#psd;datum_des_todes#psd;staatsangehoerigkeit_peb#psd;\n"
    
    description += "\n"
    return description

def generate_employee_data(employees):
    """Generate the [Stammdaten] section of the LODAS file."""
    data = "[Stammdaten]\n"
    
    for employee in employees:
        mapped_data = map_employee_to_lodas(employee)
        
        # Record type 1: Main employee data
        line = '1;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["duevo_familienname"]}";'
        line += f'"{mapped_data["duevo_vorname"]}";'
        line += f'{mapped_data["staatsangehoerigkeit"]};'
        line += f'{mapped_data["geburtsdatum_ttmmjj"]};'
        line += f' {mapped_data["geschlecht"]};\n'
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
        line += f'"{mapped_data["geburtsland"]}";'
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
        line += f'{mapped_data["lfd_brutto"]};'
        line += f'{mapped_data["summe_gehalt"]};'
        line += f'{mapped_data["pauschalsteuer"]};'
        line += f'{mapped_data["jobticket"]};'
        line += f'{mapped_data["entlohnungsform"]};\n'
        data += line
        
        # Record type 9: Education
        line = '9;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["arbeits_ausbildungsbeginn"]};'
        line += f'{mapped_data["arbeits_ausbildungsende"]};'
        line += f'{mapped_data["beginn_ausbildung"]};'
        line += f'{mapped_data["ende_ausbildung_tatsaechlich"]};'
        line += f'{mapped_data["ende_ausbildung_vertrag"]};'
        line += f'{mapped_data["studienbescheinigung"]};'
        line += f'{mapped_data["urlaubsanspruch"]};'
        line += f'{mapped_data["grundurlaubsanspruch"]};\n'
        data += line
        
        # Record type 10: Child
        line = '10;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["kind_nummer"]};'
        line += f'"{mapped_data["familienname_kind"]}";'
        line += f'"{mapped_data["vorname_kind"]}";'
        line += f'{mapped_data["geburtsdatum_kind"]};'
        line += f'{mapped_data["anzahl_kinderfreibetraege"]};\n'
        data += line
        
        # Record type 11: Flags
        line = '11;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'{mapped_data["erstbeschaeftigung"]};'
        line += f'{mapped_data["arbeitszeit_18_std"]};'
        line += f'{mapped_data["automatische_loeschung"]};'
        line += f'{mapped_data["arbeitsbescheinigung"]};'
        line += f'{mapped_data["bescheinigung_313"]};'
        line += f'{mapped_data["eel_meldung"]};'
        line += f'{mapped_data["ehrenamtliche_taetigkeit"]};'
        line += f'{mapped_data["einmalbezuege"]};'
        line += f'{mapped_data["kennzeichnung_arbeitgeber"]};'
        line += f'{mapped_data["ersteintrittsdatum_aag"]};\n'
        data += line
        
        # Record type 12: Documents
        line = '12;'
        line += f'"{mapped_data["pnr_betriebliche"]}";'
        line += f'"{mapped_data["ausweis_nr"]}";'
        line += f'"{mapped_data["ausstellende_dienststelle"]}";'
        line += f'{mapped_data["sb_ausweis_gueltig"]};'
        line += f'"{mapped_data["ort_dienststelle"]}";'
        line += f'{mapped_data["datum_des_todes"]};'
        line += f'{mapped_data["staatsangehoerigkeit_peb"]};\n'
        data += line
    
    return data