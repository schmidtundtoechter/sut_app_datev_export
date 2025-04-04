import frappe
from frappe import _
from datetime import datetime
from sut_app_datev_export.sut_app_datev_export.utils.died_mappings import map_value_to_died

def get_employees_for_export():
    """Get all employees marked for export, grouped by company."""
    employees_by_company = {}
    
    # Get all employees marked for export with only the specified fields
    employees = frappe.get_all(
        'Employee',
        filters={'custom_for_next_export': 1},
        fields=[
            'name', 'company', 'employee_name', 'first_name', 'last_name', 
            'date_of_birth', 'gender', 'marital_status', 'custom_land',
            'custom_arbeitsverhältnis', 'designation'
        ]
    )
    
    # Group by company
    for employee in employees:
        company = employee.company
        if company not in employees_by_company:
            employees_by_company[company] = []
        
        employees_by_company[company].append(employee)
    
    return employees_by_company

def map_employee_to_lodas(employee):
    """Map ERPNext employee fields to LODAS field format using DIED tables."""
    mapped_data = {
        # Employee identification
        'pnr_betriebliche': f"BPNR {employee.name}",
        
        # Personal details
        'duevo_familienname': employee.last_name or "",
        'duevo_vorname': employee.first_name or "",
        
        # Mapped fields using DIED tables
        'staatsangehoerigkeit': map_value_to_died("custom_land", employee.custom_land),
        'geburtsdatum_ttmmjj': format_date(employee.date_of_birth),
        'geschlecht': map_value_to_died("gender", employee.gender),
        'familienstand': map_value_to_died("marital_status", employee.marital_status),
        
        # Additional mapped fields
        'custom_arbeitsverhältnis': employee.custom_arbeitsverhältnis,
        'designation': employee.designation
    }
    
    return mapped_data

def format_date(date_str):
    """Format date to DD.MM.YYYY format."""
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except:
        return ""

def validate_employee_data(employees_by_company):
    """Validate that employee data is complete for LODAS export."""
    validation_errors = []
    
    for company, employees in employees_by_company.items():
        for employee in employees:
            # Check for mandatory fields
            if not employee.last_name:
                validation_errors.append(f"Employee {employee.name}: Missing last name")
            
            if not employee.first_name:
                validation_errors.append(f"Employee {employee.name}: Missing first name")
            
            if not employee.date_of_birth:
                validation_errors.append(f"Employee {employee.name}: Missing date of birth")
    
    if validation_errors:
        error_message = "\n".join(validation_errors)
        frappe.log_error(f"Employee data validation errors:\n{error_message}", 
                         "DATEV Export Validation Error")
        frappe.throw(_("Some employees have incomplete data. See error log for details."))