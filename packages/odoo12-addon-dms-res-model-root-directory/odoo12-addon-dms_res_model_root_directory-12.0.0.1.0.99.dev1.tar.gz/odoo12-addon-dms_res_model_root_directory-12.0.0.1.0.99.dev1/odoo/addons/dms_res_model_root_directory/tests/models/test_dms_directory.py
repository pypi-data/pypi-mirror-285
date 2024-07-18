from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDMSDirectory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.directory_env = self.env["dms.directory"]
        self.root_directory = self.env.ref(
            "dms_res_model_root_directory.insurance_data_directory"
        )

    def test_unique_directory_params_root(self):
        directory_vals = {
            "name": "Copy directory",
            "is_root_directory": True,
            "model_id": self.root_directory.model_id.id,
            "res_model": self.root_directory.res_model,
            "category_id": self.root_directory.category_id.id,
        }

        self.assertRaises(ValidationError, self.directory_env.create, directory_vals)

    def test_unique_directory_params_not_root(self):
        model = self.root_directory.model_id
        record = self.env[model.model].create({"name": "Test"})

        directory_vals = {
            "name": "Copy directory",
            "is_root_directory": False,
            "model_id": model.id,
            "res_model": model.model,
            "res_id": record.id,
            "category_id": self.root_directory.category_id.id,
            "parent_id": self.root_directory.id,
        }
        directory = self.directory_env.create(directory_vals)
        assert directory
