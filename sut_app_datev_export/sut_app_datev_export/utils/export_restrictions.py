import frappe
from frappe import _

def get_export_restrictions_dict(settings):
    """Get export restrictions as a dictionary for quick lookup."""
    restrictions = {}
    try:
        if hasattr(settings, 'mehrfach_export_unterdruecken'):
            for restriction in settings.mehrfach_export_unterdruecken:
                restrictions[restriction.field_name] = restriction.no_export
    except Exception as e:
        frappe.log_error(f"Error getting export restrictions: {str(e)}", "DATEV Export Error")
    
    return restrictions

def should_export_field_value(field_name, field_value, settings):
    """Check if a specific field value should be exported based on restrictions."""
    try:
        restrictions = get_export_restrictions_dict(settings)
        
        # If field is in restrictions and no_export is True, return empty
        if field_name in restrictions and restrictions[field_name]:
            return ""
        
        # Otherwise return the original value
        return field_value
        
    except Exception as e:
        frappe.log_error(f"Error checking field export restriction for {field_name}: {str(e)}", "DATEV Export Error")
        return field_value  # Return original value on error

def apply_field_restrictions(mapped_data, settings):
    """Apply export restrictions to all fields in mapped data."""
    try:
        restrictions = get_export_restrictions_dict(settings)
        
        for field_name, no_export in restrictions.items():
            if no_export and field_name in mapped_data:
                mapped_data[field_name] = ""
                
    except Exception as e:
        frappe.log_error(f"Error applying field restrictions: {str(e)}", "DATEV Export Error")
    
    return mapped_data

def log_export_restriction(employee_name, field_name, reason="field restricted"):
    """Log when a field is restricted from export."""
    frappe.log_error(
        f"Export restriction applied for employee {employee_name}: {field_name} - {reason}", 
        "DATEV Export Restriction"
    )