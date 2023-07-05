from google.cloud import bigquery
from typing import List


class BigQueryClient:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)

    def upload_data(self, dataset_id, table_id, data: List[dict]):
        dataset_ref = self.client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)

        errors = self.client.insert_rows_json(table_ref, data)
        if errors:
            raise Exception(f"Error inserting rows: {errors}")

    def get_table_data(self, dataset_id, table_id) -> List[dict]:
        query = f'SELECT Date, Payee, Category, Amount FROM `{dataset_id}.{table_id}`'

        query_job = self.client.query(query)
        rows = query_job.result()
        rows_list = list(rows)
        print(f"Download {len(rows_list)} rows from BigQuery")

        return rows_list
