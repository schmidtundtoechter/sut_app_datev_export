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

        # Generate LODAS files
        file_paths = generate_lodas_files(employees_by_company, settings)

        # Send email with attachments
        if file_paths:
            send_export_email(export_email, file_paths)

            # Record export in history
            record_export_history(settings, file_paths)

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
        frappe.log_error(frappe.get_traceback(), "DATEV Export Error")
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

        # Generate LODAS file for this employee
        file_paths = generate_single_employee_file(employee_dict, settings)

        # Send email with attachments
        if file_paths:
            send_export_email(export_email, file_paths)

            # Record export in history
            record_export_history(settings, file_paths)

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
        frappe.log_error(frappe.get_traceback(), "DATEV Export Error")
        frappe.throw(_("Export failed: {0}").format(str(e)))

def prepare_employee_dict(employee_id):
    """Prepare a dictionary with employee data from DocType."""
    try:
        # Fetch employee document
        employee_doc = frappe.get_doc("Employee", employee_id)

        # Convert to a dictionary - handle both Doc objects and dictionaries
        if hasattr(employee_doc, 'as_dict'):
            employee_dict = employee_doc.as_dict()
        else:
            employee_dict = dict(employee_doc)

        # Ensure 'name' property is set
        if 'name' not in employee_dict:
            employee_dict['name'] = employee_id

        # Get fields from Personalerfassungsbogen if available
        if frappe.db.exists('DocType', 'Personalerfassungsbogen'):
            try:
                # Get table columns to check which fields are available
                db_fields = frappe.db.get_table_columns('Personalerfassungsbogen')

                # Build the fields list from existing columns
                fields = ['name', 'employee']
                for field in db_fields:
                    if field not in fields:
                        fields.append(field)

                # Get Personalerfassungsbogen data
                personalerfassungsbogen = frappe.get_all(
                    'Personalerfassungsbogen',
                    filters={'employee': employee_id},
                    fields=fields
                )

                # Add Personalerfassungsbogen data if available
                if personalerfassungsbogen:
                    peb_data = personalerfassungsbogen[0]
                    peb_name = peb_data.pop('name', None)
                    peb_data.pop('employee', None)  # Remove redundant field

                    for field, value in peb_data.items():
                        employee_dict[field] = value

                    # Get children data if Kinder Tabelle exists
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
                            employee_dict['children'] = children
            except Exception as e:
                frappe.log_error(f"Error getting Personalerfassungsbogen data: {str(e)}", "DATEV Export Error")

        return employee_dict

    except Exception as e:
        frappe.log_error(f"Error preparing employee dict: {str(e)}", "DATEV Export Error")
        # Create a minimal dict with required fields
        return {
            'name': employee_id,
            'company': frappe.db.get_value('Employee', employee_id, 'company')
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