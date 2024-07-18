from odoo.tests import TransactionCase
from unittest.mock import patch
from ...services.record_directory_service import RecordDirectoryService


class TestDMSFile(TransactionCase):
    def setUp(self):
        super().setUp()
        self.file_env = self.env["dms.file"]
        self.root_directory = self.env.ref(
            "dms_res_model_root_directory.insurance_data_directory"
        )
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.partner_directory = self.env["dms.directory"].create(
            {
                "name": "Existing directory",
                "res_id": self.partner.id,
                "res_model": self.partner._name,
                "parent_id": self.root_directory.id,
            }
        )
        self.file_vals = {
            "name": "Test File",
            "root_directory_id": self.root_directory.id,
            "res_id": self.partner.id,
            "res_model": self.partner._name,
            "content": b"0000",
        }

    @patch.object(
        RecordDirectoryService, "get_record_directory_under_parent_directory"
    )  # noqa
    def test_create_file_with_directory(self, mock_get_directory):
        # Mock the RecordDirectoryService to return a created directory
        mock_get_directory.return_value = self.partner_directory

        file = self.file_env.create([self.file_vals])

        mock_get_directory.assert_called_once_with(self.partner, self.root_directory)
        assert file.directory_id == self.partner_directory
        assert file.res_id == self.partner.id
        assert file.res_model == self.partner._name

    @patch.object(
        RecordDirectoryService, "get_record_directory_under_parent_directory"
    )  # noqa
    @patch("odoo.addons.dms.models.dms_file.File.create")  # noqa
    def test_create_file_params(self, mock_file_create, mock_get_directory):
        # Mock the RecordDirectoryService to return a created directory
        mock_get_directory.return_value = self.partner_directory

        self.file_env.create([self.file_vals])

        expected_params = {
            "name": "Test File",
            "directory_id": self.partner_directory.id,
            "content": b"0000",
        }
        mock_file_create.assert_called_once_with([expected_params])
