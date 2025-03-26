import frappe

def employee_on_update(doc, method=None):
    """Set 'for_next_export' flag whenever an employee record is saved."""
    if not doc.custom_for_next_export:
        doc.db_set('custom_for_next_export', 1, update_modified=False)
        frappe.db.commit()