from odoo import models


class DMSDirectory(models.Model):
    _inherit = "dms.directory"

    def move_files_to(self, new_directory, record_linked=False, autodelete=False):
        """
        Move files from this directory to new directory
        """

        write_params = {"directory_id": new_directory.id}
        if record_linked:
            write_params["res_model"] = new_directory.res_model
            write_params["res_id"] = new_directory.res_id

        for file in self.file_ids:
            file.write(write_params)

        if autodelete and not self.file_ids:
            # Delete empty old directory
            self.unlink()
