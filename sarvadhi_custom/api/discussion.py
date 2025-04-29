import frappe

@frappe.whitelist(allow_guest=True)
def get_announcements(channel=None, page=1, limit=5):
    filters = {"published": 1}
    if channel:
        filters["type_of_announcement"] = channel

    try:
        start = (int(page) - 1) * int(limit)

        announcements = frappe.get_all(
            "Sarvadhi Announcements",
            fields=["name", "announcement_name", "description", "created_by", "creation"],
            filters=filters,
            order_by="creation desc",
            start=start,
            page_length=int(limit)
        )

        total_count = frappe.db.count("Sarvadhi Announcements", filters=filters)

        for announcement in announcements:
            # Reactions
            reactions = frappe.get_all(
                "User Table For Announcement",
                filters={"parent": announcement["name"]},
                fields=["user", "reaction"]
            )
            announcement["reactions"] = reactions

            # Attachments
            attachments = frappe.get_all(
                "File",
                filters={
                    "attached_to_doctype": "Sarvadhi Announcements",
                    "attached_to_name": announcement["name"]
                },
                fields=["file_url", "file_name"]
            )
            announcement["attachments"] = [
                {"url": a.file_url, "name": a.file_name} for a in attachments
            ]

            # User Image
            email = frappe.db.get_value("User", {"username": announcement["created_by"]}, "name")
            user_image = frappe.db.get_value("User", email, "user_image") if email else None
            announcement["user_image"] = user_image or "/files/default_avatar.jpg"

            # Format creation date
            if announcement.get("creation"):
                announcement["creation"] = announcement["creation"].isoformat()

        return {
            "message": announcements,
            "total_count": total_count,
            "page": int(page),
            "limit": int(limit)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_announcements")
        return {"error": "Failed to fetch announcements."}


@frappe.whitelist(allow_guest=True)
def fetch_channels():
    try:
        user = frappe.session.user
        return frappe.get_all(
            "Discussion Channel",
            fields=["name", "channel_name", "icon"],
            filters=[["Members", "user", "=", user]]
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in fetch_channels")
        return {"error": "An error occurred while fetching channels."}


@frappe.whitelist(allow_guest=True)
def update_reaction(post_id=None, emoji=None):
    data = frappe.form_dict
    post_id = data.get("post_id") or post_id
    emoji = data.get("emoji") or emoji

    if not post_id:
        frappe.throw("Post ID is required")

    try:
        user = frappe.session.user
        announcement = frappe.get_doc("Sarvadhi Announcements", post_id)

        existing_reaction = next(
            (r for r in announcement.reactions if r.user == user), None
        )

        if existing_reaction:
            existing_reaction.reaction = emoji
        else:
            announcement.append("reactions", {"user": user, "reaction": emoji})

        announcement.save()
        frappe.db.commit()
        return {"status": "success"}

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in update_reaction")
        return {"error": "Failed to update reaction."}


def set_created_by(doc, method):
    if not doc.get("created_by"):
        username = frappe.db.get_value("User", frappe.session.user, "username")
        doc.created_by = username if username else frappe.session.user
 


@frappe.whitelist(allow_guest=True)
def get_users_by_role(roles):
    if isinstance(roles, str):
        roles = frappe.parse_json(roles)

    try:
        user_links = frappe.get_all(
            "Has Role",
            filters={"role": ["in", roles]},
            fields=["parent"]
        )

        user_ids = list({u["parent"] for u in user_links})

        return frappe.get_all(
            "User",
            filters={"name": ["in", user_ids]},
            fields=["name", "username"]
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in get_users_by_role")
        return {"error": "Failed to fetch users by role."}


@frappe.whitelist(allow_guest=True)
def get_attachments():
    try:
        attachments = frappe.get_all(
            'File',
            fields=["name", 'attached_to_doctype', 'attached_to_name', 'file_url'],
            limit=1
        )
        return attachments
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in get_attachments")
        return {"error": "Failed to fetch attachments."}





@frappe.whitelist()
def get_all_users():
    users = frappe.get_all(
        "User",
        filters={"enabled": 1},  # Only fetch active users
        fields=["name", "username" ],  # Adjust fields as needed
    )
    return users