from odoo.tests import TransactionCase
from unittest.mock import patch


class TestAddDMSFileWizard(TransactionCase):
    @patch("odoo.addons.dms_res_model_root_directory.models.dms_file.File.create")
    def test_add_document(self, create_mock):
        root_directory = self.env.ref(
            "dms_res_model_root_directory.insurance_data_directory"
        )
        partner = self.env["res.partner"].create({"name": "Test partner"})
        add_file_wizard = (
            self.env["add.dms.file.wizard"]
            .with_context(
                {
                    "active_model": partner._name,
                    "active_ids": [partner.id],
                }
            )
            .create(
                {
                    "file_name": "File name",
                    "file_data": b"0000",
                    "root_directory_id": root_directory.id,
                }
            )
        )

        add_file_wizard.add_dms_file()

        create_mock.assert_called_once_with(
            [
                {
                    "res_model": partner._name,
                    "res_id": partner.id,
                    "name": add_file_wizard.file_name,
                    "content": add_file_wizard.file_data,
                    "root_directory_id": add_file_wizard.root_directory_id.id,
                }
            ]
        )
