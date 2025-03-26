// Copyright (c) 2025, ahmad900mohammad@gmail.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("DATEV Export SUT Settings", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('DATEV Export SUT Settings', {
    refresh: function(frm) {
      frm.add_custom_button(__('Export all marked employees'), function() {
        frappe.call({
          method: 'datev_export_sut.datev_export_sut.doctype.datev_export_sut_settings.datev_export_sut_settings.export_employees',
          freeze: true,
          freeze_message: __('Exporting employee data...'),
          callback: function(r) {
            if (r.message) {
              frappe.msgprint({
                title: __('Export Complete'),
                indicator: 'green',
                message: __('Exported {0} employees. Email sent to {1}', [r.message.count, r.message.email])
              });
            }
          }
        });
      }, __('Actions'));
    }
  });