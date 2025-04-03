// Copyright (c) 2025, sarvadhi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Discussion Post", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Discussion Post', {
    is_poll: function(frm) {
        // Show or hide the Poll Options table based on "Is Poll" checkbox
        frm.toggle_display('poll_options', frm.doc.is_poll);
    },
    
    refresh: function(frm) {
        // Ensure the toggle works when the form loads
        frm.toggle_display('poll_options', frm.doc.is_poll);
    }
});
frappe.ui.form.on('Discussion Post', {
    onload: function(frm) {
            if (!frm.doc.created_by) {  // Only set if empty
                frm.set_value('created_by', frappe.session.user);
            }
    }
})