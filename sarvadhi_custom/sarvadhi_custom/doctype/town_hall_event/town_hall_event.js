// Copyright (c) 2025, sarvadhi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Town Hall Event", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Town Hall Event', {
    refresh(frm) {
        // Show the custom button only if the document is not new
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Registrations'), function () {
                const eventName = frm.doc.name;

                frappe.set_route('List', 'Town Hall Event Registration', {
                    town_hall_event: eventName
                });
            }, __('Actions'));
        }
    }
});