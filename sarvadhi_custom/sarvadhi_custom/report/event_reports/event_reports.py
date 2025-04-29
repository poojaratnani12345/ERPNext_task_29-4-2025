import frappe
from frappe.utils import nowdate

def execute(filters=None):
    conditions = ""
    if filters:
        if filters.get("event"):
            conditions += f" AND e.start_datetime >= IFNULL('{filters.get('from_date')}', '2000-01-01')"
        if filters.get("to_date"):
            conditions += f" AND e.start_datetime <= '{filters.get('to_date')}'"
        if filters.get("event"):
            conditions += f" AND r.town_hall_event = '{filters.get('event')}'"

    columns = [
        {"label": "Event Name", "fieldname": "event_name", "fieldtype": "Link", "options": "Town Hall Event"},
        {"label": "Total Registrations", "fieldname": "registrations", "fieldtype": "Int"},
    ]

    data = frappe.db.sql(f"""
        SELECT r.town_hall_event AS event_name, COUNT(*) AS registrations
        FROM `tabTown Hall Event Registration` r
        JOIN `tabTown Hall Event` e ON r.town_hall_event = e.name
        WHERE 1=1 {conditions}
        GROUP BY r.town_hall_event
        ORDER BY registrations DESC
    """, as_dict=True)
    
    chart = {
        "data": {
            "labels": [d.event_name for d in data],
            "datasets": [
                {
                    "name": "Registrations",
                    "values": [d.registrations for d in data]
                }
            ]
        },
        "type": "pie"
    }

    return columns, data, None, chart

