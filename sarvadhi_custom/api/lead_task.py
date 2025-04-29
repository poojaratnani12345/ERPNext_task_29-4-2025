import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_leads(status=None, salesperson=None):
    """
    Fetch leads based on filters: status and salesperson using a raw SQL query.
    Joins Lead table with Customer Interaction Log table to fetch salesperson.
    """
    query = """
        SELECT 
            l.name AS lead_name,
            l.custom_custom_customer AS customer_name,
            cil.salesperson AS salesperson,
            l.status AS lead_status,
            l.custom_next_contact_date AS next_contact_date
        FROM 
            `tabLead` l
        LEFT JOIN 
            `tabCustomer Interaction Log` cil
        ON 
            l.custom_custom_customer = cil.customer
        WHERE 
            1=1
    """

    filters = []
    if status:
        filters.append(f"l.status = '{frappe.db.escape(status)}'")
    if salesperson:
        filters.append(f"cil.sales_person = '{frappe.db.escape(salesperson)}'")

    if filters:
        query += " AND " + " AND ".join(filters)

    # Execute the query
    leads = frappe.db.sql(query, as_dict=True)

    return leads









def send_lead_status_notification(doc, method):
    print("Lead status changed to 'In Progress', sending email notification...")
    """
    Sends an automated email to the assigned Salesperson when a Lead reaches the "In Progress" status.
    The salesperson is fetched from the linked Customer Interaction Log.
    """
    if doc.status == "In Progress":
        customer_interaction_log = doc.custom_custom_sales_person
        print("Customer Interaction Log:", customer_interaction_log)

        if not customer_interaction_log:
            frappe.log_error(
                f"No Customer Interaction Log linked to lead: {doc.name}",
                "Lead Status Notification Error"
            )
            return

        # Fetch the salesperson from the linked Customer Interaction Log
        salesperson = frappe.db.get_value(
            "Customer Interaction Log",
            customer_interaction_log,
            "sales_person"
        )
        print("Salesperson:", salesperson)
        if not salesperson:
            frappe.log_error(
                f"No salesperson found in Customer Interaction Log: {customer_interaction_log}",
                "Lead Status Notification Error"
            )
            return

        user_email = frappe.db.get_value("User", {"enabled": 1, "name": salesperson}, "email")
        print("User Email:", user_email)
        if not user_email:
            frappe.log_error(
                f"No email found for salesperson: {salesperson}",
                "Lead Status Notification Error"
            )
            return

        subject = _("Lead Updated: {0}").format(doc.name)
        message = f"""
            <p>Dear {salesperson},</p>
            <p>The lead <b>{doc.lead_name}</b> has been marked as 'In Progress'. Please take the necessary actions.</p>
            <ul>
                <li><b>Lead Name:</b> {doc.lead_name}</li>
                <li><b>Customer Name:</b> {doc.customer_name}</li>
                <li><b>Next Contact Date:</b> {doc.custom_next_contact_date}</li>
            </ul>
            <p>Thank you,</p>
            <p>Your Sales Management System</p>
        """

        try:
            frappe.sendmail(
                recipients=user_email,
                subject=subject,
                message=message,
                reference_doctype="Lead",
                reference_name=doc.name,
                new=True
            )
            frappe.msgprint(_("Email notification sent to {0}").format(salesperson))
        except Exception as e:
            frappe.log_error(title="Error Sending Lead Status Notification", message=str(e))