from odoo.tests import common

from ...services.record_directory_service import RecordDirectoryService


class TestRecordDirectoryService(common.TransactionCase):
    def setUp(self):
        super(TestRecordDirectoryService, self).setUp()
        self.record = self.env["res.partner"].create({"name": "Test Partner"})
        self.parent_directory = self.env.ref(
            "dms_res_model_root_directory.insurance_data_directory"
        )

    def test_get_record_directory_under_parent_directory_found(self):
        # Create a directory under the parent directory
        directory = self.env["dms.directory"].create(
            {
                "name": self.record.name,
                "res_id": self.record.id,
                "res_model": self.record._name,
                "parent_id": self.parent_directory.id,
            }
        )

        service = RecordDirectoryService(self.env)
        result = service.get_record_directory_under_parent_directory(
            self.record, self.parent_directory
        )

        assert result == directory

    def test_get_record_directory_under_parent_directory_not_found(self):
        service = RecordDirectoryService(self.env)
        result = service.get_record_directory_under_parent_directory(
            self.record, self.parent_directory
        )

        assert type(result) == self.env["dms.directory"].__class__
        assert result.name == self.record.name
        assert result.res_id == self.record.id
        assert result.res_model == self.record._name
        assert result.parent_id == self.parent_directory

    def test_search_record_directory_under_parent_directory_not_found(self):
        service = RecordDirectoryService(self.env)
        result = service.search_record_directory_under_parent_directory(
            self.record, self.parent_directory
        )
        assert not result
