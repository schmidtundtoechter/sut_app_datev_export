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