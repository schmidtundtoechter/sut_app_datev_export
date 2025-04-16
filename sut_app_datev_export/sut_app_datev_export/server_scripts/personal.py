import frappe

def employee_on_update(doc, method=None):
    """Set 'for_next_export' flag whenever an personal employee record is saved."""
    get_emp_doc = frappe.get_doc("Employee" , doc.employee)
    if not get_emp_doc.custom_for_next_export:
        get_emp_doc.db_set('custom_for_next_export', 1, update_modified=False)
        frappe.db.commit()