# Copyright (c) 2025, ahmad900mohammad@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


# class DATEVExportSUTSettings(Document):
# 	pass


import frappe
import tempfile
import os
from frappe import _
from datetime import datetime
from sut_app_datev_export.sut_app_datev_export.utils.employee_data import get_employees_for_export, validate_employee_data , map_employee_to_lodas
from sut_app_datev_export.sut_app_datev_export.utils.file_builder import (
    generate_lodas_files,
    generate_lodas_file_header,
    generate_record_description,
    generate_employee_data
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
            return {"count": total_employees, "email": export_email}
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

        # Get the employee data
        employee_doc = frappe.get_doc("Employee", employee)

        # Create a structure similar to get_employees_for_export
        employees_by_company = {
            employee_doc.company: [employee_doc]
        }

        # Validate company mappings
        validate_company_mapping(settings, employees_by_company)

        # Validate employee data
        validate_employee_data(employees_by_company)

        # Generate LODAS file for this employee
        file_paths = generate_single_employee_file(employee_doc, settings)

        # Send email with attachments
        if file_paths:
            send_export_email(export_email, file_paths)

            # Record export in history
            record_export_history(settings, file_paths)

            # Return success
            return {"email": export_email}
        else:
            frappe.throw(_("No files were generated. Check error logs."))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "DATEV Export Error")
        frappe.throw(_("Export failed: {0}").format(str(e)))

def generate_single_employee_file(employee, settings):
    """Generate LODAS file for a single employee."""
    consultant_number = settings.consultant_number

    # Get company to client number mapping
    client_numbers = {}
    for mapping in settings.company_client_mapping:
        client_numbers[mapping.company] = mapping.client_number

    # Skip if no mapping exists for the employee's company
    if employee.company not in client_numbers:
        frappe.throw(_("No client number mapping found for company: {0}").format(employee.company))

    client_number = client_numbers[employee.company]

    # Generate file content
    content = generate_lodas_file_header(consultant_number, client_number)
    content += generate_record_description()
    content += generate_employee_data([employee])

    # Create temporary file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"DATEV_LODAS_Single_{employee.name}_{timestamp}.txt"
    temp_path = os.path.join(tempfile.gettempdir(), filename)

    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return [{
        'path': temp_path,
        'filename': filename,
        'company': employee.company,
        'employee_count': 1
    }]


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
            "The following companies have employees marked for export but no Company to Client  mapping: {0}. "
            "Please add these mappings in DATEV Export SUT Settings."
        ).format(", ".join(unmapped)))

def record_export_history(settings, file_paths):
    """Record export in history table."""
    total_employees = sum(f['employee_count'] for f in file_paths)

    settings.append('export_history', {
        'export_date': datetime.now(),
        'employee_count': total_employees,
        'status': 'Success',
        'message': f"Exported {total_employees} employees from {len(file_paths)} companies"
    })
    settings.save()

def reset_export_flags(employees):
    """Reset export flags for all exported employees."""
    for employee in employees:
        frappe.db.set_value('Employee', employee.name, 'custom_for_next_export', 0, update_modified=False)

    frappe.db.commit()