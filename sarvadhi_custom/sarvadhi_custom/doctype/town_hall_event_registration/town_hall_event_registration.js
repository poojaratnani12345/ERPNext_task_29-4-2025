// Copyright (c) 2025, sarvadhi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Town Hall Event Registration", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Town Hall Event Registration", {
    refresh(frm) {
    },
    validate(frm) {
        let email = frm.doc.email;
        if (email && !validateEmail(email)) {
            frappe.msgprint(__("Please enter a valid email address."));
            frappe.validated = false; 
        }
    }
})

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

