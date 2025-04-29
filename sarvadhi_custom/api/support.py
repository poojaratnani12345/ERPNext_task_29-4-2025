from isodate import parse_date
import frappe
from frappe.core.doctype.user.user import now_datetime
from frappe.desk.doctype.changelog_feed.changelog_feed import redis_cache
from frappe.email.receive import add_days
import frappe.rate_limiter
from frappe.utils import get_datetime, time_diff_in_seconds
from frappe.utils.redis_wrapper import RedisWrapper


redis_cache = RedisWrapper()
@frappe.whitelist()
def get_issue_types():
    issue_types = frappe.get_all("Issue Type", fields=["name"])
    print(issue_types)
    return issue_types


@frappe.whitelist(allow_guest=True)  
def create_issue():
    try:
        # ip_address = frappe.local.request_ip

        # max_requests = 2  
        # time_window_minutes = 1  
    
        # rate_limit_key = f"rate_limit:{ip_address}"
        # print('rate_limit_key:', rate_limit_key)

        # request_count = redis_cache.get(rate_limit_key)
        # if request_count:
        #     request_count = int(request_count)
        #     if request_count >= max_requests:
        #         frappe.msgprint('you have already submitted the form twice in the last minute. Please try again later.')
        #         return {
        #             "error": "You have already submitted the form twice in the last minute. Please try again later.",
        #             "status_code": 429 
        #         }
        # else:
        #     request_count = 0

        # new_request_count = redis_cache.incr(rate_limit_key)

        # if request_count == 0:
        #     redis_cache.expire(rate_limit_key, time_window_minutes * 60)

        # if new_request_count > max_requests:
        #     frappe.msgprint('you have already submitted the form twice in the last minute. Please try again later.')
        #     return {
        #         "error": "You have already submitted the form twice in the last minute. Please try again later.",
        #         "status_code": 429  
        #     }

        form_data = frappe.local.form_dict  
        files = frappe.local.request.files  

        issue = frappe.get_doc({
            "doctype": "Issue",
            "issue_type": form_data.get("issue_type"),
            "subject": 'Issue',
            "description": form_data.get("description"),
            "status": "Open", 
            'priority': "Medium"
        })
        print("Issue Document:", issue)

        issue.insert(ignore_permissions=True)
        frappe.db.commit()

        print("Issue created:", issue.name)

        if files:
            for file_key, file_data in files.items():
                file_doc = frappe.get_doc(
                    {
                        "doctype": "File",
                        "file_name": file_data.filename,
                        "content": file_data.stream.read(),
                        "attached_to_doctype": "Issue",
                        "attached_to_name": issue.name,
                    }
                )
                file_doc.insert(ignore_permissions=True)
                frappe.db.commit()

            print("File(s) attached successfully")
        else:
            print("No files uploaded")

        return {"message": "Issue created successfully", "issue_name": issue.name}

    except ValueError as e:
        frappe.log_error("Validation Error", str(e))
        return {"error": f"Validation error: {str(e)}"}

    except frappe.MandatoryError as e:
        frappe.log_error("Mandatory Field Error", str(e))
        return {"error": f"Mandatory field(s) missing: {str(e)}"}

    except Exception as e:
        frappe.log_error("Error creating Issue", str(e))
        return {"error": "An error occurred while creating the issue."}
    




@frappe.whitelist(allow_guest=True)  
def send_reminder_to_support_team():
    try:
        print("Scheduler Triggered: send_reminder_to_support_team")
        current_time = now_datetime()
        cutoff_date = add_days(current_time, -2)
        print("Current Time:", current_time)
        print("Cutoff Date:", cutoff_date)
       
        unassigned_issues=get_unassigned_issues()
        print("unassign issue:",unassigned_issues)

        if unassigned_issues:
            recipients = get_support_team_email()
            if not recipients:
                frappe.log_error("No Support Agents Found", "Scheduler Error")
                return

            print("Recipients:", recipients)
            subject = "Reminder: Unassigned Issues Pending"
            message = f"""
            Dear Support Team,

            The following issues have been unassigned for more than 2 days:

            {generate_issue_list(unassigned_issues)}

            Please review and assign them as soon as possible.

            Regards,
            System Administrator
            """
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message,
                now=True,
            )

            frappe.log_error("Reminder Email Sent to Support Team", "Scheduler Success")

    except Exception as e:
        frappe.log_error(f"Error in Scheduler: {str(e)}", "Scheduler Error")


def get_support_team_email():
    support_users = frappe.get_all(
        "User",
        filters=[
            ["Has Role", "role", "=", "Support Team"], 
            ["User", "enabled", "=", 1],           
        ],
        fields=["email"]  
    )
    return [user.email for user in support_users]


def generate_issue_list(issues):
    issue_list = []
    for issue in issues:
        issue_list.append(f"- Issue #{issue.name}: {issue.subject} (Created on {issue.creation})")
    return "\n".join(issue_list)



def get_unassigned_issues():
    """
    Fetch all issues that do not have corresponding ToDo records.
    """
    try:
        all_issues = frappe.get_all(
            "Issue",
            fields=["name"], 
            filters={"status": "Open"}  
        )
        all_issue_names = {issue.name for issue in all_issues}  
        print('all_issue_names:',all_issue_names)

        assigned_issues = frappe.get_all(
            "ToDo",
            fields=["reference_name"],
            filters={"reference_type": "Issue",'status':'Open'}
        )
        assigned_issue_names = {issue.reference_name for issue in assigned_issues}  
        print('assigned_issue_names:',assigned_issue_names)

        unassigned_issue_names = all_issue_names - assigned_issue_names
        print('unassigned_issue_names:',unassigned_issue_names)

        unassigned_issues = frappe.get_all(
            "Issue",
            filters={"name": ["in", list(unassigned_issue_names)]},
            fields=["name", "subject", "status", "creation"]  
        )

        return unassigned_issues

    except Exception as e:
        frappe.log_error(f"Error fetching unassigned issues: {str(e)}", "Scheduler Error")
        return []
    











import frappe

@frappe.whitelist(allow_guest=True)
def validate_recaptcha_suport_form(recaptcha_response):
    # Bypass reCAPTCHA validation during development
    if "localhost" in frappe.request.host:
        return {"success": True}

    # Perform actual reCAPTCHA validation
    # (Your validation logic here)