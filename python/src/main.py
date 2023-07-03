import os, datetime
from flask import Flask, request
from category_assigner_v2 import process
from bigquery_client import BigQueryClient
from cloud_storage_client import CloudStorageClient
from data_classes import TransactionOriginal, KnownPayee

app = Flask(__name__)

PROJECT_ID = os.environ["project_id"]
DATASET_ID = os.environ["bq_dataset"]
TABLE_ID = os.environ["bq_table"]

bigquery_client = BigQueryClient(project_id=PROJECT_ID)
gcs_client = CloudStorageClient(project_id=PROJECT_ID)


@app.route('/', methods=['POST'])
def index():
    body = request.json
    print(body)
    bucket = body["bucket"]
    name = body["name"]

    if not name.endswith(".csv"):
        return "No csv object detected", 200

    name_parts = name.split("/")
    directory = name_parts[0]

    message = "Invalid directory"

    if directory == "to_process":
        data_to_categorise = gcs_client.download_csv(bucket_name=bucket, source_blob_name=name)
        categorised_data = bigquery_client.get_table_data(dataset_id=DATASET_ID, table_id=TABLE_ID)

        data_to_categorise_mapped = [TransactionOriginal.create_from_dict(row) for row in data_to_categorise]
        categorised_data_mapped = [KnownPayee.create_from_bq(row) for row in categorised_data]
        predicted_data = process(data_to_categorise_mapped, categorised_data_mapped)
        current_timestamp = datetime.datetime.now().timestamp()
        formatted_timestamp = datetime.datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d%H:%M:%S')
        gcs_client.upload_categorised_transactions(bucket_name=bucket, data=predicted_data, destination_blob_name=f"staging/{formatted_timestamp}.csv")
        message = f"Processed file to categorise: {name}"
    # elif directory == "processed":
    #     print(f"Inserting gs://{bucket}/{name} into {DATASET_ID}:{TABLE_ID}")
    #     bigquery_client.insert_from_gcs(gcs_uri=f"gs://{bucket}/{name}", dataset_id=DATASET_ID, table_id=TABLE_ID)
    #     message = f"Inserted gs://{bucket}/{name} into BigQuery"
    elif directory == "staging":
        message = "File upload to staging directory"
    return message, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
