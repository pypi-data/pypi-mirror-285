from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class DMSDirectory(models.Model):
    _inherit = "dms.directory"

    name = fields.Char(string="Name", required=True, index=True, translate=True)

    @api.constrains("res_model", "category_id", "is_root_directory")
    def _check_unique_root_directory_with_same_model_and_category(self):
        for record in self:
            if record.is_root_directory and record.category_id:
                domain = [
                    ("res_model", "=", record.res_model),
                    ("category_id", "=", record.category_id.id),
                    ("is_root_directory", "=", True),
                ]
                if self.search_count(domain) > 1:
                    raise ValidationError(
                        _(
                            """
                            No more than one root directory with the
                            same model and category is allowed!
                            """
                        )
                    )
