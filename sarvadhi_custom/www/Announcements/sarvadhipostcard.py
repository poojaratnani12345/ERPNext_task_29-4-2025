import frappe

def get_context(context):


    postcards = frappe.get_all("Sarvadhi Announcements",
        filters={"published": 1},
        fields=["name","announcement_name","subject", "description","created_by"],
        order_by="creation desc",
        limit_page_length=10
    )

    context.postcards = postcards 
    
    return context

