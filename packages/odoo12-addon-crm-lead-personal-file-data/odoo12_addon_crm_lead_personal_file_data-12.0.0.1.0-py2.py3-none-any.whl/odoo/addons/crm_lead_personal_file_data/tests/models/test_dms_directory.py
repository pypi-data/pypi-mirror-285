from odoo.tests import common


class TestDmsDirectory(common.TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestDmsDirectory, self).setUp(*args, **kwargs)
        self.old_directory = self.env.ref("dms.directory_07_demo")
        self.new_directory = self.env.ref("dms.directory_05_demo")
        self.partner = self.env["res.partner"].create({"name": "New partner"})

    def test_move_files_to(self):
        assert len(self.old_directory.file_ids) == 3
        assert not self.new_directory.file_ids

        file_ids = self.old_directory.file_ids

        self.old_directory.move_files_to(self.new_directory)

        assert len(self.new_directory.file_ids) == 3
        assert self.new_directory.file_ids == file_ids

    def test_move_files_to_autodelete(self):
        self.old_directory.move_files_to(self.new_directory, autodelete=True)

        # directory deleted from db
        assert not self.env["dms.directory"].search(
            [("id", "=", self.old_directory.id)]
        )

    def test_move_files_to_record_linked(self):
        params = {
            "name": self.partner.name,
            "res_model": self.partner._name,
            "res_id": self.partner.id,
        }
        # new directory linked to partner record
        self.new_directory.write(params)

        self.old_directory.move_files_to(self.new_directory, record_linked=True)

        assert len(self.new_directory.file_ids) == 3
        assert self.new_directory.file_ids[0].res_model == self.partner._name
        assert self.new_directory.file_ids[0].res_id == self.partner.id
