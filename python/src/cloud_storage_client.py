import csv
import tempfile
from typing import List
from data_classes import CategorisedTransaction

from google.cloud import storage


class CloudStorageClient:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = storage.Client(project=self.project_id)

    def upload_categorised_transactions(self, bucket_name, data: List[CategorisedTransaction], destination_blob_name):
        bucket = self.client.bucket(bucket_name)

        rows = []
        for transaction in data:
            row_dict = {
                'Date': transaction.date,
                'Payee': transaction.payee,
                'Amount': transaction.amount,
                'Category': transaction.category,
                'Particulars': transaction.particulars,
                'Code': transaction.code,
                'Reference': transaction.reference
            }
            rows.append(row_dict)

        # Create a temporary file to store the CSV data
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)

            # Write the rows to the temporary file
            writer.writeheader()
            writer.writerows(rows)

        # Upload the temporary file to Google Cloud Storage
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file.name)

        # Delete the temporary file
        temp_file.close()

    def download_csv(self, bucket_name, source_blob_name) -> List[dict]:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        # Download the file as a string
        file_contents = blob.download_as_text()

        # Parse the CSV data and convert it to a list of dictionaries
        rows = []
        csv_reader = csv.DictReader(file_contents.splitlines())
        for row in csv_reader:
            rows.append(dict(row))

        print(f"Downloaded {len(rows)} rows from GCS")
        return rows
