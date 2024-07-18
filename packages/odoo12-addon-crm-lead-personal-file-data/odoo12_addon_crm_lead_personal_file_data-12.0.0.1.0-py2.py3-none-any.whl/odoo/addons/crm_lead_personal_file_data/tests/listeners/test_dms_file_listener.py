from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import SavepointCase


class TestDmsFileListener(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestDmsFileListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.lead = self.env["crm.lead"].create(
            {"name": "Test Lead", "partner_id": self.partner.id}
        )
        self.pending_assigment_dir = self.env.ref(
            "crm_lead_personal_file_data.pending_partner_assignment"
        )
        self.personal_data_dir = self.env.ref(
            "crm_lead_personal_file_data.personal_data_directory"
        )
        self.file_params = {
            "name": self.lead.name,
            "content": b"0000",
            "root_directory_id": self.pending_assigment_dir.id,
            "res_model": self.lead._name,
            "res_id": self.lead.id,
        }

    def test_on_record_create(self):
        assert self.file_params["res_id"] == self.lead.id

        # Activate listener
        file = self.env["dms.file"].create(self.file_params)

        assert file.directory_id.parent_id == self.personal_data_dir
        assert file.res_model == self.partner._name
        assert file.res_id == self.partner.id
        assert not self.env["dms.directory"].search(
            [
                ("parent_id", "=", self.pending_assigment_dir.id),
                ("res_model", "=", self.lead._name),
                ("res_id", "=", self.lead.id),
            ]
        )  # lead directory deleted
