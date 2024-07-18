from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import SavepointCase


class TestCrmLeadListener(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestCrmLeadListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.lead = self.env["crm.lead"].create(
            {
                "name": "Test Lead",
            }
        )
        self.pending_assigment_dir = self.env.ref(
            "crm_lead_personal_file_data.pending_partner_assignment"
        )
        self.personal_data_dir = self.env.ref(
            "crm_lead_personal_file_data.personal_data_directory"
        )
        self.file = self.env["dms.file"].create(
            {
                "name": self.lead.name,
                "content": b"0000",
                "root_directory_id": self.pending_assigment_dir.id,
                "res_model": self.lead._name,
                "res_id": self.lead.id,
            }
        )

    def test_on_record_write(self):
        lead_directory = self.file.directory_id
        assert lead_directory.parent_id == self.pending_assigment_dir

        # Activate listener
        self.lead.write({"partner_id": self.partner.id})

        assert self.file.directory_id.parent_id == self.personal_data_dir
        assert self.file.res_model == self.partner._name
        assert self.file.res_id == self.partner.id
        assert not self.env["dms.directory"].search(
            [
                ("parent_id", "=", self.pending_assigment_dir.id),
                ("res_model", "=", self.lead._name),
                ("res_id", "=", self.lead.id),
            ]
        )  # lead directory deleted
