
import os
 
from ..core.base import Tool
from .terminal import shell_helper


class GetBigQueryTableSchema(Tool):
    def call(
        self,
        project: str, 
        dataset: str,
        table: str,
        billing_project: str,
        include_description: bool = False
    ) -> dict:
        """Given a list of fully-specified tables, retrieve the schema for 
        each table in the list.

        Args:
            project (str): Project of the table
            dataset (str): Dataset of the table
            table (str): Table name or "*" to get all tables in the dataset.
            billing_project (str): The project to be billed for the query.
            include_description (bool): Whether to include the description of the column.
                Defaults to False.

        Returns:
            dict: A dictionary with table full names as keys and their schema as values.

        Usage:
            get_table_schemas(
                project='bigquery-public-dataset',
                dataset='stackoverflow',
                table='comments',
                billing_project="YOUR_BILLING_PROJECT"
            )
        """
        try:
            import bigquery
        except ImportError:
            raise ImportError("You need to install the google-cloud-bigquery package to use this tool.")

        client = bigquery.Client(project=billing_project)
        schema_info = {}

        if table == "*":
            table_ids = [f"{project}.{dataset}.{table.table_id}" for table in client.list_tables(dataset)]
        else:
            table_ids = [f"{project}.{dataset}.{table}"]

        output = ""
        for table_id in table_ids:
            table_ref = client.get_table(table_id)  # Make an API request.
            schema_info[table_id] = [field.to_api_repr() for field in table_ref.schema]

            for k,v in schema_info.items():
                output += f"\n{k}"
                for field in v:
                    output += f"\n\t{field['name']}\t{field['type']}"
                    if include_description:
                        output += f"\t{field.get('description', '')}"

        return output


class AuthenticateToGCP(Tool):
    _require_confirmation = True

    def call(self):
        """
        You must run this tool once before using any google cloud CLI tools such as 
        `gcloud` or `bq`.
        """

        # check if the GOOGLE_APPLICATION_CREDENTIALS environment variable is set
        if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            raise ValueError(
                "You must set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key file."
            )

        # authenticate to gcloud
        shell_helper("gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS")
