import frappe

def get_context(context):
    context.channels = frappe.get_all(
        "Discussion Channel",
        fields=["name", "channel_name", "description"]
    )
