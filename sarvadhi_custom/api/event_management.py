
import frappe
from frappe import _
from frappe.email.doctype.email_account.email_account import datetime
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
        # Insert registration
        reg_doc = frappe.get_doc(registration_data)
        reg_doc.insert(ignore_permissions=True)

        # Commit changes
        frappe.db.commit()

        # Fetch event details
        event_doc = frappe.get_doc("Town Hall Event", event_name)

        # Attach event info to context
        context = {
            "doc": event_doc,
            "full_name": full_name,
            "event_name": event_name,
            "start_datetime": event_doc.start_datetime,
            "end_datetime": event_doc.end_datetime,
        }

        # Compose subject and message directly
        subject = f"Thank You for Registering for {context['event_name']}"
        message = f"""
        <p>Hello {context['full_name']},</p>
        <p>Thank you for registering for the event <strong>{context['event_name']}</strong>.</p>
        <p><strong>Date & Time:</strong> {context['start_datetime']} - {context['end_datetime']}</p>
        <p>We look forward to seeing you there!</p>
        """

        # Send the email
        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message,
            reference_doctype="Town Hall Event Registration",
            reference_name=reg_doc.name
        )

        return {
            "message": _("Registration successful"),
            "registration_id": reg_doc.name,
            "full_name": full_name,
            "event": event_name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Event Registration Failed"))
        frappe.throw(_("An error occurred during registration. Please try again."))



@frappe.whitelist()
def update_completed_events():
    """
    Finds all Town Hall Events whose end_datetime is in the past,
    and updates their status to 'Completed' if not already done.
    """
    now = datetime.now()

    events = frappe.get_all("Town Hall Event", filters={
        "end_datetime": ("<", now),
        "status": ("!=", "Completed")
    }, fields=["name"])

    for event in events:
        try:
            doc = frappe.get_doc("Town Hall Event", event.name)
            doc.status = "Completed"
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger().info(f"Updated event {event.name} status to 'Completed'")
        except Exception as e:
            frappe.logger().error(f"Failed to update event {event.name}: {str(e)}")

    frappe.db.commit()