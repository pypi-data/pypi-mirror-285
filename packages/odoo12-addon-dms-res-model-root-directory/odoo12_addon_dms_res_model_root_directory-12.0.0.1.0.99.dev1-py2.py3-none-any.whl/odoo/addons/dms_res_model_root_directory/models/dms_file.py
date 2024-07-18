from odoo import api, models
from ..services.record_directory_service import RecordDirectoryService


class File(models.Model):
    _inherit = "dms.file"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "root_directory_id" in vals:
                record = self.env[vals["res_model"]].browse(vals["res_id"])
                root_dir = self.env["dms.directory"].browse(vals["root_directory_id"])

                service = RecordDirectoryService(self.env)
                directory = service.get_record_directory_under_parent_directory(
                    record, root_dir
                )
                vals["directory_id"] = directory.id
                vals.pop("root_directory_id", None)
                # Delete params so dms.File._create_model_attachment` is executed
                vals.pop("res_id", None)
                vals.pop("res_model", None)

        return super(File, self).create(vals_list)
