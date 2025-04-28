import frappe
from frappe import _
from datetime import datetime
from sut_app_datev_export.sut_app_datev_export.utils.died_mappings import map_value_to_died, format_date

def get_employees_for_export():
    """Get all employees marked for export, grouped by company."""
    employees_by_company = {}
    
    # Get all employees marked for export with their fields
    employees = frappe.get_all(
        'Employee',
        filters={'custom_for_next_export': 1},
        fields=[
            # Standard fields always needed
            'name', 'company', 'employee_name',
            
            # All employee fields needed for DATEV export
            'custom_land', 'custom_anschriftenzusatz', 'custom_befristung_arbeitserlaubnis',
            'custom_arbeitsverhältnis', 'custom_befristung_aufenthaltserlaubnis', 'relieving_date',
            'employment_type', 'custom_summe_gehalt_bei_offener_vertragsverhandlung',
            'date_of_joining', 'personal_email', 'custom_ersteintritt_ins_unternehmen_',
            'last_name', 'date_of_birth', 'gender', 'custom_hausnummer',
            'custom_höchster_schulabschluss', 'custom_höchste_berufsausbildung',
            'custom_steueridentnummer', 'custom_summe_wochenarbeitszeit', 
            'custom_ort', 'employee_number', 'custom_plz', 
            'custom_befristung_gdb_bescheid', 'custom_schwerbehinderung',
            'custom_straße', 'cell_number', 'first_name'
        ]
    )
    
    # Group by company
    for employee in employees:
        company = employee.company
        if company not in employees_by_company:
            employees_by_company[company] = []
        
        # Get Personalerfassungsbogen data for this employee
        personalerfassungsbogen_data = get_personalerfassungsbogen_data(employee.name)
        
        # Add Personalerfassungsbogen data to employee
        if personalerfassungsbogen_data:
            for field, value in personalerfassungsbogen_data.items():
                employee[field] = value
        
        employees_by_company[company].append(employee)
    
    return employees_by_company

def get_personalerfassungsbogen_data(employee_name):
    """Get data from Personalerfassungsbogen DocType for an employee."""
    # Check if the DocType exists
    if not frappe.db.exists('DocType', 'Personalerfassungsbogen'):
        return {}
    
    # Get Personalerfassungsbogen record linked to this employee
    personalerfassungsbogen = frappe.get_all(
        'Personalerfassungsbogen',
        filters={'employee': employee_name},
        fields=[
            # All fields from Personalerfassungsbogen
            'abweichender_kontoinhaber', 'akademischer_grad', 'alleinerziehend',
            'anzahl_kinderfreibeträge', 'arbeits_ausbildungsbeginn_tt_mm_jjjj',
            'arbeits_ausbildungsende_tt_mm_jjjj', 'arbeitsbescheinigung_im_austrittsmonat_elektr_ueberm',
            'arbeitszeit_18_std_mit_zulassung_aa', 'ausstellende_dienststelle', 
            'ausweis_nr_aktenzeichen', 'automatische_loeschung_nach_austritt_unterdruecken',
            'basislohn', 'beginn_der_ausbildung', 'bescheinigung_nach_313_sgb_iii_elektronisch_ueberm',
            'bic', 'datum_des_todes', 'eel_meldung_nach_austritt_des_arbeitnehmers',
            'ehrenamtliche_taetigkeit', 'einmalbezuege_nach_austritt_d_arbeitnehmers_berechnen',
            'entlohnungsform', 'erstbeschaeftigung', 'ersteintrittsdatum_fuer_aag_und_brutto_netto_verwenden',
            'familienname_personaldaten_kinderdaten_allgemeine_angaben',
            'geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben',
            'geburtsland', 'geburtsname', 'geburtsort', 'grundurlaubsanspruch',
            'iban', 'jobticket_hoehe_des_geldwerten_vorteils',
            'kennzeichnung_arbeitgeber_haupt_nebenarbeitgeber', 'kind_nummer',
            'konfessionszugehoerigkeit_steuerpflichtiger', 'lfd_brutto_vereinbart',
            'namenszusatz_geburtsname', 'namenszusatz_mitarbeitername',
            'ort_der_dienststelle', 'pauschalsteuer_berechnen',
            'sb_ausweis_gueltig_ab_tt_mm_jjjj', 'staatsangehoerigkeit',
            'steuerklasse_personaldaten_steuer_steuerkarte_allgemeine_daten',
            'studienbescheinigung', 'stundenlohn', 'stundenlohn_1',
            'tatsaechliches_ende_der_ausbildung', 'urlaubsanspruch_aktuelles_jahr',
            'verheiratet', 'versicherungsnummer',
            'voraussichtliches_ende_der_ausbildung_gem_vertrag',
            'vorname_personaldaten_kinderdaten_allgemeine_angaben',
            'vorsatzwort_geburtsname', 'vorsatzwort_mitarbeitername'
        ]
    )
    
    # Return the first record if found, otherwise an empty dict
    return personalerfassungsbogen[0] if personalerfassungsbogen else {}

def map_employee_to_lodas(employee):
    """Map ERPNext employee fields to LODAS field format using DIED tables."""
    # All field mappings
    fields_to_map = {
        # Employee identification & basic data
        'pnr_betriebliche': f"BPNR {employee.name}",  # Always include employee number
        'duevo_familienname': employee.get('last_name', ""),
        'duevo_vorname': employee.get('first_name', ""),
        'staatsangehoerigkeit': map_value_to_died("custom_land", employee.get('custom_land')),
        'geburtsdatum_ttmmjj': format_date(employee.get('date_of_birth')),
        'geschlecht': map_value_to_died("gender", employee.get('gender')),
        
        # Address fields
        'adresse_strassenname': employee.get('custom_straße', ""),
        'adresse_strasse_nr': employee.get('custom_hausnummer', ""),
        'adresse_ort': employee.get('custom_ort', ""),
        'adresse_plz': employee.get('custom_plz', ""),
        'adresse_anschriftenzusatz': employee.get('custom_anschriftenzusatz', ""),
        
        # Employment information
        'employment_type': map_value_to_died("employment_type", employee.get('employment_type')),
        'arbeitsverhältnis': map_value_to_died("custom_arbeitsverhältnis", employee.get('custom_arbeitsverhältnis')),
        'eintrittsdatum': format_date(employee.get('date_of_joining')),
        'austrittsdatum': format_date(employee.get('relieving_date')),
        'ersteintritt': format_date(employee.get('custom_ersteintritt_ins_unternehmen_')),
        
        # Tax and social security information
        'steueridentnummer': employee.get('custom_steueridentnummer', ""),
        'steuerklasse': map_value_to_died("steuerklasse_personaldaten_steuer_steuerkarte_allgemeine_daten", 
                                      employee.get('steuerklasse_personaldaten_steuer_steuerkarte_allgemeine_daten')),
        'konfession': map_value_to_died("konfessionszugehoerigkeit_steuerpflichtiger", 
                                    employee.get('konfessionszugehoerigkeit_steuerpflichtiger')),
        
        # Bank details
        'iban': employee.get('iban', ""),
        'bic': employee.get('bic', ""),
        'abweichender_kontoinhaber': employee.get('abweichender_kontoinhaber', ""),
        
        # Personal details
        'email': employee.get('personal_email', ""),
        'telefon': employee.get('cell_number', ""),
        'akademischer_grad': employee.get('akademischer_grad', ""),
        'namenszusatz': employee.get('namenszusatz_mitarbeitername', ""),
        'vorsatzwort': employee.get('vorsatzwort_mitarbeitername', ""),
        'geburtsname': employee.get('geburtsname', ""),
        'namenszusatz_geburt': employee.get('namenszusatz_geburtsname', ""),
        'vorsatzwort_geburt': employee.get('vorsatzwort_geburtsname', ""),
        'geburtsort': employee.get('geburtsort', ""),
        'geburtsland': map_value_to_died("geburtsland", employee.get('geburtsland')),
        'familienstand': map_value_to_died("verheiratet", employee.get('verheiratet')),
        'versicherungsnummer': employee.get('versicherungsnummer', ""),
        
        # Work information
        'summe_wochenarbeitszeit': employee.get('custom_summe_wochenarbeitszeit', ""),
        'schwerbehinderung': map_value_to_died("custom_schwerbehinderung", employee.get('custom_schwerbehinderung')),
        'höchster_schulabschluss': map_value_to_died("custom_höchster_schulabschluss", employee.get('custom_höchster_schulabschluss')),
        'höchste_berufsausbildung': map_value_to_died("custom_höchste_berufsausbildung", employee.get('custom_höchste_berufsausbildung')),
        'befristung_gdb_bescheid': format_date(employee.get('custom_befristung_gdb_bescheid')),
        'befristung_arbeitserlaubnis': format_date(employee.get('custom_befristung_arbeitserlaubnis')),
        'befristung_aufenthaltserlaubnis': format_date(employee.get('custom_befristung_aufenthaltserlaubnis')),
        'alleinerziehend': map_value_to_died("alleinerziehend", employee.get('alleinerziehend')),
        
        # Salary information
        'basislohn': employee.get('basislohn', ""),
        'stundenlohn': employee.get('stundenlohn', ""),
        'stundenlohn_1': employee.get('stundenlohn_1', ""),
        'lfd_brutto': employee.get('lfd_brutto_vereinbart', ""),
        'summe_gehalt': employee.get('custom_summe_gehalt_bei_offener_vertragsverhandlung', ""),
        'pauschalsteuer': map_value_to_died("pauschalsteuer_berechnen", employee.get('pauschalsteuer_berechnen')),
        'jobticket': employee.get('jobticket_hoehe_des_geldwerten_vorteils', ""),
        'entlohnungsform': map_value_to_died("entlohnungsform", employee.get('entlohnungsform')),
        
        # Education and training
        'arbeits_ausbildungsbeginn': format_date(employee.get('arbeits_ausbildungsbeginn_tt_mm_jjjj')),
        'arbeits_ausbildungsende': format_date(employee.get('arbeits_ausbildungsende_tt_mm_jjjj')),
        'beginn_ausbildung': format_date(employee.get('beginn_der_ausbildung')),
        'ende_ausbildung_tatsaechlich': format_date(employee.get('tatsaechliches_ende_der_ausbildung')),
        'ende_ausbildung_vertrag': format_date(employee.get('voraussichtliches_ende_der_ausbildung_gem_vertrag')),
        'studienbescheinigung': format_date(employee.get('studienbescheinigung')),
        'urlaubsanspruch': employee.get('urlaubsanspruch_aktuelles_jahr', ""),
        'grundurlaubsanspruch': employee.get('grundurlaubsanspruch', ""),
        
        # Child information
        'kind_nummer': employee.get('kind_nummer', ""),
        'familienname_kind': employee.get('familienname_personaldaten_kinderdaten_allgemeine_angaben', ""),
        'vorname_kind': employee.get('vorname_personaldaten_kinderdaten_allgemeine_angaben', ""),
        'geburtsdatum_kind': format_date(employee.get('geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben')),
        'anzahl_kinderfreibetraege': employee.get('anzahl_kinderfreibeträge', ""),
        
        # Additional flags and indicators
        'erstbeschaeftigung': map_value_to_died("erstbeschaeftigung", employee.get('erstbeschaeftigung')),
        'arbeitszeit_18_std': map_value_to_died("arbeitszeit_18_std_mit_zulassung_aa", employee.get('arbeitszeit_18_std_mit_zulassung_aa')),
        'automatische_loeschung': map_value_to_died("automatische_loeschung_nach_austritt_unterdruecken", employee.get('automatische_loeschung_nach_austritt_unterdruecken')),
        'arbeitsbescheinigung': map_value_to_died("arbeitsbescheinigung_im_austrittsmonat_elektr_ueberm", employee.get('arbeitsbescheinigung_im_austrittsmonat_elektr_ueberm')),
        'bescheinigung_313': map_value_to_died("bescheinigung_nach_313_sgb_iii_elektronisch_ueberm", employee.get('bescheinigung_nach_313_sgb_iii_elektronisch_ueberm')),
        'eel_meldung': map_value_to_died("eel_meldung_nach_austritt_des_arbeitnehmers", employee.get('eel_meldung_nach_austritt_des_arbeitnehmers')),
        'ehrenamtliche_taetigkeit': map_value_to_died("ehrenamtliche_taetigkeit", employee.get('ehrenamtliche_taetigkeit')),
        'einmalbezuege': map_value_to_died("einmalbezuege_nach_austritt_d_arbeitnehmers_berechnen", employee.get('einmalbezuege_nach_austritt_d_arbeitnehmers_berechnen')),
        'kennzeichnung_arbeitgeber': map_value_to_died("kennzeichnung_arbeitgeber_haupt_nebenarbeitgeber", employee.get('kennzeichnung_arbeitgeber_haupt_nebenarbeitgeber')),
        'ersteintrittsdatum_aag': map_value_to_died("ersteintrittsdatum_fuer_aag_und_brutto_netto_verwenden", employee.get('ersteintrittsdatum_fuer_aag_und_brutto_netto_verwenden')),
        
        # Office and official documents
        'ausweis_nr': employee.get('ausweis_nr_aktenzeichen', ""),
        'ausstellende_dienststelle': employee.get('ausstellende_dienststelle', ""),
        'sb_ausweis_gueltig': format_date(employee.get('sb_ausweis_gueltig_ab_tt_mm_jjjj')),
        'ort_dienststelle': employee.get('ort_der_dienststelle', ""),
        'datum_des_todes': format_date(employee.get('datum_des_todes')),
        'staatsangehoerigkeit_peb': map_value_to_died("staatsangehoerigkeit", employee.get('staatsangehoerigkeit')),
    }
    
    return fields_to_map

def validate_employee_data(employees_by_company):
    """Validate that essential employee data is complete for LODAS export."""
    validation_errors = []
    
    for company, employees in employees_by_company.items():
        for employee in employees:
            # Check for essential fields (add more as needed)
            if not employee.get('last_name'):
                validation_errors.append(f"Employee {employee.name}: Missing last name")
            
            if not employee.get('first_name'):
                validation_errors.append(f"Employee {employee.name}: Missing first name")
            
            if not employee.get('date_of_birth'):
                validation_errors.append(f"Employee {employee.name}: Missing date of birth")
                
            if not employee.get('gender'):
                validation_errors.append(f"Employee {employee.name}: Missing gender")
                
            if not employee.get('date_of_joining'):
                validation_errors.append(f"Employee {employee.name}: Missing joining date")
    
    if validation_errors:
        error_message = "\n".join(validation_errors)
        frappe.log_error(f"Employee data validation errors:\n{error_message}", 
                         "DATEV Export Validation Error")
        
        # Show first 5 errors to the user, with "..." if there are more
        user_message = "\n".join(validation_errors[:5])
        if len(validation_errors) > 5:
            user_message += "\n..."
        
        frappe.throw(_("Some employees have incomplete data:\n{0}\n\nSee error log for details.").format(user_message))