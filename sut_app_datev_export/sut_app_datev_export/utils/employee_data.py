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
            'name', 'company', 'employee_name', 'designation',

            # All employee fields needed for DATEV export
            'custom_land', 'custom_anschriftenzusatz', 'custom_befristung_arbeitserlaubnis',
            'custom_arbeitsverhältnis', 'custom_befristung_aufenthaltserlaubnis', 'relieving_date',
            'date_of_joining', 'personal_email', 'custom_ersteintritt_ins_unternehmen_',
            'last_name', 'date_of_birth', 'gender', 'custom_hausnummer',
            'custom_höchster_schulabschluss', 'custom_höchste_berufsausbildung',
            'custom_steueridentnummer', 'custom_summe_wochenarbeitszeit',
            'custom_ort', 'employee_number', 'custom_plz',
            'custom_befristung_gdb_bescheid', 'custom_schwerbehinderung',
            'custom_straße', 'cell_number', 'first_name', 'custom_summe_gehalt',

            # Wage type fields - only include if they exist
            'custom_lohnart_gg', 'custom_lohnart_p1', 'custom_lohnart_p2',
            'custom_lohnart_p3', 'custom_lohnart_p4', 'custom_lohnart_z1',
            'custom_lohnart_z2'
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
                if field != 'kinder_tabelle':
                    employee[field] = value

            # Add children data if available
            if 'kinder_tabelle' in personalerfassungsbogen_data and personalerfassungsbogen_data['kinder_tabelle']:
                employee['children'] = personalerfassungsbogen_data['kinder_tabelle']

        employees_by_company[company].append(employee)

    return employees_by_company

def get_personalerfassungsbogen_data(employee_name):
    """Get data from Personalerfassungsbogen DocType for an employee."""
    # Check if the DocType exists
    if not frappe.db.exists('DocType', 'Personalerfassungsbogen'):
        return {}

    # Get fields that exist in Personalerfassungsbogen
    all_fields = []
    db_fields = frappe.db.get_table_columns('Personalerfassungsbogen')

    # Standard fields to always include
    standard_fields = [
        'abweichender_kontoinhaber', 'akademischer_grad', 'alleinerziehend',
        'anzahl_kinderfreibeträge', 'arbeits_ausbildungsbeginn_tt_mm_jjjj',
        'arbeits_ausbildungsende_tt_mm_jjjj', 'arbeitsbescheinigung_im_austrittsmonat_elektr_ueberm',
        'arbeitszeit_18_std_mit_zulassung_aa', 'ausstellende_dienststelle',
        'ausweis_nr_aktenzeichen', 'automatische_loeschung_nach_austritt_unterdruecken',
        'basislohn', 'beginn_der_ausbildung', 'bescheinigung_nach_313_sgb_iii_elektronisch_ueberm',
        'bic', 'datum_des_todes', 'eel_meldung_nach_austritt_des_arbeitnehmers',
        'ehrenamtliche_taetigkeit', 'einmalbezuege_nach_austritt_d_arbeitnehmers_berechnen',
        'entlohnungsform', 'erstbeschaeftigung', 'ersteintrittsdatum_fuer_aag_und_brutto_netto_verwenden',
        'geburtsland', 'geburtsname', 'geburtsort', 'grundurlaubsanspruch',
        'iban', 'jobticket_hoehe_des_geldwerten_vorteils',
        'kennzeichnung_arbeitgeber_haupt_nebenarbeitgeber',
        'konfessionszugehoerigkeit_steuerpflichtiger',
        'namenszusatz_geburtsname', 'namenszusatz_mitarbeitername',
        'ort_der_dienststelle', 'pauschalsteuer_berechnen', 'abteilung_datev_lodas',
        'sb_ausweis_gueltig_ab_tt_mm_jjjj', 'staatsangehoerigkeit',
        'steuerklasse_personaldaten_steuer_steuerkarte_allgemeine_daten',
        'studienbescheinigung', 'stundenlohn', 'stundenlohn_1',
        'tatsaechliches_ende_der_ausbildung', 'urlaubsanspruch_aktuelles_jahr',
        'verheiratet', 'versicherungsnummer',
        'voraussichtliches_ende_der_ausbildung_gem_vertrag',
        'vorsatzwort_geburtsname', 'vorsatzwort_mitarbeitername'
    ]

    # Add wage fields if they exist in the database
    wage_fields = [
        'custom_gehalt_des_grundvertrags',
        'custom_gehalt_projekt_1', 'custom_gehalt_projekt_2',
        'custom_gehalt_projekt_3', 'custom_gehalt_projekt_4',
        'custom_zulage_zulage_1', 'custom_zulage_zulage_2',
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt',
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt_1',
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt_2',
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt_3'
    ]

    # Filter fields to only include those that exist in the database
    for field in standard_fields:
        if field in db_fields:
            all_fields.append(field)

    for field in wage_fields:
        if field in db_fields:
            all_fields.append(field)

    # Always include 'name' for linking to children
    all_fields.append('name')

    # Get Personalerfassungsbogen record linked to this employee
    try:
        personalerfassungsbogen = frappe.get_all(
            'Personalerfassungsbogen',
            filters={'employee': employee_name},
            fields=all_fields
        )
    except Exception as e:
        frappe.log_error(f"Error fetching Personalerfassungsbogen for {employee_name}: {str(e)}",
                        "DATEV Export Error")
        return {}

    # Return empty dict if no record found
    if not personalerfassungsbogen:
        return {}

    # Get the data
    data = personalerfassungsbogen[0]
    peb_name = data.pop('name')

    # Get children data
    if frappe.db.exists('DocType', 'Kinder Tabelle'):
        try:
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
                data['kinder_tabelle'] = children
        except Exception as e:
            frappe.log_error(f"Error fetching children for {employee_name}: {str(e)}",
                            "DATEV Export Error")

    return data

def map_employee_to_lodas(employee):
    """Map ERPNext employee fields to LODAS field format using DIED tables."""
    # All field mappings - with safe access using get()
    fields_to_map = {
        # Employee identification & basic data
        'pnr_betriebliche': f"BPNR {employee.get('name', '')}",  # Always include employee number
        'duevo_familienname': employee.get('last_name', ""),
        'duevo_vorname': employee.get('first_name', ""),
        'staatsangehoerigkeit': map_value_to_died("custom_land", employee.get('custom_land')),
        'geburtsdatum_ttmmjj': format_date(employee.get('date_of_birth')),
        'geschlecht': map_value_to_died("gender", employee.get('gender')),

        # Job title / Position
        'berufsbezeichnung': employee.get('designation', ""),

        # Department number
        'abteilung_datev_lodas': employee.get('abteilung_datev_lodas', ""),

        # Address fields
        'adresse_strassenname': employee.get('custom_straße', ""),
        'adresse_strasse_nr': employee.get('custom_hausnummer', ""),
        'adresse_ort': employee.get('custom_ort', ""),
        'adresse_plz': employee.get('custom_plz', ""),
        'adresse_anschriftenzusatz': employee.get('custom_anschriftenzusatz', ""),

        # Employment information
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
        'summe_gehalt': employee.get('custom_summe_gehalt', ""),
        'lfd_brutto_vereinbart': employee.get('custom_summe_gehalt', ""),  # Use custom_summe_gehalt for lfd_brutto_vereinbart
        'pauschalsteuer': map_value_to_died("pauschalsteuer_berechnen", employee.get('pauschalsteuer_berechnen')),
        'jobticket': employee.get('jobticket_hoehe_des_geldwerten_vorteils', ""),
        'entlohnungsform': map_value_to_died("entlohnungsform", employee.get('entlohnungsform')),

        # Education date fields with format correction from arbeits_ausbildungsbeginn_tt_mm_jjjj
        'arbeits_ausbildungsbeginn': format_date(employee.get('arbeits_ausbildungsbeginn_tt_mm_jjjj')),
        'arbeits_ausbildungsende': format_date(employee.get('arbeits_ausbildungsende_tt_mm_jjjj')),

        # Wage type fields
        'custom_lohnart_gg': employee.get('custom_lohnart_gg', ""),
        'custom_lohnart_p1': employee.get('custom_lohnart_p1', ""),
        'custom_lohnart_p2': employee.get('custom_lohnart_p2', ""),
        'custom_lohnart_p3': employee.get('custom_lohnart_p3', ""),
        'custom_lohnart_p4': employee.get('custom_lohnart_p4', ""),
        'custom_lohnart_z1': employee.get('custom_lohnart_z1', ""),
        'custom_lohnart_z2': employee.get('custom_lohnart_z2', ""),

        # Wage amount fields - only include if they exist
        'custom_gehalt_des_grundvertrags': employee.get('custom_gehalt_des_grundvertrags', ""),
        'custom_gehalt_projekt_1': employee.get('custom_gehalt_projekt_1', ""),
        'custom_gehalt_projekt_2': employee.get('custom_gehalt_projekt_2', ""),
        'custom_gehalt_projekt_3': employee.get('custom_gehalt_projekt_3', ""),
        'custom_gehalt_projekt_4': employee.get('custom_gehalt_projekt_4', ""),
        'custom_zulage_zulage_1': employee.get('custom_zulage_zulage_1', ""),
        'custom_zulage_zulage_2': employee.get('custom_zulage_zulage_2', ""),

        # Additional wage logic fields
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt': employee.get('custom_ist_zusätzliche_vergütung_zum_grundgehalt', ""),
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt_1': employee.get('custom_ist_zusätzliche_vergütung_zum_grundgehalt_1', ""),
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt_2': employee.get('custom_ist_zusätzliche_vergütung_zum_grundgehalt_2', ""),
        'custom_ist_zusätzliche_vergütung_zum_grundgehalt_3': employee.get('custom_ist_zusätzliche_vergütung_zum_grundgehalt_3', ""),

        # Default empty values for child information
        'kind_nummer': "",
        'familienname_kind': "",
        'vorname_kind': "",
        'geburtsdatum_kind': "",
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

    # Fetch department code from linked Abteilung DocType
    if employee.get('abteilung_datev_lodas'):
        try:
            department_doc = frappe.get_doc("Abteilung fuer DATEV Lodas Export", employee['abteilung_datev_lodas'])
            employee['abteilungscode'] = department_doc.abteilungscode
            # employee['abteilungsbezeichnung'] = department_doc.abteilungsbezeichnung  # optional for UI
        except Exception as e:
            frappe.log_error(f"Could not fetch Abteilung fields: {str(e)}", "DATEV Export Error")

    # Map to export field
    fields_to_map['kst_abteilungs_nr'] = employee.get('abteilungscode', "")

    return fields_to_map

def map_child_to_lodas(employee, child):
    """Create a mapping specifically for a child record."""
    # Start with the employee's basic data
    child_mapping = map_employee_to_lodas(employee)

    # Update with child specific information
    child_mapping.update({
        'kind_nummer': child.get('kind_nummer', ""),
        'familienname_kind': child.get('familienname_personaldaten_kinderdaten_allgemeine_angaben', ""),
        'vorname_kind': child.get('vorname_personaldaten_kinderdaten_allgemeine_angaben', ""),
        'geburtsdatum_kind': format_date(child.get('geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben')),
    })

    return child_mapping

def validate_employee_data(employees_by_company):
    """Validate that essential employee data is complete for LODAS export."""
    validation_errors = []

    for company, employees in employees_by_company.items():
        for employee in employees:
            # Check for essential fields (add more as needed)
            if not employee.get('last_name'):
                validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Missing last name")

            if not employee.get('first_name'):
                validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Missing first name")

            if not employee.get('date_of_birth'):
                validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Missing date of birth")

            if not employee.get('gender'):
                validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Missing gender")

            if not employee.get('date_of_joining'):
                validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Missing joining date")

            # Validate child data if children exist
            if employee.get('children'):
                for i, child in enumerate(employee['children']):
                    if not child.get('kind_nummer'):
                        validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Child {i+1} missing number")

                    if not child.get('vorname_personaldaten_kinderdaten_allgemeine_angaben'):
                        validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Child {i+1} missing first name")

                    if not child.get('familienname_personaldaten_kinderdaten_allgemeine_angaben'):
                        validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Child {i+1} missing last name")

                    if not child.get('geburtsdatum_personaldaten_kinderdaten_allgemeine_angaben'):
                        validation_errors.append(f"Employee {employee.get('name', 'Unknown')}: Child {i+1} missing birth date")

    if validation_errors:
        error_message = "\n".join(validation_errors)
        frappe.log_error(f"Employee data validation errors:\n{error_message}",
                         "DATEV Export Validation Error")

        # Show first 5 errors to the user, with "..." if there are more
        user_message = "\n".join(validation_errors[:5])
        if len(validation_errors) > 5:
            user_message += "\n..."

        frappe.throw(_("Some employees have incomplete data:\n{0}\n\nSee error log for details.").format(user_message))