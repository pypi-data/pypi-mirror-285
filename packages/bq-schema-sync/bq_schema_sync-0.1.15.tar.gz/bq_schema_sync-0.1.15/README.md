# bq-schema-sync

`bq-schema-sync` is a Python package designed to help synchronize Google BigQuery table schemas with local schema definitions. It provides tools for comparing schemas, applying changes, validating schema definitions, generating migration scripts, managing schema versions, and enforcing schema validation rules.

## Features

- **Schema Comparison**: Identify differences between local schema definitions and BigQuery table schemas.
- **Schema Synchronization**: Apply changes to BigQuery table schemas based on local definitions.
- **Validation**: Ensure that local schema definitions adhere to BigQuery constraints and best practices.
- **Migration Script Generation**: Generate SQL scripts to manually apply schema changes.
- **Schema Versioning**: Track schema changes over time, save versions, list versions, and apply specific versions.
- **Dry Run Mode**: Preview changes without applying them to the BigQuery table.
- **Schema Validation Rules**: Enforce custom validation rules to ensure schema definitions meet specific criteria.

## Installation

You can install `bq-schema-sync` using pip:

    pip install bq-schema-sync

## Usage

### Command-Line Interface (CLI)

#### Initialize Configuration

Generate a template configuration file:

    bq-schema-sync init

#### Compare Schemas

Compare the local schema with the BigQuery table schema:

    bq-schema-sync compare --config config.yaml --dry-run

#### Apply Changes

Sync the local schema with the BigQuery table schema:

    bq-schema-sync apply --config config.yaml --dry-run

#### Generate Migration Script

Generate a SQL script for manual schema migration:

    bq-schema-sync generate-script --config config.yaml --output migration.sql

#### Validate Schema

Validate the local schema against BigQuery constraints and custom validation rules:

    bq-schema-sync validate --config config.yaml

#### Save Schema Version

Save the current schema version with a description:

    bq-schema-sync save-version --config config.yaml --description "Added new field 'email'"

#### List Schema Versions

List all saved schema versions:

    bq-schema-sync list-versions --config config.yaml

#### Apply Schema Version

Apply a specific schema version:

    bq-schema-sync apply-version --config config.yaml --version 1

### Python API

You can also use `bq-schema-sync` as a Python module:

    from bq_schema_sync import SchemaSync
    from google.cloud import bigquery

    # Initialize SchemaSync with configuration details
    client = bigquery.Client(project='my-gcp-project')
    schema_sync = SchemaSync(
        project_id='my-gcp-project',
        dataset_id='my_dataset',
        table_id='my_table',
        schema={'fields': [{'name': 'id', 'type': 'STRING', 'mode': 'REQUIRED', 'description': 'Unique identifier'}]},
        client=client
    )

    # Compare schemas
    differences = schema_sync.compare_schemas()
    print("Schema Differences:", differences)

    # Apply changes to sync the BigQuery table schema with the local schema
    schema_sync.apply_changes()

    # Generate migration script
    schema_sync.generate_migration_script('migration_scripts/update_my_table_schema.sql')

    # Validate the local schema
    schema_sync.validate_schema()

    # Save the current schema version
    schema_sync.save_version("Initial schema definition")

    # List all schema versions
    versions = schema_sync.list_versions()
    for version in versions:
        print(f"Version: {version['version']}, Timestamp: {version['timestamp']}, Description: {version['description']}")

    # Apply a specific schema version
    schema_sync.apply_version(1)

## Configuration File

The configuration file should be in YAML format and include the following details:

    project_id: your-gcp-project-id
    dataset_id: your-dataset-id
    table_id: your-table-id
    schema:
      fields:
        - name: id
          type: STRING
          mode: REQUIRED
          description: "Unique identifier"
        - name: created_at
          type: TIMESTAMP
          mode: NULLABLE
          description: "Record creation timestamp"

## Example Schema

Here is an example schema file in YAML format (`config.yaml`):

    project_id: your-gcp-project-id
    dataset_id: your-dataset-id
    table_id: your-table-id
    schema:
      fields:
        - name: id
          type: STRING
          mode: REQUIRED
          description: "Unique identifier"
        - name: created_at
          type: TIMESTAMP
          mode: NULLABLE
          description: "Record creation timestamp"

## Testing

You can run tests using `unittest`:

    python -m unittest discover tests

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Author

This project is developed and maintained by Victor Hasim Elexpe Ahamri. You can follow me on Twitter [@victorelexpe](https://twitter.com/victorelexpe) and visit my website [elexpe.dev](https://elexpe.dev).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
