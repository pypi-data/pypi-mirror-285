import unittest
from bq_schema_sync.schema_sync import SchemaSync
from google.cloud import bigquery
from unittest.mock import MagicMock


class TestSchemaSync(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=bigquery.Client)
        self.schema = {
            "fields": [
                {"name": "id", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier"},
                {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "Record creation timestamp"}
            ]
        }
        self.schema_sync = SchemaSync(
            project_id="test_project",
            dataset_id="test_dataset",
            table_id="test_table",
            schema=self.schema,
            client=self.mock_client,
            dry_run=True
        )

    def test_compare_schemas(self):
        # Add your test implementation here
        pass

    def test_load_schema(self):
        # Add your test implementation here
        pass


if __name__ == '__main__':
    unittest.main()
