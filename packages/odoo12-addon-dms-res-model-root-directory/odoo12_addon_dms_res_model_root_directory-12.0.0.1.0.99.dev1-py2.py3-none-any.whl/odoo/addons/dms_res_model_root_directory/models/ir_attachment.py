from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _dms_directories_create(self):
        """
        Monkey-patched method from dms module
        Create directories with a different name for res.partners
        """

        items = self._get_dms_directories(self.res_model, False)
        for item in items:
            model_item = self.env[self.res_model].browse(self.res_id)
            ir_model_item = self.env["ir.model"].search(
                [("model", "=", self.res_model)]
            )
            if self.res_model == "res.partner":
                dir_name = f"{model_item.vat} - {model_item.name}"
            else:
                dir_name = model_item.display_name

            self.env["dms.directory"].sudo().with_context(check_name=False).create(
                {
                    "name": dir_name,
                    "model_id": ir_model_item.id,
                    "res_model": self.res_model,
                    "res_id": self.res_id,
                    "parent_id": item.id,
                    "storage_id": item.storage_id.id,
                }
            )
