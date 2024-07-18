class RecordDirectoryService:
    def __init__(self, env):
        self.env = env
        self.directory_env = env["dms.directory"]

    def get_record_directory_under_parent_directory(self, record, parent_directory):
        """
        Get (or create if not found) record directory
        under parent directory recived as parameter
        """
        directory = self.search_record_directory_under_parent_directory(
            record, parent_directory
        )
        if not directory:
            directory = self.directory_env.create(
                {
                    "name": record.name,
                    "res_id": record.id,
                    "res_model": record._name,
                    "parent_id": parent_directory.id,
                    "category_id": parent_directory.category_id.id,
                }
            )

        return directory

    def search_record_directory_under_parent_directory(self, record, parent_directory):
        """
        Search record directory under parent directory
        """

        return self.directory_env.search(
            [
                ("res_id", "=", record.id),
                ("res_model", "=", record._name),
                ("parent_id", "=", parent_directory.id),
            ],
            limit=1,
        )
