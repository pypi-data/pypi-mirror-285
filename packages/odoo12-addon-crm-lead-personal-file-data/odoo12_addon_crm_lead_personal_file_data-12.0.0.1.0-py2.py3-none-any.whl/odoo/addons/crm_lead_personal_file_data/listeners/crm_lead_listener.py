from odoo.addons.component.core import Component
from odoo.addons.dms_res_model_root_directory.services.record_directory_service import (
    RecordDirectoryService,
)


class CrmLeadListener(Component):
    _name = "crm.lead.listener"
    _inherit = "base.event.listener"
    _apply_on = ["crm.lead"]

    def on_record_write(self, record, fields=None):
        """
        When a partner is assigned to a CRMLead that has dms
        files in pending assignment directory, move all
        files to a personal data directory from the given partner.
        """

        if not record.partner_id:
            return

        service = RecordDirectoryService(self.env)
        pending_assigment_dir = self.env.ref(
            "crm_lead_personal_file_data.pending_partner_assignment"
        )
        pending_assigment_lead_dir = (
            service.search_record_directory_under_parent_directory(
                record, pending_assigment_dir
            )
        )

        if pending_assigment_lead_dir:
            personal_data_dir = self.env.ref(
                "crm_lead_personal_file_data.personal_data_directory"
            )
            personal_data_partner_dir = (
                service.get_record_directory_under_parent_directory(
                    record.partner_id, personal_data_dir
                )
            )

            pending_assigment_lead_dir.move_files_to(
                personal_data_partner_dir, record_linked=True, autodelete=True
            )
