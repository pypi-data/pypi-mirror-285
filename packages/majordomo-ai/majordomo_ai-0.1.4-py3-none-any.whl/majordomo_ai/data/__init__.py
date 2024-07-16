"""
The data module
"""

from .dataset import (
        create_dataset_from_documents, 
        )

from .utils import (
    setup_webpage_data_source,
    setup_azure_data_source,
    setup_aws_data_source,
    setup_slack_data_source,
    setup_local_data_source,
    setup_dataset,
    setup_image_database,
        )

from .tables import (
        create_table_from_csv, 
        sql_tables_query,
        fetch_image_from_sql,
        )

