frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        // Add Export button to Employee form
        frm.add_custom_button(__('Export to DATEV'), function() {
            frappe.confirm(
                __('Export this employee to DATEV LODAS?'),
                function() {
                    // On Yes

                    frappe.call({
                        method: 'sut_app_datev_export.sut_app_datev_export.doctype.datev_export_sut_settings.datev_export_sut_settings.export_single_employee',
                        args: {
                            employee: frm.doc.name
                        },
                        freeze: true,
                        freeze_message: __('Exporting employee data...'),
                        callback: function(r) {
                            if (r.message) {
                                frappe.msgprint({
                                    title: __('Export Complete'),
                                    indicator: 'green',
                                    message: __('Employee exported successfully. Email sent to {0}', [r.message.email])
                                });

                               
                                    
                            }
                        }
                    }); // end call 
                   
                }
            );
        }, __('Aktionen'));


            // Add button to navigate to the filtered list of Personalerfassungsbogen
            frm.add_custom_button(__('Übersicht Personalerfassungsbogen'), function() {
                frappe.set_route('List', 'Personalerfassungsbogen', {
                    'employee': frm.doc.name
                });
            }, __('Aktionen'));


            frm.add_custom_button(__('Übersicht GEHALTSVERHANDLUNG'), function() {
                frappe.set_route('List', 'GEHALTSVERHANDLUNG', {
                    'zum_mitarbeiter': frm.doc.name
                });
            }, __('Aktionen'));


            frm.add_custom_button(__('Neuer Personalerfassungsbogen'), function() {
                frappe.new_doc('Personalerfassungsbogen', {
                    'employee': frm.doc.name,
                    'employee_name': frm.doc.employee_name // Assuming employee_name is the field name
                });
            }, __('Aktionen'));


    } , 
        onload: function(frm) {
        // Add a red warning across the screen
        frm.dashboard.clear_headline(); // Clear existing headline

        frm.dashboard.set_headline(`
            <div style="
                background-color: #ffcccc;
                color: red;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                padding: 12px;
                border: 2px solid red;
                margin-bottom: 15px;
            ">
                ⚠️ Achtung! Alle rückwirkenden Änderungen der Gehaltsbestandteile werden beim DATEV Import nur für den aktuell laufenden Monat berücksichtigt!
                Rückwirkungen müssen manuell an die Lohnabrechnung gemeldet werden!
            </div>
        `);
    }
});