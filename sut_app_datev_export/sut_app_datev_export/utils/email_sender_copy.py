import frappe
import os
from frappe import _

def send_export_email(recipient, file_paths):
    """Send email with LODAS files as attachments."""
    subject = _("DATEV LODAS Export")

    # Prepare message
    message = format_email_message(file_paths)

    # Create attachments
    attachments = []
    for file_info in file_paths:
        file_path = file_info['path']
        filename = file_info['filename']

        with open(file_path, 'rb') as f:
            content = f.read()

        # Save file in ERPNext using the File doctype directly
        folder = create_datev_folder()
        file_doc = frappe.new_doc("File")
        file_doc.file_name = filename
        file_doc.content = content
        file_doc.folder = folder
        file_doc.is_private = 1
        file_doc.attached_to_doctype = "DATEV Export SUT Settings"
        file_doc.attached_to_name = "DATEV Export SUT Settings"
        file_doc.save()

        attachments.append({
            "fname": filename,
            "fcontent": content
        })

    # Send email
    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=message,
        attachments=attachments,
        reference_doctype="DATEV Export SUT Settings",
        reference_name="DATEV Export SUT Settings"
    )

    # Clean up temporary files
    for file_info in file_paths:
        try:
            os.remove(file_info['path'])
        except:
            pass

def format_email_message(file_paths):
    """Format detailed email message."""
    message = "<p>DATEV LODAS export completed successfully.</p>"
    message += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
    message += "<tr><th>Company</th><th>Employees</th><th>File</th></tr>"

    for file_info in file_paths:
        company = file_info['company']
        employee_count = file_info['employee_count']
        filename = file_info['filename']

        message += f"<tr><td>{company}</td><td>{employee_count}</td><td>{filename}</td></tr>"

    message += "</table>"
    message += "<p>The export flags for these employees have been reset.</p>"

    return message

def create_datev_folder():
    """Create folder for DATEV exports if it doesn't exist."""
    if not frappe.db.exists("File", {"file_name": "DATEV Exports", "is_folder": 1}):
        folder = frappe.new_doc("File")
        folder.file_name = "DATEV Exports"
        folder.is_folder = 1
        folder.folder = "Home"
        folder.save()

    return "Home/DATEV Exports"