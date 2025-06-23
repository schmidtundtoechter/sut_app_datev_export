// Copyright (c) 2025, ahmad900mohammad@gmail.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Personalerfassungsbogen", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Personalerfassungsbogen', {
    refresh: function(frm) {
        // Check if linked to an Employee
        if(frm.doc.employee) {
            // Add button to navigate to the Employee list view with filter
            frm.add_custom_button(__('View Employee'), function() {
                frappe.set_route('List', 'Employee', {
                    'name': frm.doc.employee
                });
            }, __('Aktionen'));
        }
    }
});

// Function to validate decimal format
function validateDecimalFormat(value, fieldName, frm) {
    // Skip validation if field is empty
    if (!value) return true;
    
    // Convert to string to handle the validation
    let valueStr = value.toString();
    
    // Check for both comma and dot as decimal separators
    let beforeDecimal = '';
    
    if (valueStr.includes('.')) {
        // Split by comma and check the part before comma
        let parts = valueStr.split('.');
        beforeDecimal = parts[0];
    } else {
        // No decimal separator, check the whole number
        beforeDecimal = valueStr;
    }
    
    // Check if the part before decimal separator has more than 2 digits
    if (beforeDecimal.length > 2) {
        frappe.msgprint({
            title: __('Invalid Format'),
            message: __('Only 2 digits are allowed before the decimal separator. Example: 15,42 '),
            indicator: 'red'
        });
        
        // Clear the field
        frm.set_value(fieldName, '');
        return false;
    }
    
    return true;
}

frappe.ui.form.on('Personalerfassungsbogen', {
    stundenlohn: function(frm) {
        validateDecimalFormat(frm.doc.stundenlohn, 'stundenlohn', frm);
    },
    
    stundenlohn_1: function(frm) {
        console.log(frm.doc.stundenlohn_1)
        validateDecimalFormat(frm.doc.stundenlohn_1, 'stundenlohn_1', frm);
    },
    
  
});