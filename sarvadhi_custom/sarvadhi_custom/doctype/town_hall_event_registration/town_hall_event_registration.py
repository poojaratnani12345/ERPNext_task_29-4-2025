import frappe
from frappe.model.document import Document, _
from frappe.utils import validate_email_address

class TownHallEventRegistration(Document):
    def validate(self):
        if self.first_name or self.last_name:
            self.full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()

        self.check_max_participants()

    def check_max_participants(self):
        event = frappe.get_doc("Town Hall Event", self.town_hall_event)
        confirmed_regs = frappe.db.count(
            "Town Hall Event Registration",
            {"town_hall_event": event.name, "status": "Confirmed"}
        )
        if event.max_participants and confirmed_regs >= event.max_participants:
            frappe.throw(_(
                "Cannot register: Maximum participants ({0}) reached for the event '{1}'"
            ).format(event.max_participants, event.event_name))