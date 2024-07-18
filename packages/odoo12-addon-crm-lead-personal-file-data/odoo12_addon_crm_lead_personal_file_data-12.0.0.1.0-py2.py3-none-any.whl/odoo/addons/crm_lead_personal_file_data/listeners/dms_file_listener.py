from odoo.addons.component.core import Component
from odoo.addons.dms_res_model_root_directory.services.record_directory_service import (
    RecordDirectoryService,
)


class DmsFileListener(Component):
    _name = "dms.file.listener"
    _inherit = "base.event.listener"
    _apply_on = ["dms.file"]

    def on_record_create(self, record, fields=None):
        """
        When a dms file from pending partner assignment directory
        is linked to a CRMLead that already has a partner, move all
        files to a personal data directory from the given partner.
        """

        if not record.res_model == "crm.lead":
            return

        lead = self.env[record.res_model].browse(record.res_id)
        pending_assigment_dir = self.env.ref(
            "crm_lead_personal_file_data.pending_partner_assignment"
        )

        if lead.partner_id and record.directory_id.parent_id == pending_assigment_dir:
            service = RecordDirectoryService(self.env)
            personal_data_dir = self.env.ref(
                "crm_lead_personal_file_data.personal_data_directory"
            )
            personal_data_partner_dir = (
                service.get_record_directory_under_parent_directory(
                    lead.partner_id, personal_data_dir
                )
            )
            record.directory_id.move_files_to(
                personal_data_partner_dir, record_linked=True, autodelete=True
            )
