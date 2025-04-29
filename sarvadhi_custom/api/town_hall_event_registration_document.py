
import frappe
from frappe import _
from frappe.utils import validate_email_address

@frappe.whitelist(allow_guest=True)
def register_for_event():
    """
    Whitelisted API to register for a Town Hall Event.
    """
    data = frappe.form_dict

    required_fields = ["event_name", "full_name", "email"]
    missing_fields = [f for f in required_fields if not data.get(f)]

    if missing_fields:
        frappe.throw(_("Missing required fields: {0}").format(", ".join(missing_fields)))

    event_name = data.get("event_name")
    full_name = data.get("full_name")
    email = data.get("email")
    phone = data.get("phone")

    if not validate_email_address(email):
        frappe.throw(_("Invalid email address: {0}").format(email))

    if not frappe.db.exists("Town Hall Event", event_name):
        frappe.throw(_("Event '{0}' does not exist").format(event_name))

    # Optional: Split full_name into first and last name
    names = full_name.strip().split(" ", 1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""

    registration_data = {
        "doctype": "Town Hall Event Registration",
        "town_hall_event": event_name,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "status": "Pending"  
    }

    try:
        registration_doc = frappe.get_doc(registration_data)
        registration_doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "message": _("Registration successful"),
            "registration_id": registration_doc.name,
            "full_name": full_name,
            "event": event_name,
            "phone": phone,
            "email": email
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Event Registration Failed"))
        frappe.throw(_("An error occurred during registration. Please try again."))