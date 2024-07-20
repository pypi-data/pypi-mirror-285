import json
import yaml
import re
from datetime import datetime
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError


class SchemaSync:
    def __init__(self, project_id, dataset_id, table_id, schema, client=None, dry_run=False):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.schema = schema
        self.client = client or bigquery.Client(project=project_id)
        self.dry_run = dry_run
        self.metadata_table = f"{project_id}.{dataset_id}.schema_versions"
        self._ensure_metadata_table()

    def _ensure_metadata_table(self):
        dataset_ref = self.client.dataset(self.dataset_id)
        table_ref = dataset_ref.table('schema_versions')

        try:
            self.client.get_table(table_ref)
        except GoogleAPIError:
            schema = [
                bigquery.SchemaField("version", "INT64", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("schema", "STRING", mode="REQUIRED"),
            ]
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table)
            print(f"Created metadata table {self.metadata_table}")

    def validate_custom_rules(self):
        required_fields = ["id"]
        allowed_types = {"STRING", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP"}
        naming_convention = re.compile("^[a-z0-9_]+$")

        for field in self.schema['fields']:
            if 'name' not in field or 'type' not in field:
                raise ValueError("Each field must have a 'name' and 'type'")
            if field['name'] in required_fields:
                required_fields.remove(field['name'])
            if field['type'] not in allowed_types:
                raise ValueError(f"Field '{field['name']}' has an invalid type '{field['type']}'")
            if not naming_convention.match(field['name']):
                raise ValueError(f"Field '{field['name']}' does not follow the naming convention")

        if required_fields:
            raise ValueError(f"Missing required fields: {', '.join(required_fields)}")

    def compare_schemas(self):
        try:
            table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
            table = self.client.get_table(table_ref)
            current_schema = {field.name: field.to_api_repr() for field in table.schema}
            local_schema = {field['name']: field for field in self.schema['fields']}
            differences = self._diff_schemas(current_schema, local_schema)
            return differences
        except GoogleAPIError as e:
            raise RuntimeError(f"Failed to compare schemas: {e}")

    def _diff_schemas(self, current_schema, local_schema):
        differences = {
            'added': [field for field in local_schema if field not in current_schema],
            'removed': [field for field in current_schema if field not in local_schema],
            'modified': [
                field for field in local_schema
                if field in current_schema and local_schema[field] != current_schema[field]
            ]
        }
        return differences

    def apply_changes(self):
        self.validate_custom_rules()  # Validate schema rules before applying changes
        differences = self.compare_schemas()
        if self.dry_run:
            print("Dry run mode: The following changes would be applied:")
            print("Added fields:", differences['added'])
            print("Removed fields:", differences['removed'])
            print("Modified fields:", differences['modified'])
        else:
            try:
                # Apply schema changes based on differences (implementation specific)
                print("Changes Applied:", differences)
            except GoogleAPIError as e:
                raise RuntimeError(f"Failed to apply schema changes: {e}")

    def generate_migration_script(self, output_path):
        differences = self.compare_schemas()
        try:
            with open(output_path, 'w') as file:
                for field in differences['added']:
                    file.write(f"ALTER TABLE {self.dataset_id}.{self.table_id} ADD COLUMN {field}...\n")
                for field in differences['removed']:
                    file.write(f"ALTER TABLE {self.dataset_id}.{self.table_id} DROP COLUMN {field}...\n")
                for field in differences['modified']:
                    file.write(f"ALTER TABLE {self.dataset_id}.{self.table_id} ALTER COLUMN {field}...\n")
        except IOError as e:
            raise RuntimeError(f"Failed to write migration script: {e}")

    def validate_schema(self):
        try:
            self.validate_custom_rules()  # Validate schema rules during validation
            print("Schema Validated")
        except Exception as e:
            raise RuntimeError(f"Failed to validate schema: {e}")

    def save_version(self, description):
        self.validate_custom_rules()  # Validate schema rules before saving version
        version_num = self._get_next_version_number()
        version_data = {
            'version': version_num,
            'timestamp': datetime.utcnow(),
            'description': description,
            'schema': json.dumps(self.schema)
        }
        self.client.insert_rows_json(self.metadata_table, [version_data])
        print(f"Schema version {version_num} saved successfully.")

    def list_versions(self):
        query = f"SELECT version, timestamp, description FROM `{self.metadata_table}` ORDER BY version"
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]

    def apply_version(self, version_num):
        query = f"SELECT schema FROM `{self.metadata_table}` WHERE version = {version_num}"
        query_job = self.client.query(query)
        result = query_job.result()
        row = next(result, None)
        if row is None:
            raise ValueError(f"Version {version_num} not found.")
        self.schema = json.loads(row['schema'])
        self.validate_custom_rules()  # Validate schema rules after applying version
        print(f"Schema version {version_num} applied successfully.")

    def _get_next_version_number(self):
        query = f"SELECT MAX(version) as max_version FROM `{self.metadata_table}`"
        query_job = self.client.query(query)
        result = query_job.result()
        row = next(result, None)
        if row and row['max_version'] is not None:
            return row['max_version'] + 1
        else:
            return 1
