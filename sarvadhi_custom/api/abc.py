import frappe

@frappe.whitelist()
def get_custom_data():
    frappe.response['message'] = {
        "status": "success",
        "data": {
            "name": "John Doe",
            "role": "Developer"
        }
    }
