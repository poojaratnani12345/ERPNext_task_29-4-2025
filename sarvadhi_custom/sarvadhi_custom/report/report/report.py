import frappe

def execute(filters=None):
    if filters is None:
        filters = {}

    filters.setdefault("customer_name", None)
    filters.setdefault("salesperson", None)
    query = """
    SELECT 
        l.name AS "Lead ID",
        l.lead_name AS "Lead Name",
        c.customer_name AS "Customer Name",
        (
            SELECT cil.salesperson
            FROM `tabCustomer Interaction Log` cil
            WHERE cil.customer = c.name
            ORDER BY cil.interaction_date DESC
            LIMIT 1
        ) AS "Salesperson",
        l.modified AS "Last Modified",
        l.status AS "Lead Status"
    FROM 
        `tabLead` l
    LEFT JOIN 
        `tabCustomer` c ON l.custom_custom_customer = c.name
    WHERE 
        -- Filter by Customer
        (c.name = %(customer_name)s OR %(customer_name)s IS NULL)
        
        -- Filter by Salesperson
        AND (
            %(salesperson)s IS NULL
            OR EXISTS (
                SELECT 1
                FROM `tabCustomer Interaction Log` cil
                WHERE cil.customer = c.name AND cil.salesperson = %(salesperson)s
            )
        );
    """

    # Execute the query with the preprocessed filters
    data = frappe.db.sql(query, filters, as_dict=True)

    # Define columns
    columns = [
        {"label": "Lead ID", "fieldname": "Lead ID", "fieldtype": "Data", "width": 120},
        {"label": "Lead Name", "fieldname": "Lead Name", "fieldtype": "Data", "width": 150},
        {"label": "Customer Name", "fieldname": "Customer Name", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Salesperson", "fieldname": "Salesperson", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Last Modified", "fieldname": "Last Modified", "fieldtype": "Datetime", "width": 150},
        {"label": "Lead Status", "fieldname": "Lead Status", "fieldtype": "Data", "width": 120},
    ]


    # Return the required values
    return columns, data, None, None, None, False




