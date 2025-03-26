frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        console.log('////////////////////////////////')
        // Add Export button to Employee form
        frm.add_custom_button(__('Export to DATEV'), function() {
            frappe.confirm(
                __('Export this employee to DATEV LODAS?'),
                function() {
                    // On Yes
                    frappe.call({
                        method: 'datev_export_sut.datev_export_sut.doctype.datev_export_sut_settings.datev_export_sut_settings.export_single_employee',
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
                    });
                }
            );
        }, __('Actions'));
    }
});