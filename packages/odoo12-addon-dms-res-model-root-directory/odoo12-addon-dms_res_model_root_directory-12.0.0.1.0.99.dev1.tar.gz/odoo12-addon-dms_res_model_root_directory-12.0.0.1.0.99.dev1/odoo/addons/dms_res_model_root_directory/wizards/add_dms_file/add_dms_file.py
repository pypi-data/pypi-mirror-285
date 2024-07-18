from odoo import fields, api, models


class AddDmsFileWizard(models.TransientModel):
    _name = "add.dms.file.wizard"
    _description = "Add document to current model instance"
    file_data = fields.Binary(string="File", required=True)
    file_name = fields.Char(
        string="File Name",
        required=True,
    )
    root_directory_id = fields.Many2one(
        "dms.directory",
        string="Root directory",
        required=True,
    )
    res_model = fields.Char()

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["res_model"] = self.env.context["active_model"]
        return defaults

    def add_dms_file(self):
        dms_file_vals_list = []
        create_params = {
            "name": self.file_name,
            "content": self.file_data,
            "root_directory_id": self.root_directory_id.id,
            "res_model": self.res_model,
            "res_id": False,
        }
        for res_id in self.env.context.get("active_ids"):
            create_params["res_id"] = res_id
            dms_file_vals_list.append(create_params)

        self.env["dms.file"].create(dms_file_vals_list)

        return {"type": "ir.actions.act_window_close"}
