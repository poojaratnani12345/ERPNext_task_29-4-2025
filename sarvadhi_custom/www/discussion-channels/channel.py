import frappe

def get_context(context):
    channel_name = frappe.form_dict.get("name")

    if not channel_name:
        frappe.throw("Channel name is required")

    # Fetch all channels for the sidebar
    context.channels = frappe.get_all("Discussion Channel", fields=["name", "channel_name"])

    # Fetch the selected channel details
    context.channel = frappe.get_doc("Discussion Channel", channel_name)

    # Fetch posts of the selected channel
    context.posts = frappe.get_all(
        "Discussion Post",
        filters={"channel": channel_name},  # 🛠 Fix: Use "channel"
        fields=["*"]
    )



@frappe.whitelist(allow_guest=True)
def submit_vote():
    poll_id = frappe.form_dict.get("poll_id")
    vote = frappe.form_dict.get("vote")

    if not poll_id or not vote:
        return {"status": "error", "message": "Invalid vote submission"}

    poll = frappe.get_doc("Discussion Post", poll_id)
    
    # Find the selected option and update vote count
    for option in poll.poll_options:
        if option.option_text == vote:
            option.vote_count += 1
    
    # Increase total votes count
    poll.total_votes += 1
    poll.save()

    return {"status": "success", "message": "Vote recorded successfully!"}


