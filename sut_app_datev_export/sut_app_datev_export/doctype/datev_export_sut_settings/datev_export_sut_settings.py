# UPDATED: Add timezone imports at the top of datev_export_sut_settings.py
from frappe.model.document import Document

import frappe
import tempfile
import os
from frappe import _
from datetime import datetime
from frappe.utils import now_datetime, get_datetime  # Add these imports for timezone handling
from sut_app_datev_export.sut_app_datev_export.utils.employee_data import get_employees_for_export, validate_employee_data, map_employee_to_lodas
from sut_app_datev_export.sut_app_datev_export.utils.file_builder import (
    generate_lodas_files,
    generate_lodas_file_header,
    generate_record_description,
    generate_employee_data,
    generate_single_employee_file
)
from sut_app_datev_export.sut_app_datev_export.utils.email_sender import send_export_email

class DATEVExportSUTSettings(Document):
    def validate(self):
        """Validate settings."""
        # Validate consultant number is 6 digits
        if not self.consultant_number or not self.consultant_number.isdigit() or len(self.consultant_number) != 6:
            frappe.throw(_("Consultant number must be exactly 6 digits"))

        # Validate client mappings
        for mapping in self.company_client_mapping:
            if not mapping.client_number or not mapping.client_number.isdigit() or len(mapping.client_number) != 5:
                frappe.throw(_("Client number must be exactly 5 digits for company: {0}").format(mapping.company))

@frappe.whitelist()
def export_employees():
    """Main export function."""
    try:
        settings = frappe.get_single('DATEV Export SUT Settings')
        export_email = settings.export_email

        # Get employees marked for export
        employees_by_company = get_employees_for_export()

        # If no employees to export
        if not employees_by_company:
            frappe.msgprint(_("No employees marked for export."))
            return {"count": 0, "email": export_email}

        # Validate company mappings
        validate_company_mapping(settings, employees_by_company)

        # Validate employee data
        validate_employee_data(employees_by_company)

        # NEW: Apply export restrictions and handle special field logic
        process_export_restrictions(employees_by_company, settings)

        # Generate LODAS files (now with settings parameter for dynamic restrictions)
        file_paths = generate_lodas_files(employees_by_company, settings)

        # Send email with attachments
        if file_paths:
            send_export_email(export_email, file_paths)

            # Record export in history
            record_export_history(settings, file_paths)

            # NEW: Update stored values after successful export
            update_employee_stored_values([emp for emps in employees_by_company.values() for emp in emps])

            # Reset export flags
            reset_export_flags([emp for emps in employees_by_company.values() for emp in emps])

            # Return success
            total_employees = sum(len(emps) for emps in employees_by_company.values())
            total_children = sum(len(emp.get('children', [])) for emps in employees_by_company.values() for emp in emps)
            return {
                "count": total_employees,
                "children_count": total_children,
                "email": export_email
            }
        else:
            frappe.throw(_("No files were generated. Check error logs."))

    except Exception as e:
        # frappe.log_error(frappe.get_traceback(), "DATEV Export Error")
        frappe.throw(_("Export failed: {0}").format(str(e)))

@frappe.whitelist()
def export_single_employee(employee):
    """Export a single employee to DATEV LODAS."""
    try:
        settings = frappe.get_single('DATEV Export SUT Settings')
        export_email = settings.export_email

        # Get the employee data as a dictionary
        employee_dict = prepare_employee_dict(employee)

        # Create a structure similar to get_employees_for_export
        employees_by_company = {
            employee_dict['company']: [employee_dict]
        }

        # Validate company mappings
        validate_company_mapping(settings, employees_by_company)

        # Validate employee data
        validate_employee_data(employees_by_company)

        # NEW: Apply export restrictions and handle special field logic for single employee too
        process_export_restrictions(employees_by_company, settings)

        # Generate LODAS file for this employee (now with settings parameter for dynamic restrictions)
        file_paths = generate_single_employee_file(employee_dict, settings)

        # Send email with attachments
        if file_paths:
            send_export_email(export_email, file_paths)

            # Record export in history
            record_export_history(settings, file_paths)

            # NEW: Update stored values after successful single employee export
            update_employee_stored_values([employee_dict])

            frappe.db.set_value("Employee", employee, "custom_for_next_export", 0, update_modified=False)
            frappe.db.commit()
            # Return success with children count
            children_count = file_paths[0].get('children_count', 0)
            return {
                "count": 1,
                "children_count": children_count,
                "email": export_email
            }
        else:
            frappe.throw(_("No files were generated. Check error logs."))

    except Exception as e:
        # frappe.log_error(frappe.get_traceback(), "DATEV Export Error")
        frappe.throw(_("Export failed: {0}").format(str(e)))

# NEW FUNCTIONS FOR DYNAMIC EXPORT RESTRICTIONS
def process_export_restrictions(employees_by_company, settings):
    """Process export restrictions and special field logic for all employees."""
    try:
        # Get export restrictions from child table
        export_restrictions = get_export_restrictions(settings)
        
        # Debug: Log what we found
        # frappe.log_error(f"Processing export restrictions: {export_restrictions}", "DATEV Export Debug")
        
        for company, employees in employees_by_company.items():
            for employee in employees:
                # Apply export restrictions
                apply_export_restrictions(employee, export_restrictions)
                
                # Handle special field logic for az_wtl_indiv
                handle_special_field_logic(employee)
                
    except Exception as e:
        # frappe.log_error(f"Error in process_export_restrictions: {str(e)}", "DATEV Export Error")
        raise

def get_export_restrictions(settings):
    """Get export restrictions from the child table."""
    restrictions = {}
    try:
        if hasattr(settings, 'mehrfach_export_unterdruecken'):
            for restriction in settings.mehrfach_export_unterdruecken:
                restrictions[restriction.field_name] = restriction.no_export
    except Exception as e:pass
        # frappe.log_error(f"Error getting export restrictions: {str(e)}", "DATEV Export Error")
    
    return restrictions

def apply_export_restrictions(employee, restrictions):
    """Apply export restrictions to employee data."""
    try:
        for field_name, no_export in restrictions.items():
            if no_export and field_name in employee:
                # Set field to empty if export is restricted
                original_value = employee[field_name]
                employee[field_name] = ""
                # frappe.log_error(f"Field {field_name} restricted for employee {employee.get('name', 'Unknown')}: '{original_value}' -> ''", 
                #                 "DATEV Export Restriction")
    except Exception as e:pass
        # frappe.log_error(f"Error applying export restrictions: {str(e)}", "DATEV Export Error")

def handle_special_field_logic(employee):
    """Handle special logic for az_wtl_indiv field based on stored value comparison."""
    try:
        current_value = employee.get('custom_summe_wochenarbeitszeit')
        stored_value = employee.get('custom_stored_value_of_summe_wochenarbeitszeit')
        
        # Convert to strings for comparison, handling None values
        current_str = str(current_value) if current_value is not None else ""
        stored_str = str(stored_value) if stored_value is not None else ""
        
        # NEW LOGIC: Check if stored value is empty/None
        if not stored_value or stored_str.strip() == "" or stored_str.lower() == "none":
            # Stored value is empty → ALLOW export
            employee['_restrict_az_wtl_indiv'] = False
            # frappe.log_error(f"az_wtl_indiv ALLOWED for employee {employee.get('name', 'Unknown')} - stored value is empty", 
            #                 "DATEV Export Special Logic")
        elif current_str == stored_str:
            # Values are equal → DON'T export
            employee['_restrict_az_wtl_indiv'] = True
            # frappe.log_error(f"az_wtl_indiv RESTRICTED for employee {employee.get('name', 'Unknown')} - values are equal (current: {current_str}, stored: {stored_str})", 
            #                 "DATEV Export Special Logic")
        else:
            # Values are different → ALLOW export
            employee['_restrict_az_wtl_indiv'] = False
            # frappe.log_error(f"az_wtl_indiv ALLOWED for employee {employee.get('name', 'Unknown')} - values changed (current: {current_str}, stored: {stored_str})", 
            #                 "DATEV Export Special Logic")
            
    except Exception as e:pass
        # frappe.log_error(f"Error in handle_special_field_logic for employee {employee.get('name', 'Unknown')}: {str(e)}", 
                        # "DATEV Export Error")

def update_employee_stored_values(employees):
    """Update stored values after successful export."""
    try:
        for employee in employees:
            employee_name = employee.get('name')
            if not employee_name:
                continue
                
            current_value = employee.get('custom_summe_wochenarbeitszeit')
            
            # Update the stored value to match current value
            frappe.db.set_value('Employee', employee_name, 
                              'custom_stored_value_of_summe_wochenarbeitszeit', 
                              current_value, update_modified=False)
            
        frappe.db.commit()
        # frappe.log_error(f"Updated stored values for {len(employees)} employees", "DATEV Export Success")
        
    except Exception as e:pass
        # frappe.log_error(f"Error updating stored values: {str(e)}", "DATEV Export Error")

# EXISTING FUNCTIONS - UNCHANGED
def prepare_employee_dict(employee_id):
    """Prepare a dictionary with employee data from DocType - FIXED: Use same logic as bulk export."""
    try:
        # FIXED: Use the SAME logic as get_employees_for_export() to ensure consistency
        
        # Get basic employee data with ALL required fields (same as bulk export)
        employee_data = frappe.get_all(
            'Employee',
            filters={'name': employee_id},
            fields=[
                # Standard fields always needed
                'name', 'company', 'employee_name', 'designation',
                
                # All employee fields needed for DATEV export following Excel mapping
                'custom_land', 'custom_anschriftenzusatz', 'custom_befristung_arbeitserlaubnis',
                'custom_arbeitsverhältnis', 'custom_befristung_aufenthaltserlaubnis', 'relieving_date',
                'date_of_joining', 'personal_email', 'custom_ersteintritt_ins_unternehmen_',
                'last_name', 'date_of_birth', 'gender', 'custom_hausnummer',
                'custom_höchste_berufsausbildung', 'custom_höchster_schulabschluss',
                'custom_steueridentnummer', 'custom_summe_wochenarbeitszeit', 
                'custom_ort', 'employee_number', 'custom_plz', 
                'custom_befristung_gdb_bescheid', 'custom_schwerbehinderung',
                'custom_straße', 'cell_number', 'first_name', 'custom_summe_gehalt',
                'employment_type',
                
                # NEW: Add the stored value field for comparison
                'custom_stored_value_of_summe_wochenarbeitszeit',
                
                # Wage type fields - only include if they exist
                'custom_lohnart_gg', 'custom_lohnart_p1', 'custom_lohnart_p2', 
                'custom_lohnart_p3', 'custom_lohnart_p4', 'custom_lohnart_z1', 
                'custom_lohnart_z2',
                
                # CRITICAL: Add the wage amount fields from Employee DocType
                'custom_gehalt_des_grundvertrags',
                'custom_gehalt_projekt_1', 'custom_gehalt_projekt_2', 
                'custom_gehalt_projekt_3', 'custom_gehalt_projekt_4',
                'custom_zulage_zulage_1', 'custom_zulage_zulage_2',
                'custom_ist_zusätzliche_vergütung_zum_grundgehalt',
                'custom_ist_zusätzliche_vergütung_zum_grundgehalt_1',
                'custom_ist_zusätzliche_vergütung_zum_grundgehalt_2',
                'custom_ist_zusätzliche_vergütung_zum_grundgehalt_3'
            ]
        )

        if not employee_data:
            raise Exception(f"Employee {employee_id} not found")
            
        employee_dict = employee_data[0]

        # FIXED: Use the SAME Personalerfassungsbogen logic as bulk export
        from sut_app_datev_export.sut_app_datev_export.utils.employee_data import get_personalerfassungsbogen_data
        
        personalerfassungsbogen_data = get_personalerfassungsbogen_data(employee_id)
        
        # Add Personalerfassungsbogen data to employee (same as bulk export)
        if personalerfassungsbogen_data:
            for field, value in personalerfassungsbogen_data.items():
                if field != 'kinder_tabelle':
                    employee_dict[field] = value
            
            # Add children data if available
            if 'kinder_tabelle' in personalerfassungsbogen_data and personalerfassungsbogen_data['kinder_tabelle']:
                employee_dict['children'] = personalerfassungsbogen_data['kinder_tabelle']

        # # DEBUG: Log what we got for comparison
        # frappe.log_error(f"Single employee data for {employee_id}:", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_des_grundvertrags: {employee_dict.get('custom_gehalt_des_grundvertrags')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_projekt_1: {employee_dict.get('custom_gehalt_projekt_1')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_gehalt_projekt_2: {employee_dict.get('custom_gehalt_projekt_2')}", "DATEV Export Debug")
        # frappe.log_error(f"custom_lohnart_gg: {employee_dict.get('custom_lohnart_gg')}", "DATEV Export Debug")

        return employee_dict

    except Exception as e:
        # frappe.log_error(f"Error preparing employee dict: {str(e)}", "DATEV Export Error")
        # Create a minimal dict with required fields
        return {
            'name': employee_id,
            'company': frappe.db.get_value('Employee', employee_id, 'company'),
            'custom_stored_value_of_summe_wochenarbeitszeit': frappe.db.get_value('Employee', employee_id, 'custom_stored_value_of_summe_wochenarbeitszeit')
        }

def validate_company_mapping(settings, employees_by_company):
    """Validate that all relevant companies have client number mappings."""
    # Get mapped companies
    mapped_companies = {m.company: m.client_number for m in settings.company_client_mapping}

    # Find unmapped companies
    unmapped = []
    for company in employees_by_company.keys():
        if company not in mapped_companies:
            unmapped.append(company)

    if unmapped:
        frappe.throw(_(
            "The following companies have employees marked for export but no Company to Client mapping: {0}. "
            "Please add these mappings in DATEV Export SUT Settings."
        ).format(", ".join(unmapped)))

def record_export_history(settings, file_paths):
    """Record export in history table - FIXED: Use correct timezone."""
    total_employees = sum(f.get('employee_count', 0) for f in file_paths)
    total_children = sum(f.get('children_count', 0) for f in file_paths)

    # FIXED: Use now_datetime() which respects Frappe's timezone settings
    current_time = now_datetime()

    settings.append('export_history', {
        'export_date': current_time,  # FIXED: Use timezone-aware datetime
        'employee_count': total_employees,
        'status': 'Success',
        'message': f"Exported {total_employees} employees and {total_children} children from {len(file_paths)} companies"
    })
    settings.save()

def reset_export_flags(employees):
    """Reset export flags for all exported employees."""
    for employee in employees:
        frappe.db.set_value('Employee', employee.name, 'custom_for_next_export', 0, update_modified=False)
        # frappe.db.set_value('Employee', employee.name, 'custom_bereits_exportiert', 1, update_modified=False)

    frappe.db.commit()