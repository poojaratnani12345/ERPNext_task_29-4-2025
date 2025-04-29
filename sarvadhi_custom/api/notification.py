import frappe
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def notify_shift_end(doc=None, method=None):
    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "company_email", "default_shift"])
    current_time = datetime.now().time()
    today = datetime.now().date()

    for emp in employees:
        if not emp.get("default_shift") or not emp.get("company_email"):
            continue

        shift = frappe.get_value("Shift Type", emp["default_shift"], ["end_time"])
        if not shift:
            frappe.log_error(f"No Shift Type found for employee {emp['name']}")
            continue

        end_time = convert_to_time(shift)

        if current_time <= end_time:
            continue

        checkins = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": emp["name"],
                "time": ["between", [datetime.combine(today, datetime.min.time()), datetime.combine(today, datetime.max.time())]],
                "log_type": "OUT"
            },
            fields=["time"],
            order_by="time desc"
        )

        if not checkins or checkins[0]["time"].time() < end_time:
            send_shift_end_email(emp, end_time)
            log_employee_notification(emp)
            notify_hr_manager(emp)


def convert_to_time(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return datetime.strptime(f"{hours:02}:{minutes:02}:{seconds:02}", "%H:%M:%S").time()


def send_shift_end_email(emp, end_time):
    subject = "Shift Time Over Notification"
    message = f"Dear {emp['name']},<br><br>Your shift time has ended at {end_time}. Please ensure you check out.<br><br>Best Regards,<br>HR Team"
    try:
        frappe.sendmail(
            recipients=emp["company_email"],
            subject=subject,
            message=message,
            now=True
        )
    except Exception as e:
        frappe.log_error("Failed to send shift end email", str(e))


def log_employee_notification(emp):
    try:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": "You have not checked out after shift end time.",
            "for_user": emp["company_email"],
            "type": "Alert",
            "document_type": "Employee",
            "document_name": emp["name"],
            "email_content": "You have not checked out after shift end time."
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("Notification log created for employee:", emp["company_email"])
    except Exception as e:
        frappe.log_error("Failed to log employee notification", str(e))


def notify_hr_manager(emp):
    hr_manager = get_hr_manager()
    print("HR Manager:", hr_manager)
    if not hr_manager:
        return

    try:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"{emp['company_email']} has not checked out after shift end time.",
            "for_user": hr_manager,
            "type": "Alert",
            "document_type": "Employee",
            "document_name": emp["name"],
            "email_content": f"{emp['company_email']} has not checked out after shift end time."
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("Notification log created for HR Manager:", hr_manager)
    except Exception as e:
        frappe.log_error("Failed to notify HR Manager", str(e))


def get_hr_manager():
    hr_managers = frappe.get_all('Has Role', filters={'role': 'HR Manager'}, fields=['parent'])
    if hr_managers:
        return hr_managers[0]['parent']

    managers = frappe.get_all('Employee', filters={'designation': 'HR Manager'}, fields=['company_email','name'])
    if managers and managers[0].get('company_email'):
        print("HR Manager User ID:", managers[0]['company_email'])
        print("HR Manager Name:", managers[0]['name'])
        return managers[0]['company_email']

    return None












