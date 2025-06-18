import frappe

def employee_on_update(doc, method=None):
    """Set 'for_next_export' flag whenever an employee record is saved."""
    if not doc.custom_for_next_export:
        frappe.db.set_value("Employee", doc.name, "custom_for_next_export", 1, update_modified=False)
        frappe.db.commit()
