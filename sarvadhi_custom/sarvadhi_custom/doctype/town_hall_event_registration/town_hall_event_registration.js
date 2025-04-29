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


frappe.ui.form.on("Town Hall Event Registration", {
    refresh(frm) {
        // Auto-prepend country code to phone number
        frm.set_query("country", function () {
            return { filters: [["Country"]] };
        });
    },
    country(frm) {
        if (frm.doc.phone && frm.doc.country) {
            const countryInfo = frappe.get_region_info(frm.doc.country);
            const countryCode = countryInfo ? countryInfo.code : "";
            if (!frm.doc.phone.startsWith(`+${countryCode}`)) {
                frm.set_value("phone", `+${countryCode}${frm.doc.phone}`);
            }
        }
    }
});