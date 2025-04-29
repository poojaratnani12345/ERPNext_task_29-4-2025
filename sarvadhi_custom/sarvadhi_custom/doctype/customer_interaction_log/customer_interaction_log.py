# Copyright (c) 2025, sarvadhi and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class CustomerInteractionLog(Document):
	def on_save(self, method):
		"""
		Sends an email notification to the assigned salesperson when a lead's status changes to 'In Progress'.
		"""
		# Check if the lead status is 'In Progress'
		if self.status == "In Progress":
			print("Lead status is 'In Progress', sending email notification...")
			# Get the assigned salesperson
			salesperson = self.sales_person
			print("Salesperson:", salesperson)
			if not salesperson:
				frappe.log_error("No salesperson assigned to lead: {}".format(self.name), "Lead Status Notification Error")
				return

			# Fetch user details for the salesperson
			user_email = salesperson
			if not user_email:
				frappe.log_error("No email found for salesperson: {}".format(salesperson), "Lead Status Notification Error")
				return

			# Prepare email content
			subject = frappe._("Lead Updated: {0}").format(self.name)
			message = f"""
				<p>Dear {salesperson},</p>
				<p>The lead <b>{self.lead_name}</b> has been marked as 'In Progress'. Please take the necessary actions.</p>
				<ul>
					<li><b>Lead Name:</b> {self.lead_name}</li>
					<li><b>Customer Name:</b> {self.customer_name}</li>
					<li><b>Next Contact Date:</b> {self.custom_next_contact_date}</li>
				</ul>
				<p>Thank you,</p>
				<p>Your Sales Management System</p>
			"""

			# Send the email
			try:
				frappe.sendmail(
					recipients=user_email,
					subject=subject,
					message=message,
					reference_doctype="Lead",
					reference_name=self.name,
					new=True
				)
				frappe.msgprint(frappe._("Email notification sent to {0}").format(salesperson))
			except Exception as e:
				frappe.log_error(title="Error Sending Lead Status Notification", message=str(e))
