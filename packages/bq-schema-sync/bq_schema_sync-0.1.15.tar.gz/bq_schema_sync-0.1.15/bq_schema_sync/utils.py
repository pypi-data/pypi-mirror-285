import logging
import os
import yaml


def setup_logging(level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level
    )
    logger = logging.getLogger(__name__)
    return logger


def load_config(config_path):
    """Load the appropriate configuration file based on the environment."""
    environment = os.getenv('ENVIRONMENT', 'develop')

    # Remove any existing environment suffix before appending the current environment
    base_name, ext = os.path.splitext(config_path)
    if base_name.endswith('.develop') or base_name.endswith('.main'):
        base_name = base_name.rsplit('.', 1)[0]

    config_file = f'{base_name}.{environment}{ext}'
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def init_config():
    """Initialize a template configuration file."""
    template_config = {
        'project_id': 'your-gcp-project-id',
        'dataset_id': 'your-dataset-id',
        'table_id': 'your-table-id',
        'schema': {
            'fields': [
                {'name': 'id', 'type': 'STRING', 'mode': 'REQUIRED', 'description': 'Unique identifier'},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'mode': 'NULLABLE',
                 'description': 'Record creation timestamp'}
            ]
        }
    }

    with open('config.yaml', 'w') as file:
        yaml.dump(template_config, file, default_flow_style=False)
    logger = setup_logging()
    logger.info("Template config.yaml created successfully.")


def validate_config(config):
    """Validate the configuration file."""
    required_fields = ['project_id', 'dataset_id', 'table_id', 'schema']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required configuration field: {field}")

    if 'fields' not in config['schema']:
        raise ValueError("Missing 'fields' in schema configuration")
